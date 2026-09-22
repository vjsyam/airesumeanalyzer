import os
import json
import re
import random
from typing import Dict, Any, List, Optional, Tuple
from google import genai
from google.genai import types
from services.humanizer import humanize_text, HUMAN_SYSTEM_INSTRUCTIONS

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

def get_client(api_key: Optional[str] = None) -> Optional[genai.Client]:
    effective_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if effective_key and effective_key.strip():
        try:
            return genai.Client(api_key=effective_key.strip())
        except Exception as e:
            print(f"Error creating GenAI client: {e}")
            return None
    return None

def clean_json_response(raw_text: str) -> Dict[str, Any]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return json.loads(cleaned)

def call_gemini_json(client: genai.Client, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
    last_err = None
    for model_name in GEMINI_MODELS:
        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
                system_instruction=system_instruction or HUMAN_SYSTEM_INSTRUCTIONS
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            if response and response.text:
                return clean_json_response(response.text)
        except Exception as e:
            last_err = e
            continue
            
    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt + "\n\nRespond ONLY with valid JSON without markdown formatting.",
            )
            if response and response.text:
                return clean_json_response(response.text)
        except Exception as e:
            last_err = e
            continue
            
    raise RuntimeError(f"Gemini API call failed across all models: {last_err}")

def call_gemini_text(client: genai.Client, prompt: str, system_instruction: str = "") -> str:
    last_err = None
    for model_name in GEMINI_MODELS:
        try:
            config = types.GenerateContentConfig(
                temperature=0.35,
                system_instruction=system_instruction or HUMAN_SYSTEM_INSTRUCTIONS
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Gemini API call failed: {last_err}")

# ==========================================
# 1. SKILL EXTRACTION (Single-Purpose LLM Call #1)
# ==========================================
def extract_skills_llm(resume_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    client = get_client(api_key)
    if client:
        prompt = f"""
Analyze the following resume text and extract all explicitly demonstrated technical skills, tools, frameworks, certifications, and domain methodologies.
Do not invent skills not mentioned in the text.

Resume Text:
\"\"\"
{resume_text[:12000]}
\"\"\"

Return a valid JSON object matching this exact schema:
{{
  "technical_skills": ["e.g. Python", "FastAPI", "PostgreSQL", "Docker"],
  "tools_and_platforms": ["e.g. Git", "AWS EC2", "Kubernetes", "Jira"],
  "certifications": ["e.g. AWS Certified Solutions Architect", "CKA"],
  "methodologies": ["e.g. Agile", "CI/CD", "Test-Driven Development", "Microservices"]
}}
"""
        try:
            result = call_gemini_json(client, prompt)
            return {
                "technical_skills": result.get("technical_skills", []),
                "tools_and_platforms": result.get("tools_and_platforms", []),
                "certifications": result.get("certifications", []),
                "methodologies": result.get("methodologies", []),
                "is_llm_generated": True
            }
        except Exception as e:
            print(f"Gemini skill extraction failed ({e}), using fallback parser.")

    return fallback_extract_skills(resume_text)

# ==========================================
# 2. JOB DESCRIPTION MATCHING (Single-Purpose LLM Call #2)
# ==========================================
def match_job_description_llm(
    resume_text: str,
    resume_skills: Dict[str, Any],
    jd_text: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    client = get_client(api_key)
    all_extracted_skills = (
        resume_skills.get("technical_skills", []) +
        resume_skills.get("tools_and_platforms", []) +
        resume_skills.get("certifications", []) +
        resume_skills.get("methodologies", [])
    )

    if client:
        prompt = f"""
Compare the candidate's resume skills against the Job Description.

Candidate's Extracted Skills:
{json.dumps(all_extracted_skills)}

Resume Text Excerpt:
\"\"\"
{resume_text[:8000]}
\"\"\"

Job Description:
\"\"\"
{jd_text[:8000]}
\"\"\"

Task:
1. Identify all skills in the Job Description that the candidate clearly possesses (matched_skills).
2. Identify important skills, libraries, frameworks, or cloud tools mentioned in the Job Description that the candidate does NOT mention or show proof of (missing_skills).
3. Identify domain keywords or specific system concepts in the JD that are absent from the resume (keyword_gaps).
4. Compute an accurate keyword match ratio between 0.0 and 1.0 based on core qualifications.
5. Provide a 2-sentence objective summary of the alignment.

Return a valid JSON object matching this schema:
{{
  "matched_skills": ["Python", "FastAPI", "PostgreSQL"],
  "missing_skills": ["Redis", "Kubernetes", "GraphQL"],
  "keyword_gaps": ["distributed tracing", "high-throughput streaming", "system design"],
  "match_ratio": 0.65,
  "fit_summary": "Strong core engineering alignment with Python and relational databases. Gaps primarily center around container orchestration and caching layers."
}}
"""
        try:
            result = call_gemini_json(client, prompt)
            return {
                "matched_skills": result.get("matched_skills", []),
                "missing_skills": result.get("missing_skills", []),
                "keyword_gaps": result.get("keyword_gaps", []),
                "match_ratio": float(result.get("match_ratio", 0.65)),
                "fit_summary": humanize_text(result.get("fit_summary", "")),
                "is_llm_generated": True
            }
        except Exception as e:
            print(f"Gemini JD match failed ({e}), using fallback matcher.")

    return fallback_match_jd(all_extracted_skills, resume_text, jd_text)

# ==========================================
# 3. BULLET-LEVEL IMPROVEMENT SUGGESTIONS (Single-Purpose LLM Call #4)
# ==========================================
def generate_bullet_suggestions_llm(
    resume_text: str,
    jd_text: str,
    missing_skills: List[str],
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    from services.parser import extract_experience_bullets
    
    extracted_bullets = extract_experience_bullets(resume_text)
    client = get_client(api_key)
    
    if client and extracted_bullets:
        bullet_list_formatted = "\n".join([
            f"- [{b['context']}]: \"{b['bullet']}\""
            for b in extracted_bullets[:10]
        ])
        
        prompt = f"""
{HUMAN_SYSTEM_INSTRUCTIONS}

You are an expert technical resume coach. Your task is to rewrite 3 to 4 of the candidate's ACTUAL work experience or project bullets to better target the provided Job Description.

MANDATORY INTEGRITY CONSTRAINTS:
1. You MUST select original bullets ONLY from the candidate's extracted list below. NEVER invent bullets or rewrite contact info, college names, graduation dates, or degree lines.
2. The rewritten bullet must stay true to the specific domain and project of that bullet. (If the bullet is about frontend UI, improve the UI work. If it is about database/API, improve the backend. If it is about ML/LLM, improve the ML engineering).
3. Do NOT replace a candidate's actual achievement with an unrelated task from a different domain.
4. Upgrade the bullet to:
   - Use strong active voice
   - Incorporate concrete outcomes (latencies, percentages, throughput, scale, test coverage)
   - Naturally integrate relevant technologies or methods from the Job Description
   - Strictly avoid corporate clichés ("results-driven", "spearheaded", "cutting-edge", "leveraged", "team player")
   - Use standard commas/periods, NEVER em-dashes (—)

Candidate's Extracted Experience & Project Bullets:
\"\"\"
{bullet_list_formatted}
\"\"\"

Target Job Description:
\"\"\"
{jd_text[:6000]}
\"\"\"

Missing Skills from JD to optionally weave in where relevant:
{json.dumps(missing_skills[:8])}

Return a valid JSON array of objects with this schema:
[
  {{
    "target_location": "Project: [Project or Role Name]",
    "original_bullet": "[Exact original bullet text from the candidate list]",
    "rewritten_bullet": "[Rewritten, high-impact bullet anchored in the same project with concrete metrics]",
    "rationale": "[1 concise sentence explaining the specific technical improvement made to this bullet]"
  }}
]
"""
        try:
            result = call_gemini_json(client, prompt)
            suggestions = []
            raw_suggestions = result if isinstance(result, list) else result.get("suggestions", [])

            for item in raw_suggestions:
                orig = item.get("original_bullet", "").strip()
                rewritten = item.get("rewritten_bullet", "").strip()
                if orig and rewritten:
                    suggestions.append({
                        "target_location": humanize_text(item.get("target_location", "Work Experience")),
                        "original_bullet": orig,
                        "rewritten_bullet": humanize_text(rewritten),
                        "rationale": humanize_text(item.get("rationale", "").strip())
                    })
            if suggestions:
                return suggestions
        except Exception as e:
            print(f"Gemini bullet suggestions failed ({e}), using fallback generator.")

    return fallback_bullet_suggestions(resume_text, jd_text, missing_skills)

# ==========================================
# 4. COVER LETTER GENERATOR (Single-Purpose LLM Call #5)
# ==========================================
def generate_cover_letter_llm(
    resume_text: str,
    jd_text: str,
    tone: str = "direct",
    candidate_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    client = get_client(api_key)
    
    tone_instructions = {
        "direct": "Concise, technical, and outcome-oriented. 3 short paragraphs. No flowery introductions.",
        "conversational": "Natural, thoughtful, professional peer tone. Sounds like an email to a respected engineering lead.",
        "executive": "Strategic perspective focusing on architectural decisions, team velocity, product reliability, and engineering rigor."
    }.get(tone.lower(), "Concise, technical, and outcome-oriented.")

    if client:
        # Seed variation for dynamic regeneration
        seed_prompt = f"Generation variation seed: {random.randint(100, 99999)}."
        prompt = f"""
{HUMAN_SYSTEM_INSTRUCTIONS}
{seed_prompt}

Write a tailored cover letter from the candidate ({candidate_name or 'the applicant'}) to the hiring team for this Job Description.

Tone requirement: {tone_instructions}

MANDATORY CONSTRAINTS:
- Do NOT sound like a standard AI template. No "I am writing to express my enthusiastic interest...", no "In today's fast-paced landscape...".
- NEVER use clichés: "results-driven", "proven track record", "passionate about", "leverage", "dynamic", "team player", "spearheaded".
- Do NOT use em-dashes (—) or en-dashes (–).
- Highlight 2 specific technical accomplishments or projects from the resume that directly solve problems mentioned in the Job Description.
- Length: 250 to 350 words total across 3 or 4 focused paragraphs.

Candidate Resume:
\"\"\"
{resume_text[:9000]}
\"\"\"

Job Description:
\"\"\"
{jd_text[:6000]}
\"\"\"

Return ONLY the raw cover letter text (with standard salutation and sign-off with {candidate_name or 'the candidate'}).
"""
        try:
            letter = call_gemini_text(client, prompt)
            humanized_letter = humanize_text(letter)
            return {
                "cover_letter": humanized_letter,
                "word_count": len(humanized_letter.split()),
                "tone": tone,
                "is_llm_generated": True
            }
        except Exception as e:
            print(f"Gemini cover letter failed ({e}), using fallback generator.")

    return fallback_generate_cover_letter(resume_text, jd_text, tone, candidate_name)

# ==========================================
# HIGH-FIDELITY SEMANTIC FALLBACK IMPLEMENTATIONS
# ==========================================
KNOWN_TECH_DICTIONARY = [
    "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++", "C#", "Ruby", "PHP", "SQL",
    "React", "Next.js", "Vue", "Angular", "Node.js", "Express", "FastAPI", "Django", "Flask",
    "Spring Boot", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "Git", "GitHub Actions", "CI/CD",
    "GraphQL", "REST", "gRPC", "Kafka", "RabbitMQ", "Microservices", "Linux", "Tailwind CSS",
    "PyTorch", "TensorFlow", "Pandas", "NumPy", "Scikit-Learn", "LangChain", "OpenAI API", "Gemini API",
    "WebSockets", "Supabase", "Jest", "PyTest", "Postman", "Vercel"
]

def fallback_extract_skills(text: str) -> Dict[str, Any]:
    found_tech = []
    lower_text = text.lower()
    
    for tech in KNOWN_TECH_DICTIONARY:
        t_low = tech.lower()
        # Word boundary disambiguation for single letters or common English words
        if t_low == "go":
            if re.search(r'\b(?:golang|go\s+(?:developer|engineer|programming|language|backend|code))\b', lower_text):
                found_tech.append("Go")
        elif t_low in ["c", "c++", "c#"]:
            if tech == "C" and re.search(r'\b(?:c\s*\/\s*c\+\+|ansi\s+c|embedded\s+c|c\s+programming|c\s+language)\b', lower_text):
                found_tech.append("C")
            elif tech == "C++" and re.search(r'\bc\+\+\b', lower_text):
                found_tech.append("C++")
            elif tech == "C#" and re.search(r'\bc#\b', lower_text):
                found_tech.append("C#")
        elif t_low == "r":
            if re.search(r'\b(?:r\s+(?:programming|language|scripting|studio)|rstudio)\b', lower_text):
                found_tech.append("R")
        elif t_low == "rest":
            if re.search(r'\b(?:restful|rest\s+api|rest\s+apis|restful\s+architecture)\b', lower_text):
                found_tech.append("REST")
        elif t_low == "java":
            if re.search(r'\bjava\b(?!\s*script)', lower_text):
                found_tech.append("Java")
        else:
            pattern = r'\b' + re.escape(t_low) + r'\b'
            if re.search(pattern, lower_text):
                found_tech.append(tech)

    tools = [t for t in found_tech if t in ["Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "Git", "GitHub Actions", "Postman", "Vercel"]]
    certs = ["Google Cloud Certified"] if "google cloud" in lower_text or ("aws" in lower_text and "cert" in lower_text) else []
    methodologies = [m for m in ["Microservices", "REST", "CI/CD", "Agile", "WebSockets"] if m in found_tech or (m.lower() in lower_text and m not in ["REST"])]
    tech_skills = [t for t in found_tech if t not in tools and t not in methodologies]

    # Return only genuine extracted skills (no fake defaults)
    return {
        "technical_skills": tech_skills,
        "tools_and_platforms": tools,
        "certifications": certs,
        "methodologies": methodologies,
        "is_llm_generated": False
    }

def fallback_match_jd(resume_skills: List[str], resume_text: str, jd_text: str) -> Dict[str, Any]:
    jd_tech = []
    lower_jd = jd_text.lower()
    for tech in KNOWN_TECH_DICTIONARY:
        t_low = tech.lower()
        if t_low == "go":
            if re.search(r'\b(?:golang|go\s+(?:developer|engineer|programming|language|backend))\b', lower_jd):
                jd_tech.append("Go")
        elif t_low == "c":
            if re.search(r'\b(?:c\s*\/\s*c\+\+|c\s+programming|c\s+language)\b', lower_jd):
                jd_tech.append("C")
        elif t_low == "rest":
            if re.search(r'\b(?:restful|rest\s+api|rest\s+apis|restful\s+architecture)\b', lower_jd):
                jd_tech.append("REST")
        elif t_low == "java":
            if re.search(r'\bjava\b(?!\s*script)', lower_jd):
                jd_tech.append("Java")
        else:
            pattern = r'\b' + re.escape(t_low) + r'\b'
            if re.search(pattern, lower_jd):
                jd_tech.append(tech)
            
    if not jd_tech:
        jd_tech = ["Python", "SQL", "Git", "REST", "Docker"]

    lower_resume = resume_text.lower()
    resume_skills_lower = set(s.lower() for s in resume_skills)
    
    matched = []
    missing = []
    
    for tech in jd_tech:
        t_low = tech.lower()
        is_matched = False
        if t_low in resume_skills_lower:
            is_matched = True
        elif t_low == "go":
            if re.search(r'\b(?:golang|go\s+(?:developer|engineer|programming|language|backend))\b', lower_resume):
                is_matched = True
        elif t_low == "c":
            if re.search(r'\b(?:c\s*\/\s*c\+\+|c\s+programming|c\s+language)\b', lower_resume):
                is_matched = True
        elif t_low == "rest":
            if re.search(r'\b(?:restful|rest\s+api|rest\s+apis|restful\s+architecture)\b', lower_resume):
                is_matched = True
        elif t_low == "java":
            if re.search(r'\bjava\b(?!\s*script)', lower_resume):
                is_matched = True
        else:
            if re.search(r'\b' + re.escape(t_low) + r'\b', lower_resume):
                is_matched = True
                
        if is_matched:
            matched.append(tech)
        else:
            missing.append(tech)
    
    ratio = len(matched) / max(len(jd_tech), 1)
    
    potential_gaps = ["System Design", "Database Indexing", "Container Orchestration", "Asynchronous Processing", "Test Automation", "Query Optimization"]
    keyword_gaps = [
        g for g in potential_gaps
        if g.lower() not in lower_resume and (g.lower() in lower_jd or len(missing) >= 2)
    ]
    if not keyword_gaps and missing:
        keyword_gaps = [f"{m} architecture" if m in ["Docker", "Kubernetes", "AWS"] else f"{m} integration" for m in missing[:3]]

    summary = f"Identified {len(matched)} matching core skills out of {len(jd_tech)} required technical competencies ({round(ratio*100)}% keyword coverage)."
    
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "keyword_gaps": keyword_gaps[:4],
        "match_ratio": round(ratio, 2),
        "fit_summary": humanize_text(summary),
        "is_llm_generated": False
    }

def semantic_rewrite_single_bullet(orig_bullet: str, jd_missing: List[str], jd_text: str) -> Tuple[str, str]:
    """
    Intelligently upgrades the candidate's EXACT accomplishment.
    Preserves what the candidate built while injecting active voice, metrics, and relevant JD alignment.
    Never substitutes unrelated tasks.
    """
    clean_b = orig_bullet.strip().lstrip("•-*–— ").strip()
    core = clean_b.rstrip(".,; ")
    lower = core.lower()
    
    # 1. Determine upgraded active verb and strip passive phrases
    upgraded_core = core
    verb_applied = "Engineered"
    
    if re.match(r'^(?:worked on|helped with|assisted with|assisted in|involved in|participated in)\s+', lower):
        upgraded_core = re.sub(r'^(?:worked on|helped with|assisted with|assisted in|involved in|participated in)\s+', '', core, flags=re.I)
        verb_applied = "Engineered and optimized"
    elif re.match(r'^(?:responsible for|tasked with|duties included)\s+', lower):
        upgraded_core = re.sub(r'^(?:responsible for|tasked with|duties included)\s+', '', core, flags=re.I)
        verb_applied = "Architected and delivered"
    elif re.match(r'^(?:interface with|interfaced with)\s+', lower):
        upgraded_core = re.sub(r'^(?:interface with|interfaced with)\s+', '', core, flags=re.I)
        verb_applied = "Integrated live"
    elif re.match(r'^(?:built|created|developed|implemented|designed)\s+', lower):
        first_word = core.split()[0].lower()
        rest = " ".join(core.split()[1:])
        verb_applied = "Architected" if first_word in ["built", "created", "designed"] else "Engineered"
        upgraded_core = rest
    elif re.match(r'^(?:used|utilized|leveraged)\s+', lower):
        upgraded_core = re.sub(r'^(?:used|utilized|leveraged)\s+', '', core, flags=re.I)
        verb_applied = "Applied"
    elif re.match(r'^(?:fixed|resolved|refactored)\s+', lower):
        first_word = core.split()[0].capitalize()
        rest = " ".join(core.split()[1:])
        verb_applied = f"{first_word} and optimized"
        upgraded_core = rest
    else:
        words = core.split()
        first_word = words[0].capitalize() if words else "Engineered"
        rest = " ".join(words[1:]) if len(words) > 1 else core
        verb_applied = first_word
        upgraded_core = rest

    # Clean leading indefinite articles that sound awkward after a verb
    upgraded_core = re.sub(r'^(?:a|an|the)\s+', '', upgraded_core, flags=re.I).strip()

    # 2. Check if the original bullet ALREADY contains quantifiable metrics
    has_existing_metric = any(re.search(pat, lower) for pat in [
        r'\b\d+(?:\.\d+)?%\b', r'\b\d+\s*(?:ms|s|sec)\b', r'\b\d+(?:,\d{3})+\b',
        r'\b\d+\s*(?:k|m|million|billion|gb)\b', r'\$\s*\d+', r'\b\d+x\b'
    ])

    if has_existing_metric:
        rewritten = f"{verb_applied} {upgraded_core}."
        rationale = "Elevated opening action verb to active voice while preserving existing quantifiable outcome metrics."
    else:
        # Contextual metric based on the specific domain found in their bullet
        if any(k in lower for k in ["feed", "stock", "chart", "perspective", "stream", "graph", "visual", "telemetry", "real-time"]):
            metric = "streaming visual updates at sub-50ms rendering latency across live market sessions"
            domain = "real-time streaming and data visualization"
        elif any(k in lower for k in ["test", "unit", "pytest", "jest", "coverage", "mock", "qa"]):
            metric = "expanding test coverage to 92% and cutting regression turnaround times by 40%"
            domain = "automated testing and test coverage"
        elif any(k in lower for k in ["sql", "postgres", "mysql", "query", "queries", "database", "indexing", "redis", "cache"]):
            metric = "reducing average query latency by 38% under peak concurrent loads"
            domain = "database query latency and indexing"
        elif any(k in lower for k in ["api", "fastapi", "rest", "endpoint", "backend", "service", "microservice"]):
            metric = "maintaining sub-40ms response times and 99.9% uptime across 10,000+ daily requests"
            domain = "service scalability and low-latency API delivery"
        elif any(k in lower for k in ["react", "frontend", "ui", "component", "tailwind", "css", "interface", "web"]):
            metric = "improving client-side load performance by 35% with clean component reusability"
            domain = "responsive UI and frontend performance"
        elif any(k in lower for k in ["docker", "kubernetes", "ci/cd", "pipeline", "github actions", "deploy"]):
            metric = "cutting deployment cycle turnaround by 45% with automated validation guardrails"
            domain = "CI/CD automation and containerized deployments"
        elif any(k in lower for k in ["bot", "review", "webhook", "agent", "llm", "ai", "token"]):
            metric = "increasing automated review throughput by 50% with robust validation guardrails"
            domain = "automated tool intelligence and workflow execution"
        else:
            metric = "optimizing execution efficiency by 30% with robust error handling and automated validation"
            domain = "outcome quantification"

        rewritten = f"{verb_applied} {upgraded_core}, {metric}."
        rationale = f"Retained core {domain} implementation, replaced passive phrasing with active engineering leadership, and added concrete benchmark metrics."

    return humanize_text(rewritten), humanize_text(rationale)

def fallback_bullet_suggestions(resume_text: str, jd_text: str, missing_skills: List[str]) -> List[Dict[str, Any]]:
    from services.parser import extract_experience_bullets
    
    extracted = extract_experience_bullets(resume_text)
    
    if not extracted:
        lines = [
            l.strip().lstrip("•-*–— ").strip()
            for l in resume_text.split("\n")
            if len(l.strip()) > 35 and not any(k in l.lower() for k in ["@", "linkedin", "github", "college", "university", "bachelor"])
        ]
        extracted = [{"context": "Work Experience", "bullet": l} for l in lines[:4]]

    if not extracted:
        extracted = [{
            "context": "Software Development Experience",
            "bullet": "Developed software application features and automated unit tests for project deliverables."
        }]

    target_bullets = extracted[:4]
    rewrites = []
    
    for item in target_bullets:
        orig = item["bullet"]
        context = item["context"]
        
        rewritten, rationale = semantic_rewrite_single_bullet(orig, missing_skills, jd_text)
        
        rewrites.append({
            "target_location": context,
            "original_bullet": orig,
            "rewritten_bullet": rewritten,
            "rationale": rationale
        })

    return rewrites

def fallback_generate_cover_letter(
    resume_text: str, 
    jd_text: str, 
    tone: str, 
    candidate_name: Optional[str] = None
) -> Dict[str, Any]:
    from services.parser import extract_experience_bullets
    
    extracted = extract_experience_bullets(resume_text)
    
    # Extract candidate name if not provided
    clean_name = (candidate_name or "").strip()
    if not clean_name or clean_name.lower() in ["applicant", "candidate", "undefined", "null"]:
        lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
        if lines and len(lines[0].split()) <= 4 and "@" not in lines[0] and not any(k in lines[0].lower() for k in ["resume", "curriculum", "cv"]):
            clean_name = lines[0].title()
        else:
            clean_name = "Applicant"

    # Natural project references
    def natural_project_ref(raw_title: str) -> str:
        clean = re.sub(r'^(?:project|role|experience)\s*:\s*', '', raw_title, flags=re.I).strip()
        clean = re.sub(r'\((?:forage|remote|hybrid|contract|internship)\)', '', clean, flags=re.I).strip()
        if not clean or clean.lower() in ["work experience", "projects", "engineering project"]:
            return "core full-stack application development"
        if "simulation" in clean.lower() or "forage" in clean.lower():
            return f"the {clean}"
        return clean

    p1 = extracted[0]["context"] if len(extracted) > 0 else "full-stack application development"
    p2 = extracted[1]["context"] if len(extracted) > 1 else "backend services and data persistence"
    
    clean_p1 = natural_project_ref(p1)
    clean_p2 = natural_project_ref(p2)
    
    tone_lower = (tone or "direct").lower()

    if tone_lower == "conversational":
        openings = [
            f"Dear Hiring Team,\n\nI was excited to come across this engineering opening. Reviewing your technical requirements and product roadmap, I immediately recognized the architectural patterns and problem-solving standards I enjoy working with daily.",
            f"Dear Hiring Team,\n\nI am writing to apply for this engineering role. Your team's emphasis on clean software craft, system reliability, and rapid product iteration matches the standards I prioritize in my own software projects.",
            f"Dear Hiring Team,\n\nI wanted to reach out regarding this position. Having followed the challenges your engineering team is solving, I see a clear overlap with the systems and APIs I have been developing recently."
        ]
        
        bodies = [
            f"During my work on {clean_p1}, I focused on designing clean service boundaries, automating unit testing, and keeping query latencies low under load. In parallel, while developing {clean_p2}, I prioritized building intuitive user interfaces and resilient data persistence. I value pragmatic engineering decisions: choosing reliable tools, measuring production performance, and keeping code maintainable for teammates.",
            f"In my recent work on {clean_p1}, I built scalable endpoints and focused on measurable latency improvements, ensuring reliable throughput. Additionally, my experience developing {clean_p2} gave me firsthand ownership of end-to-end features, from database schemas to responsive client-side telemetry. I enjoy collaborating with teammates who care deeply about developer experience and product velocity."
        ]
        
        closings = [
            f"I would welcome the opportunity to talk with your engineering team about how my background with modern service architecture can help deliver on your upcoming milestones. Thank you for your time and consideration.\n\nSincerely,\n{clean_name}",
            f"I look forward to discussing how my practical experience building maintainable software can contribute to your team's goals. Thank you for considering my application.\n\nSincerely,\n{clean_name}"
        ]
        letter = f"{random.choice(openings)}\n\n{random.choice(bodies)}\n\n{random.choice(closings)}"

    elif tone_lower == "executive":
        openings = [
            f"Dear Engineering Leadership,\n\nI am writing to submit my application for this role. My technical background centers on architecting resilient distributed systems, maintaining disciplined code hygiene, and accelerating product delivery velocity.",
            f"Dear Engineering Leadership,\n\nI am applying for this software engineering position to contribute to your core architectural objectives and product scalability. My experience spans modular system design, automated validation pipelines, and high-throughput data persistence."
        ]
        
        bodies = [
            f"Throughout my work on {clean_p1}, I prioritized measurable system reliability, establishing rigorous testing standards and optimizing database query latencies. Similarly, leading the development of {clean_p2}, I ensured architectural simplicity, automated deployment pipelines, and robust telemetry tracking. I approach engineering from a business-aligned perspective: minimizing architectural technical debt while maximizing throughput and feature velocity.",
            f"In spearheading technical deliverables for {clean_p1}, I emphasized architectural resilience and latency optimization under concurrent load. On {clean_p2}, I implemented clean component abstraction layers and end-to-end verification suites, ensuring zero-defect deployments. I focus on creating long-term maintainability and predictable release cycles across all systems I build."
        ]
        
        closings = [
            f"I welcome the opportunity to discuss how my commitment to technical rigor and scalable architecture will support your engineering milestones. Thank you for your time and evaluation.\n\nSincerely,\n{clean_name}",
            f"I would appreciate the chance to discuss how my systems background and engineering standards align with your technical roadmap. Thank you for your review.\n\nSincerely,\n{clean_name}"
        ]
        letter = f"{random.choice(openings)}\n\n{random.choice(bodies)}\n\n{random.choice(closings)}"

    else:
        # Default: "direct" (Technical, outcome-focused, concise)
        openings = [
            f"Dear Hiring Team,\n\nI am writing to apply for this engineering role. My technical background aligns directly with the core requirements outlined in your job specification.",
            f"Dear Hiring Team,\n\nI am submitting my application for this position. Reviewing your technical stack and requirements, I see a clear match with the applications and data pipelines I actively engineer.",
            f"Dear Hiring Team,\n\nI am writing to express my interest in this engineering opening. My day-to-day work focuses on building scalable software services, optimizing data persistence, and delivering clean, well-tested code."
        ]
        
        bodies = [
            f"In my work on {clean_p1}, I engineered performant service endpoints and integrated automated test harnesses, driving measurable improvements in latency and system reliability. Additionally, on {clean_p2}, I designed modular architectures and streamlined data handling, achieving high query efficiency and clean code boundaries. I prioritize active outcome metrics, maintainable patterns, and zero unnecessary dependencies.",
            f"While developing {clean_p1}, I implemented low-latency endpoints and optimized database indexing, maintaining sub-40ms response times under concurrent request loads. On {clean_p2}, I containerized services and automated testing pipelines, ensuring consistent deployment velocity. My focus is on writing maintainable, resilient software that directly solves customer problems."
        ]
        
        closings = [
            f"I look forward to discussing how my practical software development experience can support your engineering deliverables. Thank you for your time.\n\nSincerely,\n{clean_name}",
            f"I would welcome the opportunity to discuss how my technical skills and disciplined development practices align with your team's needs. Thank you for your consideration.\n\nSincerely,\n{clean_name}"
        ]
        letter = f"{random.choice(openings)}\n\n{random.choice(bodies)}\n\n{random.choice(closings)}"

    cleaned = humanize_text(letter)
    return {
        "cover_letter": cleaned,
        "word_count": len(cleaned.split()),
        "tone": tone_lower,
        "is_llm_generated": False
    }
