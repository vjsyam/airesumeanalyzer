import os
import pytest
from fastapi.testclient import TestClient
from main import app
from services.humanizer import humanize_text, validate_humanization, clean_dashes, scrub_cliches
from services.parser import parse_resume_file, extract_text_from_docx
from services.ats import compute_ats_score

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["llm_provider"] == "Google Gemini"

def test_sample_data():
    response = client.get("/api/sample-data")
    assert response.status_code == 200
    data = response.json()
    assert "backend_engineer" in data["resumes"]
    assert "staff_backend" in data["job_descriptions"]

def test_humanizer_scrubs_cliches_and_dashes():
    raw_input = "A results-driven and passionate about team player—who leveraged cutting-edge tools to spearheaded synergy."
    cleaned = humanize_text(raw_input)
    assert "results-driven" not in cleaned.lower()
    assert "passionate about" not in cleaned.lower()
    assert "spearheaded" not in cleaned.lower()
    assert "—" not in cleaned
    assert "–" not in cleaned
    validation = validate_humanization(cleaned)
    assert validation["is_compliant"] is True

def test_docx_file_parsing():
    sample_path = os.path.join(os.path.dirname(__file__), "sample_resumes", "Morgan_Reed_Resume.docx")
    assert os.path.exists(sample_path)
    result = parse_resume_file(sample_path, "Morgan_Reed_Resume.docx")
    assert "morgan reed" in result["raw_text"].lower()
    assert result["word_count"] > 50
    assert result["structure"]["contact_info"]["has_email"] is True

def test_ats_scoring_dimensions():
    dummy_structure = {
        "contact_info": {"has_email": True, "has_phone": True, "has_links": True},
        "detected_sections": {
            "experience": True, "skills": True, "education": True, "projects": True
        }
    }
    dummy_layout = {
        "has_columns_suspected": False,
        "tables_count": 0,
        "images_count": 0,
        "word_count": 450
    }
    dummy_bullets = [
        {"bullet": "Engineered high-throughput API endpoints reducing latency by 35% under peak traffic."},
        {"bullet": "Maintained sub-40ms response times across 18 million daily requests with 99.98% uptime."},
        {"bullet": "Built automated testing suites raising coverage to 92% and preventing regressions."}
    ]
    score_result = compute_ats_score(dummy_structure, dummy_layout, keyword_match_ratio=0.85, bullets=dummy_bullets)
    assert 75 <= score_result["overall_score"] <= 100
    assert "breakdown" in score_result
    assert "keyword_match" in score_result["breakdown"]
    assert "measurable_impact" in score_result["breakdown"]
    assert "formatting_compatibility" in score_result["breakdown"]
    assert "section_structure" in score_result["breakdown"]

def test_analyze_endpoint_with_sample():
    response = client.post(
        "/api/analyze",
        data={
            "sample_resume_id": "backend_engineer",
            "job_description": "We need a Senior Python and FastAPI engineer with PostgreSQL experience."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "ats_score" in data
    assert "skills" in data
    assert "match_analysis" in data
    assert len(data["suggestions"]) > 0

def test_cover_letter_generation_and_export():
    # 1. Generate Cover Letter
    res = client.post(
        "/api/cover-letter",
        json={
            "resume_text": "Alex Vance. Senior Backend Engineer with Python and FastAPI experience.",
            "job_description": "Senior Backend role requiring Python microservices.",
            "tone": "direct"
        }
    )
    assert res.status_code == 200
    cover_data = res.json()
    assert "cover_letter" in cover_data
    assert cover_data["human_compliant"] is True

    # 2. Export to DOCX
    export_res = client.post(
        "/api/export/docx",
        json={
            "cover_letter": cover_data["cover_letter"],
            "candidate_name": "Alex Vance"
        }
    )
    assert export_res.status_code == 200
    assert "application/vnd.openxmlformats" in export_res.headers.get("content-type", "")
    assert len(export_res.content) > 1000

if __name__ == "__main__":
    print("Running tests...")
    test_health_check()
    print("[PASS] Health check passed")
    test_sample_data()
    print("[PASS] Sample data passed")
    test_humanizer_scrubs_cliches_and_dashes()
    print("[PASS] Humanizer /human rules passed")
    test_docx_file_parsing()
    print("[PASS] DOCX parser passed")
    test_ats_scoring_dimensions()
    print("[PASS] ATS scoring passed")
    test_analyze_endpoint_with_sample()
    print("[PASS] /api/analyze endpoint passed")
    test_cover_letter_generation_and_export()
    print("[PASS] Cover letter generation and DOCX export passed")
    print("ALL TESTS PASSED SUCCESSFULLY!")
