import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  AlertCircle, 
  CheckCircle2, 
  AlertTriangle, 
  FileText, 
  CheckSquare, 
  TrendingUp, 
  RotateCcw,
  Bot
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export default function SubmitApplication({ onSubmitted, setActiveTab }) {
  const [formData, setFormData] = useState({
    applicant_id: `APP-${Math.floor(10000 + Math.random() * 90000)}`,
    full_name: 'Marcus Vance',
    email: 'marcus.v@example.com',
    monthly_income: 6200,
    monthly_rent: 1650,
    credit_score: 725,
    employment_duration: 4.5,
    previous_evictions: 0,
    existing_loans: 1,
    employment_status: 'Full-time',
    rental_history_duration: 5.0,
    previous_residences: 2,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // Preset loading
  const loadPreset = (type) => {
    const randId = `APP-${Math.floor(10000 + Math.random() * 90000)}`;
    if (type === 'normal') {
      setFormData({
        applicant_id: randId,
        full_name: 'David Miller',
        email: 'david.m@example.com',
        monthly_income: 6500,
        monthly_rent: 1750,
        credit_score: 730,
        employment_duration: 5.2,
        previous_evictions: 0,
        existing_loans: 1,
        employment_status: 'Full-time',
        rental_history_duration: 6.0,
        previous_residences: 2,
      });
    } else if (type === 'rent_inversion') {
      setFormData({
        applicant_id: randId,
        full_name: 'Sarah Jenkins',
        email: 's.jenkins@example.com',
        monthly_income: 1900,
        monthly_rent: 3600,
        credit_score: 590,
        employment_duration: 1.0,
        previous_evictions: 0,
        existing_loans: 4,
        employment_status: 'Part-time',
        rental_history_duration: 2.5,
        previous_residences: 3,
      });
    } else if (type === 'credit_discordance') {
      setFormData({
        applicant_id: randId,
        full_name: 'Elena Rostova',
        email: 'elena.r@example.com',
        monthly_income: 7800,
        monthly_rent: 2200,
        credit_score: 825,
        employment_duration: 4.0,
        previous_evictions: 3,
        existing_loans: 8,
        employment_status: 'Full-time',
        rental_history_duration: 5.0,
        previous_residences: 4,
      });
    } else if (type === 'unemployed_luxury') {
      setFormData({
        applicant_id: randId,
        full_name: 'Julian Hayes',
        email: 'j.hayes@example.com',
        monthly_income: 500,
        monthly_rent: 4200,
        credit_score: 480,
        employment_duration: 0.0,
        previous_evictions: 1,
        existing_loans: 2,
        employment_status: 'Unemployed',
        rental_history_duration: 1.0,
        previous_residences: 3,
      });
    } else if (type === 'tenure_mismatch') {
      setFormData({
        applicant_id: randId,
        full_name: 'Robert Chen',
        email: 'r.chen@example.com',
        monthly_income: 9200,
        monthly_rent: 2400,
        credit_score: 680,
        employment_duration: 28.0,
        previous_evictions: 0,
        existing_loans: 1,
        employment_status: 'Full-time',
        rental_history_duration: 0.5,
        previous_residences: 8,
      });
    }
    setResult(null);
    setErrorMsg(null);
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    try {
      const res = await fetch('/api/applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Inference failed');
      }

      const data = await res.json();
      setResult(data);
      if (onSubmitted) onSubmitted();
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Convert feature contributions to bar chart data
  const featureChartData = result?.top_contributing_features
    ? Object.entries(result.top_contributing_features).map(([name, pct]) => ({
        name: name.replace(/_/g, ' '),
        percentage: Number(pct),
      })).slice(0, 6)
    : [];

  return (
    <div className="p-8 space-y-8 max-w-6xl mx-auto">
      {/* Presets Bar */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">1-Click Test Scenarios</span>
          </div>
          <span className="text-[11px] text-slate-400">Pre-populate real-world or anomalous test profiles</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
          <button
            type="button"
            onClick={() => loadPreset('normal')}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition-all text-left flex items-center justify-between cursor-pointer"
          >
            <span>🟢 Normal Baseline</span>
          </button>
          <button
            type="button"
            onClick={() => loadPreset('rent_inversion')}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 transition-all text-left flex items-center justify-between cursor-pointer"
          >
            <span>🔴 Rent Inversion</span>
          </button>
          <button
            type="button"
            onClick={() => loadPreset('credit_discordance')}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 transition-all text-left flex items-center justify-between cursor-pointer"
          >
            <span>🟠 Credit Mismatch</span>
          </button>
          <button
            type="button"
            onClick={() => loadPreset('unemployed_luxury')}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 transition-all text-left flex items-center justify-between cursor-pointer"
          >
            <span>🔴 Unemployed Luxury</span>
          </button>
          <button
            type="button"
            onClick={() => loadPreset('tenure_mismatch')}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 transition-all text-left flex items-center justify-between cursor-pointer"
          >
            <span>🟠 Tenure Mismatch</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Submission Form */}
      <form onSubmit={handleSubmit} className="glass-panel p-7 rounded-2xl border border-slate-800 space-y-7">
        <div>
          <h3 className="text-base font-bold text-white tracking-tight">1. Applicant Identification</h3>
          <p className="text-xs text-slate-400 mt-0.5">Primary tenant demographics and identifier</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Applicant ID</label>
              <input
                type="text"
                name="applicant_id"
                required
                value={formData.applicant_id}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Legal Name</label>
              <input
                type="text"
                name="full_name"
                required
                value={formData.full_name}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Contact</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-base font-bold text-white tracking-tight">2. Financial & Lease Parameters</h3>
          <p className="text-xs text-slate-400 mt-0.5">Income, target monthly rent, and credit bureau rating</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Monthly Income ($)</label>
              <input
                type="number"
                name="monthly_income"
                min="0"
                step="any"
                required
                value={formData.monthly_income}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Target Monthly Rent ($)</label>
              <input
                type="number"
                name="monthly_rent"
                min="0"
                step="any"
                required
                value={formData.monthly_rent}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-xs font-semibold text-slate-300">Credit Score (300 - 850)</label>
                <span className="text-xs font-mono font-bold text-emerald-400">{formData.credit_score}</span>
              </div>
              <input
                type="range"
                name="credit_score"
                min="300"
                max="850"
                value={formData.credit_score}
                onChange={handleChange}
                className="w-full accent-emerald-500 cursor-pointer"
              />
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-base font-bold text-white tracking-tight">3. Employment & Credit Background</h3>
          <p className="text-xs text-slate-400 mt-0.5">Work classification, continuous job duration, and active loan counts</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Employment Status</label>
              <select
                name="employment_status"
                value={formData.employment_status}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="Full-time">Full-time</option>
                <option value="Self-employed">Self-employed</option>
                <option value="Part-time">Part-time</option>
                <option value="Retired">Retired</option>
                <option value="Unemployed">Unemployed</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Employment Duration (Years)</label>
              <input
                type="number"
                name="employment_duration"
                min="0"
                step="any"
                value={formData.employment_duration}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Active Loans Count</label>
              <input
                type="number"
                name="existing_loans"
                min="0"
                max="25"
                value={formData.existing_loans}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-base font-bold text-white tracking-tight">4. Residential & Rental History</h3>
          <p className="text-xs text-slate-400 mt-0.5">Court evictions, verifiable rental history, and residential turnover</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Previous Evictions</label>
              <input
                type="number"
                name="previous_evictions"
                min="0"
                max="10"
                value={formData.previous_evictions}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Rental History Duration (Years)</label>
              <input
                type="number"
                name="rental_history_duration"
                min="0"
                step="any"
                value={formData.rental_history_duration}
                onChange={handleChange}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-xs font-semibold text-slate-300">Previous Residences (Past 5 Yrs)</label>
                <span className="text-xs font-mono font-bold text-emerald-400">{formData.previous_residences}</span>
              </div>
              <input
                type="range"
                name="previous_residences"
                min="1"
                max="12"
                value={formData.previous_residences}
                onChange={handleChange}
                className="w-full accent-emerald-500 cursor-pointer"
              />
            </div>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 flex items-center gap-2 cursor-pointer transition-all"
          >
            {loading ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin" />
                <span>Evaluating via Deep Autoencoder...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Evaluate & Ingest Application</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Real-Time Underwriting Assessment Result */}
      {result && (
        <div className="glass-panel p-7 rounded-2xl border border-slate-800 space-y-7 animate-in fade-in duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono uppercase text-slate-400">Application #{result.application_id}</span>
                <span className="text-xs text-slate-500">&bull;</span>
                <span className="text-xs text-slate-300 font-semibold">{result.applicant_id}</span>
              </div>
              <h3 className="text-xl font-extrabold text-white mt-1">Underwriting Assessment Results</h3>
            </div>
            <div className="flex items-center gap-3">
              {result.anomaly_category === 'High anomaly' && (
                <div className="px-3 py-1.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-400 font-bold text-sm flex items-center gap-1.5 shadow-glow-rose">
                  <AlertCircle className="w-4 h-4" />
                  <span>High Anomaly</span>
                </div>
              )}
              {result.anomaly_category === 'Medium anomaly' && (
                <div className="px-3 py-1.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-400 font-bold text-sm flex items-center gap-1.5 shadow-glow-amber">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Medium Anomaly</span>
                </div>
              )}
              {result.anomaly_category === 'Low anomaly' && (
                <div className="px-3 py-1.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 font-bold text-sm flex items-center gap-1.5 shadow-glow-emerald">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Low Anomaly</span>
                </div>
              )}
            </div>
          </div>

          {/* Metric Cards Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Reconstruction Error (MSE)</span>
              <div className="text-3xl font-mono font-extrabold text-white mt-1">{result.anomaly_score.toFixed(4)}</div>
              <span className="text-[11px] text-slate-500 mt-1 block">Calibrated Cutoff: P95: 0.0525</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Operational Tier</span>
              <div className={`text-xl font-bold mt-1.5 ${
                result.anomaly_category === 'High anomaly' ? 'text-rose-400' :
                result.anomaly_category === 'Medium anomaly' ? 'text-amber-400' : 'text-emerald-400'
              }`}>
                {result.anomaly_category}
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block">Validation Benchmark</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Recommendation</span>
              <div className="text-sm font-semibold text-slate-200 mt-2 line-clamp-2">
                {result.anomaly_category === 'High anomaly' ? 'Priority Underwriter Audit' :
                 result.anomaly_category === 'Medium anomaly' ? 'Expedited Document Check' : 'Standard Routine Processing'}
              </div>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800 text-xs text-slate-300">
            <strong>📋 Underwriting Directive: </strong>
            <span>{result.review_recommendation}</span>
          </div>

          {/* Feature Discrepancies & AI Explainer */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Feature attribution chart */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div>
                <h4 className="text-sm font-bold text-white">Feature Reconstruction Discrepancies</h4>
                <p className="text-xs text-slate-400 mt-0.5">Relative percentage contribution to total reconstruction error</p>
              </div>

              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={featureChartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <XAxis type="number" domain={[0, 100]} stroke="#64748b" fontSize={10} unit="%" />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={10} width={90} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '0.75rem' }} 
                      formatter={(val) => [`${val}%`, 'Contribution']}
                    />
                    <Bar dataKey="percentage" fill="#3b82f6" radius={[0, 4, 4, 0]}>
                      {featureChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#ef4444' : index === 1 ? '#f59e0b' : '#3b82f6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Generative AI Guidance */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4 text-emerald-400" />
                  <h4 className="text-sm font-bold text-white">Generative AI Verification Guidance</h4>
                </div>
                <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                  {result.ai_guidance?.source || 'Groq LPU'}
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="font-semibold text-slate-300 block mb-1">Pattern Analysis:</span>
                  <p className="text-slate-400 bg-slate-900 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed">
                    {result.ai_guidance?.explanation || 'Application aligns with reference baseline.'}
                  </p>
                </div>

                {result.ai_guidance?.fields_to_verify?.length > 0 && (
                  <div>
                    <span className="font-semibold text-slate-300 block mb-1">Fields Requiring Documentation:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {result.ai_guidance.fields_to_verify.map((f, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-amber-400 font-mono text-[11px] border border-amber-500/20">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result.ai_guidance?.suggested_steps?.length > 0 && (
                  <div>
                    <span className="font-semibold text-slate-300 block mb-1">Suggested Underwriter Verification Checklist:</span>
                    <ul className="space-y-1 text-slate-300 list-disc list-inside">
                      {result.ai_guidance.suggested_steps.map((step, i) => (
                        <li key={i} className="text-slate-400">{step}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="pt-2 border-t border-slate-800/80">
                  <span className="font-semibold text-slate-300 block mb-0.5">Manager Summary:</span>
                  <p className="text-slate-300 italic text-[11px]">
                    "{result.ai_guidance?.manager_summary}"
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              onClick={() => {
                setResult(null);
                setFormData({
                  applicant_id: `APP-${Math.floor(10000 + Math.random() * 90000)}`,
                  full_name: '',
                  email: '',
                  monthly_income: 5000,
                  monthly_rent: 1500,
                  credit_score: 700,
                  employment_duration: 3,
                  previous_evictions: 0,
                  existing_loans: 1,
                  employment_status: 'Full-time',
                  rental_history_duration: 4,
                  previous_residences: 2,
                });
              }}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-all cursor-pointer"
            >
              Submit Another Application
            </button>
            <button
              onClick={() => setActiveTab('applications')}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-xs font-bold text-slate-950 shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
            >
              View in Applications Registry
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
