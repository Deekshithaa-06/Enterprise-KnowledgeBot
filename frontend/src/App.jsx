import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, FolderOpen, AlertCircle, Database, Cpu, Sun, Moon, Plus } from 'lucide-react';
import ChatContainer from './components/ChatContainer';
import DocManager from './components/DocManager';
import SettingsPanel from './components/SettingsPanel';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [documents, setDocuments] = useState([]);
  const [hasApiKey, setHasApiKey] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const chatActionsRef = useRef(null);

  useEffect(() => { fetchDocuments(); checkApiKeyStatus(); }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const [showTimeoutModal, setShowTimeoutModal] = useState(false);

  useEffect(() => {
    let timeoutId;
    const resetTimer = () => {
      if (showTimeoutModal) return;
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        setShowTimeoutModal(true);
      }, 5 * 60 * 1000); // 5 minutes
    };

    const events = ['mousemove', 'keydown', 'scroll', 'click'];
    events.forEach(e => window.addEventListener(e, resetTimer));
    resetTimer();

    return () => {
      clearTimeout(timeoutId);
      events.forEach(e => window.removeEventListener(e, resetTimer));
    };
  }, [showTimeoutModal]);

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/documents');
      if (res.ok) setDocuments(await res.json());
    } catch (err) { console.error("Error loading documents:", err); }
  };

  const checkApiKeyStatus = async () => {
    try {
      const res = await fetch('/api/settings');
      if (res.ok) { const d = await res.json(); setHasApiKey(d.has_api_key); }
    } catch (err) { console.error("Error checking API key:", err); }
  };

  const activeDocCount = documents.filter(d => d.status === 'active').length;
  const processingCount = documents.filter(d => d.status === 'processing').length;

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="acc-logo-row">
            <div className="acc-logo-mark">&gt;</div>
            <div className="acc-logo-text">
              <span className="acc-logo-product">KnowledgeBot</span>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button className="nav-btn" onClick={() => setActiveTab('chat')}>
            <MessageSquare size={16} /> Ask Bot
          </button>
          <button
            type="button"
            className="nav-btn"
            onClick={() => {
              setActiveTab('chat');
              chatActionsRef.current?.newChat?.();
            }}
          >
            <Plus size={16} /> New Chat
          </button>
          <button className="nav-btn" onClick={() => setActiveTab('documents')}>
            <FolderOpen size={16} /> Documents
          </button>
        </nav>

        <div className="sidebar-content">
          <div className="stats-card">
            <div className="stats-title">System Status</div>
            <div className="stats-row">
              <span><Database size={12} style={{ marginRight: 5, verticalAlign: -2 }} />Indexed</span>
              <span className="stats-value purple">{activeDocCount} files</span>
            </div>
            <div className="stats-row">
              <span><Cpu size={12} style={{ marginRight: 5, verticalAlign: -2 }} />Processing</span>
              <span className="stats-value">{processingCount}</span>
            </div>
            <div className="stats-row">
              <span>API Key</span>
              <span className="stats-value" style={{ color: hasApiKey ? 'var(--success)' : 'var(--warning)' }}>
                {hasApiKey ? 'Connected' : 'Missing'}
              </span>
            </div>
          </div>
        </div>

        {/* Theme Toggle */}
        <div className="theme-toggle-wrap">
          <button className="theme-toggle-btn" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? <Sun size={15} /> : <Moon size={15} />}
            <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
            <div style={{ flex: 1 }} />
            <div className="toggle-track"><div className="toggle-thumb" /></div>
          </button>
        </div>
      </aside>

      <main className="main-panel">
        <div style={{ flex: 1, display: activeTab === 'chat' ? 'flex' : 'none', flexDirection: 'column', overflow: 'hidden' }}>
          <ChatContainer ref={chatActionsRef} documentCount={activeDocCount} />
        </div>
        <div style={{ flex: 1, display: activeTab === 'documents' ? 'flex' : 'none', flexDirection: 'column', overflow: 'hidden' }}>
          <DocManager onDocsUpdated={(d) => setDocuments(d)} />
        </div>
      </main>

      {showTimeoutModal && (
        <div className="timeout-overlay">
          <div className="timeout-modal">
            <div className="timeout-icon"><AlertCircle size={48} /></div>
            <h2 className="timeout-title">Session Inactive</h2>
            <p className="timeout-text">Your session has been inactive for 5 minutes.<br/>Would you like to continue chatting, or start a fresh session?</p>
            <div className="timeout-actions">
              <button className="btn-primary" onClick={() => setShowTimeoutModal(false)}>Continue Session</button>
              <button className="btn-secondary" onClick={() => window.location.reload()}>Start Fresh</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
