import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, BarChart2, Quote, FileText, FileSpreadsheet, Presentation, FileType } from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line,
  PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, Legend
} from 'recharts';

const renderMarkdown = (text) => {
  if (!text) return null;
  const lines = text.split('\n');
  let inList = false;
  const elements = [];
  let listItems = [];

  const parseInline = (str) => {
    let p = str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    p = p.replace(/\*(.*?)\*/g, '<em>$1</em>');
    p = p.replace(/`(.*?)`/g, '<code style="font-family:var(--font-mono);background:var(--acc-purple-subtle);padding:2px 6px;border-radius:4px;font-size:0.88em;color:var(--acc-purple);">$1</code>');
    return <span dangerouslySetInnerHTML={{ __html: p }} />;
  };

  lines.forEach((line, i) => {
    const t = line.trim();
    if (t.startsWith('- ') || t.startsWith('* ')) {
      inList = true;
      listItems.push(<li key={`li-${i}`}>{parseInline(t.substring(2))}</li>);
      return;
    }
    if (inList) { elements.push(<ul key={`ul-${i}`}>{listItems}</ul>); listItems = []; inList = false; }
    if (t.startsWith('### '))      elements.push(<h4 key={i}>{parseInline(t.substring(4))}</h4>);
    else if (t.startsWith('## '))  elements.push(<h3 key={i}>{parseInline(t.substring(3))}</h3>);
    else if (t.startsWith('# '))   elements.push(<h2 key={i}>{parseInline(t.substring(2))}</h2>);
    else if (t)                    elements.push(<p key={i}>{parseInline(t)}</p>);
    else                           elements.push(<div key={i} style={{ height: 4 }} />);
  });
  if (inList && listItems.length) elements.push(<ul key="ul-end">{listItems}</ul>);
  return <div>{elements}</div>;
};

const InteractiveChart = ({ chartConfig }) => {
  if (!chartConfig?.data?.length) return null;
  const { type, title, data } = chartConfig;
  const colors = ['#A100FF','#00A878','#E88C00','#2B7FE0','#E03E3E','#B84DFF'];
  const tt = { background:'var(--bg-card)', border:'1px solid var(--border)', borderRadius:6, color:'var(--text-primary)', fontSize:12 };

  const chart = () => {
    switch (type?.toLowerCase()) {
      case 'line':
        return (<LineChart data={data} margin={{top:10,right:30,left:0,bottom:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="label" stroke="var(--text-muted)" fontSize={11} /><YAxis stroke="var(--text-muted)" fontSize={11} />
          <RechartsTooltip contentStyle={tt} /><Legend wrapperStyle={{fontSize:11}} />
          <Line type="monotone" dataKey="value" name={title} stroke="#A100FF" strokeWidth={3} dot={{fill:'#B84DFF',r:5}} activeDot={{r:8}} />
        </LineChart>);
      case 'pie':
        return (<PieChart>
          <Pie data={data} cx="50%" cy="45%" innerRadius={55} outerRadius={80} paddingAngle={4} dataKey="value" nameKey="label" label={{fill:'var(--text-muted)',fontSize:10}}>
            {data.map((_,i) => <Cell key={i} fill={colors[i%colors.length]} />)}
          </Pie>
          <RechartsTooltip contentStyle={tt} /><Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{fontSize:11}} />
        </PieChart>);
      default:
        return (<BarChart data={data} margin={{top:10,right:30,left:0,bottom:0}}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="label" stroke="var(--text-muted)" fontSize={11} /><YAxis stroke="var(--text-muted)" fontSize={11} />
          <RechartsTooltip contentStyle={tt} /><Legend wrapperStyle={{fontSize:11}} />
          <Bar dataKey="value" name={title} radius={[5,5,0,0]}>
            {data.map((_,i) => <Cell key={i} fill={colors[i%colors.length]} />)}
          </Bar>
        </BarChart>);
    }
  };

  return (
    <div className="chat-chart-wrap">
      <div className="chart-label"><BarChart2 size={14} />{title}</div>
      <div className="chat-chart-container"><ResponsiveContainer width="100%" height="100%">{chart()}</ResponsiveContainer></div>
    </div>
  );
};

/* Supported formats data */
const supportedFormats = [
  { ext: 'PDF',  icon: FileText,        color: '#E03E3E' },
  { ext: 'DOCX', icon: FileType,        color: '#2B7FE0' },
  { ext: 'PPTX', icon: Presentation,    color: '#E88C00' },
  { ext: 'XLSX', icon: FileSpreadsheet, color: '#00A878' },
  { ext: 'CSV',  icon: FileSpreadsheet, color: '#00A878' },
  { ext: 'TXT',  icon: FileText,        color: '#8E8EA0' },
];

export default function ChatContainer({ documentCount }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeCitation, setActiveCitation] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput(''); setActiveCitation(null);
    setMessages(prev => [...prev, { role: 'user', text: q }]);
    setLoading(true);
    try {
      const res = await fetch('/api/query', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, top_k: 40 }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, res.ok
        ? { role:'bot', text: data.answer, citations: data.citations||[], chart: data.chart||null }
        : { role:'bot', text: `### Error\n\n${data.detail||'Server error.'}`, citations:[], chart:null }
      ]);
    } catch {
      setMessages(prev => [...prev, { role:'bot', text:'### Connection Error\n\nCannot reach the backend.', citations:[], chart:null }]);
    } finally { setLoading(false); }
  };

  return (
    <div className="chat-pane">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-state">
            <div className="welcome-hero">
              <div className="welcome-ring" />
              <div className="welcome-logo" />
            </div>

            <h1 className="welcome-heading"><span>What can I help you find?</span></h1>
            <p className="welcome-sub">
              Upload documents and start asking questions.
            </p>

            <div className="formats-grid">
              {supportedFormats.map(f => (
                <div key={f.ext} className="format-card">
                  <f.icon size={22} color={f.color} />
                  <span className="format-ext">{f.ext}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`message-row ${msg.role}`}>
              <div className={`msg-avatar ${msg.role === 'user' ? 'user-av' : 'bot-av'}`}>
                {msg.role === 'user' ? 'You' : <Sparkles size={14} />}
              </div>
              <div className="msg-body">
                <div className={`msg-label ${msg.role === 'bot' ? 'bot-label' : ''}`}>
                  {msg.role === 'user' ? 'You' : 'KnowledgeBot'}
                </div>
                <div className="msg-text">{msg.role === 'user' ? msg.text : renderMarkdown(msg.text)}</div>
                {msg.role === 'bot' && msg.chart && <InteractiveChart chartConfig={msg.chart} />}
                {msg.role === 'bot' && msg.citations?.length > 0 && (
                  <div className="citations-strip">
                    {msg.citations.map((c, ci) => (
                      <button key={ci} className="citation-pill"
                        onClick={() => setActiveCitation(activeCitation?.excerpt === c.excerpt ? null : c)}>
                        <Quote size={9} /> {c.doc_name} — {c.page_or_section}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="thinking-row">
            <div className="dot-pulse"><span /><span /><span /></div>
            <span>Searching documents and synthesizing answer…</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {activeCitation && (
        <div className="citation-drawer">
          <div className="citation-drawer-header">
            <span className="citation-drawer-source">Verified Source</span>
            <span className="citation-drawer-loc">{activeCitation.doc_name} — {activeCitation.page_or_section}</span>
          </div>
          <div className="citation-drawer-text">"{activeCitation.excerpt}"</div>
        </div>
      )}

      <div className="input-bar-wrap">
        <form onSubmit={handleSend} className="input-bar">
          <input type="text" className="chat-input"
            placeholder="Ask anything about your documents…"
            value={input} onChange={e => setInput(e.target.value)}
            disabled={loading} />
          <button type="submit" className="send-btn" disabled={loading || !input.trim()}>
            <Send size={15} />
          </button>
        </form>
      </div>
    </div>
  );
}
