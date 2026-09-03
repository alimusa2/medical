import React from 'react';

export default function ConfidenceBadge({ confidence }) {
  const conf = (confidence || 'HIGH').toUpperCase();

  let color = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  if (conf === 'MEDIUM') {
    color = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  } else if (conf === 'LOW') {
    color = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
  }

  return (
    <span className={`inline-flex items-center text-[10px] font-mono px-2 py-0.5 rounded border ${color}`}>
      Conf: {conf}
    </span>
  );
}
