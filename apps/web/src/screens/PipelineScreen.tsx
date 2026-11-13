import React from 'react';

export const PipelineScreen: React.FC = () => {
  const columns = [
    {
      id: "drafted",
      title: "Drafted",
      cards: [
        { id: "c-01", job: "vLLM Inference Cluster", client: "Enterprise AI Labs", bid: 650, date: "Today" }
      ]
    },
    {
      id: "submitted",
      title: "Submitted",
      cards: [
        { id: "c-02", job: "RAG Pipeline Hybrid Search", client: "Fintech Growth Co", bid: 850, date: "Yesterday" }
      ]
    },
    {
      id: "viewed",
      title: "Viewed",
      cards: [
        { id: "c-03", job: "Next.js SaaS Dashboard", client: "Cloud Ventures", bid: 720, date: "2d ago" }
      ]
    },
    {
      id: "replied",
      title: "Replied",
      cards: [
        { id: "c-04", job: "FastAPI Async Microservices", client: "SaaS Scale Group", bid: 600, date: "3d ago" }
      ]
    },
    {
      id: "interview",
      title: "Interview",
      cards: [
        { id: "c-05", job: "LangGraph Multi-Agent Architecture", client: "Autonomous Corp", bid: 1500, date: "Tomorrow 15:00 UTC" }
      ]
    },
    {
      id: "hired",
      title: "Hired",
      cards: [
        { id: "c-06", job: "Customer Churn Classifier Baseline", client: "E-Commerce Inc", bid: 2200, date: "Active Contract" }
      ]
    },
    {
      id: "lost",
      title: "Lost",
      cards: [
        { id: "c-07", job: "Legacy Script Maintenance", client: "Budget Co", bid: 350, date: "Client chose lower rate" }
      ]
    }
  ];

  return (
    <div id="pipeline-screen" className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Proposal Pipeline Board</h1>
        <p className="text-slate-400 text-xs mt-1">
          Real-time Kanban lifecycle synchronized with marketplace webhook events.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {columns.map((col) => (
          <div key={col.id} className="bg-slate-900/60 border border-slate-800 rounded-xl p-3 flex flex-col min-h-[450px]">
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">{col.title}</span>
              <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded-full font-mono">
                {col.cards.length}
              </span>
            </div>

            <div className="space-y-2 flex-1">
              {col.cards.map((c) => (
                <div key={c.id} className="bg-slate-800/80 border border-slate-700/80 hover:border-slate-600 rounded-lg p-2.5 shadow transition">
                  <div className="text-xs font-bold text-slate-200 mb-1">{c.job}</div>
                  <div className="text-[11px] text-slate-400 mb-2">{c.client}</div>
                  <div className="flex items-center justify-between text-[11px] pt-1.5 border-t border-slate-700/50">
                    <span className="font-mono text-emerald-400 font-semibold">${c.bid}</span>
                    <span className="text-slate-500 text-[10px]">{c.date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
