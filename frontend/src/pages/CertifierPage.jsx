import React, { useEffect, useState } from 'react';
import { 
  UserCheck, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  ArrowRight, 
  ShieldCheck, 
  HelpCircle, 
  FileText,
  Clock,
  Filter,
  Search,
  Layers
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { certifierApi } from '../services/api';
import { Link } from 'react-router-dom';

export default function CertifierPage() {
  const [activeTab, setActiveTab] = useState('PENDING_REVIEW'); // PENDING_REVIEW, APPROVED, NEEDS_MORE_INFO, REJECTED, ALL
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionNotes, setActionNotes] = useState({});
  const [searchTerm, setSearchTerm] = useState('');

  const loadData = () => {
    setLoading(true);
    certifierApi.getAll('ALL')
      .then(res => setEvaluations(res.data || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApprove = async (id) => {
    const notes = actionNotes[id] || "Evaluation approved & signed off by authorized certifier.";
    await certifierApi.approve(id, notes);
    loadData();
  };

  const handleRequestReview = async (id) => {
    const notes = actionNotes[id] || "Further technical review and missing clause data requested.";
    await certifierApi.requestReview(id, notes);
    loadData();
  };

  const handleReturnReviewer = async (id) => {
    const notes = actionNotes[id] || "Returned to technical reviewer for clarification/re-testing.";
    await certifierApi.returnToReviewer(id, notes);
    loadData();
  };

  // Counts for tabs
  const pendingCount = evaluations.filter(e => e.certifier_status === 'PENDING_REVIEW').length;
  const approvedCount = evaluations.filter(e => e.certifier_status === 'APPROVED').length;
  const infoRequestedCount = evaluations.filter(e => e.certifier_status === 'NEEDS_MORE_INFO').length;
  const rejectedCount = evaluations.filter(e => e.certifier_status === 'REJECTED').length;
  const totalCount = evaluations.length;

  // Filter evaluations based on activeTab and searchTerm
  const filtered = evaluations.filter(e => {
    const matchStatus = activeTab === 'ALL' || e.certifier_status === activeTab;
    const q = searchTerm.toLowerCase();
    const matchSearch = !q || 
      (e.device_name && e.device_name.toLowerCase().includes(q)) ||
      (e.device_model && e.device_model.toLowerCase().includes(q)) ||
      (e.batch_id && e.batch_id.toLowerCase().includes(q)) ||
      (e.certifier_notes && e.certifier_notes.toLowerCase().includes(q));
    return matchStatus && matchSearch;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Title & Description */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2 font-sans">
            <UserCheck className="w-6 h-6 text-indigo-600" />
            <span>Centralized Certifier Decision Workspace</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Centralized hub tracking all certifier approvals, information requests, reviewer returns, and audit trails.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search evaluations or notes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white border border-slate-200 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-indigo-500 w-48 sm:w-64 shadow-2xs"
            />
          </div>
        </div>
      </div>

      {/* Safety & Protocol Banner */}
      <div className="p-4 rounded-2xl bg-indigo-50/80 border border-indigo-100 text-xs text-indigo-950 flex items-center gap-3 shadow-2xs">
        <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0" />
        <div>
          <strong className="text-indigo-900 font-bold uppercase tracking-wide">Certifier Governance Protocol:</strong> Every certifier approval, technical info request, or rejection is recorded in the SQLite audit log with timestamps and notes. Evaluated compliance data remains fully searchable across all decision categories.
        </div>
      </div>

      {/* Centralized Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('PENDING_REVIEW')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
            activeTab === 'PENDING_REVIEW'
              ? 'bg-sky-500 text-white shadow-md shadow-sky-500/20'
              : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
          }`}
        >
          <Clock className="w-3.5 h-3.5" />
          <span>Pending Review</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-white/20 text-white font-mono">
            {pendingCount}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('APPROVED')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
            activeTab === 'APPROVED'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
              : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
          }`}
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Approved & Certified</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-white/20 text-white font-mono">
            {approvedCount}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('NEEDS_MORE_INFO')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
            activeTab === 'NEEDS_MORE_INFO'
              ? 'bg-amber-500 text-white shadow-md shadow-amber-500/20'
              : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
          }`}
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Info Requested</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-white/20 text-white font-mono">
            {infoRequestedCount}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('REJECTED')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
            activeTab === 'REJECTED'
              ? 'bg-rose-600 text-white shadow-md shadow-rose-600/20'
              : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
          }`}
        >
          <XCircle className="w-3.5 h-3.5" />
          <span>Returned / Rejected</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-white/20 text-white font-mono">
            {rejectedCount}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('ALL')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ml-auto cursor-pointer ${
            activeTab === 'ALL'
              ? 'bg-slate-800 text-white shadow-md'
              : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>All Audit Trail</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-slate-700 text-slate-200 font-mono">
            {totalCount}
          </span>
        </button>
      </div>

      {/* Evaluations List Cards */}
      <div className="space-y-4">
        {loading ? (
          <div className="bg-white rounded-2xl p-10 text-center text-slate-400 text-xs font-mono border border-slate-200">
            Loading certifier records...
          </div>
        ) : filtered.length > 0 ? (
          filtered.map((ev) => (
            <div key={ev.id} className="bg-white border border-slate-200/90 rounded-2xl p-6 space-y-4 shadow-sm hover:shadow-md transition">
              {/* Card Header Info */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-100 pb-3">
                <div>
                  <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                    <span>BATCH: {ev.batch_id}</span>
                    <span>•</span>
                    <span>Evaluation ID: #{ev.id}</span>
                  </div>
                  <div className="flex flex-wrap items-center gap-3 mt-1.5">
                    <span className="text-sm font-extrabold text-slate-900">{ev.device_name}</span>
                    <span className="text-xs text-slate-500 font-mono font-semibold">({ev.device_model})</span>
                    <StatusBadge status={ev.overall_status} size="sm" />
                    <StatusBadge status={ev.certifier_status} size="sm" />
                  </div>
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <span className="text-emerald-700 font-bold font-mono">{ev.passed_tests} PASS</span>
                  <span className="text-rose-700 font-bold font-mono">{ev.failed_tests} FAIL</span>
                  <span className="text-amber-700 font-bold font-mono">{ev.needs_review_tests} REVIEW</span>
                  <Link
                    to={`/evaluations/${ev.id}`}
                    className="px-3.5 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-600 font-bold transition flex items-center gap-1.5 text-xs"
                  >
                    <span>Inspect Evaluation</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Certifier Notes Display */}
              {ev.certifier_notes && (
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-bold text-indigo-600 font-mono">
                    <span className="flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5" /> Recorded Certifier Rationale:
                    </span>
                    <span className="font-mono text-slate-400 font-normal">
                      {ev.created_at ? new Date(ev.created_at).toLocaleString() : ''}
                    </span>
                  </div>
                  <p className="text-slate-700 italic font-sans">{ev.certifier_notes}</p>
                </div>
              )}

              {/* Action Notes Input & Buttons */}
              <div className="space-y-3 pt-1">
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-600 font-bold">Update Certifier Review Notes / Decision Rationale:</label>
                  <input
                    type="text"
                    placeholder="Enter decision rationale or specific technical notes..."
                    value={actionNotes[ev.id] !== undefined ? actionNotes[ev.id] : (ev.certifier_notes || '')}
                    onChange={(e) => setActionNotes({ ...actionNotes, [ev.id]: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                {/* Decision Action Buttons */}
                <div className="flex flex-wrap items-center justify-end gap-3 pt-1">
                  <button
                    onClick={() => handleReturnReviewer(ev.id)}
                    className="px-4 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-bold transition flex items-center gap-1.5 cursor-pointer"
                  >
                    <XCircle className="w-4 h-4 text-rose-600" />
                    <span>Return to Reviewer</span>
                  </button>
                  <button
                    onClick={() => handleRequestReview(ev.id)}
                    className="px-4 py-2 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 text-xs font-bold transition flex items-center gap-1.5 cursor-pointer"
                  >
                    <HelpCircle className="w-4 h-4 text-amber-600" />
                    <span>Request Technical Info</span>
                  </button>
                  <button
                    onClick={() => handleApprove(ev.id)}
                    className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs shadow-md shadow-emerald-600/20 transition flex items-center gap-1.5 cursor-pointer"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve & Certify</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-white rounded-2xl p-12 text-center text-slate-400 border border-slate-200 space-y-2">
            <ShieldCheck className="w-8 h-8 text-slate-300 mx-auto" />
            <div className="text-sm font-bold text-slate-700">No evaluations found in this category</div>
            <p className="text-xs text-slate-500">
              {activeTab === 'PENDING_REVIEW' ? 'All submitted evaluations have been certified or processed.' : 'No evaluation records match the selected filter.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
