import React, { useState, useEffect } from 'react';
import { FileText, Download, Copy, Check, CheckCheck, Loader2, RefreshCw } from 'lucide-react';
import { generateCoverLetter, exportDocx } from '../api';

export default function CoverLetterTab({ resumeText, jobDescription, candidateName }) {
  const [tone, setTone] = useState('direct');
  const [loading, setLoading] = useState(false);
  const [coverLetterData, setCoverLetterData] = useState(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async (selectedTone = tone) => {
    if (!resumeText || !jobDescription) {
      setError("Please perform an initial resume and job description analysis first.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await generateCoverLetter({
        resumeText,
        jobDescription,
        tone: selectedTone,
        candidateName
      });
      setCoverLetterData(data);
    } catch (err) {
      setError(err.message || 'Failed to generate cover letter.');
    } finally {
      setLoading(false);
    }
  };

  // Auto-generate on initial mount if resume & JD are present
  useEffect(() => {
    if (resumeText && jobDescription && !coverLetterData && !loading) {
      handleGenerate('direct');
    }
  }, [resumeText, jobDescription]);

  const handleToneChange = (newTone) => {
    setTone(newTone);
    handleGenerate(newTone);
  };

  const handleCopy = () => {
    if (!coverLetterData?.cover_letter) return;
    navigator.clipboard.writeText(coverLetterData.cover_letter);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadTxt = () => {
    if (!coverLetterData?.cover_letter) return;
    const blob = new Blob([coverLetterData.cover_letter], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(candidateName || 'Candidate').replace(/\s+/g, '_')}_Cover_Letter.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const handleDownloadDocx = async () => {
    if (!coverLetterData?.cover_letter) return;
    try {
      await exportDocx({
        coverLetter: coverLetterData.cover_letter,
        candidateName: candidateName || 'Applicant'
      });
    } catch (err) {
      alert("Failed to export DOCX: " + err.message);
    }
  };

  return (
    <div className="cover-letter-view">
      {/* Header and Tone Selectors */}
      <div className="cover-letter-toolbar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
          <div>
            <h2 style={{ fontSize: '1.05rem', margin: 0, fontWeight: 600 }}>Humanized Cover Letter Draft</h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Written in an authentic engineering voice. Zero corporate clichés, no em-dashes.
            </p>
          </div>

          <span className="compliance-badge">
            <CheckCheck size={12} />
            /human voice
          </span>
        </div>

        {/* Tone options */}
        <div className="tone-selector">
          <span className="mono" style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>TONE:</span>
          {['direct', 'conversational', 'executive'].map((t) => (
            <button
              key={t}
              id={`tone-btn-${t}`}
              className={`tone-btn ${tone === t ? 'active' : ''}`}
              onClick={() => handleToneChange(t)}
              disabled={loading}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div style={{ padding: '0.75rem 1rem', borderRadius: '6px', backgroundColor: 'var(--accent-danger-subtle)', color: 'var(--accent-danger)', fontSize: '0.85rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          {error}
        </div>
      )}

      {/* Initial empty state if neither generated nor loading */}
      {!coverLetterData && !loading && (
        <div style={{ padding: '3.5rem 2rem', textAlign: 'center', backgroundColor: 'var(--bg-subtle)', borderRadius: '8px', border: '1px solid var(--border-hairline)' }}>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.25rem', maxWidth: '480px', margin: '0 auto 1.5rem auto', fontSize: '0.9rem' }}>
            Generate a concise, bespoke cover letter connecting your genuine achievements to this position's engineering requirements.
          </p>
          <button className="btn-primary" onClick={() => handleGenerate()} style={{ margin: '0 auto' }}>
            Generate Humanized Cover Letter
          </button>
        </div>
      )}

      {/* Loading state before any data exists */}
      {!coverLetterData && loading && (
        <div style={{ padding: '4rem 2rem', textAlign: 'center', backgroundColor: 'var(--bg-subtle)', borderRadius: '8px', border: '1px solid var(--border-hairline)' }}>
          <Loader2 size={24} className="spin" style={{ margin: '0 auto 1rem auto', animation: 'spin 1s linear infinite', color: 'var(--accent-primary)' }} />
          <p className="mono" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Generating tailored {tone} tone cover letter with authentic project references...
          </p>
        </div>
      )}

      {/* Generated Cover Letter Document Preview */}
      {coverLetterData && (
        <div className="cover-letter-container" style={{ position: 'relative' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div className="mono" style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Word Count: {coverLetterData.word_count} | Mode: {coverLetterData.is_llm_generated ? 'Gemini 2.5 Flash' : 'Local Heuristic Engine'} | Tone: <span style={{ color: 'var(--accent-primary)', textTransform: 'capitalize' }}>{coverLetterData.tone || tone}</span>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button className="btn-ghost" onClick={handleCopy} title="Copy cover letter to clipboard">
                {copied ? <><Check size={13} color="var(--accent-primary)" /> Copied</> : <><Copy size={13} /> Copy</>}
              </button>

              <button className="btn-ghost" onClick={handleDownloadTxt} title="Download plain text file">
                <FileText size={13} /> TXT
              </button>

              <button className="btn-ghost" onClick={handleDownloadDocx} title="Download formatted Word document">
                <Download size={13} /> DOCX
              </button>

              <button 
                id="btn-regenerate-cover-letter"
                className="btn-ghost" 
                onClick={() => handleGenerate(tone)} 
                style={{ marginLeft: '0.5rem' }}
                disabled={loading}
                title="Generate fresh variation"
              >
                <RefreshCw size={13} className={loading ? "spin" : ""} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
                <span>Regenerate</span>
              </button>
            </div>
          </div>

          <div style={{ position: 'relative' }}>
            <div className={`cover-letter-paper ${loading ? 'loading-shimmer' : ''}`}>
              {coverLetterData.cover_letter}
            </div>

            {loading && (
              <div style={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                backgroundColor: 'rgba(11, 16, 26, 0.7)',
                backdropFilter: 'blur(2px)',
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem'
              }}>
                <Loader2 size={24} className="spin" style={{ animation: 'spin 1s linear infinite', color: 'var(--accent-primary)' }} />
                <span className="mono" style={{ fontSize: '0.82rem', color: 'var(--text-primary)' }}>
                  Synthesizing fresh {tone} draft...
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
