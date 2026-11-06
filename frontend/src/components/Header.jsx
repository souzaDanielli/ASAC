import React from 'react';
import { Activity, Database, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Header({ activeTab, onSelectTab, healthStatus, isOnline }) {
  const tabs = [
    { id: 'overview', label: 'Visão geral' },
    { id: 'news', label: 'Notícias' },
    { id: 'methods', label: 'Metodologia e métricas' },
    { id: 'reports', label: 'Relatório' },
  ];

  return (
    <header className="bg-white border-b border-slate-200/80 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Navigation */}
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-2xl tracking-tight text-[#1a3c34]">
                ASAC
              </span>
            </div>

            <nav className="flex space-x-1 sm:space-x-4">
              {tabs.map((tab) => {
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => onSelectTab(tab.id)}
                    className={`relative py-5 px-3 text-sm font-medium transition-colors ${
                      isActive
                        ? 'text-[#1a3c34] font-semibold'
                        : 'text-slate-500 hover:text-slate-900'
                    }`}
                  >
                    {tab.label}
                    {isActive && (
                      <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#1a3c34] rounded-t-full" />
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right Status Badge */}
          <div className="flex items-center">
            {isOnline ? (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-[#EBF7F2] text-[#1E7453] border border-[#C5E9D9]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#1E7453] animate-pulse" />
                <span>API online · SQLite conectado</span>
              </div>
            ) : (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                <span>API desconectada (modo de espera)</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

