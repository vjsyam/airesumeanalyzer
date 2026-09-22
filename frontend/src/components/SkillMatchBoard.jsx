import React, { useState } from 'react';
import { Check, X, AlertCircle, Search, Filter, Copy } from 'lucide-react';

export default function SkillMatchBoard({ skills, matchAnalysis }) {
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedSection, setCopiedSection] = useState(null);

  const handleCopyList = (items, sectionName) => {
    if (!items || items.length === 0) return;
    const text = items.join(', ');
    navigator.clipboard.writeText(text);
    setCopiedSection(sectionName);
    setTimeout(() => setCopiedSection(null), 1800);
  };

  if (!skills && !matchAnalysis) return null;

  const matched = matchAnalysis?.matched_skills || [];
  const missing = matchAnalysis?.missing_skills || [];
  const gaps = matchAnalysis?.keyword_gaps || [];

  const techSkills = skills?.technical_skills || [];
  const tools = skills?.tools_and_platforms || [];
  const certs = skills?.certifications || [];
  const methodologies = skills?.methodologies || [];

  const filterBySearch = (items) => {
    if (!searchQuery.trim()) return items;
    return items.filter((item) => item.toLowerCase().includes(searchQuery.toLowerCase().trim()));
  };

  const filteredMatched = filterBySearch(matched);
  const filteredMissing = filterBySearch(missing);
  const filteredGaps = filterBySearch(gaps);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Overview stats bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'baseline' }}>
          <h2 style={{ fontSize: '1.05rem', margin: 0 }}>Skill & Keyword Telemetry</h2>
          <span className="mono" style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Match Ratio: <strong style={{ color: 'var(--accent-primary)' }}>{Math.round((matchAnalysis?.match_ratio || 0) * 100)}%</strong>
          </span>
        </div>

        {/* Controls: Search and Filter Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={13} style={{ position: 'absolute', left: '0.6rem', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search skill..."
              className="mono"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                backgroundColor: 'var(--bg-subtle)',
                border: '1px solid var(--border-hairline)',
                borderRadius: '4px',
                padding: '0.3rem 0.6rem 0.3rem 1.8rem',
                fontSize: '0.75rem',
                color: 'var(--text-primary)',
                outline: 'none',
                width: '140px'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '0.35rem' }}>
            <button
              className={`pill-btn ${activeFilter === 'all' ? 'active' : ''}`}
              onClick={() => setActiveFilter('all')}
            >
              All Items ({matched.length + missing.length + gaps.length})
            </button>
            <button
              className={`pill-btn ${activeFilter === 'matched' ? 'active' : ''}`}
              onClick={() => setActiveFilter('matched')}
            >
              Confirmed ({matched.length})
            </button>
            <button
              className={`pill-btn ${activeFilter === 'missing' ? 'active' : ''}`}
              onClick={() => setActiveFilter('missing')}
            >
              Missing ({missing.length})
            </button>
            <button
              className={`pill-btn ${activeFilter === 'gaps' ? 'active' : ''}`}
              onClick={() => setActiveFilter('gaps')}
            >
              Keyword Gaps ({gaps.length})
            </button>
          </div>
        </div>
      </div>

      {matchAnalysis?.fit_summary && (
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          {matchAnalysis.fit_summary}
        </p>
      )}

      {/* Chips Grouping */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Matched Skills */}
        {(activeFilter === 'all' || activeFilter === 'matched') && filteredMatched.length > 0 && (
          <div>
            <div className="mono" style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent-primary)', marginBottom: '0.65rem' }}>
              Confirmed Qualifications ({filteredMatched.length})
            </div>
            <div className="chips-grid">
              {filteredMatched.map((skill, idx) => (
                <span key={idx} className="chip matched">
                  <Check size={12} strokeWidth={2.5} />
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Missing Skills from JD */}
        {(activeFilter === 'all' || activeFilter === 'missing') && filteredMissing.length > 0 && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
              <div className="mono" style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent-danger)' }}>
                Missing from Resume ({filteredMissing.length})
              </div>
              <button
                className="btn-ghost"
                style={{ padding: '0.2rem 0.55rem', fontSize: '0.72rem' }}
                onClick={() => handleCopyList(filteredMissing, 'missing')}
              >
                {copiedSection === 'missing' ? (
                  <>
                    <Check size={11} color="var(--accent-primary)" />
                    <span style={{ color: 'var(--accent-primary)' }}>Copied List</span>
                  </>
                ) : (
                  <>
                    <Copy size={11} />
                    <span>Copy Missing (CSV)</span>
                  </>
                )}
              </button>
            </div>
            <div className="chips-grid">
              {filteredMissing.map((skill, idx) => (
                <span key={idx} className="chip missing">
                  <X size={12} strokeWidth={2.5} />
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Critical Domain Keyword Gaps */}
        {(activeFilter === 'all' || activeFilter === 'gaps') && filteredGaps.length > 0 && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
              <div className="mono" style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent-warning)' }}>
                Target Domain Concepts & Keyword Gaps ({filteredGaps.length})
              </div>
              <button
                className="btn-ghost"
                style={{ padding: '0.2rem 0.55rem', fontSize: '0.72rem' }}
                onClick={() => handleCopyList(filteredGaps, 'gaps')}
              >
                {copiedSection === 'gaps' ? (
                  <>
                    <Check size={11} color="var(--accent-primary)" />
                    <span style={{ color: 'var(--accent-primary)' }}>Copied List</span>
                  </>
                ) : (
                  <>
                    <Copy size={11} />
                    <span>Copy Gaps (CSV)</span>
                  </>
                )}
              </button>
            </div>
            <div className="chips-grid">
              {filteredGaps.map((gap, idx) => (
                <span key={idx} className="chip gap">
                  <AlertCircle size={12} strokeWidth={2.5} />
                  {gap}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Extracted Structured Resume Inventory */}
        {activeFilter === 'all' && !searchQuery && (
          <div style={{ marginTop: '0.75rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-hairline)' }}>
            <div className="mono" style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
              Extracted Resume Skills Inventory
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
              {techSkills.length > 0 && (
                <div>
                  <div className="mono" style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>Technical Stack</div>
                  <div className="chips-grid">
                    {techSkills.map((s, i) => (
                      <span key={i} className="chip">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {tools.length > 0 && (
                <div>
                  <div className="mono" style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>Tools & Infrastructure</div>
                  <div className="chips-grid">
                    {tools.map((s, i) => (
                      <span key={i} className="chip">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {(certs.length > 0 || methodologies.length > 0) && (
                <div>
                  <div className="mono" style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>Certifications & Methods</div>
                  <div className="chips-grid">
                    {[...certs, ...methodologies].map((s, i) => (
                      <span key={i} className="chip">{s}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
