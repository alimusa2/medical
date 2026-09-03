import React from 'react';

export default function MetricsCard({ title, value, icon: Icon, color = 'sky', subtext }) {
  const colorSchemes = {
    purple: {
      cardBg: 'bg-purple-50/90 border-purple-100/90',
      iconBg: 'bg-purple-100 text-purple-600 border-purple-200/60',
      titleColor: 'text-purple-900',
      subtextColor: 'text-purple-700',
      sparkline: 'stroke-purple-500',
      gradientStart: '#c084fc',
      gradientEnd: '#9333ea'
    },
    emerald: {
      cardBg: 'bg-emerald-50/90 border-emerald-100/90',
      iconBg: 'bg-emerald-100 text-emerald-600 border-emerald-200/60',
      titleColor: 'text-emerald-900',
      subtextColor: 'text-emerald-700',
      sparkline: 'stroke-emerald-500',
      gradientStart: '#34d399',
      gradientEnd: '#059669'
    },
    rose: {
      cardBg: 'bg-rose-50/90 border-rose-100/90',
      iconBg: 'bg-rose-100 text-rose-600 border-rose-200/60',
      titleColor: 'text-rose-900',
      subtextColor: 'text-rose-700',
      sparkline: 'stroke-rose-500',
      gradientStart: '#f87171',
      gradientEnd: '#dc2626'
    },
    amber: {
      cardBg: 'bg-amber-50/90 border-amber-100/90',
      iconBg: 'bg-amber-100 text-amber-600 border-amber-200/60',
      titleColor: 'text-amber-900',
      subtextColor: 'text-amber-700',
      sparkline: 'stroke-amber-500',
      gradientStart: '#fbbf24',
      gradientEnd: '#d97706'
    },
    sky: {
      cardBg: 'bg-sky-50/90 border-sky-100/90',
      iconBg: 'bg-sky-100 text-sky-600 border-sky-200/60',
      titleColor: 'text-sky-900',
      subtextColor: 'text-sky-700',
      sparkline: 'stroke-sky-500',
      gradientStart: '#38bdf8',
      gradientEnd: '#0284c7'
    },
    indigo: {
      cardBg: 'bg-indigo-50/90 border-indigo-100/90',
      iconBg: 'bg-indigo-100 text-indigo-600 border-indigo-200/60',
      titleColor: 'text-indigo-900',
      subtextColor: 'text-indigo-700',
      sparkline: 'stroke-indigo-500',
      gradientStart: '#818cf8',
      gradientEnd: '#4f46e5'
    }
  };

  const scheme = colorSchemes[color] || colorSchemes.sky;

  return (
    <div className={`p-4 rounded-2xl border ${scheme.cardBg} shadow-sm flex flex-col justify-between relative overflow-hidden transition-all hover:shadow-md hover:-translate-y-0.5`}>
      {/* Card Header: Icon + Title */}
      <div className="flex items-center gap-3">
        {Icon && (
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center border ${scheme.iconBg} shrink-0 shadow-xs`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
        <span className={`text-[11px] font-bold uppercase tracking-wider font-mono leading-tight ${scheme.titleColor}`}>
          {title}
        </span>
      </div>

      {/* Main Metric Value & Subtext */}
      <div className="mt-3.5 z-10">
        <div className="text-3xl font-extrabold text-slate-900 tracking-tight font-sans">
          {value}
        </div>
        {subtext && (
          <div className={`text-[11px] font-medium mt-0.5 ${scheme.subtextColor}`}>
            {subtext}
          </div>
        )}
      </div>

      {/* SVG Trend Sparkline Wave */}
      <div className="mt-2 pt-1 w-full h-8 overflow-hidden">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 120 30" fill="none" preserveAspectRatio="none">
          <path
            d="M0 20 C 20 28, 40 10, 60 18 C 80 25, 100 8, 120 15"
            className={`${scheme.sparkline} fill-none`}
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        </svg>
      </div>
    </div>
  );
}
