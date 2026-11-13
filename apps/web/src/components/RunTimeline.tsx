import React from 'react';

interface NodeEvent {
  node: string;
  status: string;
  tokens_used: number;
  parallel_branch?: boolean;
}

interface RunTimelineProps {
  events: NodeEvent[];
  activeNode?: string;
  totalTokens: number;
  runStatus: string;
}

export const RunTimeline: React.FC<RunTimelineProps> = ({
  events,
  activeNode,
  totalTokens,
  runStatus
}) => {
  const allNodes = [
    { id: "scout", label: "Scout Agent" },
    { id: "analyst", label: "Job Analyst (Parallel)", parallel: true },
    { id: "risk_assessor", label: "Risk Assessor (Parallel)", parallel: true },
    { id: "fit_matcher", label: "Fit Matcher (Parallel)", parallel: true },
    { id: "decision_router", label: "Decision Router" },
    { id: "pricing", label: "Pricing Strategist" },
    { id: "writer", label: "Proposal Writer" },
    { id: "verifier", label: "Claim Verifier" },
    { id: "critic", label: "Critic (Max 2 Loops)" },
    { id: "compliance", label: "Compliance Guard" },
    { id: "approval_gate", label: "Human Approval Gate" },
    { id: "marketplace_submit", label: "Marketplace Submitter" }
  ];

  return (
    <div id="run-timeline" className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
          <h3 className="text-sm font-bold text-slate-200">Live Multi-Agent Graph Progress</h3>
        </div>
        <div className="text-xs text-slate-400">
          Status: <span className="font-semibold text-emerald-400 uppercase">{runStatus}</span> | Tokens: <span className="font-mono text-slate-200">{totalTokens}</span>
        </div>
      </div>

      <div className="space-y-2">
        {allNodes.map((n, idx) => {
          const isDone = events.some(e => e.node === n.id);
          const isActive = activeNode === n.id;
          
          return (
            <div 
              key={n.id}
              className={`flex items-center justify-between p-2 rounded-lg text-xs transition ${
                isActive 
                  ? "bg-sky-500/10 border border-sky-500/40 text-sky-300"
                  : isDone
                  ? "bg-slate-800/40 border border-emerald-500/30 text-slate-300"
                  : "bg-slate-950/40 border border-slate-800/60 text-slate-500"
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                  isDone ? "bg-emerald-600 text-white" : isActive ? "bg-sky-500 text-white animate-pulse" : "bg-slate-800 text-slate-400"
                }`}>
                  {isDone ? "✓" : idx + 1}
                </span>
                <span className="font-medium">{n.label}</span>
              </div>
              <div className="font-mono text-[11px]">
                {isDone ? (
                  <span className="text-emerald-400 font-semibold">Completed</span>
                ) : isActive ? (
                  <span className="text-sky-400 font-semibold animate-pulse">Running...</span>
                ) : (
                  <span className="text-slate-600">Pending</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
