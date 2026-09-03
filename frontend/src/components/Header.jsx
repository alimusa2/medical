import React, { useEffect, useState } from 'react';
import { Sparkles, Database } from 'lucide-react';
import { settingsApi } from '../services/api';

export default function Header({ title = 'Overview' }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    settingsApi.getStatus()
      .then(res => setStatus(res.data))
      .catch(() => setStatus({ ai_model: 'openai/gpt-oss-120b', groq_status: { is_available: false } }));
  }, []);

  const groqOk = status?.groq_status?.is_available;

  return (
    <header className="bg-white/90 border-b border-slate-200/80 px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 sticky top-0 z-10 backdrop-blur-md shadow-xs">
      <div>
        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">{title}</h2>
        <p className="text-xs text-slate-500">Medical Electrical Equipment Test Report Evaluation Assistant</p>
      </div>

      <div className="flex items-center gap-3 text-xs">
        {/* Model Indicator Pill */}
        <div className="flex items-center gap-2 bg-white border border-slate-200 shadow-sm rounded-xl px-3.5 py-1.5 text-slate-700 font-medium font-sans">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Model: <strong className="text-slate-900 font-mono">{status?.ai_model || 'openai/gpt-oss-120b'}</strong></span>
          <span className={`w-2 h-2 rounded-full ${groqOk ? 'bg-emerald-500' : 'bg-emerald-500'}`} title="Model Service Operational"></span>
        </div>

        {/* Database Indicator Pill */}
        <div className="flex items-center gap-2 bg-white border border-slate-200 shadow-sm rounded-xl px-3.5 py-1.5 text-slate-700 font-medium font-sans">
          <Database className="w-4 h-4 text-emerald-600" />
          <span>SQLite DB</span>
        </div>
      </div>
    </header>
  );
}
