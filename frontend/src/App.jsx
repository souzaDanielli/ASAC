import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import OverviewTab from './components/OverviewTab';
import NewsTab from './components/NewsTab';
import MethodsTab from './components/MethodsTab';
import ReportsTab from './components/ReportsTab';
import { fetchHealth } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [healthData, setHealthData] = useState(null);
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const checkHealth = () => {
      fetchHealth()
        .then((data) => {
          setHealthData(data);
          setIsOnline(data.status === 'online');
        })
        .catch(() => {
          setIsOnline(false);
        });
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#F7F9F8] text-slate-800 flex flex-col font-sans">
      {/* Top Navbar */}
      <Header
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        healthStatus={healthData}
        isOnline={isOnline}
      />

      {/* Main Content Area - Mantém os componentes montados em cache para transição instantânea */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <div className={activeTab === 'overview' ? 'block' : 'hidden'}>
          <OverviewTab healthData={healthData} />
        </div>
        <div className={activeTab === 'news' ? 'block' : 'hidden'}>
          <NewsTab />
        </div>
        <div className={activeTab === 'methods' ? 'block' : 'hidden'}>
          <MethodsTab />
        </div>
        <div className={activeTab === 'reports' ? 'block' : 'hidden'}>
          <ReportsTab />
        </div>
      </main>

      {/* Minimal Footer */}
      <footer className="py-6 border-t border-slate-200/60 bg-white/50 text-center text-xs text-slate-400 mt-12">
        <p>ASAC — Análise de Sentimento do Agronegócio e Cotações CEPEA · 2026</p>
      </footer>
    </div>
  );
}
