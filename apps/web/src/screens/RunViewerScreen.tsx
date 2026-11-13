import React, { useState } from 'react';
import { RunTimeline } from '../components/RunTimeline';

export const RunViewerScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState("timeline");

  const simulatedEvents = [
    { node: "scout", status: "completed", tokens_used: 120 },
    { node: "analyst", status: "completed", tokens_used: 280, parallel_branch: true },
    { node: "risk_assessor", status: "completed", tokens_used: 310, parallel_branch: true },
    { node: "fit_matcher", status: "completed", tokens_used: 340, parallel_branch: true },
    { node: "decision_router", status: "completed", tokens_used: 80 },
    { node: "pricing", status: "completed", tokens_used: 220 },
    { node: "writer", status: "completed", tokens_used: 420 },
    { node: "verifier", status: "completed", tokens_used: 260 },
    { node: "critic", status: "completed", tokens_used: 240 },
    { node: "compliance", status: "completed", tokens_used: 210 }
  ];

  return (
    <div id="run-viewer-screen" className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Live Agent Run Viewer</h1>
          <p className="text-slate-400 text-xs mt-1">
            Real-time SSE telemetry streamed from LangGraph execution runtime.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab("timeline")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
              activeTab === "timeline" ? "bg-emerald-600 text-white" : "bg-slate-800 text-slate-400"
            }`}
          >
            Execution Graph
          </button>
          <button
            onClick={() => setActiveTab("raw_trace")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
              activeTab === "raw_trace" ? "bg-emerald-600 text-white" : "bg-slate-800 text-slate-400"
            }`}
          >
            Raw JSON Trace
          </button>
        </div>
      </div>

      {activeTab === "timeline" ? (
        <RunTimeline
          events={simulatedEvents}
          activeNode="approval_gate"
          totalTokens={2480}
          runStatus="waiting_approval"
        />
      ) : (
        <pre className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-emerald-400 overflow-x-auto">
          {JSON.stringify({
            run_id: "run-langgraph-stream-001",
            status: "waiting_approval",
            parallel_fan_out: ["analyst", "risk_assessor", "fit_matcher"],
            decision: "BID",
            fit_score: 0.88,
            risk_score: 0.12,
            claims_verified: 4,
            unsupported_claims_removed: 1,
            revisions: 0,
            total_tokens: 2480,
            p95_latency_s: 1.45
          }, null, 2)}
        </pre>
      )}
    </div>
  );
};
