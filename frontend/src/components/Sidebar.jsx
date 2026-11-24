import React from 'react';
import { 
  LayoutDashboard, 
  FilePlus, 
  Users, 
  LineChart, 
  FileText, 
  Settings, 
  ShieldCheck, 
  Cpu, 
  Zap, 
  Database 
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, systemStatus }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'submit', label: 'Submit Application', icon: FilePlus },
    { id: 'applications', label: 'All Applications', icon: Users },
    { id: 'analytics', label: 'Anomaly Analytics', icon: LineChart },
    { id: 'reports', label: 'Reports & Export', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#080c16] border-r border-slate-800/80 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      {/* Brand Header */}
      <div>
        <div className="p-5 border-b border-slate-800/60 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight text-white">RentGuard</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">AI</span>
            </div>
            <p className="text-xs text-slate-400 font-medium">Underwriting Intelligence</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ${
                  isActive
                    ? 'bg-gradient-to-r from-emerald-500/15 to-teal-500/5 text-emerald-400 border border-emerald-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
                {isActive && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-glow-emerald"></span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Status Indicators & Compliance Card */}
      <div className="p-4 space-y-3 border-t border-slate-800/60 bg-slate-900/30">
        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-teal-400" />
              <span>Autoencoder</span>
            </span>
            <span className="text-emerald-400 font-semibold text-[11px] flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Active
            </span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Groq LPU</span>
            </span>
            <span className="text-amber-400 font-semibold text-[11px]">
              {systemStatus?.groq_configured ? 'Connected' : 'Fallback'}
            </span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-indigo-400" />
              <span>SQLite</span>
            </span>
            <span className="text-slate-300 font-semibold text-[11px]">Synced</span>
          </div>
        </div>

        <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-900/30 text-[11px] text-emerald-400/90 leading-tight">
          <p className="font-semibold mb-0.5">⚖️ Non-Adverse Directives</p>
          <p className="text-slate-400 text-[10px]">Statistical flags prioritize review. Automated denials prohibited.</p>
        </div>
      </div>
    </aside>
  );
}
