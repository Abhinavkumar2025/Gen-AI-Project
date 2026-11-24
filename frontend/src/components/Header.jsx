import React from 'react';
import { Bell, RefreshCw, UserCheck, Search } from 'lucide-react';

export default function Header({ title, subtitle, onRefresh, isRefreshing, searchQuery, setSearchQuery }) {
  return (
    <header className="h-18 px-8 border-b border-slate-800/80 bg-[#0b0f19]/80 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-white">{title}</h1>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {setSearchQuery && (
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by ID or Name..."
              value={searchQuery || ''}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 w-56 transition-all"
            />
          </div>
        )}

        {onRefresh && (
          <button
            onClick={onRefresh}
            title="Refresh Data"
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        )}

        <div className="h-4 w-px bg-slate-800" />

        <div className="flex items-center gap-2.5 pl-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-xs font-bold text-white shadow-md">
            LU
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-slate-200">Lead Underwriter</p>
            <p className="text-[10px] text-emerald-400 font-mono">Licensed Staff</p>
          </div>
        </div>
      </div>
    </header>
  );
}
