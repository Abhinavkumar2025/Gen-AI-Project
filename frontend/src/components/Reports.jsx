import React, { useState } from 'react';
import { Download, FileText, Filter, CheckCircle2, TrendingUp } from 'lucide-react';

export default function Reports({ applications }) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');

  // Filtered slice
  const filtered = applications.filter((app) => {
    const matchCat = selectedCategory === 'All' || app.anomaly_category === selectedCategory;
    const matchStatus = selectedStatus === 'All' || app.review_status === selectedStatus;
    return matchCat && matchStatus;
  });

  const avgIncome = filtered.length > 0 ? filtered.reduce((acc, a) => acc + (a.monthly_income || 0), 0) / filtered.length : 0;
  const avgRent = filtered.length > 0 ? filtered.reduce((acc, a) => acc + (a.monthly_rent || 0), 0) / filtered.length : 0;
  const avgError = filtered.length > 0 ? filtered.reduce((acc, a) => acc + (a.reconstruction_error || 0), 0) / filtered.length : 0;

  const handleDownloadCSV = () => {
    const url = `/api/reports/export?category=${encodeURIComponent(selectedCategory)}&status=${encodeURIComponent(selectedStatus)}`;
    window.location.href = url;
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Underwriting Reports & Compliance Export</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Generate verifiable underwriting audit records, export customized portfolio datasets in standard CSV format, and review portfolio statistics.
          </p>
        </div>
        <button
          onClick={handleDownloadCSV}
          className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 flex items-center gap-2 cursor-pointer transition-all self-start md:self-auto"
        >
          <Download className="w-4 h-4" />
          <span>Export Filtered Report (CSV)</span>
        </button>
      </div>

      {/* Filter Controls */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
          <Filter className="w-4 h-4 text-emerald-400" />
          <span>Report Scope Filters</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Anomaly Category Scope</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="All">All Anomaly Tiers</option>
              <option value="Low anomaly">Low Anomaly (Routine Baseline)</option>
              <option value="Medium anomaly">Medium Anomaly (Expedited Review)</option>
              <option value="High anomaly">High Anomaly (Priority Audit)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Review Decision Status Scope</label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="All">All Review Statuses</option>
              <option value="Pending">Pending Review</option>
              <option value="Under Review">Under Review</option>
              <option value="Verified">Verified (Approved)</option>
              <option value="Flagged for Clarification">Flagged for Clarification</option>
            </select>
          </div>
        </div>
      </div>

      {/* Filtered Portfolio Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-panel p-5 rounded-xl">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Cohort Records</span>
          <span className="text-3xl font-mono font-extrabold text-white mt-1 block">{filtered.length}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Applications included</span>
        </div>
        <div className="glass-panel p-5 rounded-xl">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Mean Monthly Income</span>
          <span className="text-3xl font-mono font-extrabold text-emerald-400 mt-1 block">${avgIncome.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Average gross earnings</span>
        </div>
        <div className="glass-panel p-5 rounded-xl">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Mean Target Rent</span>
          <span className="text-3xl font-mono font-extrabold text-white mt-1 block">${avgRent.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Average requested rent</span>
        </div>
        <div className="glass-panel p-5 rounded-xl">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Mean Reconstruction MSE</span>
          <span className="text-3xl font-mono font-extrabold text-amber-400 mt-1 block">{avgError.toFixed(4)}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Baseline residual score</span>
        </div>
      </div>

      {/* Report Data Preview Table */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <span className="text-xs font-bold text-white uppercase tracking-wider">Report Preview (First 10 Records)</span>
          <span className="text-xs text-slate-400 font-mono">Ready for CSV download</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">App ID</th>
                <th className="py-3 px-4">Applicant</th>
                <th className="py-3 px-4">Income</th>
                <th className="py-3 px-4">Target Rent</th>
                <th className="py-3 px-4">Credit Score</th>
                <th className="py-3 px-4">Reconstruction MSE</th>
                <th className="py-3 px-4">Anomaly Tier</th>
                <th className="py-3 px-4">Review Status</th>
                <th className="py-3 px-4">Submitted</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.slice(0, 10).map((a) => (
                <tr key={a.application_id} className="hover:bg-slate-800/30">
                  <td className="py-3 px-4 font-mono font-semibold text-emerald-400">#{a.application_id}</td>
                  <td className="py-3 px-4 text-white font-medium">{a.full_name}</td>
                  <td className="py-3 px-4 font-mono">${Number(a.monthly_income).toLocaleString()}</td>
                  <td className="py-3 px-4 font-mono">${Number(a.monthly_rent).toLocaleString()}</td>
                  <td className="py-3 px-4 font-mono">{a.credit_score}</td>
                  <td className="py-3 px-4 font-mono text-slate-300">{Number(a.reconstruction_error).toFixed(4)}</td>
                  <td className="py-3 px-4 font-semibold text-slate-200">{a.anomaly_category}</td>
                  <td className="py-3 px-4">{a.review_status}</td>
                  <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">{a.submission_date}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan="9" className="py-8 text-center text-slate-500 text-xs">
                    No applications match the report scope criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
