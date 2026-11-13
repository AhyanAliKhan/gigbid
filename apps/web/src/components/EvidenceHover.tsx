import React, { useState } from 'react';

interface EvidenceHoverProps {
  evidenceId: string;
  title: string;
  outcome: string;
  skills?: string[];
  metrics?: string;
}

export const EvidenceHover: React.FC<EvidenceHoverProps> = ({
  evidenceId,
  title,
  outcome,
  skills = [],
  metrics = "Reduced p95 latency by 48%, 5/5 client review"
}) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <span 
      className="relative inline-block"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <span className="cursor-help bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-xs px-2 py-0.5 rounded font-mono font-semibold transition hover:bg-emerald-500/30">
        [{evidenceId}]
      </span>
      {showTooltip && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-72 p-3 bg-slate-800 border border-emerald-500/50 rounded-lg shadow-xl text-left text-xs pointer-events-none">
          <div className="font-bold text-slate-100 mb-1">{title}</div>
          <div className="text-emerald-400 font-medium mb-1.5">{metrics}</div>
          <div className="text-slate-400 mb-2">Verified Outcome: {outcome}</div>
          {skills.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {skills.map((s, idx) => (
                <span key={idx} className="bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded text-[10px]">
                  {s}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </span>
  );
};
