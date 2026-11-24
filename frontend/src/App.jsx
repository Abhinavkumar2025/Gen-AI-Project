import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import SubmitApplication from './components/SubmitApplication';
import AllApplications from './components/AllApplications';
import AnomalyAnalytics from './components/AnomalyAnalytics';
import Reports from './components/Reports';
import Settings from './components/Settings';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [summary, setSummary] = useState(null);
  const [applications, setApplications] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedAppId, setSelectedAppId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Primary data fetcher
  const fetchData = async () => {
    setIsRefreshing(true);
    try {
      const [sumRes, appsRes, setRes] = await Promise.all([
        fetch('/api/dashboard/summary'),
        fetch('/api/applications'),
        fetch('/api/settings')
      ]);

      if (sumRes.ok) setSummary(await sumRes.json());
      if (appsRes.ok) {
        const appsData = await appsRes.json();
        setApplications(appsData.applications || []);
      }
      if (setRes.ok) setSystemStatus(await setRes.json());
    } catch (err) {
      console.error('Failed to load application data:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSelectApp = (appId) => {
    setSelectedAppId(appId);
    if (activeTab !== 'applications') {
      setActiveTab('applications');
    }
  };

  const getHeaderMeta = () => {
    switch (activeTab) {
      case 'dashboard':
        return { title: 'Executive Underwriting Dashboard', subtitle: 'Live tenancy portfolio anomaly stream & audit overview' };
      case 'submit':
        return { title: 'Intake & Underwriting Inference', subtitle: 'Ingest applicant parameters for real-time deep learning scoring' };
      case 'applications':
        return { title: 'Rental Applications Registry', subtitle: 'Search, filter, inspect feature residuals, and document audit decisions' };
      case 'analytics':
        return { title: 'Model Performance & Feature Attribution', subtitle: 'Autoencoder mathematical distributions, ROC/PR benchmarks, and calibration' };
      case 'reports':
        return { title: 'Underwriting Reports & Export', subtitle: 'Generate verifiable compliance audit trails and export datasets' };
      case 'settings':
        return { title: 'System Configuration & Calibration', subtitle: 'Threshold tuning, Groq API credentials, and database operations' };
      default:
        return { title: 'RentGuard AI', subtitle: '' };
    }
  };

  const meta = getHeaderMeta();

  return (
    <div className="flex min-h-screen bg-[#0b0f19] text-slate-100">
      {/* Persistent Modern Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={(tab) => {
          setActiveTab(tab);
          if (tab !== 'applications') setSelectedAppId(null);
        }} 
        systemStatus={systemStatus} 
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          title={meta.title}
          subtitle={meta.subtitle}
          onRefresh={fetchData}
          isRefreshing={isRefreshing}
          searchQuery={activeTab === 'applications' ? searchQuery : undefined}
          setSearchQuery={activeTab === 'applications' ? setSearchQuery : undefined}
        />

        <main className="flex-1 overflow-y-auto">
          {activeTab === 'dashboard' && (
            <Dashboard
              summary={summary}
              recentApps={applications}
              onSelectApp={handleSelectApp}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'submit' && (
            <SubmitApplication
              onSubmitted={fetchData}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'applications' && (
            <AllApplications
              applications={applications}
              selectedAppId={selectedAppId}
              onSelectApp={(id) => setSelectedAppId(id)}
              onCloseDrawer={() => setSelectedAppId(null)}
              onRefresh={fetchData}
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
            />
          )}

          {activeTab === 'analytics' && (
            <AnomalyAnalytics />
          )}

          {activeTab === 'reports' && (
            <Reports applications={applications} />
          )}

          {activeTab === 'settings' && (
            <Settings onRefreshAll={fetchData} />
          )}
        </main>
      </div>
    </div>
  );
}
