import re
import os
from typing import Dict, Any, List, Optional
import docx
import pdfplumber
import pypdf

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b')
LINKEDIN_REGEX = re.compile(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+', re.IGNORECASE)
GITHUB_REGEX = re.compile(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+', re.IGNORECASE)

SECTION_KEYWORDS = {
    "experience": ["experience", "work history", "employment", "professional experience", "work experience"],
    "education": ["education", "academic background", "degrees", "qualifications"],
    "skills": ["skills", "technical skills", "technologies", "competencies", "core competencies"],
    "projects": ["projects", "personal projects", "key projects", "selected projects"],
    "certifications": ["certifications", "licenses", "certificates", "accreditations"],
    "summary": ["summary", "professional summary", "about me", "profile"]
}

def extract_text_from_pdf(file_path: str) -> Dict[str, Any]:
    """
    Extracts text and layout metrics from a PDF file using pdfplumber with fallback to pypdf.
    """
    full_text = []
    page_count = 0
    tables_found = 0
    images_found = 0
    has_columns_suspected = False

    try:
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text(layout=False) or ""
                full_text.append(text)
                
                # Check for tables
                try:
                    tables = page.extract_tables()
                    if tables:
                        tables_found += len(tables)
                except Exception:
                    pass

                # Check for images / figures
                try:
                    if hasattr(page, 'images') and page.images:
                        images_found += len(page.images)
                except Exception:
                    pass

                # Heuristic for multi-column layout:
                # Compare words x0 distribution across left/right quadrants
                try:
                    words = page.extract_words()
                    if words and len(words) > 30:
                        midpoint = page.width / 2
                        left_words = sum(1 for w in words if w['x1'] < midpoint)
                        right_words = sum(1 for w in words if w['x0'] > midpoint)
                        ratio = min(left_words, right_words) / max(left_words, right_words, 1)
                        if ratio > 0.45 and right_words > 15:
                            has_columns_suspected = True
                except Exception:
                    pass
    except Exception as e:
        # Fallback to pypdf
        full_text = []
        try:
            reader = pypdf.PdfReader(file_path)
            page_count = len(reader.pages)
            for page in reader.pages:
                t = page.extract_text() or ""
                full_text.append(t)
        except Exception as fallback_err:
            raise RuntimeError(f"Failed to parse PDF: {str(e)} | Fallback error: {str(fallback_err)}")

    raw_text = "\n\n".join(full_text).strip()
    return {
        "text": raw_text,
        "page_count": page_count,
        "tables_count": tables_found,
        "images_count": images_found,
        "has_columns_suspected": has_columns_suspected,
        "char_count": len(raw_text),
        "word_count": len(raw_text.split())
    }

def extract_text_from_docx(file_path: str) -> Dict[str, Any]:
    """
    Extracts text and structure from a DOCX file using python-docx.
    """
    doc = docx.Document(file_path)
    paragraphs_text = []
    
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            paragraphs_text.append(t)
            
    tables_found = len(doc.tables)
    table_texts = []
    for table in doc.tables:
        for row in table.rows:
            row_vals = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_vals:
                table_texts.append(" | ".join(row_vals))

    combined_text = "\n".join(paragraphs_text + table_texts).strip()
    
    return {
        "text": combined_text,
        "page_count": max(1, len(combined_text) // 2500), # rough estimate for docx
        "tables_count": tables_found,
        "images_count": 0,
        "has_columns_suspected": False,
        "char_count": len(combined_text),
        "word_count": len(combined_text.split())
    }

ACTION_VERBS = {
    "built", "developed", "engineered", "designed", "implemented", "created", "maintained",
    "optimized", "architected", "wrote", "collaborated", "integrated", "automated", "led",
    "trained", "configured", "deployed", "constructed", "resolved", "refactored", "managed",
    "analyzed", "fine-tuned", "reduced", "increased", "accelerated", "served", "orchestrated",
    "evaluated", "migrated", "scaled", "authored", "achieved", "delivered", "programmed"
}

EDUCATION_INDICATORS = [
    "university", "college", "institute", "bachelor", "master", "b.e", "b.tech", "m.tech",
    "b.s", "m.s", "ph.d", "cgpa", "gpa", "expected", "degree", "school", "high school",
    "matriculation", "coursework", "secondary"
]

def is_education_or_contact_line(line: str) -> bool:
    lower = line.lower()
    if any(ind in lower for ind in EDUCATION_INDICATORS):
        return True
    if EMAIL_REGEX.search(line) or PHONE_REGEX.search(line):
        return True
    if "linkedin.com" in lower or "github.com" in lower or ".vercel.app" in lower or "http" in lower:
        return True
    if re.search(r'\b\d{1,2}\.\d{1,2}\s*/\s*10\b', lower) or re.search(r'\b[234]\.\d{1,2}\s*/\s*4\b', lower):
        return True
    return False

MONTH_DATE_PATTERN = re.compile(
    r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b',
    re.IGNORECASE
)
YEAR_RANGE_PATTERN = re.compile(
    r'\b(?:20\d\d|19\d\d)\s*[-–—]\s*(?:20\d\d|present|expected|current)\b',
    re.IGNORECASE
)

def is_role_or_project_header(line: str) -> bool:
    """Detects company names, role titles, and date lines that serve as section subheadings."""
    clean_line = line.strip()
    if not clean_line:
        return False
    lower = clean_line.lower()

    # Prefixes like "Role:", "Project:", "Company:", "Experience:"
    if re.match(r'^(?:role|project|company|position|organization|client)\s*:\s*', lower):
        return True

    # Contains dates like "May 2026", "2022 - Present", "Jun 2023 - Dec 2024"
    if MONTH_DATE_PATTERN.search(clean_line) or YEAR_RANGE_PATTERN.search(clean_line):
        return True
    if " - present" in lower or "| present" in lower or "expected may" in lower:
        return True

    # Multi-field header like "Software Engineer | Acme Corp | 2022"
    if "|" in clean_line and len(clean_line.split("|")) >= 2:
        return True

    # Common role titles or simulations without bullets
    title_keywords = [
        "engineer", "developer", "simulation", "intern", "internship", "architect", 
        "lead", "specialist", "fellow", "contributor", "forage", "consultant"
    ]
    if any(tk in lower for tk in title_keywords) and len(clean_line.split()) <= 12 and not clean_line.startswith(("•", "-", "*")):
        if not clean_line.endswith("."):
            return True

    return False

def extract_experience_bullets(text: str) -> List[Dict[str, Any]]:
    """
    Intelligently extracts genuine work experience and project bullets from resume text.
    Strictly excludes contact headers, college/degree lines, and company/role title lines.
    """
    lines = text.split("\n")
    bullets = []
    
    current_section = "Experience"
    current_role_or_project = "Work Experience"
    
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
            
        lower_line = line.lower()
        clean_line = re.sub(r'[^a-zA-Z\s]', '', lower_line).strip()
        
        # Section detection
        if clean_line in ["education", "academic background", "academics"]:
            current_section = "Education"
            continue
        elif clean_line in ["skills", "technical skills", "technologies", "core competencies"]:
            current_section = "Skills"
            continue
        elif clean_line in ["experience", "work experience", "professional experience", "employment", "work history"]:
            current_section = "Experience"
            continue
        elif clean_line in ["projects", "key projects", "selected projects", "personal projects", "technical projects"]:
            current_section = "Projects"
            continue
        elif clean_line in ["certifications", "achievements", "honors", "awards"]:
            current_section = "Certifications"
            continue
            
        # Ignore lines in Education, Skills, or Certifications sections
        if current_section in ["Education", "Skills", "Certifications"]:
            continue
            
        # Check if line is contact info or education leak
        if is_education_or_contact_line(line):
            continue
            
        # Check if line is a role/project header (company name, simulation title, date line)
        if is_role_or_project_header(line):
            # Clean up the context string: remove raw date suffixes, prefixes, and platform tags
            cleaned_title = re.sub(r'^(?:role|project|company|position|organization)\s*:\s*', '', line, flags=re.IGNORECASE)
            cleaned_title = re.sub(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b', '', cleaned_title, flags=re.IGNORECASE)
            cleaned_title = re.sub(r'\b(?:20\d\d|19\d\d)\s*[-–—]\s*(?:20\d\d|present|expected|current)\b', '', cleaned_title, flags=re.IGNORECASE)
            cleaned_title = re.sub(r'\((?:forage|remote|hybrid|contract|internship)\)', '', cleaned_title, flags=re.IGNORECASE)
            cleaned_title = re.sub(r'\|\s*', ' - ', cleaned_title)
            cleaned_title = re.sub(r'[-–—]\s*(?:present|expected|current)\b', '', cleaned_title, flags=re.IGNORECASE)
            cleaned_title = re.sub(r'\s*-\s*-\s*', ' - ', cleaned_title)
            cleaned_title = re.sub(r'\s{2,}', ' ', cleaned_title).strip(" -|,\t ")
            current_role_or_project = cleaned_title if len(cleaned_title) > 3 else "Engineering Project"
            continue

        # Detect if this is an actual bullet point
        is_bullet = False
        stripped_bullet = line
        
        if line.startswith(("•", "-", "*", "–", "—")):
            is_bullet = True
            stripped_bullet = line.lstrip("•-*–— ").strip()
        elif re.match(r'^\d+[\.\)]\s+', line):
            is_bullet = True
            stripped_bullet = re.sub(r'^\d+[\.\)]\s+', '', line).strip()
        else:
            first_word = clean_line.split()[0] if clean_line.split() else ""
            if first_word in ACTION_VERBS and len(clean_line.split()) >= 6:
                is_bullet = True
                stripped_bullet = line

        # Only accept if it looks like a real sentence describing work done
        if is_bullet and len(stripped_bullet.split()) >= 6:
            # Final sanity check: make sure the bullet itself is not just a role title
            if not is_role_or_project_header(stripped_bullet):
                bullets.append({
                    "section": current_section,
                    "context": current_role_or_project,
                    "bullet": stripped_bullet
                })

    return bullets

def analyze_resume_structure(text: str) -> Dict[str, Any]:
    """
    Detects sections, contact information, and readability indicators.
    """
    lower_text = text.lower()
    
    # 1. Contact Info
    emails = list(set(EMAIL_REGEX.findall(text)))
    phones = list(set(PHONE_REGEX.findall(text)))
    phones = [p.strip() for p in phones if len(re.sub(r'\D', '', p)) >= 10]
    linkedin = list(set(LINKEDIN_REGEX.findall(text)))
    github = list(set(GITHUB_REGEX.findall(text)))
    
    contact_info = {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
        "has_email": len(emails) > 0,
        "has_phone": len(phones) > 0,
        "has_links": (len(linkedin) + len(github)) > 0
    }
    
    # 2. Section detection
    lines = [line.strip().lower() for line in text.split("\n") if line.strip()]
    detected_sections = {}
    
    for sec_name, keywords in SECTION_KEYWORDS.items():
        found = False
        for line in lines:
            clean_line = re.sub(r'[^a-z\s]', '', line).strip()
            if any(clean_line == kw or clean_line.startswith(kw) for kw in keywords):
                found = True
                break
            if len(clean_line) < 35 and any(kw in clean_line for kw in keywords):
                found = True
                break
        detected_sections[sec_name] = found

    return {
        "contact_info": contact_info,
        "detected_sections": detected_sections,
        "missing_sections": [sec for sec, exists in detected_sections.items() if not exists]
    }

def parse_resume_file(file_path: str, filename: str) -> Dict[str, Any]:
    """
    Main parser entrypoint. Accepts PDF or DOCX and returns comprehensive text and layout metrics.
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        metrics = extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        metrics = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Only .pdf and .docx are supported.")
        
    structure = analyze_resume_structure(metrics["text"])
    
    return {
        "raw_text": metrics["text"],
        "filename": filename,
        "page_count": metrics["page_count"],
        "tables_count": metrics["tables_count"],
        "images_count": metrics["images_count"],
        "has_columns_suspected": metrics["has_columns_suspected"],
        "word_count": metrics["word_count"],
        "char_count": metrics["char_count"],
        "structure": structure
    }
