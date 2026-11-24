import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  Zap, 
  Database, 
  Save, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Sparkles, 
  ExternalLink 
} from 'lucide-react';

export default function Settings({ onRefreshAll }) {
  const [settings, setSettings] = useState(null);
  const [mediumThreshold, setMediumThreshold] = useState(0.0525);
  const [highThreshold, setHighThreshold] = useState(0.1420);
  const [thresholdMsg, setThresholdMsg] = useState(null);
  const [savingThresholds, setSavingThresholds] = useState(false);

  // Groq LLM state
  const [groqKey, setGroqKey] = useState('');
  const [groqModel, setGroqModel] = useState('llama-3.3-70b-versatile');
  const [testingLLM, setTestingLLM] = useState(false);
  const [llmTestResult, setLlmTestResult] = useState(null);

  // Reseed state
  const [sampleCount, setSampleCount] = useState(150);
  const [reseeding, setReseeding] = useState(false);
  const [reseedMsg, setReseedMsg] = useState(null);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await fetch('/api/settings');
        if (res.ok) {
          const data = await res.json();
          setSettings(data);
          setMediumThreshold(data.medium_threshold || 0.0525);
          setHighThreshold(data.high_threshold || 0.1420);
          setGroqModel(data.groq_model || 'llama-3.3-70b-versatile');
        }
      } catch (err) {
        console.error('Failed to load settings:', err);
      }
    };
    fetchSettings();
  }, []);

  const handleSaveThresholds = async (e) => {
    e.preventDefault();
    setSavingThresholds(true);
    setThresholdMsg(null);
    try {
      const res = await fetch('/api/settings/thresholds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          medium_threshold: parseFloat(mediumThreshold),
          high_threshold: parseFloat(highThreshold),
        }),
      });
      if (res.ok) {
        setThresholdMsg({ type: 'success', text: 'Thresholds saved and calibrated successfully!' });
        if (onRefreshAll) onRefreshAll();
      } else {
        const err = await res.json();
        setThresholdMsg({ type: 'error', text: err.detail || 'Failed to save thresholds' });
      }
    } catch (err) {
      setThresholdMsg({ type: 'error', text: err.message });
    } finally {
      setSavingThresholds(false);
    }
  };

  const handleTestLLM = async () => {
    setTestingLLM(true);
    setLlmTestResult(null);
    try {
      const res = await fetch('/api/settings/test-llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          groq_api_key: groqKey.trim() || undefined,
          groq_model: groqModel,
          provider: 'groq'
        }),
      });
      const data = await res.json();
      setLlmTestResult(data);
    } catch (err) {
      setLlmTestResult({ status: 'error', detail: err.message });
    } finally {
      setTestingLLM(false);
    }
  };

  const handleReseed = async () => {
    setReseeding(true);
    setReseedMsg(null);
    try {
      const res = await fetch('/api/settings/reseed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sample_count: parseInt(sampleCount) }),
      });
      if (res.ok) {
        const data = await res.json();
        setReseedMsg({ type: 'success', text: `Successfully seeded ${data.seeded_count} synthetic applications into SQLite!` });
        if (onRefreshAll) onRefreshAll();
      } else {
        const err = await res.json();
        setReseedMsg({ type: 'error', text: err.detail || 'Failed to reseed' });
      }
    } catch (err) {
      setReseedMsg({ type: 'error', text: err.message });
    } finally {
      setReseeding(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">System Settings & Threshold Tuning</h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure unsupervised deep learning anomaly boundaries, manage Groq API credentials, and re-seed database artifacts.
        </p>
      </div>

      {/* Threshold Calibration Form */}
      <form onSubmit={handleSaveThresholds} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-white">1. Anomaly Classification Thresholds</h3>
        </div>

        <p className="text-xs text-slate-400">
          Reconstruction error thresholds calibrated against the normal validation distribution.
          Applications with error below P95 are Low Anomaly; between P95 and P99 are Medium; above P99 are High Anomaly.
        </p>

        {thresholdMsg && (
          <div className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
            thresholdMsg.type === 'success' ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-400' : 'bg-rose-500/15 border border-rose-500/30 text-rose-400'
          }`}>
            {thresholdMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            <span>{thresholdMsg.text}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-slate-300">Medium Threshold (P95 Cutoff)</label>
              <span className="text-xs font-mono font-bold text-amber-400">{Number(mediumThreshold).toFixed(4)}</span>
            </div>
            <input
              type="number"
              step="0.005"
              min="0.001"
              max="5.0"
              value={mediumThreshold}
              onChange={(e) => setMediumThreshold(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
            />
            <span className="text-[10px] text-slate-500 block">Baseline normal cutoff ~0.0525</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-slate-300">High Threshold (P99 Cutoff)</label>
              <span className="text-xs font-mono font-bold text-rose-400">{Number(highThreshold).toFixed(4)}</span>
            </div>
            <input
              type="number"
              step="0.005"
              min="0.001"
              max="15.0"
              value={highThreshold}
              onChange={(e) => setHighThreshold(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
            />
            <span className="text-[10px] text-slate-500 block">Priority audit cutoff ~0.1420</span>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={savingThresholds}
            className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center gap-2 cursor-pointer transition-all"
          >
            <Save className="w-4 h-4" />
            <span>{savingThresholds ? 'Updating Thresholds...' : 'Save Calibrated Thresholds'}</span>
          </button>
        </div>
      </form>

      {/* Groq AI Underwriting Explainer */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-bold text-white">2. Groq LPU Generative AI Explainer</h3>
          </div>
          <span className="px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold">
            {settings?.groq_configured ? '⚡ Groq Connected' : 'Deterministic Fallback Active'}
          </span>
        </div>

        <p className="text-xs text-slate-400">
          Groq LPUs deliver ultra-fast natural-language underwriting explanations.
          If no key is configured, RentGuard AI guarantees zero downtime via our built-in deterministic rule engine.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Groq API Key (starts with gsk_)</label>
            <input
              type="password"
              placeholder="gsk_..."
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs font-mono text-white focus:outline-none focus:border-amber-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Groq LLM Model</label>
            <select
              value={groqModel}
              onChange={(e) => setGroqModel(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
            >
              <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile (Recommended)</option>
              <option value="llama-3.1-8b-instant">llama-3.1-8b-instant (Fastest)</option>
              <option value="mixtral-8x7b-32768">mixtral-8x7b-32768</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleTestLLM}
            disabled={testingLLM}
            className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold text-xs shadow-md shadow-amber-500/20 flex items-center gap-2 cursor-pointer transition-all"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>{testingLLM ? 'Pinging Groq LPU API...' : 'Test Groq Connection'}</span>
          </button>
          <a
            href="https://console.groq.com/keys"
            target="_blank"
            rel="noreferrer"
            className="text-xs text-slate-400 hover:text-white flex items-center gap-1 font-medium"
          >
            <span>Get free Groq API key</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        {llmTestResult && (
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5 text-xs animate-in fade-in">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-white">Engine Source: {llmTestResult.source}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                llmTestResult.status === 'success' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-300'
              }`}>
                {llmTestResult.status.toUpperCase()}
              </span>
            </div>
            {llmTestResult.summary && (
              <p className="text-slate-400 italic">"{llmTestResult.summary}"</p>
            )}
            {llmTestResult.detail && (
              <p className="text-rose-400">{llmTestResult.detail}</p>
            )}
          </div>
        )}
      </div>

      {/* Database Seeding & Maintenance */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">3. Database Seeding & Reset</h3>
        </div>

        <p className="text-xs text-slate-400">
          Populate SQLite with freshly evaluated synthetic rental applications for demonstrations and underwriting drills.
        </p>

        {reseedMsg && (
          <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{reseedMsg.text}</span>
          </div>
        )}

        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="w-full sm:w-64">
            <label className="block text-xs font-semibold text-slate-400 mb-1">Applications to Seed: {sampleCount}</label>
            <input
              type="range"
              min="50"
              max="300"
              step="25"
              value={sampleCount}
              onChange={(e) => setSampleCount(e.target.value)}
              className="w-full accent-indigo-500 cursor-pointer"
            />
          </div>

          <button
            type="button"
            onClick={handleReseed}
            disabled={reseeding}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-indigo-600/20 flex items-center gap-2 cursor-pointer transition-all self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reseeding ? 'animate-spin' : ''}`} />
            <span>{reseeding ? 'Seeding Records via Autoencoder...' : 'Populate / Reseed SQLite'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
