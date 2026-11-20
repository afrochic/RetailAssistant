'use client';
import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';
import { Leaf, Plus, Menu, X, Sparkles, SlidersHorizontal, ShieldCheck, ExternalLink, RotateCcw, Copy, Check, Info, BookOpen, CircleHelp, Send, Square } from 'lucide-react';

type Preferences = { max_price?: number | null; min_price?: number | null; currency: 'KES'; category?: string | null; brand?: string | null; required_labels?: string[]; excluded_ingredients?: string[]; in_stock?: boolean };
type Reference = { id: string; name: string; description: string; price: number | null; currency: 'KES'; url: string | null; category: string[]; stock: string; source_record_id: string; reason: string };
type Response = { answer: string; references: Reference[]; mode: string; retrieval: string; preferences: Preferences; notices: string[]; retry_after: number | null; request_id: string };
type Message = { id: string; role: 'user' | 'assistant'; content: string; result?: Response; error?: boolean };
type System = { ready: boolean; reason: string | null; generation_configured: boolean; catalogue_count: number; model: string; retrieval: string; source_snapshot_date: string | null };
const KEY = 'retailassist.mvp.session.v1';
const examples = [
  { title: 'A better breakfast', text: 'Find breakfast oats under KSh 1,000.', icon: '☀' },
  { title: 'Tea, just how you like it', text: 'Show me tea options under KSh 1,500.', icon: '♧' },
  { title: 'Compare before you choose', text: 'Compare coconut oil products under KSh 2,000.', icon: '◇' },
  { title: 'Something for your routine', text: 'Find natural beauty products under KSh 2,500.', icon: '✧' },
];
function safeLink(value: string | null): string | null {
  try { const url = new URL(value || ''); return url.protocol === 'https:' && !url.username && !url.password ? url.href : null; } catch { return null; }
}
function money(value: number) { return new Intl.NumberFormat('en-KE', { maximumFractionDigits: 2 }).format(value); }

export default function Chat() {
  const [BASE, setBase] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [preferences, setPreferences] = useState<Preferences>({ currency: 'KES' });
  const [busy, setBusy] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [filters, setFilters] = useState(false);
  const [help, setHelp] = useState(false);
  const [system, setSystem] = useState<System | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [status, setStatus] = useState('');
  const abort = useRef<AbortController | null>(null);
  const epoch = useRef(0);
  const end = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const helpRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch('/api/runtime-config', { signal: controller.signal, cache: 'no-store' }).then(r => r.ok ? r.json() : Promise.reject()).then(data => setBase(data.apiBaseUrl)).catch(() => setStatus('Backend URL is not configured. Set API_BASE_URL on the frontend.'));
    return () => controller.abort();
  }, []);

  useEffect(() => {
    try {
      const raw = JSON.parse(sessionStorage.getItem(KEY) || 'null');
      if (raw && Array.isArray(raw.messages)) {
        setMessages(raw.messages.filter((m: Message) => ['user', 'assistant'].includes(m.role) && typeof m.content === 'string').slice(-24));
        if (raw.preferences?.currency === 'KES') setPreferences(raw.preferences);
      }
    } catch { /* Session storage is optional; no server persistence. */ }
    setHydrated(true);
  }, []);
  useEffect(() => {
    if (!hydrated) return;
    try { sessionStorage.setItem(KEY, JSON.stringify({ messages: messages.slice(-24), preferences })); } catch { /* Private mode remains usable. */ }
  }, [messages, preferences, hydrated]);
  useEffect(() => {
    if (!BASE) return;
    const controller = new AbortController();
    fetch(`${BASE}/api/system-info`, { signal: controller.signal, credentials: 'omit' }).then(r => r.ok ? r.json() : Promise.reject()).then(setSystem).catch(() => setSystem(null));
    return () => controller.abort();
  }, [BASE]);
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [messages, busy]);
  useEffect(() => () => { abort.current?.abort(); }, []);

  useEffect(() => {
    if (!help) return;
    const previous = document.activeElement as HTMLElement | null;
    const focusable = () => Array.from(helpRef.current?.querySelectorAll<HTMLElement>('button, a[href], input, select, textarea, [tabindex="0"]') || []);
    focusable()[0]?.focus();
    const keyboard = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { setHelp(false); return; }
      if (event.key === 'Tab') {
        const nodes = focusable(); const first = nodes[0]; const last = nodes[nodes.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    };
    document.addEventListener('keydown', keyboard);
    return () => { document.removeEventListener('keydown', keyboard); previous?.focus(); };
  }, [help]);

  function newChat() {
    epoch.current += 1; abort.current?.abort(); setMessages([]); setPreferences({ currency: 'KES' }); setInput(''); setBusy(false); setMobileMenu(false); setStatus('New anonymous conversation.'); inputRef.current?.focus();
  }
  function stop() { epoch.current += 1; abort.current?.abort(); setBusy(false); setStatus('Request stopped. You can try again.'); }
  async function send(text = input) {
    const question = text.trim(); if (!question || busy || question.length > 1500) return;
    if (!BASE) { setStatus('Backend URL is not configured. Set API_BASE_URL and restart or redeploy the frontend.'); return; }
    const token = ++epoch.current;
    const controller = new AbortController(); abort.current = controller;
    const previous = messages.filter(m => !m.error).slice(-8).map(m => ({ role: m.role, content: m.content.slice(0, 1200) }));
    setMessages(current => [...current, { id: crypto.randomUUID(), role: 'user', content: question }]); setInput(''); setBusy(true); setStatus('Checking catalogue evidence and your preferences…');
    const timeout = setTimeout(() => controller.abort(), 45000);
    try {
      const r = await fetch(`${BASE}/api/chat`, { method: 'POST', credentials: 'omit', signal: controller.signal, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: question, history: previous, preferences, k: 4 }) });
      const payload = await r.json();
      if (!r.ok) throw new Error(payload.error?.message || `The backend returned ${r.status}. Please try again.`);
      if (token !== epoch.current) return;
      const data = payload as Response;
      if (typeof data.answer !== 'string' || !Array.isArray(data.references)) throw new Error('The backend returned an unexpected response.');
      setPreferences(data.preferences); setMessages(current => [...current, { id: crypto.randomUUID(), role: 'assistant', content: data.answer, result: data }]);
      setStatus(data.mode === 'groq_grounded' ? 'Catalogue-grounded Groq response received.' : 'A transparent catalogue or safety response is shown.');
    } catch (error) {
      if (token !== epoch.current) return;
      const message = controller.signal.aborted ? 'The request timed out or was stopped. The backend may still finish a bounded request; please wait before retrying.' : error instanceof Error ? error.message : 'The connection was interrupted. Check the backend and try again.';
      setMessages(current => [...current, { id: crypto.randomUUID(), role: 'assistant', content: message, error: true }]); setStatus(message);
    } finally { clearTimeout(timeout); if (token === epoch.current) setBusy(false); }
  }
  function retry() {
    const lastUser = [...messages].reverse().find(m => m.role === 'user');
    if (lastUser) void send(lastUser.content);
  }
  async function copy(message: Message) { try { await navigator.clipboard.writeText(message.content); setCopied(message.id); setTimeout(() => setCopied(null), 1800); } catch { setStatus('Clipboard access is unavailable. Select the message text to copy it.'); } }
  const count = system?.catalogue_count || 0;
  const filterCount = Number(preferences.max_price != null) + Number(Boolean(preferences.category)) + Number(Boolean(preferences.brand));

  return <div className="app-shell">
    <a className="skip" href="#composer">Skip to chat input</a>
    {mobileMenu && <button className="sidebar-scrim" onClick={() => setMobileMenu(false)} aria-label="Close navigation" />}
    <aside className={`sidebar ${mobileMenu ? 'is-open' : ''}`}>
      <Link className="brand" href="/" aria-label="RetailAssist home"><span className="brand-symbol"><Leaf size={21} /></span><span>retail<strong>assist</strong><i>.</i></span></Link>
      <button className="new-chat" onClick={newChat}><Plus size={17} /> New conversation <span>＋</span></button>
      <div className="sidebar-section"><span className="side-caption">YOUR SPACE TO DISCOVER</span><button className="side-item selected" onClick={() => setMobileMenu(false)}><Sparkles size={17} /> Shopping companion <span className="small-ai">AI</span></button><button className="side-item" onClick={() => { setHelp(true); setMobileMenu(false); }}><BookOpen size={17} /> About the catalogue</button></div>
      <div className="sidebar-note"><span className="note-spark">✳</span><h3>A little clarity.<br />A more thoughtful choice.</h3><p>Tell us what you’re looking for. We’ll start with what’s actually in the catalogue.</p></div>
      <div className="sidebar-bottom"><div className="source-pill"><ShieldCheck size={15} /><span>Catalogue-grounded answers</span></div><button className="side-item" onClick={() => setHelp(true)}><CircleHelp size={17} /> Good to know <Info size={14} /></button><p>Independent student project.<br />No account. No checkout. Just a conversation.</p></div>
    </aside>
    <main className="main">
      <header className="topbar"><div className="topbar-title"><button className="icon-button mobile-toggle" onClick={() => setMobileMenu(true)} aria-label="Open navigation"><Menu size={20} /></button><span>RetailAssist <span className="subtle-plus">/</span> <span className="companion-label">your shopping companion</span></span></div><div className="topbar-right"><span className="private-badge"><span /> Anonymous session</span><button className="icon-button" onClick={() => setHelp(true)} aria-label="About this project"><Info size={18} /></button></div></header>
      <div className="chat-scroll">
        {!messages.length ? <section className="welcome" aria-labelledby="welcome-heading"><div className="welcome-flower"><Leaf size={36} strokeWidth={1.4} /><span>✧</span></div><div className="welcome-eyebrow">A LITTLE HELP FINDING YOUR EVERYDAY</div><h1 id="welcome-heading">What feels like<br /><span>a good find today?</span></h1><p className="welcome-intro">From your morning oats to your evening tea,<br className="desktop-break" /> let’s find something that fits your routine.</p><div className="welcome-evidence"><ShieldCheck size={14} /><span>{count ? `${count.toLocaleString()} approved catalogue records` : 'Approved Client X catalogue'} · source references included</span></div><div className="example-grid">{examples.map(example => <button key={example.title} onClick={() => void send(example.text)} disabled={busy}><span className="example-icon">{example.icon}</span><strong>{example.title}</strong><span>{example.text}</span><Sparkles size={14} className="example-spark" /></button>)}</div><p className="welcome-footnote">Not sure where to start? Tell us your product interest and budget in KES.</p></section> : <section className="messages" aria-label="Conversation">{messages.map(message => <article key={message.id} className={`message ${message.role} ${message.error ? 'error-message' : ''}`}><div className={`message-avatar ${message.role}`}>{message.role === 'assistant' ? <Leaf size={19} /> : <span>You</span>}</div><div className="message-body"><div className="message-author">{message.role === 'assistant' ? 'RetailAssist' : 'You'}{message.result && <span className="mode-tag">{message.result.mode === 'groq_grounded' ? 'Groq · grounded' : message.result.mode.startsWith('fallback') ? 'Catalogue fallback' : message.result.mode.includes('safety') || message.result.mode.includes('medical') ? 'Safety response' : 'Catalogue'}</span>}</div><div className="markdown"><ReactMarkdown skipHtml components={{ a: ({ children }) => <span>{children}</span>, img: () => null }}>{message.content}</ReactMarkdown></div>{message.result?.references.length ? <div className="references"><div className="references-heading"><BookOpen size={13} /> CHECK THE ORIGINAL LISTINGS</div>{message.result.references.map(reference => <div key={reference.id} className="reference"><span className="reference-id">CX:{reference.source_record_id}</span><div><strong>{reference.name}</strong><p>{reference.description}</p><span className="reference-price">{reference.price == null ? 'Price not confirmed' : `KES ${money(reference.price)}`}<span> · stock {reference.stock.replaceAll('_', ' ')}</span></span></div>{safeLink(reference.url) && <a href={safeLink(reference.url)!} target="_blank" rel="noopener noreferrer" aria-label={`Open retailer listing for ${reference.name}`}><ExternalLink size={15} /></a>}</div>)}</div> : null}{message.result?.notices.length ? <div className="response-notices">{message.result.notices.map(notice => <p key={notice}><Info size={12} />{notice}</p>)}{message.result.retry_after && <p><Info size={12} />Wait at least {message.result.retry_after} seconds before retrying. No automatic provider retry was made.</p>}</div> : null}<div className="message-tools">{message.error ? <button onClick={retry} disabled={busy}><RotateCcw size={13} /> Try again</button> : message.role === 'assistant' ? <button onClick={() => void copy(message)} aria-label="Copy response">{copied === message.id ? <Check size={14} /> : <Copy size={14} />}{copied === message.id ? 'Copied' : 'Copy'}</button> : null}</div></div></article>)}{busy && <div className="message assistant"><div className="message-avatar assistant"><Leaf size={19} /></div><div className="message-body"><div className="message-author">RetailAssist</div><div className="thinking" role="status"><span /><span /><span /><p>Checking catalogue evidence and your preferences…</p></div></div></div>}<div ref={end} /></section>}
      </div>
      <div className="composer-area" id="composer">{!BASE || (system && !system.ready) ? <div className="setup-notice"><Info size={14} /><span>{!BASE ? 'Backend URL is not configured. Add API_BASE_URL and restart or redeploy.' : 'The approved catalogue or public-request safeguards need setup. See QUICKSTART.md.'}</span></div> : null}<div className="composer-box">{filters && <div className="preferences"><div><label htmlFor="budget">Budget · KES</label><input id="budget" type="number" min="1" max="1000000" placeholder="Any budget" value={preferences.max_price ?? ''} onChange={event => setPreferences(p => ({ ...p, max_price: event.target.value ? Number(event.target.value) : null }))} /></div><div><label htmlFor="category">Category</label><select id="category" value={preferences.category || ''} onChange={event => setPreferences(p => ({ ...p, category: event.target.value || null }))}><option value="">Any category</option>{['Foods', 'Drinks', 'Natural Beauty', 'Supplements & Vitamins', 'Aromatherapy', 'Sports Nutrition'].map(c => <option key={c}>{c}</option>)}</select></div><button className="reset-preferences" onClick={() => setPreferences({ currency: 'KES' })}>Reset</button></div>}<form onSubmit={event => { event.preventDefault(); void send(); }}><label className="sr-only" htmlFor="message-input">Ask RetailAssist about catalogue products</label><textarea id="message-input" ref={inputRef} value={input} onChange={event => setInput(event.target.value)} placeholder="What are you looking for?" maxLength={1500} rows={2} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); void send(); } }} /><div className="composer-actions"><button className={`preference-toggle ${filterCount ? 'has-filters' : ''}`} type="button" onClick={() => setFilters(!filters)} aria-expanded={filters} aria-label="Shopping preferences"><SlidersHorizontal size={15} /> Preferences {filterCount > 0 && <span>{filterCount}</span>}</button><span className="composer-hint">{input.length > 1200 ? `${input.length}/1500` : 'A product interest. A budget. Your words.'}</span>{busy ? <button className="send-button" type="button" onClick={stop} aria-label="Stop waiting"><Square size={14} /> Stop</button> : <button className="send-button" type="submit" disabled={input.trim().length < 2}><Send size={15} /> Send</button>}</div></form></div><p className="bottom-disclaimer"><ShieldCheck size={11} /> An independent student project using a Client X snapshot. Not medical advice. Confirm prices and stock with the retailer.</p><span className="sr-only" role="status" aria-live="polite">{status}</span></div>
    </main>
    {help && <div className="modal-backdrop" onClick={() => setHelp(false)}><section ref={helpRef} className="help-modal" role="dialog" aria-modal="true" aria-labelledby="help-title" onClick={event => event.stopPropagation()}><button className="icon-button help-close" onClick={() => setHelp(false)} aria-label="Close information"><X size={19} /></button><div className="help-symbol"><Leaf size={28} /></div><span className="welcome-eyebrow">A NOTE ON THE GOOD FINDS</span><h2 id="help-title">A thoughtful companion.<br />An honest starting point.</h2><p>This independent student project uses an approved product export from the Client X workspace. It is not an official Client X service.</p><p>Prices are recorded in KES. Current availability, ingredient details and health outcomes are not assumed. Marketing descriptions are not clinical evidence.</p><p>Messages persist only in this browser tab, but submitting them sends the current request and limited conversation context to the backend and, when configured, Groq. Do not share personal medical details.</p><p>Groq composes responses using verified catalogue evidence and supported explanation sentences when available. If its quota, connection or grounding checks fail, you’ll see clearly labelled catalogue facts instead.</p><div className="help-details"><span>Session</span><strong>Tab-local persistence · provider transfer on submit</strong><span>Catalogue</span><strong>{count ? `${count.toLocaleString()} records` : 'Pending manual preparation'}</strong><span>Retrieval</span><strong>{system?.retrieval || 'Not connected'}</strong><span>Generation</span><strong>{system?.generation_configured ? system.model : 'Catalogue fallback / not connected'}</strong><span>Snapshot date</span><strong>{system?.source_snapshot_date || 'Not provided by the export'}</strong></div><p className="help-small">Avoid sharing personal medical information. Medical concerns belong with a qualified healthcare professional.</p><button className="help-done" onClick={() => setHelp(false)}>Let’s keep it thoughtful <Sparkles size={15} /></button></section></div>}
  </div>;
}
