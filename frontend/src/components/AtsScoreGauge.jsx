import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ChevronRight, ShieldCheck, Zap, ArrowUpRight } from 'lucide-react';

export default function AtsScoreGauge({ atsData }) {
  if (!atsData) return null;

  const { overall_score, verdict, summary, breakdown } = atsData;
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = overall_score;
    if (start === end) {
      setDisplayScore(end);
      return;
    }
    const duration = 750;
    const stepTime = 16;
    const steps = duration / stepTime;
    const increment = end / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setDisplayScore(end);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [overall_score]);

  const getScoreColorClass = (val) => {
    if (val >= 85) return 'high';
    if (val >= 70) return 'medium';
    return 'low';
  };

  const getProgressFillClass = (val) => {
    if (val >= 80) return '';
    if (val >= 60) return 'warning';
    return 'danger';
  };

  return (
    <div className="ats-score-editorial">
      {/* Left Column: Standalone Editorial Number */}
      <div className="score-display-block">
        <span className="mono" style={{ fontSize: '0.74rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)' }}>
          ATS COMPATIBILITY RATING
        </span>
        
        <div className={`score-number ${getScoreColorClass(overall_score)}`}>
          {displayScore}
          <span style={{ fontSize: '1.75rem', fontWeight: 500, color: 'var(--text-muted)', marginLeft: '0.2rem' }}>/100</span>
        </div>

        <div className="score-benchmark-badge">
          <ShieldCheck size={13} color="var(--accent-primary)" />
          <span>Target: 80+ for top 10% screening tier</span>
        </div>

        <div className="score-verdict">{verdict}</div>
        <p className="score-summary">{summary}</p>
      </div>

      {/* Right Column: Breakdown Telemetry */}
      <div className="submetrics-list">
        {/* 1. Target Keyword & Hard Skill Alignment */}
        {breakdown.keyword_match && (
          <div className="submetric-row">
            <div className="submetric-header">
              <span className="submetric-label">{breakdown.keyword_match.label} ({breakdown.keyword_match.weight || 55}%)</span>
              <span className="submetric-value">{breakdown.keyword_match.score}%</span>
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${getProgressFillClass(breakdown.keyword_match.score)}`}
                style={{ width: `${breakdown.keyword_match.score}%` }}
              />
            </div>
            <span className="submetric-notes">{breakdown.keyword_match.notes}</span>
          </div>
        )}

        {/* 2. Quantifiable Metrics & Impact */}
        {breakdown.measurable_impact && (
          <div className="submetric-row">
            <div className="submetric-header">
              <span className="submetric-label">{breakdown.measurable_impact.label} ({breakdown.measurable_impact.weight || 20}%)</span>
              <span className="submetric-value">{breakdown.measurable_impact.score}%</span>
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${getProgressFillClass(breakdown.measurable_impact.score)}`}
                style={{ width: `${breakdown.measurable_impact.score}%` }}
              />
            </div>
            <div className="submetric-notes">
              {Array.isArray(breakdown.measurable_impact.notes)
                ? breakdown.measurable_impact.notes.map((note, i) => (
                    <div key={i} style={{ marginTop: '0.2rem' }}>• {note}</div>
                  ))
                : breakdown.measurable_impact.notes}
            </div>
          </div>
        )}

        {/* 3. Section Structure */}
        {breakdown.section_structure && (
          <div className="submetric-row">
            <div className="submetric-header">
              <span className="submetric-label">{breakdown.section_structure.label} ({breakdown.section_structure.weight || 15}%)</span>
              <span className="submetric-value">{breakdown.section_structure.score}%</span>
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${getProgressFillClass(breakdown.section_structure.score)}`}
                style={{ width: `${breakdown.section_structure.score}%` }}
              />
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginTop: '0.25rem' }}>
              {Object.entries(breakdown.section_structure.sections || {}).map(([sec, data]) => (
                <span key={sec} className="mono" style={{ fontSize: '0.72rem', color: data.found ? 'var(--text-secondary)' : 'var(--accent-danger)' }}>
                  {data.found ? '✓' : '✗'} {sec}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 4. Formatting & Parseability */}
        {breakdown.formatting_compatibility && (
          <div className="submetric-row">
            <div className="submetric-header">
              <span className="submetric-label">{breakdown.formatting_compatibility.label} ({breakdown.formatting_compatibility.weight || 10}%)</span>
              <span className="submetric-value">{breakdown.formatting_compatibility.score}%</span>
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${getProgressFillClass(breakdown.formatting_compatibility.score)}`}
                style={{ width: `${breakdown.formatting_compatibility.score}%` }}
              />
            </div>
            <div className="submetric-notes">
              {Array.isArray(breakdown.formatting_compatibility.notes)
                ? breakdown.formatting_compatibility.notes.map((note, i) => (
                    <div key={i} style={{ marginTop: '0.2rem' }}>• {note}</div>
                  ))
                : breakdown.formatting_compatibility.notes}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
