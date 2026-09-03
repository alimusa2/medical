import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  FileText, 
  Download, 
  Send, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Sparkles,
  Info,
  ChevronRight,
  X,
  ShieldAlert,
  Layers,
  Search,
  Filter,
  SlidersHorizontal,
  ExternalLink,
  UserCheck
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import ConfidenceBadge from '../components/ConfidenceBadge';
import { evaluationApi, certifierApi, reportsApi } from '../services/api';

export default function EvaluationDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [submittingCertifier, setSubmittingCertifier] = useState(false);
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [activeStandardFilter, setActiveStandardFilter] = useState('ALL');

  useEffect(() => {
    evaluationApi.get(id)
      .then(res => setEvaluation(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <div className="p-8 text-center text-slate-400 font-mono text-xs">Loading TRF evaluation details...</div>;
  }

  if (!evaluation) {
    return <div className="p-8 text-center text-rose-600 font-bold text-sm">Evaluation record not found.</div>;
  }

  let aiSummary = null;
  if (evaluation.ai_summary) {
    try {
      aiSummary = JSON.parse(evaluation.ai_summary);
    } catch (e) {
      aiSummary = { summary: evaluation.ai_summary };
    }
  }

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const res = await evaluationApi.generateReport(evaluation.id);
      setDownloadUrl(reportsApi.getDownloadUrl(res.data.filename));
    } catch (err) {
      console.error("Failed to generate PDF report:", err);
    } finally {
      setGeneratingReport(false);
    }
  };

  const handleSubmitCertifier = async () => {
    setSubmittingCertifier(true);
    try {
      await certifierApi.requestReview(evaluation.id, "Submitted for technical certifier sign-off.");
      navigate('/certifier');
    } catch (err) {
      console.error(err);
      setSubmittingCertifier(false);
    }
  };

  const results = evaluation.results || [];
  const uniqueStandards = Array.from(new Set(results.map(r => r.standard_code).filter(Boolean)));

  const filteredResults = results.filter(r => {
    const statusMatch = activeFilter === 'ALL' || r.status === activeFilter;
    const stdMatch = activeStandardFilter === 'ALL' || r.standard_code === activeStandardFilter;
    return statusMatch && stdMatch;
  });

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Prominent Prototype Disclaimer Banner */}
      <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-3 shadow-2xs">
        <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="text-xs leading-relaxed">
          <strong className="text-amber-950 font-bold uppercase tracking-wider block mb-0.5">
            Prototype Decision Support Disclaimer Notice
          </strong>
          This system provides an automated evaluation based on the uploaded TRF and the internal standards knowledge base. 
          It is intended for demonstration and decision-support purposes only and does not replace final certification by authorized personnel.
        </div>
      </div>

      {/* Header Decision Banner */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <span>BATCH: {evaluation.batch_id}</span>
            <span>•</span>
            <span>Ref ID: #{evaluation.id}</span>
            <span>•</span>
            <span className="text-indigo-600 font-bold">{evaluation.device_type_name || 'Medical Equipment'}</span>
          </div>

          <div className="flex items-center gap-3">
            <StatusBadge status={evaluation.overall_status} size="normal" />
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight font-sans">
              {evaluation.device_model ? `${evaluation.device_model}` : 'TRF Compliance Evaluation'}
              <span className="text-sm font-semibold text-slate-500 ml-2 font-mono">({evaluation.manufacturer || 'Medical Systems'})</span>
            </h1>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          {downloadUrl ? (
            <a
              href={downloadUrl}
              download
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/20 transition cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Download PDF Report</span>
            </a>
          ) : (
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs border border-slate-200 transition cursor-pointer"
            >
              <FileText className="w-4 h-4 text-indigo-600" />
              <span>{generatingReport ? "Generating PDF..." : "Generate PDF Report"}</span>
            </button>
          )}

          <button
            onClick={handleSubmitCertifier}
            disabled={submittingCertifier}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/25 transition cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Submit to Certifier Queue</span>
          </button>
        </div>
      </div>

      {/* Certifier Governance & Decision Status Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900 uppercase font-mono">Certifier Decision Status</div>
              <div className="text-[11px] text-slate-500">Formal technical certifier sign-off status and recorded audit trail</div>
            </div>
          </div>
          <StatusBadge status={evaluation.certifier_status || 'PENDING_REVIEW'} size="normal" />
        </div>

        {evaluation.certifier_notes ? (
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs space-y-1">
            <div className="text-[11px] font-bold text-indigo-600 font-mono">Certifier Recorded Rationale / Notes:</div>
            <p className="text-slate-700 italic font-sans">{evaluation.certifier_notes}</p>
          </div>
        ) : (
          <div className="text-xs text-slate-400 italic">No certifier review notes recorded yet. Pending formal certifier sign-off.</div>
        )}
      </div>

      {/* Summary Counters Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="bg-white p-4 text-center border border-slate-200/90 rounded-2xl shadow-sm">
          <div className="text-2xl font-bold text-slate-900 font-mono">{evaluation.total_tests}</div>
          <div className="text-[11px] text-slate-500 uppercase font-mono mt-1 font-bold">Total Evaluated</div>
        </div>
        <div className="bg-emerald-50/80 p-4 text-center border border-emerald-100 rounded-2xl shadow-sm">
          <div className="text-2xl font-bold text-emerald-700 font-mono">{evaluation.passed_tests}</div>
          <div className="text-[11px] text-emerald-800 uppercase font-mono mt-1 font-bold">Passed</div>
        </div>
        <div className="bg-rose-50/80 p-4 text-center border border-rose-100 rounded-2xl shadow-sm">
          <div className="text-2xl font-bold text-rose-700 font-mono">{evaluation.failed_tests}</div>
          <div className="text-[11px] text-rose-800 uppercase font-mono mt-1 font-bold">Failed</div>
        </div>
        <div className="bg-amber-50/80 p-4 text-center border border-amber-100 rounded-2xl shadow-sm">
          <div className="text-2xl font-bold text-amber-700 font-mono">{evaluation.needs_review_tests}</div>
          <div className="text-[11px] text-amber-800 uppercase font-mono mt-1 font-bold">Needs Review</div>
        </div>
        <div className="bg-slate-100/70 p-4 text-center border border-slate-200 rounded-2xl shadow-sm">
          <div className="text-2xl font-bold text-slate-600 font-mono">{evaluation.not_applicable_tests || 0}</div>
          <div className="text-[11px] text-slate-500 uppercase font-mono mt-1 font-bold">Not Applicable</div>
        </div>
      </div>

      {/* Device Specification & Classification Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-3">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center gap-2">
          <Info className="w-4 h-4 text-indigo-600" />
          <span>Extracted Device Specification & Safety Pathway</span>
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <div className="text-slate-400 text-[10px] font-bold">DEVICE CATEGORY</div>
            <div className="font-bold text-slate-900 mt-1">{evaluation.device_type_name || 'Medical Equipment'}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <div className="text-slate-400 text-[10px] font-bold">MODEL NUMBER</div>
            <div className="font-bold text-indigo-600 mt-1">{evaluation.device_model || 'N/A'}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <div className="text-slate-400 text-[10px] font-bold">MANUFACTURER</div>
            <div className="font-bold text-slate-900 mt-1">{evaluation.manufacturer || 'N/A'}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
            <div className="text-slate-400 text-[10px] font-bold">SAFETY PATHWAY</div>
            <div className="mt-1">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                evaluation.pathway === 'IVD / Laboratory Equipment'
                  ? 'bg-purple-100 text-purple-700 border border-purple-200'
                  : 'bg-sky-100 text-sky-700 border border-sky-200'
              }`}>
                {evaluation.pathway || 'ME Equipment (IEC 60601 Pathway)'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Detected Applicable Standards Hierarchy Grid */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-600" />
            <span>Detected IEC / ISO Standards Hierarchy & Selection Rationale</span>
          </h3>
          <span className="text-[10px] font-mono font-bold text-slate-400">Structured Hierarchy Rules</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {uniqueStandards.map((code, idx) => {
            const sampleRes = results.find(r => r.standard_code === code);
            const stdCategory = sampleRes?.standard_category || 'General';

            return (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold font-mono text-indigo-600 text-sm">{code}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    stdCategory === 'General' ? 'bg-sky-100 text-sky-700' :
                    stdCategory === 'Collateral' ? 'bg-indigo-100 text-indigo-700' :
                    stdCategory === 'Particular' ? 'bg-emerald-100 text-emerald-700' :
                    'bg-slate-200 text-slate-700'
                  }`}>
                    {stdCategory} Standard
                  </span>
                </div>
                <div className="text-slate-500 text-[11px] leading-snug">
                  Applicable evaluation area mapping based on identified device characteristics and safety pathway.
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* AI Summary Block */}
      {aiSummary && (
        <div className="bg-gradient-to-r from-violet-50/90 via-indigo-50/70 to-purple-50/90 border border-indigo-100 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-indigo-100 pb-3">
            <h3 className="text-xs font-bold text-indigo-900 uppercase tracking-wider flex items-center gap-2 font-mono">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span>AI-Assisted Evaluation Summary</span>
            </h3>
            <span className="text-[10px] font-mono font-bold text-indigo-500">Groq LLM Validated Summary</span>
          </div>

          <p className="text-xs text-slate-700 leading-relaxed font-sans">{aiSummary.summary}</p>

          {aiSummary.key_findings && aiSummary.key_findings.length > 0 && (
            <div className="space-y-1.5 pt-2">
              <h4 className="text-xs font-bold text-indigo-900">Key Assessment Findings:</h4>
              <ul className="list-disc list-inside text-xs text-slate-700 space-y-1 font-sans">
                {aiSummary.key_findings.map((kf, i) => (
                  <li key={i}>{kf}</li>
                ))}
              </ul>
            </div>
          )}

          {aiSummary.recommendation && (
            <div className="p-3.5 rounded-xl bg-white/80 border border-indigo-200/80 text-xs text-indigo-950 font-medium shadow-2xs">
              <strong className="text-indigo-900 font-bold">Recommended Action:</strong> {aiSummary.recommendation}
            </div>
          )}
        </div>
      )}

      {/* Standard Comparison Table with Filters */}
      <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-extrabold text-slate-900 tracking-tight font-sans">
              IEC Standards vs TRF Evidence Comparison Matrix
            </h3>
            <p className="text-xs text-slate-500">Click any row to inspect complete evidence traceability and reasoning</p>
          </div>

          {/* Filter Tabs */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <div className="flex items-center gap-1 bg-slate-100 border border-slate-200 p-1 rounded-xl">
              {['ALL', 'PASS', 'FAIL', 'NEEDS REVIEW', 'NOT APPLICABLE'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveFilter(tab)}
                  className={`px-2.5 py-1 rounded-lg transition font-medium ${
                    activeFilter === tab ? 'bg-indigo-600 text-white font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-mono uppercase text-[10px] border-b border-slate-200">
              <tr>
                <th className="p-3.5 font-bold">Standard & Category</th>
                <th className="p-3.5 font-bold">Requirement Area / Test</th>
                <th className="p-3.5 font-bold">Evidence Found</th>
                <th className="p-3.5 font-bold">TRF Reported</th>
                <th className="p-3.5 font-bold">System Evaluation</th>
                <th className="p-3.5 font-bold">Reasoning / Rationale</th>
                <th className="p-3.5 text-right font-bold">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {filteredResults.map((res) => (
                <tr
                  key={res.id}
                  onClick={() => setSelectedItem(res)}
                  className="hover:bg-indigo-50/40 transition cursor-pointer"
                >
                  <td className="p-3.5 font-mono">
                    <div className="font-bold text-indigo-600">{res.standard_code || 'IEC 60601-1'}</div>
                    <div className="text-[10px] text-slate-400">{res.standard_category || 'General'}</div>
                  </td>

                  <td className="p-3.5 font-bold text-slate-900">{res.test_name}</td>

                  <td className="p-3.5 font-mono">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      res.evidence_found === 'Yes' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                      res.evidence_found === 'Partial' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                      'bg-slate-100 text-slate-600'
                    }`}>
                      {res.evidence_found || 'Yes'}
                    </span>
                  </td>

                  <td className="p-3.5 font-mono font-semibold text-slate-700">
                    {res.trf_result || '-'}
                  </td>

                  <td className="p-3.5">
                    <StatusBadge status={res.status} size="sm" />
                  </td>

                  <td className="p-3.5 text-slate-500 max-w-xs truncate">
                    {res.reason}
                  </td>

                  <td className="p-3.5 text-right">
                    <ChevronRight className="w-4 h-4 text-slate-400 inline" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Evidence Traceability Drawer / Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white max-w-xl w-full p-6 rounded-2xl border border-slate-200 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-extrabold text-slate-900 text-base flex items-center gap-2 font-sans">
                <Info className="w-5 h-5 text-indigo-600" />
                <span>Evidence Traceability & Finding Rationale</span>
              </h3>
              <button
                onClick={() => setSelectedItem(null)}
                className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-900 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs font-sans">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">Standard Clause & Category:</span>
                <span className="font-bold font-mono text-indigo-600">
                  {selectedItem.standard_code} ({selectedItem.standard_category})
                </span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">Requirement Area / Test:</span>
                <span className="font-bold text-slate-900">{selectedItem.test_name}</span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">Source Traceability:</span>
                <span className="font-mono text-slate-700">{selectedItem.source_location || 'TRF Test Results Section'}</span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">Extracted TRF Evidence Result:</span>
                <span className="font-mono text-emerald-700 font-bold">
                  {selectedItem.observed_value} {selectedItem.unit !== 'N/A' ? selectedItem.unit : ''}
                </span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">TRF Reported Status:</span>
                <span className="font-mono font-bold text-slate-800">{selectedItem.trf_result || 'PASS'}</span>
              </div>

              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">System Evaluation Result:</span>
                <StatusBadge status={selectedItem.status} size="sm" />
              </div>

              <div className="pt-2 space-y-1">
                <span className="text-slate-800 font-bold font-mono">System Evaluation Rationale:</span>
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 leading-relaxed font-mono text-[11px]">
                  {selectedItem.reason}
                </div>
              </div>

              {selectedItem.status === 'NEEDS REVIEW' && (
                <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs font-medium">
                  <strong>Non-Blind Verification Note:</strong> The TRF result was flagged for human reviewer inspection because evidence is missing or baseline criteria could not be independently verified against internal standards KB.
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 text-right">
              <button
                onClick={() => setSelectedItem(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition cursor-pointer"
              >
                Close Traceability Drawer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
