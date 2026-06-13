import React, { useState, useEffect } from 'react';
import { Activity, Target, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

const OuroborosPanel = () => {
  const [logs, setLogs] = useState([]);
  const [activeTarget, setActiveTarget] = useState("Scanning...");

  useEffect(() => {
    // Polling data dari Backend API setiap 2 detik
    const fetchState = async () => {
      try {
        // Gunakan URL relatif agar berjalan di VPS maupun lokal
        const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
        const response = await fetch(`${base}/api/state`);
        const data = await response.json();
        
        if (data.logs && data.logs.length > 0) {
          setLogs(data.logs);
        }
        
        if (data.singularity && data.singularity.target) {
          setActiveTarget(data.singularity.target);
        }
      } catch (err) {
        console.error("Gagal terhubung ke Backend API:", err);
      }
    };

    fetchState();
    const interval = setInterval(fetchState, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gridColumn: 'span 2' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity className="neon-text-red" size={24} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Ouroboros Attack Engine</h3>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <StatBadge icon={<Target size={14} />} label="Active Target" value={activeTarget} />
          <StatBadge icon={<ShieldAlert size={14} />} label="WAF Status" value="Live Adapting" color="var(--neon-red)" />
        </div>
      </div>

      <div style={{ 
        background: '#050508', 
        borderRadius: '8px', 
        padding: '1rem', 
        flexGrow: 1, 
        overflowY: 'auto',
        maxHeight: '250px',
        fontFamily: 'JetBrains Mono',
        fontSize: '0.85rem',
        border: '1px solid rgba(255,0,60,0.2)',
        boxShadow: 'inset 0 0 20px rgba(0,0,0,0.8)',
        display: 'flex',
        flexDirection: 'column-reverse'
      }}>
        <div style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          <span className="blink">_</span>
        </div>
        {[...logs].reverse().map((log, index) => (
          <motion.div 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            key={index} 
            style={{ marginBottom: '0.5rem', display: 'flex', gap: '1rem' }}
          >
            <span style={{ color: 'var(--text-muted)' }}>[{log.timestamp || new Date().toLocaleTimeString()}]</span>
            <span style={{ color: getColor(log.level) }}>{log.message}</span>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

const StatBadge = ({ icon, label, value, color = 'var(--neon-cyan)' }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(0,0,0,0.4)', padding: '0.25rem 0.75rem', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.05)' }}>
    {React.cloneElement(icon, { color })}
    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{label}:</span>
    <span style={{ color, fontSize: '0.8rem', fontWeight: 600 }}>{value}</span>
  </div>
);

const getColor = (type) => {
  switch(type) {
    case 'info': return 'var(--text-main)';
    case 'attack': return '#ffa500';
    case 'warning': return '#ffdd00';
    case 'success': return 'var(--neon-cyan)';
    case 'critical': return 'var(--neon-red)';
    default: return 'var(--text-main)';
  }
};

export default OuroborosPanel;
