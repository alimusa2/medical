import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ClipboardCheck, Search, ArrowRight, Layers } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { evaluationApi } from '../services/api';

export default function EvaluationsPage() {
  const [evaluations, setEvaluations] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    evaluationApi.list()
      .then(res => setEvaluations(Array.isArray(res.data) ? res.data : []))
      .catch(err => {
        console.error(err);
        setEvaluations([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const safeEvals = Array.isArray(evaluations) ? evaluations : [];
  const filteredEvals = safeEvals.filter(e => {
    if (!e) return false;
    const statusMatch = filter === 'ALL' || e.overall_status === filter;
    const q = searchTerm.toLowerCase();
    const searchMatch = !q || 
      (e.device_model && e.device_model.toLowerCase().includes(q)) ||
      (e.device_type_name && e.device_type_name.toLowerCase().includes(q)) ||
      (e.manufacturer && e.manufacturer.toLowerCase().includes(q)) ||
      (e.batch_id && e.batch_id.toLowerCase().includes(q));
    return statusMatch && searchMatch;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2 font-sans">
            <ClipboardCheck className="w-6 h-6 text-indigo-600" />
            <span>TRF Compliance Evaluations Workspace</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Inspect all medical device test report evaluations across 15 standard categories.
          </p>
        </div>

        {/* Search Bar & Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by device, model, mfr..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white border border-slate-200 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-indigo-500 w-48 sm:w-60 shadow-2xs"
            />
          </div>

          <div className="flex items-center gap-1 bg-white border border-slate-200 p-1 rounded-xl shadow-2xs text-xs font-semibold">
            {['ALL', 'PASS', 'FAIL', 'NEEDS REVIEW'].map((tab) => (
              <button
                key={tab}
                onClick={() => setFilter(tab)}
                className={`px-3 py-1 rounded-lg transition ${
                  filter === tab ? 'bg-indigo-600 text-white shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Table Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-mono uppercase text-[10px] border-b border-slate-200">
              <tr>
                <th className="p-4 font-bold">Device Name & Model</th>
                <th className="p-4 font-bold">Device Category & Pathway</th>
                <th className="p-4 font-bold">Overall Compliance</th>
                <th className="p-4 text-center font-bold">Passed / Failed / Review / N/A</th>
                <th className="p-4 font-bold">Certifier Decision</th>
                <th className="p-4 text-right font-bold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-400">
                    Loading evaluations...
                  </td>
                </tr>
              ) : filteredEvals.length > 0 ? (
                filteredEvals.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-50/80 transition">
                    <td className="p-4 font-semibold text-slate-900">
                      <div className="text-sm font-bold">{ev.device_model || 'Medical Device'}</div>
                      <div className="text-[10px] font-mono text-slate-400">{ev.manufacturer || 'Demo Manufacturer'} • Batch #{ev.batch_id}</div>
                    </td>

                    <td className="p-4 font-mono">
                      <div className="text-indigo-600 font-bold">{ev.device_type_name || 'Medical Equipment'}</div>
                      <div className="text-[10px] text-slate-500">{ev.pathway || 'ME Equipment'}</div>
                    </td>

                    <td className="p-4">
                      <StatusBadge status={ev.overall_status} size="sm" />
                    </td>

                    <td className="p-4 text-center font-mono font-bold">
                      <span className="text-emerald-600">{ev.passed_tests} P</span>
                      <span className="text-slate-300 mx-1">/</span>
                      <span className="text-rose-600">{ev.failed_tests} F</span>
                      <span className="text-slate-300 mx-1">/</span>
                      <span className="text-amber-600">{ev.needs_review_tests} R</span>
                      <span className="text-slate-300 mx-1">/</span>
                      <span className="text-slate-400">{ev.not_applicable_tests || 0} NA</span>
                    </td>

                    <td className="p-4">
                      <StatusBadge status={ev.certifier_status} size="sm" />
                    </td>

                    <td className="p-4 text-right">
                      <Link
                        to={`/evaluations/${ev.id}`}
                        className="px-3.5 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-600 font-bold transition inline-flex items-center gap-1 text-xs"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-400">
                    No evaluations match the selected filter.
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
