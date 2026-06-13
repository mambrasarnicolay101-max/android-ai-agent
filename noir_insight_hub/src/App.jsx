import { useState } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('Overview')

  const menuItems = ['Overview', 'Analytics', 'System Health', 'Settings']

  return (
    <div className="dashboard-container">
      {/* Sidebar Component */}
      <aside className="sidebar">
        <div className="logo">Noir Insight Hub</div>
        <ul className="nav-menu">
          {menuItems.map(item => (
            <li 
              key={item} 
              className={activeTab === item ? 'active' : ''}
              onClick={() => setActiveTab(item)}
            >
              {item}
            </li>
          ))}
        </ul>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header>
          <h1>{activeTab}</h1>
          <div className="user-profile">
            <span className="user-name">Admin (Agentic)</span>
            <div className="avatar"></div>
          </div>
        </header>

        {/* Dynamic Panel Rendering */}
        <div className="panel-content">
          {activeTab === 'Overview' && (
            <div className="dashboard-grid">
              <div className="glass-card">
                <p className="card-title">Active AI Nodes</p>
                <h2 className="card-value">1,024</h2>
              </div>
              <div className="glass-card">
                <p className="card-title">Token Output (Today)</p>
                <h2 className="card-value">4.5M</h2>
              </div>
              <div className="glass-card">
                <p className="card-title">System Load</p>
                <h2 className="card-value" style={{ color: 'var(--accent)' }}>24%</h2>
              </div>
              <div className="glass-card chart-container">
                <p className="card-title">Node Network Activity (Live)</p>
                <div className="chart-mockup"></div>
              </div>
            </div>
          )}

          {activeTab === 'Analytics' && (
            <div className="dashboard-grid">
              <div className="glass-card chart-container">
                <p className="card-title">Threat Detection History</p>
                <div className="chart-mockup" style={{ borderBottomColor: 'var(--secondary)', background: 'linear-gradient(to top, rgba(255, 51, 102, 0.2), transparent)' }}></div>
              </div>
            </div>
          )}

          {activeTab === 'System Health' && (
            <div className="dashboard-grid">
              <div className="glass-card">
                <p className="card-title">API Latency</p>
                <h2 className="card-value">45ms</h2>
              </div>
              <div className="glass-card">
                <p className="card-title">Database Uptime</p>
                <h2 className="card-value">99.9%</h2>
              </div>
            </div>
          )}

          {activeTab === 'Settings' && (
            <div className="glass-card">
              <p className="card-title">Agent Configuration</p>
              <p style={{ color: 'var(--text-muted)' }}>Auto-deployment enabled. Edge routing active.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
