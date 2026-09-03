import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  Loader2, 
  AlertCircle, 
  ArrowRight,
  Sparkles,
  Play,
  Download,
  ShieldCheck
} from 'lucide-react';
import { documentApi, evaluationApi, samplesApi } from '../services/api';

export default function UploadPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [stepIndex, setStepIndex] = useState(-1);
  const [errorMsg, setErrorMsg] = useState(null);
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [completedEval, setCompletedEval] = useState(null);
  const [samples, setSamples] = useState([]);
  const [runningSample, setRunningSample] = useState(null);

  useEffect(() => {
    samplesApi.list()
      .then(res => setSamples(res.data || []))
      .catch(err => console.error(err));
  }, []);

  const pipelineSteps = [
    "Reading document & verifying file structure",
    "Extracting medical device metadata & test values",
    "Identifying applicable IEC / ISO standard clauses",
    "Mapping extracted test evidence to requirement rules",
    "Executing deterministic evaluation matrix"
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    const ext = file.name.split('.').pop().toLowerCase();
    const allowed = ['pdf', 'csv', 'xlsx', 'xls', 'docx', 'doc'];
    if (!allowed.includes(ext)) {
      setErrorMsg(`Unsupported file type '.${ext}'. Supported formats: PDF, CSV, XLSX, DOCX`);
      return;
    }
    setErrorMsg(null);
    setSelectedFile(file);
  };

  const handleRunSampleDemo = async (filename) => {
    setRunningSample(filename);
    setUploading(true);
    setErrorMsg(null);
    setStepIndex(0);

    try {
      setStepIndex(1);
      await new Promise(r => setTimeout(r, 400));
      setStepIndex(2);
      await new Promise(r => setTimeout(r, 400));
      setStepIndex(3);
      await new Promise(r => setTimeout(r, 400));
      setStepIndex(4);
      
      const evalRes = await samplesApi.runSample(filename);
      const ev = evalRes.data;
      setCompletedEval(ev);

      await new Promise(r => setTimeout(r, 400));
      setStepIndex(5);
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to run demonstration TRF evaluation.");
      setUploading(false);
    } finally {
      setRunningSample(null);
    }
  };

  const startPipeline = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setErrorMsg(null);
    setStepIndex(0);

    try {
      // Step 1: Upload document
      const uploadRes = await documentApi.upload(selectedFile);
      const doc = uploadRes.data;
      setUploadedDoc(doc);
      await new Promise(r => setTimeout(r, 500));

      // Step 2: Extracting device data
      setStepIndex(1);
      await new Promise(r => setTimeout(r, 500));

      // Step 3: Identifying standards
      setStepIndex(2);
      await new Promise(r => setTimeout(r, 500));

      // Step 4: Mapping test evidence
      setStepIndex(3);
      await new Promise(r => setTimeout(r, 500));

      // Step 5: Evaluating results
      setStepIndex(4);
      const evalRes = await evaluationApi.run(doc.id);
      const ev = evalRes.data;
      setCompletedEval(ev);

      await new Promise(r => setTimeout(r, 500));
      setStepIndex(5);
    } catch (err) {
      console.error("Pipeline failed:", err);
      setErrorMsg(err.response?.data?.detail || "Document evaluation pipeline failed. Please verify document formatting.");
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center space-y-1">
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight font-sans">
          Upload Medical Device Test Report Form (TRF)
        </h1>
        <p className="text-xs text-slate-500 max-w-lg mx-auto leading-relaxed">
          Upload a TRF PDF to automatically identify the medical device, detect applicable IEC/ISO standards, and evaluate test evidence.
        </p>
      </div>

      {/* Main Upload Workspace Card */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-8 shadow-sm space-y-6">
        {!uploading && stepIndex === -1 ? (
          <>
            {/* Drag & Drop Target Zone */}
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
                dragActive
                  ? 'border-indigo-500 bg-indigo-50/50'
                  : selectedFile
                  ? 'border-emerald-500/80 bg-emerald-50/40'
                  : 'border-slate-300 hover:border-indigo-400 bg-slate-50/70 hover:bg-slate-50'
              }`}
            >
              <input
                type="file"
                id="file-upload"
                accept=".pdf,.csv,.xlsx,.xls,.docx,.doc"
                onChange={handleFileChange}
                className="hidden"
              />

              <div className="flex flex-col items-center justify-center space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sky-500 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-md shadow-indigo-500/20 text-white">
                  <UploadCloud className="w-8 h-8" />
                </div>

                {selectedFile ? (
                  <div className="space-y-1">
                    <div className="text-base font-bold text-emerald-700 flex items-center justify-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                      <span>{selectedFile.name}</span>
                    </div>
                    <p className="text-xs font-mono text-slate-500">
                      {(selectedFile.size / 1024).toFixed(1)} KB • {selectedFile.name.split('.').pop().toUpperCase()} Format Selected
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="text-sm font-semibold text-slate-800">
                      Drag and drop your TRF document here, or{' '}
                      <label htmlFor="file-upload" className="text-indigo-600 hover:text-indigo-700 cursor-pointer underline font-bold">
                        browse files
                      </label>
                    </div>
                    <p className="text-xs text-slate-500 font-mono">
                      Supported formats: PDF, CSV, XLSX, DOCX
                    </p>
                  </>
                )}
              </div>
            </div>

            {errorMsg && (
              <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2 font-medium">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-3 pt-2">
              {selectedFile && (
                <button
                  onClick={() => setSelectedFile(null)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
                >
                  Clear Selection
                </button>
              )}
              <button
                disabled={!selectedFile}
                onClick={startPipeline}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-xs shadow-md transition ${
                  selectedFile
                    ? 'bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white shadow-indigo-600/25 cursor-pointer'
                    : 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200'
                }`}
              >
                <Sparkles className="w-4 h-4" />
                <span>Evaluate TRF</span>
              </button>
            </div>
          </>
        ) : (
          /* 5-Stage Processing Pipeline Visualization */
          <div className="py-6 space-y-8">
            <div className="text-center space-y-1.5">
              <h2 className="text-xl font-extrabold text-slate-900 font-sans">
                {stepIndex < 5 ? "Processing Test Report Form..." : "Evaluation Complete!"}
              </h2>
              {stepIndex === 5 && completedEval && (
                <div className="inline-block px-3.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-bold font-mono shadow-2xs">
                  Overall Status: {completedEval.overall_status}
                </div>
              )}
            </div>

            {/* 5 Stepper Items */}
            <div className="space-y-3 max-w-md mx-auto">
              {pipelineSteps.map((stepName, idx) => {
                const isCurrent = idx === stepIndex;
                const isDone = idx < stepIndex;

                return (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono transition">
                    <div className="flex items-center gap-3">
                      <span className="text-slate-400 font-bold">{idx + 1}.</span>
                      <span className={isDone ? 'text-slate-900 font-bold' : isCurrent ? 'text-indigo-600 font-extrabold' : 'text-slate-500'}>
                        {stepName}
                      </span>
                    </div>

                    <div>
                      {isDone ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      ) : isCurrent ? (
                        <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
                      ) : (
                        <span className="text-slate-300">-</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {stepIndex === 5 && completedEval && (
              <div className="flex justify-center gap-4 pt-4 border-t border-slate-100">
                <button
                  onClick={() => navigate(`/evaluations/${completedEval.id}`)}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/25 transition cursor-pointer"
                >
                  <span>View Detailed Evaluation Report</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Demo TRF Quick Selector Section */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2 font-mono">
          <FileText className="w-4 h-4 text-indigo-600" />
          <span>Or Select a Preloaded Synthetic TRF Demonstration (15 Device Categories)</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {samples.map((s, i) => (
            <button
              key={i}
              onClick={() => handleRunSampleDemo(s.filename)}
              disabled={uploading}
              className="flex items-center justify-between p-3 rounded-xl bg-slate-50/80 hover:bg-indigo-50/50 border border-slate-200 hover:border-indigo-300 text-left transition group cursor-pointer"
            >
              <div className="overflow-hidden pr-2">
                <div className="text-xs font-bold text-slate-900 group-hover:text-indigo-700 truncate">{s.label}</div>
                <div className="text-[10px] font-mono text-slate-500 truncate">{s.filename}</div>
              </div>
              <Play className="w-3.5 h-3.5 text-indigo-600 group-hover:scale-110 transition shrink-0" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
