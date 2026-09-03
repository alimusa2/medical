import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';

import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DisclaimerBanner from './components/DisclaimerBanner';

import Dashboard from './pages/Dashboard';
import UploadPage from './pages/UploadPage';
import DocumentReviewPage from './pages/DocumentReviewPage';
import EvaluationsPage from './pages/EvaluationsPage';
import EvaluationDetailPage from './pages/EvaluationDetailPage';
import StandardsPage from './pages/StandardsPage';
import ReportsPage from './pages/ReportsPage';
import CertifierPage from './pages/CertifierPage';
import SettingsPage from './pages/SettingsPage';

function LayoutWrapper() {
  const location = useLocation();

  const getPageTitle = (path) => {
    if (path === '/') return 'Dashboard Overview';
    if (path.startsWith('/upload')) return 'Upload Test Report Form';
    if (path.startsWith('/documents')) return 'Document Inspection & Review';
    if (path.startsWith('/evaluations')) return 'Test Compliance Evaluations';
    if (path.startsWith('/standards')) return 'Standards & Acceptance Rules';
    if (path.startsWith('/reports')) return 'Generated Evaluation Reports';
    if (path.startsWith('/certifier')) return 'Certifier Governance & Decision Workspace';
    if (path.startsWith('/settings')) return 'System Diagnostics & Settings';
    return 'Technical Review Workspace';
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#f4f6fb] text-slate-900 font-sans">
      <DisclaimerBanner />
      <div className="flex flex-1 min-h-screen">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0">
          <Header title={getPageTitle(location.pathname)} />
          <div className="flex-1 p-6 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/documents" element={<Dashboard />} />
              <Route path="/documents/:id" element={<DocumentReviewPage />} />
              <Route path="/evaluations" element={<EvaluationsPage />} />
              <Route path="/evaluations/:id" element={<EvaluationDetailPage />} />
              <Route path="/standards" element={<StandardsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/certifier" element={<CertifierPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <LayoutWrapper />
    </BrowserRouter>
  );
}
