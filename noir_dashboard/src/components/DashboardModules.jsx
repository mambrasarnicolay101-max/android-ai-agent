import React, { useState, useEffect } from 'react';
import { Network, Globe, BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';

export const SingularityFeed = () => {
  const [feeds, setFeeds] = useState([]);

  useEffect(() => {
    const fetchState = async () => {
      try {
        const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
        const response = await fetch(`${base}/api/state`);
        const data = await response.json();
        
        if (data.singularity && data.singularity.cycle > 0) {
          // Buat feed dummy berdasarkan data singularity karena backend tidak mengirim feed array
          setFeeds([{
            target: data.singularity.target || 'Unknown Target',
            status: 'Distilled',
            vuln: `Cycle ${data.singularity.cycle} | Mode: ${data.singularity.mode || 'Auto'}`
          }]);
        }
      } catch (err) {
        console.error("Gagal terhubung ke Backend API:", err);
      }
    };

    fetchState();
    const interval = setInterval(fetchState, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <Network size={20} className="neon-text-cyan" />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Singularity Loop</h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', overflowY: 'auto' }}>
        {feeds.length === 0 ? (
          <div style={{color: 'var(--text-muted)', fontSize: '0.8rem'}}>Menunggu deteksi target baru...</div>
        ) : (
          feeds.map((feed, i) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              key={i} 
              style={{ 
                background: 'rgba(0,0,0,0.3)', 
                padding: '1rem', 
                borderRadius: '8px',
                borderLeft: feed.status === 'Distilled' ? '2px solid var(--neon-cyan)' : '2px solid #ffa500'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display:'flex', alignItems:'center', gap:'4px' }}>
                  <Globe size={12}/> {feed.target}
                </span>
                <span style={{ fontSize: '0.7rem', color: feed.status === 'Distilled' ? 'var(--neon-cyan)' : '#ffa500' }}>
                  {feed.status}
                </span>
              </div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{feed.vuln}</div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export const OmniscienceStats = () => {
  const [stats, setStats] = useState({ methods: 55, blueprints: 12, patterns: 8, literature: 3 });

  useEffect(() => {
    const fetchState = async () => {
      try {
        const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
        const response = await fetch(`${base}/api/state`);
        const data = await response.json();
        
        if (data.loot_count !== undefined) {
          setStats(prev => ({ ...prev, patterns: data.loot_count }));
        }
      } catch (err) {}
    };
    fetchState();
    const interval = setInterval(fetchState, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gridColumn: 'span 2' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <BookOpen size={20} color="var(--text-main)" />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Omniscience KB Stats</h3>
      </div>

      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'space-between' }}>
         <StatCard title="Total Methods" value={stats.methods} subtitle="Operational techniques" />
         <StatCard title="Blueprints" value={stats.blueprints} subtitle="Executable payloads" />
         <StatCard title="Loot Acquired" value={stats.patterns} subtitle="Captured intelligence" />
         <StatCard title="Literature" value={stats.literature} subtitle="Academic papers" />
      </div>
    </div>
  );
};

const StatCard = ({ title, value, subtitle }) => (
  <div style={{ flex: 1, background: 'rgba(255,255,255,0.02)', padding: '1.25rem', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
    <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--neon-cyan)', marginBottom: '0.25rem' }}>{value}</div>
    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{title}</div>
    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{subtitle}</div>
  </div>
);
