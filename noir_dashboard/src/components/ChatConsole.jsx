import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';

export default function ChatConsole() {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'system', text: 'NOIR Console aktif. Ketik perintah — gunakan "di pc, ..." untuk menjalankan di laptop.' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Cleanup abort controller on unmount
  useEffect(() => () => controllerRef.current?.abort(), []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userText = inputValue.trim();
    setMessages(prev => [...prev, { id: Date.now(), sender: 'user', text: userText }]);
    setInputValue('');
    setIsLoading(true);

    // Abort controller untuk timeout 90 detik
    controllerRef.current = new AbortController();
    const timeoutId = setTimeout(() => controllerRef.current.abort(), 90000);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026'
        },
        body: JSON.stringify({ message: userText, device_id: 'LAPTOP_MASTER' }),
        signal: controllerRef.current.signal
      });

      clearTimeout(timeoutId);
      const data = await res.json();

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'system',
        text: data.reply || data.error || data.detail || 'Respons kosong dari server.'
      }]);
    } catch (err) {
      clearTimeout(timeoutId);
      const isTimeout = err.name === 'AbortError';
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'error',
        text: isTimeout
          ? '[TIMEOUT] Server tidak merespons dalam 90 detik. Coba lagi.'
          : `[ERROR] ${err.message}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) handleSend(e);
  };

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', height: '100%', width: '100%',
      background: '#0a0b0f', fontFamily: "'JetBrains Mono', 'Consolas', monospace",
      fontSize: '0.82rem', border: '1px solid rgba(0,243,255,0.15)',
      borderRadius: '12px', overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.6rem',
        padding: '0.75rem 1rem', background: '#050508',
        borderBottom: '1px solid rgba(255,255,255,0.08)'
      }}>
        <div style={{
          width: '8px', height: '8px', borderRadius: '50%',
          background: isLoading ? '#ffa500' : '#00f3ff',
          boxShadow: isLoading ? '0 0 8px #ffa500' : '0 0 8px #00f3ff',
          animation: 'pulse 1.5s infinite'
        }} />
        <span style={{ color: '#a0aec0', fontWeight: 600, letterSpacing: '1px', fontSize: '0.78rem' }}>
          NOIR SYSTEM CONSOLE
        </span>
        {isLoading && (
          <span style={{ marginLeft: 'auto', color: '#ffa500', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} />
            Memproses...
          </span>
        )}
      </div>

      {/* Area Pesan */}
      <div style={{
        flex: 1, overflowY: 'auto', padding: '1rem',
        display: 'flex', flexDirection: 'column', gap: '0.75rem'
      }}>
        {messages.map((msg) => (
          <div key={msg.id} style={{
            display: 'flex', alignItems: 'flex-start', gap: '0.6rem',
            flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
            maxWidth: '88%',
            alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start'
          }}>
            {/* Avatar */}
            <div style={{
              padding: '5px', borderRadius: '6px', flexShrink: 0,
              background: msg.sender === 'user' ? 'rgba(99,102,241,0.3)' :
                          msg.sender === 'error' ? 'rgba(255,0,60,0.3)' : 'rgba(0,243,255,0.1)',
              color: msg.sender === 'user' ? '#818cf8' :
                     msg.sender === 'error' ? '#ff6680' : '#00f3ff'
            }}>
              {msg.sender === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>

            {/* Bubble */}
            <div style={{
              padding: '0.6rem 0.9rem', borderRadius: '8px',
              lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-word',
              background: msg.sender === 'user' ? 'rgba(99,102,241,0.12)' :
                          msg.sender === 'error' ? 'rgba(255,0,60,0.08)' : 'rgba(0,0,0,0.4)',
              border: msg.sender === 'user' ? '1px solid rgba(99,102,241,0.3)' :
                      msg.sender === 'error' ? '1px solid rgba(255,0,60,0.3)' : '1px solid rgba(255,255,255,0.06)',
              color: msg.sender === 'user' ? '#c7d2fe' :
                     msg.sender === 'error' ? '#ff9999' : '#cbd5e0'
            }}>
              {msg.text}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ padding: '5px', borderRadius: '6px', background: 'rgba(0,243,255,0.1)', color: '#00f3ff' }}>
              <Bot size={14} />
            </div>
            <div style={{
              padding: '0.6rem 1rem', borderRadius: '8px',
              background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.06)',
              color: '#00f3ff', display: 'flex', gap: '4px', alignItems: 'center'
            }}>
              <span style={{ animation: 'blink 1s infinite' }}>▌</span>
              <span style={{ color: 'rgba(0,243,255,0.6)', fontSize: '0.75rem' }}>Memproses perintah...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} style={{
        padding: '0.75rem', background: '#050508',
        borderTop: '1px solid rgba(255,255,255,0.08)',
        display: 'flex', alignItems: 'center', gap: '0.5rem'
      }}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder={isLoading ? 'Menunggu respons...' : 'di pc, jalankan perintah: whoami'}
          style={{
            flex: 1, background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px', padding: '0.6rem 0.9rem',
            color: '#e2e8f0', outline: 'none', fontSize: '0.82rem',
            fontFamily: "'JetBrains Mono', monospace",
            opacity: isLoading ? 0.6 : 1,
            transition: 'border-color 0.2s'
          }}
          onFocus={e => e.target.style.borderColor = 'rgba(0,243,255,0.4)'}
          onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
        />
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          style={{
            padding: '0.6rem 0.9rem', borderRadius: '8px',
            background: isLoading ? 'rgba(99,102,241,0.3)' : 'rgba(99,102,241,0.7)',
            border: 'none', color: '#fff', cursor: isLoading ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'background 0.2s'
          }}
        >
          {isLoading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={16} />}
        </button>
      </form>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
      `}</style>
    </div>
  );
}
