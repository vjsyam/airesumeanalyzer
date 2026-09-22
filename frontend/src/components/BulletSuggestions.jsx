import React, { useState } from 'react';
import { Copy, Check, CheckCheck, Sparkles, Target, ArrowRight } from 'lucide-react';

export default function BulletSuggestions({ suggestions }) {
  const [copiedIdx, setCopiedIdx] = useState(null);
  const [allCopied, setAllCopied] = useState(false);

  if (!suggestions || suggestions.length === 0) return null;

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 1800);
  };

  const handleCopyAll = () => {
    const allText = suggestions.map((s, i) => `• ${s.rewritten_bullet}`).join('\n\n');
    navigator.clipboard.writeText(allText);
    setAllCopied(true);
    setTimeout(() => setAllCopied(false), 2000);
  };

  return (
    <div className="suggestions-flow">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.05rem', margin: 0 }}>Bullet-Level Rewrite Suggestions</h2>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Action-oriented before-and-after improvements anchored directly in your actual projects and experience.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            className="btn-ghost"
            style={{ padding: '0.35rem 0.8rem', fontSize: '0.76rem', borderColor: 'var(--border-hairline)', backgroundColor: 'var(--bg-subtle)' }}
            onClick={handleCopyAll}
          >
            {allCopied ? (
              <>
                <Check size={13} color="var(--accent-primary)" />
                <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>All Bullets Copied!</span>
              </>
            ) : (
              <>
                <Copy size={13} />
                <span>Copy All Improved Bullets</span>
              </>
            )}
          </button>
          <span className="compliance-badge">
            <CheckCheck size={12} />
            /human voice rules applied
          </span>
          <span className="compliance-badge" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderColor: 'var(--border-hairline)', color: 'var(--text-secondary)' }}>
            Zero clichés & no em-dashes
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {suggestions.map((item, idx) => (
          <div key={idx} className="suggestion-item">
            <div className="suggestion-meta">
              <span className="suggestion-location-tag">
                <Target size={12} />
                {item.target_location}
              </span>
              
              <button
                className="btn-ghost"
                style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem' }}
                onClick={() => handleCopy(item.rewritten_bullet, idx)}
              >
                {copiedIdx === idx ? (
                  <>
                    <Check size={12} color="var(--accent-primary)" />
                    <span style={{ color: 'var(--accent-primary)', fontWeight: 500 }}>Copied to Clipboard</span>
                  </>
                ) : (
                  <>
                    <Copy size={12} />
                    <span>Copy Rewrite</span>
                  </>
                )}
              </button>
            </div>

            {/* Side by side diff */}
            <div className="diff-grid">
              <div className="diff-box original">
                <div className="diff-box-title">Current Resume Bullet</div>
                <div>{item.original_bullet}</div>
              </div>

              <div className="diff-box improved">
                <div className="diff-box-title" style={{ color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span>Targeted High-Impact Revision</span>
                </div>
                <div>{item.rewritten_bullet}</div>
              </div>
            </div>

            <div className="suggestion-rationale">
              <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--accent-primary)', fontWeight: 600 }}>ALIGNMENT RATIONALE:</span>
              <span>{item.rationale}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
