import React, { useState, useEffect } from 'react';
import { Key, Eye, EyeOff, Save, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react';

export default function SettingsPanel({ onApiKeySaved }) {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => { fetchSettingsStatus(); }, []);

  const fetchSettingsStatus = async () => {
    try {
      const res = await fetch('/api/settings');
      const data = await res.json();
      if (data.has_api_key) { setIsSaved(true); setApiKey('••••••••••••••••••••••••••••••••'); }
    } catch (err) { console.error("Error checking settings:", err); }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!apiKey.trim() || apiKey === '••••••••••••••••••••••••••••••••') {
      setMessage({ text: 'Enter a valid new API Key.', type: 'warning' }); return;
    }
    setLoading(true); setMessage({ text: '', type: '' });
    try {
      const res = await fetch('/api/settings', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey.trim() }),
      });
      const data = await res.json();
      if (res.ok) {
        setIsSaved(true); setApiKey('••••••••••••••••••••••••••••••••');
        setMessage({ text: 'API Key saved successfully.', type: 'success' });
        if (onApiKeySaved) onApiKeySaved();
      } else { setMessage({ text: data.detail || 'Save failed.', type: 'error' }); }
    } catch { setMessage({ text: 'Backend connection failed.', type: 'error' }); }
    finally { setLoading(false); }
  };

  return (
    <div className="settings-panel">
      <div>
        <h2 className="page-heading">Gemini Configuration</h2>
        <p className="page-sub">Connect your Google Gemini API key to enable AI-powered answers and chart generation.</p>
      </div>

      {message.text && (
        <div className={`notif-banner ${message.type}`}>
          {message.type === 'success' && <CheckCircle size={16} />}
          {(message.type === 'error' || message.type === 'warning') && <AlertCircle size={16} />}
          <span>{message.text}</span>
        </div>
      )}

      <div className="settings-card">
        <div className="settings-card-title">
          <Key size={16} style={{ color: '#A100FF' }} />
          API Key
        </div>

        <form onSubmit={handleSave} style={{ display:'flex', flexDirection:'column', gap:18 }}>
          <div className="form-group">
            <label className="form-label">Gemini API Key</label>
            <div className="form-input-wrap">
              <Key size={15} className="form-input-icon" />
              <input
                type={showKey ? 'text' : 'password'}
                className="form-input"
                placeholder={isSaved ? "Saved — enter new key to update" : "AIzaSy…"}
                value={apiKey}
                onChange={e => setApiKey(e.target.value)}
                disabled={loading}
              />
              <button type="button" className="form-input-toggle" onClick={() => setShowKey(!showKey)}>
                {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            <Save size={16} />
            {loading ? 'Saving…' : 'Save Configuration'}
          </button>
        </form>
      </div>

      <div className="settings-card">
        <div className="settings-card-title">Setup Guide</div>
        <div className="setup-steps">
          <div className="step-row">
            <span className="step-num">1</span>
            <span>
              Visit{' '}
              <a href="https://aistudio.google.com/" target="_blank" rel="noreferrer"
                 style={{ color:'#A100FF', textDecoration:'none', fontWeight:600 }}>
                Google AI Studio <ExternalLink size={11} style={{ verticalAlign:-1 }} />
              </a>{' '}
              and generate a free API key.
            </span>
          </div>
          <div className="step-row">
            <span className="step-num">2</span>
            <span>Paste the key above and click Save Configuration.</span>
          </div>
          <div className="step-row">
            <span className="step-num">3</span>
            <span>Upload documents, then ask questions — KnowledgeBot will generate answers with citations and charts.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
