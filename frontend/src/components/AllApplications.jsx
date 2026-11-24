import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  ExternalLink, 
  X, 
  CheckCircle2, 
  AlertTriangle, 
  AlertCircle, 
  Clock, 
  Save, 
  History, 
  User, 
  DollarSign, 
  Home, 
  FileCheck 
} from 'lucide-react';

export default function AllApplications({ 
  applications, 
  selectedAppId, 
  onSelectApp, 
  onCloseDrawer, 
  onRefresh, 
  searchQuery, 
  setSearchQuery 
}) {
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [appDetails, setAppDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Review Update state
  const [newStatus, setNewStatus] = useState('Verified');
  const [reviewerName, setReviewerName] = useState('Lead Underwriter');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [savingReview, setSavingReview] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Fetch app details when selectedAppId changes
  useEffect(() => {
    if (!selectedAppId) {
      setAppDetails(null);
      return;
    }
    const fetchDetails = async () => {
      setDetailsLoading(true);
      setSaveSuccess(false);
      try {
        const res = await fetch(`/api/applications/${selectedAppId}`);
        if (res.ok) {
          const data = await res.json();
          setAppDetails(data);
          // Default status to existing or Verified
          const latestHistory = data.review_history?.[data.review_history.length - 1];
          if (latestHistory) {
            setNewStatus(latestHistory.status);
          }
        }
      } catch (err) {
        console.error('Failed to load application details:', err);
      } finally {
        setDetailsLoading(false);
      }
    };
    fetchDetails();
  }, [selectedAppId]);

  const handleSaveReview = async (e) => {
    e.preventDefault();
    if (!reviewerNotes.trim()) {
      alert('Please enter reviewer notes explaining your decision.');
      return;
    }
    setSavingReview(true);
    try {
      const res = await fetch(`/api/applications/${selectedAppId}/review`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          reviewer_name: reviewerName.trim(),
          notes: reviewerNotes.trim(),
        }),
      });
      if (res.ok) {
        setSaveSuccess(true);
        setReviewerNotes('');
        // Refresh details
        const refreshed = await fetch(`/api/applications/${selectedAppId}`);
        if (refreshed.ok) {
          setAppDetails(await refreshed.json());
        }
        if (onRefresh) onRefresh();
      }
    } catch (err) {
      console.error('Failed to save review:', err);
    } finally {
      setSavingReview(false);
    }
  };

  // Filter applications locally
  const filteredApps = applications.filter((app) => {
    const matchesCat = categoryFilter === 'All' || app.anomaly_category === categoryFilter;
    const matchesStatus = statusFilter === 'All' || app.review_status === statusFilter;
    const matchesSearch = !searchQuery || 
      app.applicant_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.full_name?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesStatus && matchesSearch;
  });

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
    <div className="p-8 space-y-6 max-w-7xl mx-auto relative">
      {/* Filters Header Bar */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          {/* Anomaly Category filter */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs">
            {['All', 'High anomaly', 'Medium anomaly', 'Low anomaly'].map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                  categoryFilter === cat
                    ? 'bg-emerald-500/20 text-emerald-400 font-semibold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {cat === 'All' ? 'All Tiers' : cat.replace(' anomaly', '')}
              </button>
            ))}
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs">
            {['All', 'Pending', 'Under Review', 'Verified', 'Flagged for Clarification'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-2.5 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                  statusFilter === st
                    ? 'bg-blue-500/20 text-blue-400 font-semibold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {st === 'Flagged for Clarification' ? 'Clarification' : st}
              </button>
            ))}
          </div>
        </div>

        <div className="text-xs text-slate-400">
          Showing <span className="text-white font-mono font-bold">{filteredApps.length}</span> of {applications.length} applications
        </div>
      </div>

      {/* Applications Table */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4 font-semibold">App ID</th>
                <th className="py-3.5 px-4 font-semibold">Applicant</th>
                <th className="py-3.5 px-4 font-semibold">Income</th>
                <th className="py-3.5 px-4 font-semibold">Target Rent</th>
                <th className="py-3.5 px-4 font-semibold">Credit Score</th>
                <th className="py-3.5 px-4 font-semibold">Employment</th>
                <th className="py-3.5 px-4 font-semibold">Reconstruction MSE</th>
                <th className="py-3.5 px-4 font-semibold">Anomaly Tier</th>
                <th className="py-3.5 px-4 font-semibold">Review Status</th>
                <th className="py-3.5 px-4 text-right font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredApps.map((app) => (
                <tr
                  key={app.application_id}
                  onClick={() => onSelectApp(app.application_id)}
                  className={`hover:bg-slate-800/40 transition-colors cursor-pointer ${
                    selectedAppId === app.application_id ? 'bg-slate-800/60' : ''
                  }`}
                >
                  <td className="py-3.5 px-4 font-mono font-semibold text-emerald-400">#{app.application_id}</td>
                  <td className="py-3.5 px-4">
                    <div className="font-semibold text-white">{app.full_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{app.applicant_id}</div>
                  </td>
                  <td className="py-3.5 px-4 font-mono font-medium">${Number(app.monthly_income).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td className="py-3.5 px-4 font-mono font-medium">${Number(app.monthly_rent).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td className="py-3.5 px-4 font-mono font-medium">{app.credit_score}</td>
                  <td className="py-3.5 px-4">{app.employment_status}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-300">{Number(app.reconstruction_error).toFixed(4)}</td>
                  <td className="py-3.5 px-4">{getCategoryBadge(app.anomaly_category)}</td>
                  <td className="py-3.5 px-4">{getStatusBadge(app.review_status)}</td>
                  <td className="py-3.5 px-4 text-right">
                    <span className="text-slate-400 hover:text-emerald-400 inline-flex items-center gap-1 font-semibold text-[11px]">
                      Inspect
                      <ExternalLink className="w-3 h-3" />
                    </span>
                  </td>
                </tr>
              ))}
              {filteredApps.length === 0 && (
                <tr>
                  <td colSpan="10" className="py-12 text-center text-slate-500 text-xs">
                    No applications found matching the selected filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Slide-over Inspection Drawer */}
      {selectedAppId && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end">
          <div className="w-full max-w-2xl bg-[#0f172a] border-l border-slate-800 h-full overflow-y-auto p-7 space-y-6 shadow-2xl">
            {/* Drawer Header */}
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono uppercase text-emerald-400">Application #{selectedAppId}</span>
                  <span className="text-xs text-slate-500">&bull;</span>
                  <span className="text-xs text-slate-400 font-mono">{appDetails?.applicant_id}</span>
                </div>
                <h3 className="text-2xl font-extrabold text-white mt-1">{appDetails?.full_name}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{appDetails?.email} &bull; Submitted {appDetails?.created_at}</p>
              </div>
              <button
                onClick={onCloseDrawer}
                className="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {detailsLoading ? (
              <div className="py-20 text-center text-slate-400 text-sm">Loading application parameters...</div>
            ) : appDetails ? (
              <div className="space-y-6 text-xs">
                {/* Anomaly Score Banner */}
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-slate-400 uppercase tracking-wider text-[10px] font-semibold block">Autoencoder Reconstruction MSE</span>
                    <span className="text-2xl font-mono font-extrabold text-white">{Number(appDetails.reconstruction_error).toFixed(4)}</span>
                  </div>
                  <div>
                    {getCategoryBadge(appDetails.anomaly_category)}
                  </div>
                </div>

                {/* Key Financial Parameters */}
                <div>
                  <h4 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-emerald-400" />
                    <span>Financial & Tenancy Parameters</span>
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Monthly Income</span>
                      <span className="text-white font-mono font-bold text-sm">${Number(appDetails.monthly_income).toLocaleString()}</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Target Monthly Rent</span>
                      <span className="text-white font-mono font-bold text-sm">${Number(appDetails.monthly_rent).toLocaleString()}</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Rent-to-Income Ratio</span>
                      <span className={`font-mono font-bold text-sm ${
                        (appDetails.monthly_rent / appDetails.monthly_income) > 0.45 ? 'text-rose-400' : 'text-emerald-400'
                      }`}>
                        {((appDetails.monthly_rent / (appDetails.monthly_income || 1)) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Credit Score</span>
                      <span className="text-white font-mono font-bold text-sm">{appDetails.credit_score}</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Employment Duration</span>
                      <span className="text-white font-mono font-bold text-sm">{appDetails.employment_duration} yrs</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Employment Status</span>
                      <span className="text-white font-bold text-xs">{appDetails.employment_status}</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Prior Evictions</span>
                      <span className={`font-mono font-bold text-sm ${appDetails.previous_evictions > 0 ? 'text-rose-400' : 'text-white'}`}>
                        {appDetails.previous_evictions}
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Existing Loans</span>
                      <span className="text-white font-mono font-bold text-sm">{appDetails.existing_loans}</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80">
                      <span className="text-slate-400 text-[10px] block">Residential Moves (5 Yrs)</span>
                      <span className="text-white font-mono font-bold text-sm">{appDetails.previous_residences}</span>
                    </div>
                  </div>
                </div>

                {/* Feature Discrepancies */}
                {appDetails.top_contributing_features && (
                  <div>
                    <h4 className="text-sm font-bold text-white mb-2">Discrepant Feature Attribution</h4>
                    <div className="space-y-2">
                      {Object.entries(appDetails.top_contributing_features).slice(0, 4).map(([f, pct]) => (
                        <div key={f} className="space-y-1">
                          <div className="flex justify-between text-slate-300 text-[11px]">
                            <span>{f.replace(/_/g, ' ')}</span>
                            <span className="font-mono text-emerald-400">{pct}% contribution</span>
                          </div>
                          <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-400" style={{ width: `${Math.min(pct, 100)}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Historical Review Timeline */}
                <div>
                  <h4 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                    <History className="w-4 h-4 text-indigo-400" />
                    <span>Underwriter Decision Timeline</span>
                  </h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                    {appDetails.review_history?.map((h, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-white">{h.status}</span>
                          <span className="text-[10px] text-slate-500 font-mono">{h.updated_at}</span>
                        </div>
                        <p className="text-slate-400 text-[11px]">{h.reviewer_notes}</p>
                        <span className="text-[10px] text-slate-500 block">Reviewer: {h.reviewer_name}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Update Review Status Form */}
                <form onSubmit={handleSaveReview} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <h4 className="text-sm font-bold text-white flex items-center gap-2">
                    <FileCheck className="w-4 h-4 text-emerald-400" />
                    <span>Append Underwriter Audit Decision</span>
                  </h4>

                  {saveSuccess && (
                    <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px]">
                      Decision recorded successfully in SQLite audit trail!
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-400 text-[10px] font-semibold mb-1">New Review Status</label>
                      <select
                        value={newStatus}
                        onChange={(e) => setNewStatus(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                      >
                        <option value="Verified">Verified (Approved)</option>
                        <option value="Under Review">Under Review</option>
                        <option value="Flagged for Clarification">Flagged for Clarification</option>
                        <option value="Pending">Pending</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-slate-400 text-[10px] font-semibold mb-1">Reviewer Name</label>
                      <input
                        type="text"
                        value={reviewerName}
                        onChange={(e) => setReviewerName(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-slate-400 text-[10px] font-semibold mb-1">Underwriter Verification Notes</label>
                    <textarea
                      rows="3"
                      value={reviewerNotes}
                      onChange={(e) => setReviewerNotes(e.target.value)}
                      placeholder="E.g., Requested 3 months paystubs; verified continuous salary matches stated income. Approved."
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={savingReview}
                    className="w-full py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center justify-center gap-1.5 cursor-pointer transition-all"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>{savingReview ? 'Saving Audit Entry...' : 'Save Underwriting Decision'}</span>
                  </button>
                </form>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}
