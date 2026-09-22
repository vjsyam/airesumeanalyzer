# AI Resume Analyzer — Precision ATS & Gap Optimization

A production-grade, developer-first AI resume analysis and career optimization platform. Built with a high-performance **FastAPI** backend, **Google Gemini API** integration, server-side document parsing (**pdfplumber** & **python-docx**), deterministic ATS scoring, and a reactive **React + Vite** frontend styled in a sleek dark developer aesthetic (Linear / Raycast inspired).

---

## Architecture Overview

```
                          ┌────────────────────────────────────────┐
                          │             React + Vite               │
                          │   Dark Developer UI (Port 5173)        │
                          └──────────────────┬─────────────────────┘
                                             │ HTTP / REST
                                             ▼
                          ┌────────────────────────────────────────┐
                          │            FastAPI Backend             │
                          │        Uvicorn Server (Port 8000)      │
                          └────┬──────────────────────────────┬────┘
                               │                              │
                ┌──────────────┴──────────────┐ ┌─────────────┴─────────────┐
                │    Document Parsing Engine  │ │  ATS Scoring & Telemetry  │
                │  - pdfplumber & pypdf (PDF) │ │  - 55% Keyword Match      │
                │  - python-docx (DOCX)       │ │  - 20% Measurable Impact  │
                │  - Structural Hazard Audit  │ │  - 15% Section Structure  │
                └─────────────────────────────┘ │  - 10% Layout Formatting  │
                                                └─────────────┬─────────────┘
                                                              │
                                                ┌─────────────┴─────────────┐
                                                │      LLM Orchestration    │
                                                │  - Google Gemini API      │
                                                │  - Pure Skill Taxonomy    │
                                                │  - Preserved Rewrites     │
                                                │  - Human Voice Cover Gen  │
                                                └───────────────────────────┘
```

---

## Key Features

1. **Server-Side File & Layout Parsing**:
   - Parses `.pdf` via `pdfplumber` (with fallback to `pypdf`) and `.docx` via `python-docx`.
   - **Structural Hazard Detection**: Flags multi-column layout risks, nested tables, graphical/canvas elements, and missing header sections that trip enterprise ATS parsers.
   - Cleans up temporary parsing artifacts automatically.

2. **Role-Sensitive ATS Scoring Engine**:
   - Accurately reflects real-world ATS filters (like Jobscan, Greenhouse, and Lever).
   - **55% Target Keyword Alignment**: Strict token boundary matching (`\bGo\b`, `\bREST\b`, `\bC\b`) without synthetic fallback inflation.
   - **20% Measurable Impact**: Density analysis of quantifiable numbers (`%`, `$`, `k`, `ms`, scale metrics) and active leadership verbs.
   - **15% Section Structure**: Audits essential headings (Experience, Education, Skills, Projects).
   - **10% Layout Integrity & Formatting**: Detects parsing errors, line lengths, and contact details.
   - **Knockout Threshold Filter**: Candidates lacking domain prerequisites receive realistic low scores (`< 35%` Critical Filter Risk) rather than an artificial passing floor.

3. **Project-Anchored Bullet Rewrites**:
   - **100% Context Retention**: Preserves the candidate's exact libraries, projects, frameworks, and architecture.
   - Eliminates passive phrasing (*"assisted with"*, *"worked on"*) and replaces them with active verbs (*"Architected"*, *"Engineered"*, *"Optimized"*).
   - Injects plausible domain metrics (latency reduction, throughput scaling, test coverage) with clear rationale for every revision.

4. **Humanized Cover Letter Studio (`/human` Standard)**:
   - Scrubbed of all AI tropes and corporate fluff (*"results-driven"*, *"passionate about"*, *"leverage"*, *"spearhead"*).
   - Zero em/en dashes (`—`, `–`).
   - Dynamic tone switching:
     - **Direct**: Punchy, assertive, metric-driven engineering tone.
     - **Conversational**: Engaging, narrative, modern tech culture voice.
     - **Executive**: Strategic, business-impact, architectural leadership perspective.
   - 1-click export to formatted `.docx` and `.txt`.

5. **Instant Reactive Target Role Presets**:
   - Seamlessly switch between built-in target roles (`Frontend React`, `Software Developer`, `Senior Backend`, `DevOps & Cloud`, `ML & LLM`).
   - Instantly recalculates ATS telemetry and skill matrices in real time.

---

## System Requirements

Before running the application, ensure you have the following installed:

- **Python**: `3.10` or higher (`python --version`)
- **Node.js**: `18.x` or higher (`node --version`)
- **Package Manager**: `npm` (`npm --version`) or `yarn` / `pnpm`
- **Git**: (`git --version`)

---

## Step-by-Step Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/vjsyam/airesumeanalyzer.git
cd airesumeanalyzer
```

---

### 2. Backend Setup (FastAPI)

#### A. Navigate to backend directory
```bash
cd backend
```

#### B. Create a Python Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### C. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### D. Configure Environment Variables
Copy the `.env.example` file to create your `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Edit `.env` to configure your settings:
```env
# Optional: Set your Google Gemini API Key here (or enter it in the web UI settings)
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
```
> **Note**: Even without a Gemini API Key, the application operates in **Smart Fallback Mode** with deterministic ATS calculation, skill extraction, and template-based humanized letters.

#### E. Generate Sample Resume Files (Optional but Recommended)
Creates test `.docx` files in `backend/sample_resumes/`:
```bash
python create_sample_files.py
```

#### F. Run Automated Backend Tests
Verify that all document parsers, ATS formulas, and endpoints pass:
```bash
python test_app.py
```
*Expected output: `ALL TESTS PASSED SUCCESSFULLY!`*

#### G. Start the Backend Server
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI server will be active at `http://127.0.0.1:8000`.
- API Health Check: `http://127.0.0.1:8000/health`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

---

### 3. Frontend Setup (React + Vite)

Open a **new terminal tab or window**:

#### A. Navigate to frontend directory
```bash
cd airesumeanalyzer/frontend
```

#### B. Install Node Dependencies
```bash
npm install
```

#### C. Start the Vite Development Server
```bash
npm run dev
```
The application will launch at:
```
➜  Local:   http://127.0.0.1:5173/
```
Open your browser and navigate to `http://127.0.0.1:5173/`.

#### D. (Optional) Production Build Verification
To verify the production bundle:
```bash
npm run build
```

---

## Configuring the Gemini API Key

You can provide your Gemini API key through either of two secure methods:

1. **Server Environment Variable**:
   Add `GEMINI_API_KEY=AIzaSy...` into `backend/.env`.
2. **Client-Side Key Manager**:
   Click the **API Key** button in the top-right header of the web application. Enter your key; it is stored safely in your browser's `localStorage` and sent directly via custom headers during analysis requests. No keys are ever written to git or exposed publicly.

---

## Using the Application

1. **Provide a Resume**:
   - **Upload**: Drag and drop any `.pdf` or `.docx` file into the upload zone.
   - **Presets**: Or click one of the pre-loaded candidate profiles:
     - *Alex Rivera* (Full-Stack AI Developer)
     - *Marcus Vance* (Senior Backend & Distributed Systems)
     - *Elena Rostova* (Frontend React & UX Engineer)
   - **Paste Text**: Or switch to the "Paste Text" tab and enter raw resume text.

2. **Select Target Role**:
   - Click any target role preset button:
     - `Frontend React` (Vercel)
     - `Software Developer` (CoreTech)
     - `Senior Backend` (Voxel)
     - `DevOps & Cloud` (Datadog)
     - `ML & LLM` (Anthropic)
   - Or paste any custom job description into the target JD text box.

3. **Analyze**:
   - Click **Run Full Spectrum ATS Analysis**.
   - Observe the real-time breakdown:
     - **ATS Match Gauge**: Overall 0-100 score with keyword, impact, structure, and formatting progress bars.
     - **Skills Matrix**: Matched skills, missing required skills, and keyword gaps.
     - **Bullet Rewrites**: Side-by-side before/after bullet upgrades with rationale.
     - **Cover Letter**: Tone switcher (Direct, Conversational, Executive), 1-click regenerate, and `.docx` download.
     - **Parser Telemetry**: Layout diagnostics, detected contact links, and section verification.

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server status and dependency health check |
| `GET` | `/api/sample-data` | Retrieves pre-configured candidate resumes and JD presets |
| `POST` | `/api/analyze` | Multipart or JSON payload for parsing, ATS scoring, and bullet rewrites |
| `POST` | `/api/cover-letter/generate` | Generates a humanized cover letter with tone selection |
| `POST` | `/api/cover-letter/export` | Streams a formatted `.docx` cover letter document |

---

## Troubleshooting

- **CORS Issues**: Ensure the backend is running on `127.0.0.1:8000` and frontend on `127.0.0.1:5173`. CORS middleware is pre-configured for both localhost and 127.0.0.1.
- **Port In Use (8000 / 5173)**:
  - Check active processes:
    - *Windows*: `Get-NetTCPConnection -LocalPort 8000, 5173`
    - *macOS/Linux*: `lsof -i :8000` or `lsof -i :5173`
- **PDF Extraction Note**: Resumes exported as pure rasterized images without text layers cannot be read by text parsers. Ensure resumes contain genuine text streams.

---

## License

MIT License. Designed and engineered for high-accuracy job application optimization.
