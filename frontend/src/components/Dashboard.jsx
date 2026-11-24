import React from 'react';
import { 
  Users, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  ArrowUpRight, 
  ShieldAlert, 
  TrendingUp, 
  ExternalLink 
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid 
} from 'recharts';

export default function Dashboard({ summary, recentApps, onSelectApp, setActiveTab }) {
  const totalApps = summary?.total_applications || 0;
  const normalApps = summary?.normal_applications || 0;
  const flaggedApps = summary?.flagged_applications || 0;
  const pendingReviews = summary?.pending_reviews || 0;

  const normalPct = totalApps > 0 ? ((normalApps / totalApps) * 100).toFixed(1) : '0';
  const flaggedPct = totalApps > 0 ? ((flaggedApps / totalApps) * 100).toFixed(1) : '0';

  // Pie chart data
  const pieData = [
    { name: 'Low Anomaly', value: summary?.category_distribution?.['Low anomaly'] || 0, color: '#10b981' },
    { name: 'Medium Anomaly', value: summary?.category_distribution?.['Medium anomaly'] || 0, color: '#f59e0b' },
    { name: 'High Anomaly', value: summary?.category_distribution?.['High anomaly'] || 0, color: '#ef4444' },
  ].filter(d => d.value > 0);

  // Status breakdown data
  const statusData = Object.entries(summary?.status_distribution || {}).map(([name, count]) => ({
    name,
    count,
  }));

  const getCategoryBadge = (category) => {
    switch (category) {
      case 'High anomaly':
        return <span className="badge-high px-2 py-0.5 rounded-full text-xs font-semibold">High Anomaly</span>;
      case 'Medium anomaly':
        return <span className="badge-med px-2 py-0.5 rounded-full text-xs font-semibold">Medium Anomaly</span>;
      default:
        return <span className="badge-low px-2 py-0.5 rounded-full text-xs font-semibold">Low Anomaly</span>;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Verified':
        return <span className="text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded text-xs">Verified</span>;
      case 'Under Review':
        return <span className="text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded text-xs">Under Review</span>;
      case 'Flagged for Clarification':
        return <span className="text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded text-xs">Clarification</span>;
      default:
        return <span className="text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded text-xs">Pending</span>;
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-navy-900 to-slate-900 border border-slate-800 p-7 shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-3">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Underwriting Queue Active
            </div>
            <h2 className="text-2xl font-extrabold text-white tracking-tight">
              RentGuard AI Underwriting Command Center
            </h2>
            <p className="text-sm text-slate-400 max-w-2xl mt-1">
              Unsupervised deep learning anomaly detection for residential tenancy portfolios.
              Statistical reconstruction residuals spotlight deviations for expedited verification.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setActiveTab('submit')}
              className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold text-xs transition-all shadow-lg shadow-emerald-500/20 flex items-center gap-2 cursor-pointer"
            >
              <span>Submit Application</span>
              <ArrowUpRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => setActiveTab('applications')}
              className="px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-white font-medium text-xs border border-slate-700 transition-all cursor-pointer"
            >
              Review Registry
            </button>
          </div>
        </div>
        <div className="absolute right-0 top-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Applications */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Ingested</span>
            <div className="p-2 rounded-xl bg-slate-800/80 text-slate-300">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-extrabold text-white">{totalApps.toLocaleString()}</span>
          </div>
          <div className="mt-2 flex items-center text-xs text-slate-400">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400 mr-1" />
            <span>Active database records</span>
          </div>
        </div>

        {/* Normal Baseline */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Normal Baseline</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-emerald-400">{normalApps.toLocaleString()}</span>
            <span className="text-xs font-semibold text-emerald-500/90">{normalPct}%</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Adheres to modeled baseline
          </div>
        </div>

        {/* Flagged for Review */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Flagged Outliers</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-amber-400">{flaggedApps.toLocaleString()}</span>
            <span className="text-xs font-semibold text-amber-500/90">{flaggedPct}%</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Elevated reconstruction MSE
          </div>
        </div>

        {/* Pending Human Review */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Pending Decisions</span>
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-3xl font-extrabold text-rose-400">{pendingReviews.toLocaleString()}</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Priority manual review queue
          </div>
        </div>
      </div>

      {/* Analytics Visualizations Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Anomaly Distribution Donut */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Anomaly Category Distribution</h3>
              <p className="text-xs text-slate-400 mt-0.5">Categorized by validation-calibrated P95 & P99 cutoffs</p>
            </div>
            <span className="text-xs text-slate-400 bg-slate-800/60 px-2.5 py-1 rounded-lg">Autoencoder MSE</span>
          </div>

          <div className="h-64 flex items-center justify-center">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={95}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(0,0,0,0.4)" strokeWidth={2} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '0.75rem' }} 
                    itemStyle={{ color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-500 text-xs">No application data available yet</div>
            )}
          </div>

          <div className="flex justify-center gap-6 pt-2 border-t border-slate-800/60 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
              <span className="text-slate-300">Low Anomaly</span>
              <span className="text-slate-500 font-mono">({summary?.category_distribution?.['Low anomaly'] || 0})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500"></span>
              <span className="text-slate-300">Medium</span>
              <span className="text-slate-500 font-mono">({summary?.category_distribution?.['Medium anomaly'] || 0})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-rose-500"></span>
              <span className="text-slate-300">High</span>
              <span className="text-slate-500 font-mono">({summary?.category_distribution?.['High anomaly'] || 0})</span>
            </div>
          </div>
        </div>

        {/* Review Status Breakdown Bar Chart */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Underwriting Audit Pipeline</h3>
              <p className="text-xs text-slate-400 mt-0.5">Applications segmented by underwriter workflow status</p>
            </div>
            <span className="text-xs text-slate-400 bg-slate-800/60 px-2.5 py-1 rounded-lg">Workflow</span>
          </div>

          <div className="h-64 flex items-center justify-center">
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusData} margin={{ top: 15, right: 10, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                  <Tooltip 
                    cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '0.75rem' }} 
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]}>
                    {statusData.map((entry, index) => {
                      const color = entry.name === 'Verified' ? '#10b981' :
                                    entry.name === 'Under Review' ? '#3b82f6' :
                                    entry.name === 'Pending' ? '#f43f5e' : '#f59e0b';
                      return <Cell key={`bar-${index}`} fill={color} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-500 text-xs">No status logs available yet</div>
            )}
          </div>

          <div className="text-center pt-2 border-t border-slate-800/60 text-xs text-slate-400">
            Click any application in the table below to update review status and append underwriter notes.
          </div>
        </div>
      </div>

      {/* Recent Applications Feed */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Recent Underwriting Intake Stream</h3>
            <p className="text-xs text-slate-400 mt-0.5">Most recently scored applications from the SQLite registry</p>
          </div>
          <button
            onClick={() => setActiveTab('applications')}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 cursor-pointer"
          >
            <span>View All Applications</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">App ID</th>
                <th className="py-3 px-4">Applicant</th>
                <th className="py-3 px-4">Income</th>
                <th className="py-3 px-4">Rent</th>
                <th className="py-3 px-4">Credit</th>
                <th className="py-3 px-4">Reconstruction MSE</th>
                <th className="py-3 px-4">Anomaly Tier</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {recentApps.slice(0, 7).map((app) => (
                <tr 
                  key={app.application_id}
                  onClick={() => onSelectApp(app.application_id)}
                  className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                >
                  <td className="py-3 px-4 font-mono text-emerald-400 font-semibold">#{app.application_id}</td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-white">{app.full_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{app.applicant_id}</div>
                  </td>
                  <td className="py-3 px-4 font-mono font-medium">${Number(app.monthly_income).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td className="py-3 px-4 font-mono font-medium">${Number(app.monthly_rent).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td className="py-3 px-4 font-mono font-medium">{app.credit_score}</td>
                  <td className="py-3 px-4 font-mono text-slate-300">{Number(app.reconstruction_error).toFixed(4)}</td>
                  <td className="py-3 px-4">{getCategoryBadge(app.anomaly_category)}</td>
                  <td className="py-3 px-4">{getStatusBadge(app.review_status)}</td>
                  <td className="py-3 px-4 text-right">
                    <span className="text-slate-400 hover:text-emerald-400 inline-flex items-center gap-1 font-semibold text-[11px]">
                      Inspect
                      <ExternalLink className="w-3 h-3" />
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
