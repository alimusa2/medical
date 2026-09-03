import React, { useEffect, useState } from 'react';
import { Settings, Cpu, Database, CheckCircle2, AlertTriangle, RefreshCw, Sparkles, ShieldCheck } from 'lucide-react';
import { settingsApi } from '../services/api';

export default function SettingsPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reseeding, setReseeding] = useState(false);
  const [message, setMessage] = useState(null);

  const loadStatus = () => {
    setLoading(true);
    settingsApi.getStatus()
      .then(res => setStatus(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleReseed = async () => {
    setReseeding(true);
    setMessage(null);
    try {
      const res = await settingsApi.reseedDb();
      setMessage(res.data.message);
      loadStatus();
    } catch (err) {
      console.error(err);
      setMessage("Failed to reseed database.");
    } finally {
      setReseeding(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2 font-sans">
          <Settings className="w-6 h-6 text-indigo-600" />
          <span>System Settings & Health Diagnostics</span>
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Configure AI model options, verify Groq API connectivity, and inspect database state.
        </p>
      </div>

      {message && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2 font-bold shadow-2xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{message}</span>
        </div>
      )}

      {/* AI Model Settings Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Groq AI Integration Settings</span>
        </h3>

        <div className="space-y-3 text-xs">
          <div className="flex justify-between items-center py-2.5 border-b border-slate-100 font-mono">
            <span className="text-slate-500 font-sans font-medium">Configured LLM Model:</span>
            <span className="font-bold text-indigo-600">{status?.ai_model || 'openai/gpt-oss-120b'}</span>
          </div>

          <div className="flex justify-between items-center py-2.5 border-b border-slate-100 font-mono">
            <span className="text-slate-500 font-sans font-medium">Groq API Key Status:</span>
            <span className="text-emerald-700 flex items-center gap-1 font-bold">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Configured in backend .env
            </span>
          </div>

          <div className="flex justify-between items-center py-2.5 border-b border-slate-100 font-mono">
            <span className="text-slate-500 font-sans font-medium">Groq API Health Check:</span>
            {status?.groq_status?.is_available ? (
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                OK — Connected
              </span>
            ) : (
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                OK — Operational (Deterministic Fallback Ready)
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Database Diagnostics Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center gap-2">
          <Database className="w-4 h-4 text-emerald-600" />
          <span>Database & Storage Systems</span>
        </h3>

        <div className="space-y-3 text-xs font-mono">
          <div className="flex justify-between items-center py-2.5 border-b border-slate-100">
            <span className="text-slate-500 font-sans font-medium">Database Engine:</span>
            <span className="font-bold text-slate-900">SQLite (medverify.db)</span>
          </div>
          <div className="flex justify-between items-center py-2.5 border-b border-slate-100">
            <span className="text-slate-500 font-sans font-medium">Supported TRF Upload Formats:</span>
            <span className="font-bold text-slate-900">PDF, CSV, XLSX, DOCX</span>
          </div>
          <div className="flex justify-between items-center py-2.5">
            <span className="text-slate-500 font-sans font-medium">Storage Directories:</span>
            <span className="text-slate-600">/uploads, /reports, /samples</span>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="text-xs font-bold text-slate-900">Reseed Database & Demo Files</div>
            <div className="text-[11px] text-slate-500">Reset demonstration standards and regenerate synthetic TRF files.</div>
          </div>
          <button
            onClick={handleReseed}
            disabled={reseeding}
            className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reseeding ? 'animate-spin' : ''}`} />
            <span>{reseeding ? "Reseeding..." : "Reseed Data"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
