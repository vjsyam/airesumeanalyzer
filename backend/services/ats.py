import re
from typing import Dict, Any, List

METRIC_PATTERNS = [
    r'\b\d+(?:\.\d+)?%\b',               # 35%, 99.98%
    r'\b\d+\s*(?:ms|s|sec|seconds)\b',    # 50ms, 15s
    r'\b\d+(?:,\d{3})+\b',               # 18,000, 250,000
    r'\b\d+\s*(?:k|m|million|billion|gb|tb)\b', # 10k, 18 million, 400+
    r'\$\s*\d+',                         # $50k
    r'\b\d+x\b',                         # 2x, 5x
    r'\b(?:reduced|increased|accelerated|cut|improved|scaled)\s+by\s+\d+', # reduced by 35%
    r'\b\d+\+\s*(?:stars|users|developers|requests|endpoints)\b' # 400+ stars
]

STRONG_ACTION_VERBS = {
    "architected", "engineered", "built", "designed", "developed", "implemented", "optimized",
    "automated", "scaled", "orchestrated", "reduced", "accelerated", "deployed", "constructed",
    "refactored", "integrated", "spearheaded", "mentored", "eliminated", "delivered", "authored"
}

WEAK_PASSIVE_PHRASES = [
    r'\bworked on\b', r'\bresponsible for\b', r'\bhelped with\b', r'\bassisted in\b',
    r'\btasked with\b', r'\bparticipated in\b', r'\binvolved in\b', r'\bduties included\b'
]

def analyze_bullet_quality(bullets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates bullet points using criteria from top ATS and resume screening engines:
    1. Metric quantification rate (% of bullets with measurable numbers/results)
    2. Strong active verbs vs weak passive voice
    """
    if not bullets:
        return {
            "metric_rate": 0.0,
            "metric_bullet_count": 0,
            "total_bullets": 0,
            "passive_phrase_count": 0,
            "strong_verb_count": 0,
            "score": 40
        }
        
    total = len(bullets)
    has_metric_count = 0
    strong_verb_count = 0
    passive_phrase_count = 0
    
    for b in bullets:
        text = b.get("bullet", "")
        lower = text.lower()
        
        # Check for numbers / metrics
        has_metric = any(re.search(pat, lower) for pat in METRIC_PATTERNS)
        if has_metric:
            has_metric_count += 1
            
        # Check first word for strong action verb
        words = re.sub(r'[^a-zA-Z\s]', '', lower).split()
        if words and words[0] in STRONG_ACTION_VERBS:
            strong_verb_count += 1
            
        # Check for weak passive phrases
        if any(re.search(pat, lower) for pat in WEAK_PASSIVE_PHRASES):
            passive_phrase_count += 1

    metric_rate = has_metric_count / total
    
    # Calculate quality score (0 - 100)
    # Metric rate contributes 60%, strong verbs 30%, passive penalty -10%
    quality_score = round(
        (metric_rate * 60) +
        (min(1.0, strong_verb_count / total) * 30) -
        (min(0.3, passive_phrase_count * 0.1) * 100) +
        10
    )
    quality_score = max(15, min(100, quality_score))

    return {
        "metric_rate": round(metric_rate, 2),
        "metric_bullet_count": has_metric_count,
        "total_bullets": total,
        "passive_phrase_count": passive_phrase_count,
        "strong_verb_count": strong_verb_count,
        "score": quality_score
    }

def compute_ats_score(
    structure: Dict[str, Any],
    layout_metrics: Dict[str, Any],
    keyword_match_ratio: float,
    bullets: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Rigorous, realistic ATS scoring algorithm modeled after Jobscan, Resume Worded, and modern enterprise ATS filters.
    
    Weights:
    - Target Keyword & Hard Skill Alignment: 45% (Primary recruiter filter)
    - Measurable Results & Metric Quantification: 25% (Measurable impact density)
    - Section Headings & Structural Hygiene: 15% (Parseability into standard ATS database tables)
    - Formatting & Layout Integrity: 15% (Column check, table complexity, contact parseability)
    """
    from services.parser import extract_experience_bullets
    
    if bullets is None:
        raw_text = layout_metrics.get("raw_text", "")
        bullets = extract_experience_bullets(raw_text) if raw_text else []
        
    # 1. Keyword Alignment Score (45% Weight)
    # Strict matching: 50% match ratio = 50 keyword score
    keyword_score = round(min(1.0, max(0.0, keyword_match_ratio)) * 100)
    
    # 2. Measurable Metrics & Impact Score (25% Weight)
    bullet_analysis = analyze_bullet_quality(bullets)
    metric_score = bullet_analysis["score"]
    
    # 3. Section Structure Score (15% Weight)
    detected_sections = structure.get("detected_sections", {})
    sec_points = 0
    section_breakdown = {}
    
    sec_weights = {
        "experience": 40,
        "skills": 30,
        "education": 20,
        "projects": 10
    }
    
    for sec, weight in sec_weights.items():
        found = detected_sections.get(sec, False)
        if found:
            sec_points += weight
        section_breakdown[sec] = {
            "found": found,
            "weight": weight,
            "status": "Found" if found else "Missing"
        }
    section_score = min(100, sec_points)

    # 4. Formatting, Parseability & Contact Info (15% Weight)
    format_score = 100
    format_deductions = []
    
    if layout_metrics.get("has_columns_suspected"):
        format_score -= 25
        format_deductions.append("Multi-column layout detected. Legacy ATS parsers (Taleo, iCIMS) often scramble reading orders.")
        
    tables_count = layout_metrics.get("tables_count", 0)
    if tables_count > 2:
        format_score -= 20
        format_deductions.append(f"{tables_count} complex tables found. Text inside table cells is frequently dropped by screening bots.")
    elif tables_count > 0:
        format_score -= 5
        format_deductions.append("Table formatting detected. Use simple standard headings for maximum reliability.")
        
    images_count = layout_metrics.get("images_count", 0)
    if images_count > 1:
        format_score -= 15
        format_deductions.append(f"{images_count} graphic icons detected. Cannot be indexed by ATS OCR.")
        
    word_count = layout_metrics.get("word_count", 0)
    if word_count < 200:
        format_score -= 30
        format_deductions.append("Resume contains under 200 words. Too brief for comprehensive ATS keyword indexing.")
    elif word_count > 1200:
        format_score -= 15
        format_deductions.append("Resume exceeds 1200 words. May trigger length penalties on automated 1-page screening filters.")

    contact_info = structure.get("contact_info", {})
    if not contact_info.get("has_email"):
        format_score -= 20
        format_deductions.append("Missing or unparseable email address.")
    if not contact_info.get("has_phone"):
        format_score -= 15
        format_deductions.append("Missing phone number.")

    format_score = max(20, min(100, format_score))

    # Rigorous Weighted Composite Score
    # 0.45 * keyword + 0.25 * metrics + 0.15 * section + 0.15 * format
    composite_score = round(
        (0.45 * keyword_score) +
        (0.25 * metric_score) +
        (0.15 * section_score) +
        (0.15 * format_score)
    )
    composite_score = max(10, min(99, composite_score))

    # Realistic Benchmarking
    if composite_score >= 82:
        verdict = "Top 10% ATS Screening Tier"
        summary = "Exceptional keyword alignment and strongly quantified bullet points. High probability of passing recruiter filters."
    elif composite_score >= 68:
        verdict = "Competitive Match (Moderate Keyword Gaps)"
        summary = "Solid core credentials. Adding missing target skills and quantifying more bullet points will significantly increase callback probability."
    elif composite_score >= 50:
        verdict = "Borderline (Substantial Gaps Detected)"
        summary = "Significant keyword discrepancies or lack of measurable bullet metrics. Resume risks being filtered out by automated screening."
    else:
        verdict = "Critical ATS Filter Risk"
        summary = "Low keyword overlap with the target job description. Tailor your skills and experience bullets to match requirements before submitting."

    # Build metric summary notes
    metric_pct = round(bullet_analysis['metric_rate'] * 100)
    metric_notes = [
        f"{bullet_analysis['metric_bullet_count']} of {bullet_analysis['total_bullets']} bullets ({metric_pct}%) contain quantifiable metrics (%, ms, $, scale).",
        "Industry standard: Target 60%+ of bullets with measurable outcomes." if metric_pct < 60 else "Good quantification rate matching competitive standards.",
    ]
    if bullet_analysis["passive_phrase_count"] > 0:
        metric_notes.append(f"Found {bullet_analysis['passive_phrase_count']} passive phrases (e.g. 'worked on', 'helped with'). Replace with active verbs.")

    return {
        "overall_score": composite_score,
        "verdict": verdict,
        "summary": summary,
        "breakdown": {
            "keyword_match": {
                "score": keyword_score,
                "weight": 45,
                "label": "Target Keyword Alignment",
                "notes": f"{keyword_score}% keyword & skill overlap with target job description."
            },
            "measurable_impact": {
                "score": metric_score,
                "weight": 25,
                "label": "Quantifiable Metrics & Impact",
                "notes": metric_notes
            },
            "formatting_compatibility": {
                "score": format_score,
                "weight": 15,
                "label": "Layout & Parseability",
                "notes": format_deductions if format_deductions else ["Clean single-column layout, standard typography, and valid contact information."]
            },
            "section_structure": {
                "score": section_score,
                "weight": 15,
                "label": "Standard Section Headings",
                "sections": section_breakdown
            }
        }
    }
