import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Cpu, Play } from 'lucide-react';
import { documentApi, evaluationApi } from '../services/api';

export default function DocumentReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    documentApi.get(id)
      .then(res => setDoc(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <div className="p-8 text-center text-slate-400 font-mono text-xs">Loading document extraction details...</div>;
  }

  if (!doc) {
    return <div className="p-8 text-center text-rose-600 font-bold text-sm">Document record not found.</div>;
  }

  let extractedData = null;
  if (doc.extracted_data_json) {
    try {
      extractedData = JSON.parse(doc.extracted_data_json);
    } catch (e) {}
  }

  const handleRunEvaluation = async () => {
    setEvaluating(true);
    try {
      const res = await evaluationApi.run(doc.id);
      await evaluationApi.generateReport(res.data.id);
      navigate(`/evaluations/${res.data.id}`);
    } catch (err) {
      console.error(err);
      setEvaluating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Banner Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-indigo-600 font-bold">
            <span>DOC-ID: #{doc.id}</span>
            <span>•</span>
            <span className="uppercase">{doc.file_type} File</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 mt-1 font-sans">{doc.filename}</h1>
          <p className="text-xs text-slate-500 mt-1 font-mono">Uploaded: {new Date(doc.upload_date).toLocaleString()}</p>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={evaluating}
          className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/25 transition shrink-0 cursor-pointer"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>{evaluating ? "Evaluating..." : "Run Compliance Evaluation"}</span>
        </button>
      </div>

      {/* Extracted Metadata Overview */}
      {extractedData && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Device Metadata Card */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-3">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center gap-2">
              <Cpu className="w-4 h-4 text-indigo-600" />
              <span>Extracted Device Metadata</span>
            </h3>
            <div className="space-y-2 text-xs font-sans">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">Device Name:</span>
                <span className="font-bold text-slate-900">{extractedData.device?.name || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">Model:</span>
                <span className="font-bold text-indigo-600 font-mono">{extractedData.device?.model || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500 font-medium">Manufacturer:</span>
                <span className="font-bold text-slate-900">{extractedData.device?.manufacturer || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500 font-medium">Device Category:</span>
                <span className="font-bold text-indigo-600 font-mono">{extractedData.device?.device_type || 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* Standards Detected Card */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-3">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-600" />
              <span>Standards Detected</span>
            </h3>
            <div className="space-y-2">
              {extractedData.standards?.map((s, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                  <span className="font-bold text-slate-900">{s.name}</span>
                  <span className="font-mono text-indigo-600 font-semibold">{s.edition}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Extracted Test Parameters Table */}
      <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono">
            Extracted Test Parameters ({extractedData?.tests?.length || 0})
          </h3>
          <span className="text-[10px] font-mono font-bold text-slate-400">Parameter Ingestion Log</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-mono uppercase text-[10px] border-b border-slate-200">
              <tr>
                <th className="p-3.5 font-bold">Test Parameter</th>
                <th className="p-3.5 font-bold">Observed Result</th>
                <th className="p-3.5 font-bold">Unit</th>
                <th className="p-3.5 font-bold">Evidence / Technician Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {extractedData?.tests?.map((t, idx) => (
                <tr key={idx} className="hover:bg-slate-50/80 transition">
                  <td className="p-3.5 font-bold text-slate-900">{t.test_name}</td>
                  <td className="p-3.5 font-mono text-indigo-600 font-bold">{t.result !== null ? String(t.result) : 'MISSING'}</td>
                  <td className="p-3.5 font-mono text-slate-500">{t.unit || '-'}</td>
                  <td className="p-3.5 text-slate-600">{t.evidence || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
