import React, { useState } from 'react';
import { AlertCircle, X, ShieldAlert } from 'lucide-react';

export default function DisclaimerBanner() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="bg-emerald-50/90 border-b border-emerald-200/80 px-4 py-2.5 text-emerald-950 text-xs shadow-sm flex items-center justify-between">
      <div className="flex items-center gap-3 max-w-7xl mx-auto w-full">
        <div className="w-6 h-6 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-600 shrink-0">
          <ShieldAlert className="w-4 h-4" />
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
          <span className="font-bold text-emerald-900 uppercase tracking-wide">
            DEMONSTRATION DATA ONLY:
          </span>
          <span className="text-emerald-800">
            Final technical review and certification remain the sole responsibility of qualified human personnel.
          </span>
          <span className="text-emerald-600 text-[11px] font-mono sm:border-l sm:border-emerald-200 sm:pl-2">
            Synthetic requirements & TRFs used for proof-of-concept testing.
          </span>
        </div>
      </div>
      <button
        onClick={() => setDismissed(true)}
        className="text-emerald-600 hover:text-emerald-950 p-1 rounded hover:bg-emerald-100/60 transition"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
