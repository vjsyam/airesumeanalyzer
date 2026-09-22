# AI Resume Analyzer — Precision ATS & Gap Optimization

A full-stack, developer-grade AI resume analysis web application engineered as an everyday career tool. Evaluates candidate resumes against target job descriptions using server-side document parsing, Google Gemini API orchestration, deterministic ATS scoring, and strict human voice filtering.

---

## Key Features

1. **Server-Side File Parsing**:
   - Parses PDF resumes via `pdfplumber` (with fallback to `pypdf`) and DOCX resumes via `python-docx`.
   - Layout Telemetry: Scans for multi-column hazards, nested tables, graphic elements, and contact info.
   - Automatic temp file lifecycle cleanup.

2. **Single-Purpose LLM Architecture (Gemini API)**:
   - **Call #1 (Skill Extraction)**: Structured taxonomy of technical skills, platforms, tools, and certifications.
   - **Call #2 (JD Gap Analysis)**: Pinpoints confirmed qualifications, missing requirements, and domain keyword gaps.
   - **Call #3 (ATS Score Telemetry)**: Deterministic 0-100 score weighted across keyword alignment (35%), format compatibility (25%), section structure (25%), and contact parseability (15%).
   - **Call #4 (Bullet-Level Rewrites)**: Contextual, before-and-after bullet revisions with concrete metrics and impact rationale.
   - **Call #5 (Humanized Cover Letter)**: On-demand cover letter generator with configurable tone (`direct`, `conversational`, `executive`).

3. **Strict Human Voice Standard (`/human` Skill Rules)**:
   - Zero corporate resume clichés (`"results-driven"`, `"proven track record"`, `"passionate about"`, `"leverage"`, `"dynamic"`, `"team player"`, `"spearheaded"`, etc.).
   - No em/en dashes (`—`, `–`).
   - Active voice, varied sentence rhythm, and concrete engineering metrics.

4. **Developer Tool Aesthetic**:
   - Inspired by Linear, Vercel, and Raycast.
   - Dark theme (`#090c10` canvas), `JetBrains Mono` telemetry typography, minimal borders, and zero generic cards or purple gradient fluff.
   - 1-click export of cover letters to `.docx` and `.txt`.

---

## Project Structure

```
d:/airesumeanalyzer/
├── backend/
│   ├── services/
│   │   ├── parser.py        # PDF & DOCX text extraction & structure analyzer
│   │   ├── humanizer.py     # /human skill rule validation & cliché scrubber
│   │   ├── ats.py           # ATS scoring formula and category breakdowns
│   │   ├── llm.py           # Gemini SDK orchestration & single-purpose calls
│   │   └── export.py        # DOCX export utility
│   ├── sample_resumes/      # Pre-generated sample PDF/DOCX resumes
│   ├── sample_data.py       # Built-in sample candidates & JDs
│   ├── test_app.py          # Automated test suite
│   ├── main.py              # FastAPI application & endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx           # App bar & API key modal toggle
│   │   │   ├── ApiKeyModal.jsx      # LocalStorage key manager
│   │   │   ├── AtsScoreGauge.jsx    # Editorial score number & breakdown
│   │   │   ├── SkillMatchBoard.jsx  # Monospace skill chips matrix
│   │   │   ├── BulletSuggestions.jsx# Side-by-side diff bullet comparisons
│   │   │   ├── CoverLetterTab.jsx   # Humanized cover letter generator & exporter
│   │   │   └── ResumeInspector.jsx  # Raw text & structural parse inspector
│   │   ├── App.jsx                  # Main workspace layout
│   │   ├── api.js                   # Client API service
│   │   └── index.css                # Bespoke developer tool CSS design system
│   ├── index.html                   # HTML template with Google Fonts
│   └── package.json
└── README.md
```

---

## Quickstart

### 1. Run the Backend
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Run the Frontend
```bash
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173` in your browser.

### 3. Running Automated Tests
```bash
cd backend
python test_app.py
```
