import React, { useState, useEffect } from 'react';
import { Key, X, Check, Shield } from 'lucide-react';
import { getStoredApiKey, setStoredApiKey } from '../api';

export default function ApiKeyModal({ isOpen, onClose, onSave }) {
  const [key, setKey] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setKey(getStoredApiKey());
      setSaved(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    setStoredApiKey(key);
    setSaved(true);
    setTimeout(() => {
      onSave && onSave(key);
      onClose();
    }, 600);
  };

  const handleClear = () => {
    setStoredApiKey('');
    setKey('');
    onSave && onSave('');
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Key size={16} color="var(--accent-primary)" />
            <h3 style={{ fontSize: '1rem', margin: 0 }}>Gemini API Key</h3>
          </div>
          <button className="panel-action" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          Your API key is stored locally in your browser's <code className="mono">localStorage</code> and transmitted directly to the local backend. If left blank, the app will use any key configured in <code className="mono">backend/.env</code> or our high-fidelity fallback analysis pipeline.
        </p>

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input
            type="password"
            className="modal-input"
            placeholder="AIzaSy..."
            value={key}
            onChange={(e) => setKey(e.target.value)}
            autoFocus
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
            {key ? (
              <button type="button" className="btn-ghost" onClick={handleClear} style={{ color: 'var(--accent-danger)' }}>
                Remove Key
              </button>
            ) : <div />}

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button type="button" className="btn-ghost" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                {saved ? <><Check size={14} /> Saved</> : 'Save Key'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
