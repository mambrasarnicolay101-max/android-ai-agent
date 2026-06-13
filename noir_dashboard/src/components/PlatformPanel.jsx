import React from 'react';
import { ExternalLink, Shield, Target, BookOpen, Terminal, CheckCircle2, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

const platforms = [
  {
    name: "DVWA",
    fullName: "Damn Vulnerable Web Application",
    url: "http://8.215.23.17:9090",
    status: "LIVE",
    statusColor: "var(--neon-cyan)",
    description: "Target utama Noir. Docker container aktif di VPS Alibaba.",
    attacks: ["SQL Injection", "Command Injection", "XSS", "File Inclusion", "CSRF"],
    icon: "🎯",
    badge: "ON VPS"
  },
  {
    name: "PortSwigger",
    fullName: "Web Security Academy",
    url: "https://portswigger.net/web-security",
    status: "EXTERNAL",
    statusColor: "#ffa500",
    description: "Platform riset teknik JWT, OAuth, HTTP Smuggling, GraphQL.",
    attacks: ["JWT Confusion", "OAuth Bypass", "HTTP Smuggling", "GraphQL"],
    icon: "🔬",
    badge: "FREE LABS"
  },
  {
    name: "HackTheBox",
    fullName: "HackTheBox Academy",
    url: "https://academy.hackthebox.com",
    status: "EXTERNAL",
    statusColor: "#ffa500",
    description: "Target simulasi GraphQL Batching, SSRF, dan API abuse.",
    attacks: ["GraphQL Batching", "SSRF", "API BOLA", "IDOR"],
    icon: "⚔️",
    badge: "ACADEMY"
  },
  {
    name: "OWASP WebGoat",
    fullName: "OWASP WebGoat Project",
    url: "https://owasp.org/www-project-webgoat/",
    status: "REFERENCE",
    statusColor: "var(--text-muted)",
    description: "Referensi standar OWASP Top 10 untuk SQLi, Auth Bypass.",
    attacks: ["SQLi Time-Based", "Auth Bypass", "Insecure Deserialization"],
    icon: "📚",
    badge: "OWASP"
  }
];

const PlatformPanel = () => {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: 'span 2' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
        <Target size={22} color="var(--neon-cyan)" />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Training Platforms</h3>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>
          Platform yang digunakan Noir untuk uji coba nyata
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
        {platforms.map((p, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            style={{
              background: 'rgba(0,0,0,0.3)',
              borderRadius: '10px',
              padding: '1rem',
              border: p.status === 'LIVE' ? '1px solid rgba(0,243,255,0.3)' : '1px solid rgba(255,255,255,0.05)',
              boxShadow: p.status === 'LIVE' ? '0 0 15px rgba(0,243,255,0.08)' : 'none',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {/* Live badge pulse for DVWA */}
            {p.status === 'LIVE' && (
              <div style={{
                position: 'absolute', top: '0.75rem', right: '0.75rem',
                display: 'flex', alignItems: 'center', gap: '0.3rem',
                background: 'rgba(0,243,255,0.15)', padding: '2px 8px',
                borderRadius: '20px', fontSize: '0.65rem', color: 'var(--neon-cyan)',
                border: '1px solid rgba(0,243,255,0.3)'
              }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--neon-cyan)', animation: 'pulse 1.5s infinite' }}/>
                {p.badge}
              </div>
            )}
            {p.status !== 'LIVE' && (
              <div style={{
                position: 'absolute', top: '0.75rem', right: '0.75rem',
                fontSize: '0.65rem', color: p.statusColor,
                background: 'rgba(0,0,0,0.3)', padding: '2px 8px',
                borderRadius: '20px', border: `1px solid ${p.statusColor}40`
              }}>{p.badge}</div>
            )}

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem' }}>{p.icon}</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem' }}>{p.name}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{p.fullName}</div>
              </div>
            </div>

            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem', lineHeight: 1.5 }}>
              {p.description}
            </p>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginBottom: '1rem' }}>
              {p.attacks.map((a, j) => (
                <span key={j} style={{
                  fontSize: '0.65rem', padding: '2px 8px',
                  borderRadius: '4px', background: 'rgba(255,0,60,0.1)',
                  border: '1px solid rgba(255,0,60,0.2)', color: '#ff6680'
                }}>{a}</span>
              ))}
            </div>

            <a
              href={p.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
                fontSize: '0.8rem', color: p.statusColor,
                textDecoration: 'none', fontWeight: 600,
                padding: '0.4rem 0.75rem',
                background: `${p.statusColor}15`,
                borderRadius: '6px',
                border: `1px solid ${p.statusColor}40`,
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={e => e.currentTarget.style.background = `${p.statusColor}30`}
              onMouseLeave={e => e.currentTarget.style.background = `${p.statusColor}15`}
            >
              <ExternalLink size={12} />
              {p.status === 'LIVE' ? 'Buka Platform' : 'Kunjungi'}
            </a>
          </motion.div>
        ))}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  );
};

export default PlatformPanel;
