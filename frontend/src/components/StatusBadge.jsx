import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Clock, MinusCircle, HelpCircle } from 'lucide-react';

export default function StatusBadge({ status, size = 'normal' }) {
  const st = (status || '').toUpperCase();

  let bgClass = 'bg-amber-50 text-amber-700 border-amber-200';
  let icon = <AlertTriangle className="w-3.5 h-3.5" />;
  let label = st || 'NEEDS REVIEW';

  if (st === 'PASS' || st === 'PASSED' || st === 'APPROVED' || st === 'CERTIFIED') {
    bgClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    icon = <CheckCircle2 className="w-3.5 h-3.5" />;
    label = (st === 'APPROVED' || st === 'CERTIFIED') ? 'CERTIFIED & APPROVED' : 'PASS';
  } else if (st === 'FAIL' || st === 'FAILED' || st === 'REJECTED' || st === 'RETURNED') {
    bgClass = 'bg-rose-50 text-rose-700 border-rose-200';
    icon = <XCircle className="w-3.5 h-3.5" />;
    label = (st === 'REJECTED' || st === 'RETURNED') ? 'RETURNED TO REVIEWER' : 'FAIL';
  } else if (st === 'NEEDS_MORE_INFO' || st === 'INFO_REQUESTED') {
    bgClass = 'bg-amber-50 text-amber-700 border-amber-200';
    icon = <HelpCircle className="w-3.5 h-3.5" />;
    label = 'INFO REQUESTED';
  } else if (st === 'NOT APPLICABLE' || st === 'N/A' || st === 'NOT_APPLICABLE') {
    bgClass = 'bg-slate-100 text-slate-600 border-slate-200';
    icon = <MinusCircle className="w-3.5 h-3.5" />;
    label = 'NOT APPLICABLE';
  } else if (st === 'PENDING_REVIEW' || st === 'PENDING') {
    bgClass = 'bg-sky-50 text-sky-700 border-sky-200';
    icon = <Clock className="w-3.5 h-3.5" />;
    label = 'PENDING CERTIFIER DECISION';
  }

  const px = size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-3 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full border shadow-2xs ${px} ${bgClass}`}>
      {icon}
      <span>{label}</span>
    </span>
  );
}
