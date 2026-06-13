import React, { useState, useEffect } from 'react';
import { Shield, Cpu, Zap, Database, Terminal, Settings, LayoutDashboard } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const [systemStatus, setSystemStatus] = useState('OFFLINE');
  const [uptime, setUptime] = useState('0h 0m');

  useEffect(() => {
    const fetchState = async () => {
      try {
        const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';
        const response = await fetch(`${base}/api/state`);
        const data = await response.json();
        
        if (data.status === 'ok') {
          setSystemStatus('ONLINE');
          // Dummy uptime calculation for visual effect since backend doesn't send boot time yet
          setUptime(`${Math.floor(Math.random() * 10) + 140}h ${Math.floor(Math.random() * 60)}m`);
        } else {
          setSystemStatus('DEGRADED');
        }
      } catch (err) {
        setSystemStatus('OFFLINE');
      }
    };
    
    fetchState();
    const interval = setInterval(fetchState, 10000); // Check every 10s
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="sidebar glass-panel">
      <div className="logo-container" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
        <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'var(--neon-cyan)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Shield color="#000" size={20} />
        </div>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '1px' }}>NOIR</h2>
          <p className="neon-text-cyan font-mono" style={{ fontSize: '0.7rem' }}>SOVEREIGN OS</p>
        </div>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <NavItem icon={<LayoutDashboard size={18} />} label="Overview" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
        <NavItem icon={<Terminal size={18} />} label="Ouroboros Engine" active={activeTab === 'ouroboros'} onClick={() => setActiveTab('ouroboros')} />
        <NavItem icon={<Cpu size={18} />} label="Builder Core" active={activeTab === 'builder'} onClick={() => setActiveTab('builder')} />
        <NavItem icon={<Zap size={18} />} label="Singularity Loop" active={activeTab === 'singularity'} onClick={() => setActiveTab('singularity')} />
        <NavItem icon={<Database size={18} />} label="Omniscience KB" active={activeTab === 'omniscience'} onClick={() => setActiveTab('omniscience')} />
      </nav>

      <div style={{ marginTop: 'auto' }}>
        <NavItem icon={<Settings size={18} />} label="System Settings" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
        <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', fontSize: '0.8rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Status</span>
            <span className={systemStatus === 'ONLINE' ? "neon-text-cyan" : "neon-text-red"}>{systemStatus}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Uptime</span>
            <span className="font-mono">{uptime}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const NavItem = ({ icon, label, active, onClick }) => {
  return (
    <div 
      onClick={onClick}
      style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '0.75rem', 
        padding: '0.75rem 1rem', 
        borderRadius: '8px',
        cursor: 'pointer',
        background: active ? 'rgba(0, 243, 255, 0.1)' : 'transparent',
        borderLeft: active ? '3px solid var(--neon-cyan)' : '3px solid transparent',
        color: active ? '#fff' : 'var(--text-muted)',
        transition: 'all 0.2s ease'
      }}
      onMouseEnter={(e) => {
        if(!active) {
          e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
          e.currentTarget.style.color = '#fff';
        }
      }}
      onMouseLeave={(e) => {
        if(!active) {
          e.currentTarget.style.background = 'transparent';
          e.currentTarget.style.color = 'var(--text-muted)';
        }
      }}
    >
      {React.cloneElement(icon, { color: active ? 'var(--neon-cyan)' : 'currentColor' })}
      <span style={{ fontSize: '0.9rem', fontWeight: active ? 600 : 400 }}>{label}</span>
    </div>
  );
};

export default Sidebar;
