import React from 'react';
import { FileCode, Layers, ShieldCheck, Mail, Phone, ExternalLink } from 'lucide-react';

export default function ResumeInspector({ resumeMeta, rawText }) {
  if (!resumeMeta) return null;

  const contact = resumeMeta.contact_info || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      <div>
        <h2 style={{ fontSize: '1.05rem', margin: 0 }}>Resume Parse & Layout Telemetry</h2>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
          Exact data extracted by server-side PDF/DOCX parser and AST structure analyzer.
        </p>
      </div>

      {/* Grid of parsed indicators */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div style={{ padding: '1rem', backgroundColor: 'var(--bg-subtle)', borderRadius: '4px', border: '1px solid var(--border-hairline)' }}>
          <div className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>FILE PARSED</div>
          <div className="mono" style={{ fontSize: '0.85rem', color: 'var(--text-primary)', marginTop: '0.25rem' }}>{resumeMeta.filename}</div>
          <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {resumeMeta.word_count} words • {resumeMeta.page_count} page(s)
          </div>
        </div>

        <div style={{ padding: '1rem', backgroundColor: 'var(--bg-subtle)', borderRadius: '4px', border: '1px solid var(--border-hairline)' }}>
          <div className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>LAYOUT INTEGRITY</div>
          <div className="mono" style={{ fontSize: '0.85rem', color: resumeMeta.has_columns_suspected ? 'var(--accent-danger)' : 'var(--accent-primary)', marginTop: '0.25rem' }}>
            {resumeMeta.has_columns_suspected ? 'Multi-Column (Risk)' : 'Single-Column (Clean)'}
          </div>
          <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {resumeMeta.tables_count} tables • {resumeMeta.images_count} images
          </div>
        </div>

        <div style={{ padding: '1rem', backgroundColor: 'var(--bg-subtle)', borderRadius: '4px', border: '1px solid var(--border-hairline)' }}>
          <div className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>CONTACT PARSEABILITY</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', marginTop: '0.25rem' }}>
            <span className="mono" style={{ fontSize: '0.72rem', color: contact.has_email ? 'var(--accent-primary)' : 'var(--accent-danger)' }}>
              {contact.has_email ? `✓ ${contact.email}` : '✗ Missing email'}
            </span>
            <span className="mono" style={{ fontSize: '0.72rem', color: contact.has_phone ? 'var(--accent-primary)' : 'var(--accent-danger)' }}>
              {contact.has_phone ? `✓ ${contact.phone}` : '✗ Missing phone'}
            </span>
          </div>
        </div>
      </div>

      {/* Raw extracted text box */}
      <div>
        <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
          Server-Side Extracted Text Preview
        </div>
        <div style={{
          backgroundColor: 'var(--bg-subtle)',
          border: '1px solid var(--border-hairline)',
          borderRadius: '4px',
          padding: '1rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.78rem',
          lineHeight: '1.6',
          color: 'var(--text-secondary)',
          maxHeight: '320px',
          overflowY: 'auto',
          whiteSpace: 'pre-wrap'
        }}>
          {rawText}
        </div>
      </div>
    </div>
  );
}
