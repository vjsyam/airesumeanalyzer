import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, FileText, Sparkles, AlertCircle, ArrowRight, RefreshCw, 
  Layers, CheckCircle2, ChevronRight, Loader2, Briefcase, User, 
  Code2, Terminal, ShieldAlert, Cpu, Check, FileCheck, Download, Copy
} from 'lucide-react';
import Header from './components/Header';
import AtsScoreGauge from './components/AtsScoreGauge';
import SkillMatchBoard from './components/SkillMatchBoard';
import BulletSuggestions from './components/BulletSuggestions';
import CoverLetterTab from './components/CoverLetterTab';
import ResumeInspector from './components/ResumeInspector';
import { checkHealth, fetchSampleData, analyzeResume } from './api';

export default function App() {
  const [serverStatus, setServerStatus] = useState('checking');
  const [sampleData, setSampleData] = useState(null);
  
  // Input states
  const [file, setFile] = useState(null);
  const [selectedSampleId, setSelectedSampleId] = useState('fullstack_ai_dev');
  const [pastedResumeText, setPastedResumeText] = useState('');
  const [inputMode, setInputMode] = useState('sample'); // 'sample' | 'upload' | 'paste'
  const [selectedJdKey, setSelectedJdKey] = useState('fullstack_ai');
  const [jobDescription, setJobDescription] = useState('');
  
  // Processing & Results
  const [loading, setLoading] = useState(false);
  const [analysisStep, setAnalysisStep] = useState('');
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('ats'); // 'ats' | 'skills' | 'suggestions' | 'cover-letter' | 'raw'
  const [copiedReport, setCopiedReport] = useState(false);

  const fileInputRef = useRef(null);

  useEffect(() => {
    checkHealth().then((res) => {
      setServerStatus(res.status === 'healthy' ? 'healthy' : 'offline');
    });

    fetchSampleData().then((data) => {
      setSampleData(data);
      if (data?.job_descriptions?.fullstack_ai) {
        setJobDescription(data.job_descriptions.fullstack_ai.text);
      }
    }).catch((err) => console.log('Sample data fetch error:', err));
  }, []);

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      setFile(dropped);
      setSelectedSampleId(null);
      setInputMode('upload');
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setSelectedSampleId(null);
      setInputMode('upload');
    }
  };

  const loadResumePreset = (sampleId) => {
    setSelectedSampleId(sampleId);
    setFile(null);
    setInputMode('sample');
  };

  const loadJdPreset = (jdKey) => {
    setSelectedJdKey(jdKey);
    const newJd = sampleData?.job_descriptions?.[jdKey]?.text;
    if (newJd) {
      setJobDescription(newJd);
      // If analysis has already been performed, immediately recalculate for this role
      if (results) {
        handleAnalyze(newJd);
      }
    }
  };

  const handleAnalyze = async (overrideJd = null) => {
    const targetJd = (overrideJd !== null && typeof overrideJd === 'string' ? overrideJd : jobDescription).trim();
    if (!targetJd) {
      setError('Please enter or paste a target Job Description.');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysisStep('Evaluating skills taxonomy against target role requirements and recalculating ATS telemetry...');

    try {
      const payload = {
        jobDescription: targetJd,
      };

      if (inputMode === 'upload') {
        if (!file) {
          setError('Please select or drop a PDF/DOCX resume.');
          setLoading(false);
          return;
        }
        payload.file = file;
      } else if (inputMode === 'paste') {
        if (!pastedResumeText.trim()) {
          setError('Please paste your resume text in the editor.');
          setLoading(false);
          return;
        }
        payload.rawResumeText = pastedResumeText.trim();
      } else {
        if (!selectedSampleId) {
          setError('Please select a candidate profile preset.');
          setLoading(false);
          return;
        }
        payload.sampleResumeId = selectedSampleId;
      }

      const response = await analyzeResume(payload);
      setResults(response);
    } catch (err) {
      setError(err.message || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
      setAnalysisStep('');
    }
  };

  const generateAuditReportMarkdown = () => {
    if (!results) return '';
    const candName = results.resume_meta?.candidate_name && results.resume_meta?.candidate_name !== 'Applicant'
      ? results.resume_meta.candidate_name
      : sampleData?.resumes?.[selectedSampleId]?.candidate_name || 'Candidate';
    const roleTitle = sampleData?.job_descriptions?.[selectedJdKey]?.title || 'Target Role';
    const ats = results.ats_score || {};
    const match = results.match_analysis || {};
    const bd = ats.breakdown || {};
    const suggestions = results.suggestions || [];

    return `# ATS Audit & Resume Optimization Report

**Candidate:** ${candName}  
**Target Position:** ${roleTitle}  
**Overall ATS Compatibility Rating:** ${ats.overall_score || 0}% (${ats.rating_label || 'Evaluated'})  
**Evaluation Engine:** ${results.engine || 'Gemini 2.5 Flash'}

---

## 1. ATS Telemetry Breakdown

| Evaluation Dimension | Weight | Score | Assessment |
| :--- | :---: | :---: | :--- |
| **${bd.keyword_match?.label || 'Keyword Alignment'}** | ${bd.keyword_match?.weight || 55}% | ${bd.keyword_match?.score || 0}% | ${Array.isArray(bd.keyword_match?.notes) ? bd.keyword_match.notes.join('; ') : bd.keyword_match?.notes || ''} |
| **${bd.measurable_impact?.label || 'Measurable Impact'}** | ${bd.measurable_impact?.weight || 20}% | ${bd.measurable_impact?.score || 0}% | ${Array.isArray(bd.measurable_impact?.notes) ? bd.measurable_impact.notes.join('; ') : bd.measurable_impact?.notes || ''} |
| **${bd.section_structure?.label || 'Section Structure'}** | ${bd.section_structure?.weight || 15}% | ${bd.section_structure?.score || 0}% | ${Array.isArray(bd.section_structure?.notes) ? bd.section_structure.notes.join('; ') : bd.section_structure?.notes || ''} |
| **${bd.formatting_compatibility?.label || 'Layout & Formatting'}** | ${bd.formatting_compatibility?.weight || 10}% | ${bd.formatting_compatibility?.score || 0}% | ${Array.isArray(bd.formatting_compatibility?.notes) ? bd.formatting_compatibility.notes.join('; ') : bd.formatting_compatibility?.notes || ''} |

---

## 2. Skill & Domain Keyword Telemetry

### Confirmed Qualifications (${(match.matched_skills || []).length})
${(match.matched_skills || []).map(s => `- [x] **${s}**`).join('\n')}

### Missing Required Skills (${(match.missing_skills || []).length})
${(match.missing_skills || []).map(s => `- [ ] ${s}`).join('\n')}

### Critical Domain Keyword Gaps (${(match.keyword_gaps || []).length})
${(match.keyword_gaps || []).map(g => `- ⚠️ ${g}`).join('\n')}

---

## 3. High-Impact Bullet Rewrites

${suggestions.map((item, idx) => `### ${idx + 1}. ${item.target_location}
- **Original:** ${item.original_bullet}
- **Targeted Revision:** ${item.rewritten_bullet}
- **Alignment Rationale:** ${item.rationale}
`).join('\n')}

---
*Report generated by AI Resume Analyzer — Precision ATS & Gap Optimization Engine.*
`;
  };

  const handleDownloadAuditReport = () => {
    const md = generateAuditReportMarkdown();
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `ATS_Audit_Report_${(results?.resume_meta?.candidate_name || 'Resume').replace(/\s+/g, '_')}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleCopyAuditReport = () => {
    const md = generateAuditReportMarkdown();
    navigator.clipboard.writeText(md);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  return (
    <div className="app-container">
      <Header
        serverStatus={serverStatus}
        activeEngine={results?.engine || 'Gemini 2.5 Flash'}
      />

      <main className="main-workspace">
        {/* Centered Hero Header */}
        <section className="hero-header">
          <h1 className="hero-title">Precision ATS & Resume Optimizer</h1>
          <p className="hero-subtitle">
            Server-side document parsing, context-aware bullet rewrites anchored in your genuine projects, and humanized cover letters.
          </p>
        </section>

        {/* Section 1: Inputs Dual Grid */}
        <section className="input-grid">
          {/* Left Panel: Resume Input */}
          <div className="panel-box">
            <div className="panel-header">
              <span className="panel-title">
                <FileText size={15} color="var(--accent-primary)" />
                1. Candidate Resume
              </span>
              <div style={{ display: 'flex', gap: '0.35rem' }}>
                <button
                  className={`pill-btn ${inputMode === 'upload' ? 'active' : ''}`}
                  onClick={() => setInputMode('upload')}
                >
                  Upload File
                </button>
                <button
                  className={`pill-btn ${inputMode === 'sample' ? 'active' : ''}`}
                  onClick={() => setInputMode('sample')}
                >
                  Presets
                </button>
                <button
                  className={`pill-btn ${inputMode === 'paste' ? 'active' : ''}`}
                  onClick={() => setInputMode('paste')}
                >
                  Raw Text
                </button>
              </div>
            </div>

            {inputMode === 'paste' ? (
              <textarea
                className="editor-textarea"
                placeholder="Paste raw resume text here..."
                value={pastedResumeText}
                onChange={(e) => {
                  setPastedResumeText(e.target.value);
                  setSelectedSampleId(null);
                  setFile(null);
                }}
              />
            ) : inputMode === 'upload' ? (
              <div
                className={`dropzone ${file ? 'active' : ''}`}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleFileDrop}
                onClick={() => fileInputRef.current && fileInputRef.current.click()}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  accept=".pdf,.docx,.doc"
                  onChange={handleFileSelect}
                />

                {file ? (
                  <div className="dropzone-file-info">
                    <FileCheck size={28} color="var(--accent-primary)" />
                    <span className="filename-badge">{file.name}</span>
                    <span className="mono" style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                      {(file.size / 1024).toFixed(1)} KB • Click or drop to replace
                    </span>
                  </div>
                ) : (
                  <div>
                    <Upload size={24} color="var(--text-muted)" style={{ margin: '0 auto 0.65rem auto' }} />
                    <div style={{ fontSize: '0.88rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                      Drop your resume here, or <span style={{ color: 'var(--accent-primary)', textDecoration: 'underline' }}>browse</span>
                    </div>
                    <span className="mono" style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                      Supports PDF and DOCX documents
                    </span>
                  </div>
                )}
              </div>
            ) : (
              /* Sample Preset Selector */
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{
                  padding: '1.2rem',
                  backgroundColor: 'var(--bg-subtle)',
                  borderRadius: '6px',
                  border: '1px solid var(--border-hairline)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.35rem'
                }}>
                  <div className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Active Candidate Profile
                  </div>
                  <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {sampleData?.resumes?.[selectedSampleId]?.title || selectedSampleId}
                  </div>
                  <span className="mono" style={{ fontSize: '0.74rem', color: 'var(--accent-primary)' }}>
                    {sampleData?.resumes?.[selectedSampleId]?.filename} • Real engineering bullet points
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                  <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', alignSelf: 'center' }}>PROFILE:</span>
                  <button
                    className={`pill-btn ${selectedSampleId === 'fullstack_ai_dev' ? 'active' : ''}`}
                    onClick={() => loadResumePreset('fullstack_ai_dev')}
                  >
                    Full-Stack AI Developer
                  </button>
                  <button
                    className={`pill-btn ${selectedSampleId === 'backend_engineer' ? 'active' : ''}`}
                    onClick={() => loadResumePreset('backend_engineer')}
                  >
                    Senior Backend (5+ Yrs)
                  </button>
                  <button
                    className={`pill-btn ${selectedSampleId === 'frontend_specialist' ? 'active' : ''}`}
                    onClick={() => loadResumePreset('frontend_specialist')}
                  >
                    Frontend Specialist (React)
                  </button>
                  <button
                    className={`pill-btn ${selectedSampleId === 'ai_ml_engineer' ? 'active' : ''}`}
                    onClick={() => loadResumePreset('ai_ml_engineer')}
                  >
                    ML / LLMs Engineer
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel: Job Description */}
          <div className="panel-box">
            <div className="panel-header">
              <span className="panel-title">
                <Briefcase size={15} color="var(--accent-primary)" />
                2. Target Job Description
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <span className="mono" style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                  {jobDescription.trim() ? jobDescription.trim().split(/\s+/).length : 0} words • {jobDescription.length} chars
                </span>
                {jobDescription && (
                  <button
                    className="btn-ghost"
                    style={{ padding: '0.15rem 0.45rem', fontSize: '0.7rem' }}
                    onClick={() => setJobDescription('')}
                    title="Clear Job Description text"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

            <textarea
              className="editor-textarea"
              placeholder="Paste the target job description or requirements here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />

            {/* Presets Grid */}
            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>TARGET ROLE:</span>
              <button
                id="btn-jd-software-developer"
                className={`pill-btn ${selectedJdKey === 'software_developer' ? 'active' : ''}`}
                onClick={() => loadJdPreset('software_developer')}
              >
                Software Developer (CoreTech)
              </button>
              <button
                className={`pill-btn ${selectedJdKey === 'fullstack_ai' ? 'active' : ''}`}
                onClick={() => loadJdPreset('fullstack_ai')}
              >
                Full-Stack AI (Kinetik)
              </button>
              <button
                className={`pill-btn ${selectedJdKey === 'staff_backend' ? 'active' : ''}`}
                onClick={() => loadJdPreset('staff_backend')}
              >
                Senior Backend (Voxel)
              </button>
              <button
                className={`pill-btn ${selectedJdKey === 'frontend_react' ? 'active' : ''}`}
                onClick={() => loadJdPreset('frontend_react')}
              >
                Frontend React (Vercel)
              </button>
              <button
                className={`pill-btn ${selectedJdKey === 'ml_llm_engineer' ? 'active' : ''}`}
                onClick={() => loadJdPreset('ml_llm_engineer')}
              >
                ML & LLMs (ScaleAI)
              </button>
              <button
                className={`pill-btn ${selectedJdKey === 'devops_platform' ? 'active' : ''}`}
                onClick={() => loadJdPreset('devops_platform')}
              >
                DevOps & Cloud (Datadog)
              </button>
              <button
                className={`pill-btn ${selectedJdKey === 'junior_software_eng' ? 'active' : ''}`}
                onClick={() => loadJdPreset('junior_software_eng')}
              >
                Associate SWE (Shopify)
              </button>
            </div>
          </div>
        </section>

        {/* Central Primary Run Action */}
        <section className="action-center-bar">
          <button
            id="btn-run-analysis"
            className="btn-primary-large"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 size={16} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
                <span>Running Telemetry Analysis...</span>
              </>
            ) : (
              <>
                <span>Run Comprehensive Analysis</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </section>

        {/* Status / Error feedback */}
        {error && (
          <div style={{ padding: '0.85rem 1.25rem', backgroundColor: 'var(--accent-danger-subtle)', border: '1px solid var(--accent-danger-border)', borderRadius: '6px', color: 'var(--accent-danger)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', maxWidth: '800px', margin: '0 auto' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {loading && (
          <div style={{ padding: '2rem 1.75rem', backgroundColor: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-hairline)', width: '100%', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <Loader2 size={16} className="spin" style={{ animation: 'spin 1s linear infinite', color: 'var(--accent-primary)' }} />
              <span className="mono" style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                {analysisStep}
              </span>
            </div>
            <div className="pulse-line" style={{ width: '70%' }} />
          </div>
        )}

        {/* Section 2: Results Dashboard */}
        {results && !loading && (
          <section style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
            {/* Audit Toolbar */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1rem', padding: '0 0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="mono" style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                  EVALUATING AGAINST:
                </span>
                <span className="mono" style={{ fontSize: '0.82rem', color: 'var(--accent-primary)', fontWeight: 600 }}>
                  {sampleData?.job_descriptions?.[selectedJdKey]?.title || 'Target Role'}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  id="btn-copy-audit-report"
                  className="btn-ghost"
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem', backgroundColor: 'var(--bg-subtle)' }}
                  onClick={handleCopyAuditReport}
                >
                  {copiedReport ? (
                    <>
                      <Check size={13} color="var(--accent-primary)" />
                      <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>Report Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy size={13} />
                      <span>Copy Audit Report (.md)</span>
                    </>
                  )}
                </button>
                <button
                  id="btn-download-audit-report"
                  className="btn-ghost"
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem', backgroundColor: 'var(--bg-subtle)' }}
                  onClick={handleDownloadAuditReport}
                >
                  <Download size={13} />
                  <span>Download Report (.md)</span>
                </button>
              </div>
            </div>

            {/* Centered Navigation Tabs */}
            <nav className="dashboard-tabs">
              <button
                id="tab-ats"
                className={`tab-btn ${activeTab === 'ats' ? 'active' : ''}`}
                onClick={() => setActiveTab('ats')}
              >
                <span>ATS Telemetry</span>
                <span className="tab-counter">{results.ats_score?.overall_score || 0}%</span>
              </button>
              
              <button
                id="tab-skills"
                className={`tab-btn ${activeTab === 'skills' ? 'active' : ''}`}
                onClick={() => setActiveTab('skills')}
              >
                <span>Skills & Gaps</span>
                <span className="tab-counter">
                  {results.match_analysis?.matched_skills?.length || 0} / {(results.match_analysis?.matched_skills?.length || 0) + (results.match_analysis?.missing_skills?.length || 0)}
                </span>
              </button>
              
              <button
                id="tab-suggestions"
                className={`tab-btn ${activeTab === 'suggestions' ? 'active' : ''}`}
                onClick={() => setActiveTab('suggestions')}
              >
                <span>Bullet Rewrites</span>
                <span className="tab-counter">{results.suggestions?.length || 0}</span>
              </button>
              
              <button
                id="tab-cover-letter"
                className={`tab-btn ${activeTab === 'cover-letter' ? 'active' : ''}`}
                onClick={() => setActiveTab('cover-letter')}
              >
                <span>Cover Letter Draft</span>
              </button>
              
              <button
                id="tab-raw"
                className={`tab-btn ${activeTab === 'raw' ? 'active' : ''}`}
                onClick={() => setActiveTab('raw')}
              >
                <span>Parse Telemetry</span>
              </button>
            </nav>

            {/* Tab 1: ATS Compatibility */}
            {activeTab === 'ats' && (
              <AtsScoreGauge atsData={results.ats_score} />
            )}

            {/* Tab 2: Skills & Gaps Matrix */}
            {activeTab === 'skills' && (
              <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-hairline)', borderRadius: '10px', padding: '2rem' }}>
                <SkillMatchBoard
                  skills={results.skills}
                  matchAnalysis={results.match_analysis}
                />
              </div>
            )}

            {/* Tab 3: Bullet Rewrites */}
            {activeTab === 'suggestions' && (
              <BulletSuggestions suggestions={results.suggestions} />
            )}

            {/* Tab 4: Cover Letter Draft */}
            {activeTab === 'cover-letter' && (
              <CoverLetterTab
                resumeText={results.full_text || results.raw_text_preview}
                jobDescription={jobDescription}
                candidateName={
                  results.resume_meta?.candidate_name && results.resume_meta?.candidate_name !== 'Applicant' 
                    ? results.resume_meta.candidate_name 
                    : sampleData?.resumes?.[selectedSampleId]?.candidate_name || 'Applicant'
                }
              />
            )}

            {/* Tab 5: Raw Telemetry Inspector */}
            {activeTab === 'raw' && (
              <div style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-hairline)', borderRadius: '10px', padding: '2rem' }}>
                <ResumeInspector
                  resumeMeta={results.resume_meta}
                  rawText={results.raw_text_preview}
                />
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
