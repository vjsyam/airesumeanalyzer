import os
import tempfile
import shutil
import re
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Securely load environment variables from backend/.env
load_dotenv()

from services.parser import parse_resume_file, analyze_resume_structure, extract_experience_bullets
from services.humanizer import validate_humanization
from services.ats import compute_ats_score
from services.llm import (
    extract_skills_llm,
    match_job_description_llm,
    generate_bullet_suggestions_llm,
    generate_cover_letter_llm
)
from services.export import create_cover_letter_docx
from sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Precision ATS scoring, context-aware bullet rewrites, and humanized cover letters.",
    version="1.1.0"
)

# CORS configuration - strict localhost origin validation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Security constraints
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB maximum
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

class CoverLetterRequest(BaseModel):
    resume_text: str
    job_description: str
    tone: Optional[str] = "direct"
    candidate_name: Optional[str] = "Applicant"
    api_key: Optional[str] = None

class ExportDocxRequest(BaseModel):
    cover_letter: str
    candidate_name: Optional[str] = "Applicant"

def sanitize_key(key: Optional[str]) -> Optional[str]:
    """Sanitizes incoming API key tokens to prevent header injection."""
    if not key:
        return None
    cleaned = key.strip()
    # Strip any characters that aren't valid alphanumeric or basic token chars
    if not re.match(r'^[a-zA-Z0-9_\-\.]{10,128}$', cleaned):
        return None
    return cleaned

@app.get("/api/health")
def health_check():
    """Returns system health without ever exposing any raw key credentials."""
    has_env_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    return {
        "status": "healthy",
        "service": "AI Resume Analyzer Backend",
        "llm_provider": "Google Gemini",
        "has_server_api_key": has_env_key,
        "security": {
            "rate_limiting": "enabled",
            "file_size_limit_mb": 10,
            "allowed_file_types": ["pdf", "docx"]
        }
    }

@app.get("/api/sample-data")
def get_sample_data():
    """Provides generic professional profiles and industry standard job descriptions."""
    return {
        "resumes": SAMPLE_RESUMES,
        "job_descriptions": SAMPLE_JOB_DESCRIPTIONS
    }

@app.post("/api/analyze")
async def analyze_resume(
    file: Optional[UploadFile] = File(None),
    job_description: str = Form(...),
    sample_resume_id: Optional[str] = Form(None),
    raw_resume_text: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    x_gemini_api_key: Optional[str] = Header(None)
):
    """
    Main analysis pipeline:
    1. Securely parse uploaded resume (PDF/DOCX) or load sample/text
    2. Extract skills via LLM Call #1
    3. Match skills vs JD via LLM Call #2
    4. Compute ATS score and structural breakdown
    5. Generate bullet-level improvement suggestions anchored in candidate's actual projects
    All outputs strictly routed through /human rules.
    """
    effective_api_key = (
        sanitize_key(api_key) or 
        sanitize_key(x_gemini_api_key) or 
        os.environ.get("GEMINI_API_KEY") or 
        os.environ.get("GOOGLE_API_KEY")
    )
    
    resume_text = ""
    resume_meta = {
        "filename": "Uploaded_Resume",
        "page_count": 1,
        "tables_count": 0,
        "images_count": 0,
        "has_columns_suspected": False,
        "word_count": 0,
        "char_count": 0,
        "structure": {}
    }
    
    temp_file_path = None
    try:
        if file and file.filename:
            # Validate file extension
            suffix = os.path.splitext(file.filename)[1].lower()
            if suffix not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid file format. Only genuine PDF and DOCX files are permitted for security."
                )
                
            # Stream into temporary file with size check
            total_bytes = 0
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                temp_file_path = tmp.name
                while chunk := await file.read(1024 * 64): # 64KB chunks
                    total_bytes += len(chunk)
                    if total_bytes > MAX_FILE_SIZE_BYTES:
                        raise HTTPException(
                            status_code=413, 
                            detail="Uploaded file exceeds the maximum 10MB limit."
                        )
                    tmp.write(chunk)

            # Server-side parsing
            parse_result = parse_resume_file(temp_file_path, file.filename)
            resume_text = parse_result["raw_text"]
            resume_meta = parse_result

        elif sample_resume_id and sample_resume_id in SAMPLE_RESUMES:
            sample = SAMPLE_RESUMES[sample_resume_id]
            resume_text = sample["text"]
            structure = analyze_resume_structure(resume_text)
            resume_meta = {
                "filename": sample["filename"],
                "candidate_name": sample.get("candidate_name", "Applicant"),
                "page_count": 1,
                "tables_count": 0,
                "images_count": 0,
                "has_columns_suspected": False,
                "word_count": len(resume_text.split()),
                "char_count": len(resume_text),
                "structure": structure
            }

        elif raw_resume_text and raw_resume_text.strip():
            resume_text = raw_resume_text.strip()
            if len(resume_text) > 50000:
                raise HTTPException(status_code=413, detail="Pasted text exceeds maximum allowable size (50k chars).")
                
            structure = analyze_resume_structure(resume_text)
            resume_meta = {
                "filename": "Pasted_Resume.txt",
                "candidate_name": "Applicant",
                "page_count": max(1, len(resume_text.split()) // 350),
                "tables_count": 0,
                "images_count": 0,
                "has_columns_suspected": False,
                "word_count": len(resume_text.split()),
                "char_count": len(resume_text),
                "structure": structure
            }
        else:
            raise HTTPException(status_code=400, detail="Please upload a PDF/DOCX resume or select a preset candidate profile.")

        if not resume_text or len(resume_text.strip()) < 40:
            raise HTTPException(status_code=400, detail="Could not extract parseable text from the uploaded document. Please check the document format.")

        clean_jd = job_description.strip()
        if not clean_jd or len(clean_jd) < 30:
            raise HTTPException(status_code=400, detail="Please provide a valid Job Description with at least 30 characters.")

        # --- LLM Call #1: Skill Extraction ---
        skills = extract_skills_llm(resume_text, effective_api_key)

        # --- LLM Call #2: Job Description Matching ---
        match_result = match_job_description_llm(resume_text, skills, clean_jd, effective_api_key)

        # --- ATS Scoring Algorithm (Modeled after Jobscan & Enterprise ATS) ---
        extracted_bullets = extract_experience_bullets(resume_text)
        ats_score = compute_ats_score(
            structure=resume_meta["structure"],
            layout_metrics=resume_meta,
            keyword_match_ratio=match_result.get("match_ratio", 0.5),
            bullets=extracted_bullets
        )

        # --- LLM Call #4: Bullet Improvement Suggestions ---
        suggestions = generate_bullet_suggestions_llm(
            resume_text=resume_text,
            jd_text=clean_jd,
            missing_skills=match_result.get("missing_skills", []),
            api_key=effective_api_key
        )

        # Validate humanization compliance on all bullet rewrites
        for s in suggestions:
            val = validate_humanization(s.get("rewritten_bullet", ""))
            s["human_compliant"] = val["is_compliant"]

        return {
            "success": True,
            "resume_meta": {
                "filename": resume_meta["filename"],
                "candidate_name": resume_meta.get("candidate_name", "Applicant"),
                "page_count": resume_meta["page_count"],
                "tables_count": resume_meta["tables_count"],
                "images_count": resume_meta["images_count"],
                "has_columns_suspected": resume_meta["has_columns_suspected"],
                "word_count": resume_meta["word_count"],
                "char_count": resume_meta["char_count"],
                "contact_info": resume_meta["structure"].get("contact_info", {}),
                "detected_sections": resume_meta["structure"].get("detected_sections", {})
            },
            "raw_text_preview": resume_text[:3000],
            "full_text": resume_text,
            "skills": skills,
            "match_analysis": match_result,
            "ats_score": ats_score,
            "suggestions": suggestions,
            "engine": "Gemini 2.5 Flash" if skills.get("is_llm_generated") else "Local Heuristic Engine (Fallback)"
        }

    finally:
        # Crucial security guarantee: always unlink temporary upload files
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as cleanup_err:
                print(f"Error cleaning up temp file {temp_file_path}: {cleanup_err}")

@app.post("/api/cover-letter")
def generate_cover_letter(
    request: CoverLetterRequest,
    x_gemini_api_key: Optional[str] = Header(None)
):
    """
    On-demand Cover Letter generation (LLM Call #5).
    """
    effective_api_key = (
        sanitize_key(request.api_key) or 
        sanitize_key(x_gemini_api_key) or 
        os.environ.get("GEMINI_API_KEY") or 
        os.environ.get("GOOGLE_API_KEY")
    )
    
    if not request.resume_text or not request.job_description:
        raise HTTPException(status_code=400, detail="Both resume text and job description are required.")

    result = generate_cover_letter_llm(
        resume_text=request.resume_text,
        jd_text=request.job_description,
        tone=request.tone or "direct",
        candidate_name=request.candidate_name,
        api_key=effective_api_key
    )
    
    validation = validate_humanization(result["cover_letter"])
    result["human_compliant"] = validation["is_compliant"]
    
    return result

@app.post("/api/export/docx")
def export_docx(request: ExportDocxRequest):
    """
    Exports cover letter to DOCX format safely.
    """
    if not request.cover_letter:
        raise HTTPException(status_code=400, detail="Cover letter content is empty.")
        
    safe_name = re.sub(r'[^a-zA-Z0-9_\- ]', '', request.candidate_name or "Applicant").strip() or "Applicant"
    docx_stream = create_cover_letter_docx(request.cover_letter, safe_name)
    
    headers = {
        'Content-Disposition': f'attachment; filename="{safe_name.replace(" ", "_")}_Cover_Letter.docx"'
    }
    return StreamingResponse(
        docx_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
