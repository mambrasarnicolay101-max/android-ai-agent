import React from 'react'
import Sidebar from './components/Sidebar'
import OuroborosPanel from './components/OuroborosPanel'
import BuilderPanel from './components/BuilderPanel'
import { SingularityFeed, OmniscienceStats } from './components/DashboardModules'
import PlatformPanel from './components/PlatformPanel'
import ChatConsole from './components/ChatConsole'

function App() {
  const [activeTab, setActiveTab] = React.useState('dashboard');

  // Render konten berdasarkan tab aktif
  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return (
          <>
            <OuroborosPanel />
            <BuilderPanel />
            <SingularityFeed />
            <OmniscienceStats />
          </>
        );
      case 'ouroboros':
        return (
          <>
            <OuroborosPanel />
            <PlatformPanel />
          </>
        );
      case 'builder':
        return <BuilderPanel />;
      case 'singularity':
        return <SingularityFeed />;
      case 'omniscience':
        return <OmniscienceStats />;
      case 'settings':
        return <div style={{gridColumn: 'span 2', padding: '2rem', background: 'rgba(0,0,0,0.4)', borderRadius: '12px'}}>
          <h2 style={{color: 'var(--neon-cyan)', marginBottom: '1rem'}}>System Settings</h2>
          <p>Konfigurasi parameter core Noir Sovereign OS.</p>
        </div>;
      default:
        return <OuroborosPanel />;
    }
  };

  return (
    <div className="dashboard-layout">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="main-content">
        {renderContent()}
      </div>
      <div className="chat-sidebar">
        <ChatConsole />
      </div>
    </div>
  )
}

export default App
