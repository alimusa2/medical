import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileCheck, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  FileText, 
  Download, 
  ArrowRight,
  Upload,
  RefreshCw,
  Play,
  Layers,
  Heart,
  Activity,
  Tv,
  Droplet,
  Syringe,
  Wind,
  Zap,
  Radio,
  Waves,
  Maximize,
  Sun,
  Microscope,
  ShieldCheck
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

import MetricsCard from '../components/MetricsCard';
import StatusBadge from '../components/StatusBadge';
import { evaluationApi, documentApi, samplesApi } from '../services/api';

export default function Dashboard() {
  const [evaluations, setEvaluations] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [samples, setSamples] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningSample, setRunningSample] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [evalRes, docRes, sampleRes] = await Promise.all([
        evaluationApi.list(),
        documentApi.list(),
        samplesApi.list()
      ]);
      setEvaluations(evalRes.data || []);
      setDocuments(docRes.data || []);
      setSamples(sampleRes.data || []);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunSample = async (filename) => {
    setRunningSample(filename);
    try {
      await samplesApi.runSample(filename);
      await loadData();
    } catch (err) {
      console.error("Error running sample evaluation:", err);
    } finally {
      setRunningSample(null);
    }
  };

  const totalEvals = evaluations.length;
  const passedEvals = evaluations.filter(e => e.overall_status === 'PASS').length;
  const failedEvals = evaluations.filter(e => e.overall_status === 'FAIL').length;
  const needsReviewEvals = evaluations.filter(e => e.overall_status === 'NEEDS REVIEW').length;

  const pieData = [
    { name: 'PASS', value: passedEvals, color: '#10b981' },
    { name: 'FAIL', value: failedEvals, color: '#f43f5e' },
    { name: 'NEEDS REVIEW', value: needsReviewEvals, color: '#f59e0b' },
  ];

  // Group evaluations by device category
  const categoryCounts = {};
  evaluations.forEach(e => {
    const cat = e.device_type_name || 'Medical Equipment';
    categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
  });

  const categoryData = Object.keys(categoryCounts).map(cat => ({
    category: cat.length > 15 ? cat.substring(0, 15) + '...' : cat,
    count: categoryCounts[cat]
  }));

  // Icon mapping for 15 device categories
  const getDeviceIcon = (filename = '') => {
    const fn = filename.toLowerCase();
    if (fn.includes('blood_pressure')) return { icon: Heart, bg: 'bg-purple-100 text-purple-600', btn: 'bg-purple-600 hover:bg-purple-500 text-white' };
    if (fn.includes('ecg')) return { icon: Activity, bg: 'bg-teal-100 text-teal-600', btn: 'bg-teal-600 hover:bg-teal-500 text-white' };
    if (fn.includes('patient_monitor')) return { icon: Tv, bg: 'bg-sky-100 text-sky-600', btn: 'bg-sky-600 hover:bg-sky-500 text-white' };
    if (fn.includes('infusion_pump')) return { icon: Droplet, bg: 'bg-emerald-100 text-emerald-600', btn: 'bg-emerald-600 hover:bg-emerald-500 text-white' };
    if (fn.includes('syringe_pump')) return { icon: Syringe, bg: 'bg-amber-100 text-amber-600', btn: 'bg-amber-600 hover:bg-amber-500 text-white' };
    if (fn.includes('ventilator')) return { icon: Wind, bg: 'bg-rose-100 text-rose-600', btn: 'bg-rose-600 hover:bg-rose-500 text-white' };
    if (fn.includes('defibrillator')) return { icon: Zap, bg: 'bg-red-100 text-red-600', btn: 'bg-red-600 hover:bg-red-500 text-white' };
    if (fn.includes('pulse_oximeter')) return { icon: Activity, bg: 'bg-indigo-100 text-indigo-600', btn: 'bg-indigo-600 hover:bg-indigo-500 text-white' };
    if (fn.includes('electrosurgical')) return { icon: Zap, bg: 'bg-orange-100 text-orange-600', btn: 'bg-orange-600 hover:bg-orange-500 text-white' };
    if (fn.includes('x-ray')) return { icon: Radio, bg: 'bg-purple-100 text-purple-600', btn: 'bg-purple-600 hover:bg-purple-500 text-white' };
    if (fn.includes('ultrasound')) return { icon: Waves, bg: 'bg-cyan-100 text-cyan-600', btn: 'bg-cyan-600 hover:bg-cyan-500 text-white' };
    if (fn.includes('operating_table')) return { icon: Maximize, bg: 'bg-slate-100 text-slate-600', btn: 'bg-slate-700 hover:bg-slate-600 text-white' };
    if (fn.includes('treatment_light')) return { icon: Sun, bg: 'bg-yellow-100 text-yellow-600', btn: 'bg-yellow-600 hover:bg-yellow-500 text-white' };
    if (fn.includes('laboratory')) return { icon: Microscope, bg: 'bg-emerald-100 text-emerald-600', btn: 'bg-emerald-600 hover:bg-emerald-500 text-white' };
    return { icon: ShieldCheck, bg: 'bg-indigo-100 text-indigo-600', btn: 'bg-indigo-600 hover:bg-indigo-500 text-white' };
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Hero Primary Section */}
      <div className="bg-gradient-to-r from-indigo-100/70 via-violet-50/60 to-blue-50/80 border border-indigo-100/90 rounded-2xl shadow-sm p-6 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="px-3 py-1 rounded-full text-[11px] font-mono font-bold bg-indigo-100/90 text-indigo-700 border border-indigo-200/70 shadow-2xs">
              DECISION-SUPPORT PROTOTYPE
            </span>
            <span className="text-xs text-slate-600 font-semibold font-mono">15 Medical Device Categories</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight font-sans">
            TRF Evaluation Dashboard
          </h1>
          <p className="text-xs text-slate-600 mt-1 max-w-xl leading-relaxed">
            Automated medical device test report form extraction, standards mapping, and preliminary evaluation.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button 
            onClick={loadData} 
            className="p-2.5 rounded-xl bg-white border border-slate-200/90 hover:bg-slate-50 text-slate-700 transition shadow-xs cursor-pointer"
            title="Refresh dashboard metrics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <Link
            to="/upload"
            className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold rounded-xl px-5 py-2.5 shadow-lg shadow-indigo-600/25 transition-all transform hover:-translate-y-0.5 flex items-center gap-2 text-xs"
          >
            <Upload className="w-4 h-4" />
            <span>Upload TRF Document</span>
          </Link>
        </div>
      </div>

      {/* KPI Metrics Grid (5 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricsCard title="Total TRF Evaluations" value={totalEvals} icon={FileCheck} color="purple" subtext="Preloaded & Uploaded TRFs" />
        <MetricsCard title="Passed" value={passedEvals} icon={CheckCircle2} color="emerald" subtext="Satisfied criteria" />
        <MetricsCard title="Failed" value={failedEvals} icon={XCircle} color="rose" subtext="Exceeded thresholds" />
        <MetricsCard title="Needs Review" value={needsReviewEvals} icon={AlertTriangle} color="amber" subtext="Evidence missing / incomplete" />
        <MetricsCard title="Processed Documents" value={documents.length || totalEvals} icon={FileText} color="sky" subtext="PDF, CSV, XLSX, DOCX" />
      </div>

      {/* Demonstration Synthetic TRF Library (15 Medical Devices Grid) */}
      <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <div>
            <h3 className="font-extrabold text-slate-900 text-base flex items-center gap-2 font-sans">
              <Download className="w-4 h-4 text-indigo-600" />
              <span>Demonstration Synthetic TRF Library (15 Medical Devices)</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Click any device demo file to download synthetic TRF or execute 1-click evaluation immediately.
            </p>
          </div>
          <span className="text-[10px] font-mono font-bold text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200 self-start sm:self-auto uppercase tracking-wide">
            SYNTHETIC DEMO DATA ONLY
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {samples.map((s, idx) => {
            const devStyle = getDeviceIcon(s.filename);
            const DevIcon = devStyle.icon;

            return (
              <div
                key={idx}
                className="bg-slate-50/70 hover:bg-white border border-slate-200/80 hover:border-slate-300 rounded-xl p-3.5 transition-all shadow-2xs hover:shadow-sm flex items-center justify-between gap-3"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className={`w-9 h-9 rounded-xl ${devStyle.bg} flex items-center justify-center shrink-0 border border-slate-200/50 shadow-2xs`}>
                    <DevIcon className="w-4 h-4" />
                  </div>
                  <div className="overflow-hidden">
                    <div className="font-bold text-slate-900 text-xs truncate leading-snug">{s.label}</div>
                    <div className="text-[10px] font-mono text-slate-400 truncate mt-0.5">{s.filename}</div>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    onClick={() => handleRunSample(s.filename)}
                    disabled={runningSample === s.filename}
                    className={`px-3 py-1.5 rounded-lg ${devStyle.btn} transition text-xs font-bold shadow-xs flex items-center gap-1 cursor-pointer`}
                    title="Execute automated evaluation"
                  >
                    <Play className={`w-3 h-3 ${runningSample === s.filename ? 'animate-spin' : ''}`} />
                    <span>{runningSample === s.filename ? 'Evaluating...' : 'Evaluate'}</span>
                  </button>

                  <a
                    href={s.download_url}
                    download={s.filename}
                    className="p-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-600 hover:text-slate-900 transition shadow-2xs"
                    title="Download synthetic TRF PDF"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-3">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider font-mono flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-600" />
            <span>Evaluation Status Distribution</span>
          </h3>
          <div className="h-56 flex items-center justify-center">
            {totalEvals > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                    itemStyle={{ color: '#0f172a', fontWeight: 'bold', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-slate-400 text-xs">
                No evaluation data yet. Upload a TRF file to see metrics.
              </div>
            )}
          </div>
          <div className="flex justify-center gap-6 text-xs text-slate-600 font-medium">
            <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> PASS</div>
            <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> FAIL</div>
            <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> NEEDS REVIEW</div>
          </div>
        </div>

        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-sm space-y-3">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider font-mono flex items-center gap-2">
            <FileText className="w-4 h-4 text-indigo-600" />
            <span>Device Category Breakdown (15 Supported)</span>
          </h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="category" stroke="#94a3b8" fontSize={10} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                  itemStyle={{ color: '#0f172a', fontWeight: 'bold', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#4f46e5" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Evaluations Summary Table */}
      <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-extrabold text-slate-900 tracking-tight font-sans">TRF Evaluation Summary Table</h3>
            <p className="text-xs text-slate-500 mt-0.5">Structured evaluation breakdown across all medical device categories</p>
          </div>
          <Link to="/evaluations" className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1 font-bold">
            View All <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-500 font-mono uppercase text-[10px] border-b border-slate-200">
              <tr>
                <th className="p-3.5 font-bold">Device Name & Model</th>
                <th className="p-3.5 font-bold">Device Category</th>
                <th className="p-3.5 font-bold">Safety Pathway</th>
                <th className="p-3.5 text-center font-bold">Passed / Failed / Review / N/A</th>
                <th className="p-3.5 font-bold">Overall Status</th>
                <th className="p-3.5 font-bold">Certifier Status</th>
                <th className="p-3.5 text-right font-bold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {evaluations.length > 0 ? (
                evaluations.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-50/80 transition">
                    <td className="p-3.5 font-semibold text-slate-900">
                      <div>{ev.device_model || 'Medical Device'}</div>
                      <div className="text-[10px] font-mono text-slate-400">{ev.manufacturer || 'Demo Manufacturer'}</div>
                    </td>
                    <td className="p-3.5 font-mono text-indigo-600 font-semibold">{ev.device_type_name || 'Medical Equipment'}</td>
                    <td className="p-3.5 font-mono">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        ev.pathway === 'IVD / Laboratory Equipment' 
                          ? 'bg-purple-50 text-purple-700 border border-purple-200' 
                          : 'bg-sky-50 text-sky-700 border border-sky-200'
                      }`}>
                        {ev.pathway || 'ME Equipment'}
                      </span>
                    </td>
                    <td className="p-3.5 text-center font-mono font-bold">
                      <span className="text-emerald-600">{ev.passed_tests} P</span>
                      <span className="text-slate-300 mx-1">/</span>
                      <span className="text-rose-600">{ev.failed_tests} F</span>
                      <span className="text-slate-300 mx-1">/</span>
                      <span className="text-amber-600">{ev.needs_review_tests} R</span>
                      <span className="text-slate-300 mx-1">/</span>
                      <span className="text-slate-400">{ev.not_applicable_tests || 0} NA</span>
                    </td>
                    <td className="p-3.5">
                      <StatusBadge status={ev.overall_status} size="sm" />
                    </td>
                    <td className="p-3.5">
                      <StatusBadge status={ev.certifier_status} size="sm" />
                    </td>
                    <td className="p-3.5 text-right">
                      <Link
                        to={`/evaluations/${ev.id}`}
                        className="px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-600 font-bold transition inline-flex items-center gap-1 text-xs"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-400">
                    No evaluation records found.
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
