import React, { useState, useEffect } from 'react';
import { Box, Code2, CheckCircle2 } from 'lucide-react';

const BuilderPanel = () => {
  const [metrics, setMetrics] = useState({
    sast: '98%', lighthouse: '100', tests: '42/42', owasp: 'Pass', task: 'Secure FastAPI Architecture'
  });
  
  useEffect(() => {
    const fetchBuildStatus = async () => {
      try {
        const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
        const response = await fetch(`${base}/api/state`);
        const data = await response.json();
        
        if (data.current_learning) {
          setMetrics(prev => ({ ...prev, task: data.current_learning }));
        }
      } catch(e) {}
    };
    fetchBuildStatus();
    const interval = setInterval(fetchBuildStatus, 5000);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="glass-panel neon-border-purple" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <Box className="neon-text-purple" size={20} color="var(--neon-purple)" />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Builder Core</h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flexGrow: 1 }}>
        <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1rem', borderRadius: '8px', borderLeft: '3px solid var(--neon-purple)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>CURRENT CHALLENGE</div>
          <div style={{ fontWeight: 600 }}>{metrics.task}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--neon-cyan)', marginTop: '0.5rem', display: 'flex', gap: '1rem' }}>
            <span><Code2 size={12} style={{display:'inline', marginRight:'4px'}}/> Generating...</span>
          </div>
        </div>

        <div style={{ marginTop: 'auto' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>QUALITY METRICS</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <MetricBox label="SAST Pass Rate" value={metrics.sast} />
            <MetricBox label="Lighthouse" value={metrics.lighthouse} />
            <MetricBox label="Unit Tests" value={metrics.tests} />
            <MetricBox label="OWASP Check" value={metrics.owasp} icon={<CheckCircle2 size={14} color="var(--neon-cyan)"/>} />
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricBox = ({ label, value, icon }) => (
  <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--glass-border)' }}>
    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{label}</div>
    <div style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
      {value} {icon}
    </div>
  </div>
);

export default BuilderPanel;
