import React, { useEffect, useState } from 'react';
import { BookOpen, ShieldAlert, CheckCircle2, Search } from 'lucide-react';
import { standardsApi } from '../services/api';

export default function StandardsPage() {
  const [standards, setStandards] = useState([]);
  const [requirements, setRequirements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    Promise.all([standardsApi.listStandards(), standardsApi.listRequirements()])
      .then(([stdRes, reqRes]) => {
        setStandards(stdRes.data || []);
        setRequirements(reqRes.data || []);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const filteredReqs = requirements.filter(r => {
    const q = searchTerm.toLowerCase();
    return !q || 
      (r.requirement_code && r.requirement_code.toLowerCase().includes(q)) ||
      (r.title && r.title.toLowerCase().includes(q)) ||
      (r.test_parameter && r.test_parameter.toLowerCase().includes(q));
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2 font-sans">
            <BookOpen className="w-6 h-6 text-indigo-600" />
            <span>Standards & Evaluation Rules Knowledge Base</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configured medical electrical safety standards (IEC 60601 & ISO standards knowledge base).
          </p>
        </div>

        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search requirement rules..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-white border border-slate-200 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-indigo-500 w-48 sm:w-64 shadow-2xs"
          />
        </div>
      </div>

      {/* Safety Notice */}
      <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-3 shadow-2xs">
        <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0" />
        <div>
          <strong className="text-amber-950 font-bold uppercase tracking-wide">Knowledge Base Notice:</strong> Prototype acceptance rules and standard criteria are derived from published non-copyrighted safety parameter limits for demonstration.
        </div>
      </div>

      {/* Standards List Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {standards.map((s) => (
          <div key={s.id} className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-2 hover:shadow-md transition">
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm font-bold text-indigo-600">{s.name}</span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                {s.status}
              </span>
            </div>
            <h3 className="font-extrabold text-slate-900 text-sm">{s.edition}</h3>
            <p className="text-xs text-slate-500 leading-snug">{s.description}</p>
          </div>
        ))}
      </div>

      {/* Requirements Table */}
      <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-extrabold text-slate-900 tracking-tight font-sans uppercase">
            Configured Acceptance Rules ({filteredReqs.length})
          </h3>
          <span className="text-[10px] font-mono font-bold text-slate-400">IEC Standard Thresholds</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-mono uppercase text-[10px] border-b border-slate-200">
              <tr>
                <th className="p-4 font-bold">Requirement Code</th>
                <th className="p-4 font-bold">Title</th>
                <th className="p-4 font-bold">Test Parameter</th>
                <th className="p-4 font-bold">Operator / Threshold</th>
                <th className="p-4 font-bold">Unit</th>
                <th className="p-4 font-bold">Category Flag</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-400">Loading requirements...</td>
                </tr>
              ) : filteredReqs.length > 0 ? (
                filteredReqs.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80 transition">
                    <td className="p-4 font-mono text-indigo-600 font-bold text-sm">{r.requirement_code}</td>
                    <td className="p-4 font-bold text-slate-900">{r.title}</td>
                    <td className="p-4 text-slate-700 font-medium">{r.test_parameter}</td>
                    <td className="p-4 font-mono text-amber-700 font-bold">
                      {r.operator === '<=' && `≤ ${r.maximum_value}`}
                      {r.operator === '>=' && `≥ ${r.minimum_value}`}
                      {r.expected_text && `Expected: ${r.expected_text}`}
                    </td>
                    <td className="p-4 font-mono text-slate-500">{r.unit || '-'}</td>
                    <td className="p-4">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                        Demo Acceptance Rule
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-400">No requirements match search.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
