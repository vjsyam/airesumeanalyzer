import React, { useState } from 'react';
import { Terminal, Key, ShieldCheck, Cpu } from 'lucide-react';
import ApiKeyModal from './ApiKeyModal';
import { getStoredApiKey } from '../api';

export default function Header({ serverStatus, activeEngine }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [hasCustomKey, setHasCustomKey] = useState(!!getStoredApiKey());

  return (
    <>
      <header className="app-header">
        <div className="brand-section">
          <Terminal size={18} color="var(--accent-primary)" />
          <h1 style={{ fontSize: '1rem', fontWeight: 600, margin: 0 }}>RESUME.AI</h1>
          <span className="brand-badge">TELEMETRY V1.0</span>
        </div>

        <div className="header-status">
          <div className="engine-indicator">
            <span className={`status-dot ${serverStatus === 'healthy' ? '' : 'warning'}`} />
            <span>{serverStatus === 'healthy' ? (activeEngine || 'Gemini 2.5 Flash') : 'Server Offline'}</span>
          </div>

          <button
            className="btn-ghost"
            style={{ padding: '0.35rem 0.65rem', fontSize: '0.76rem' }}
            onClick={() => setModalOpen(true)}
          >
            <Key size={13} />
            <span>{hasCustomKey ? 'API Key Set' : 'Set API Key'}</span>
          </button>
        </div>
      </header>

      <ApiKeyModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={(key) => setHasCustomKey(!!key)}
      />
    </>
  );
}
