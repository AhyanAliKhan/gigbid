import React, { useState } from 'react';

interface OnboardingScreenProps {
  currentPersona: string;
  onSelectPersona: (personaId: string) => void;
  onContinue: () => void;
}

export const OnboardingScreen: React.FC<OnboardingScreenProps> = ({
  currentPersona,
  onSelectPersona,
  onContinue
}) => {
  const [hourlyRate, setHourlyRate] = useState(85);
  const [weeklyBudget, setWeeklyBudget] = useState(120);
  const [upworkConnected, setUpworkConnected] = useState(false);

  const personas = [
    {
      id: "alex_chen_aiml",
      name: "Alex Chen",
      domain: "AI/ML Engineer",
      rate: "$85/hr",
      desc: "LLM fine-tuning, RAG systems, vLLM inference, PyTorch & agentic workflows. 20 case studies, 150 past proposals."
    },
    {
      id: "sarah_jenkins_fullstack",
      name: "Sarah Jenkins",
      domain: "Full-Stack Web Architect",
      rate: "$75/hr",
      desc: "Next.js, React, TypeScript, FastAPI, PostgreSQL & cloud microservices. 20 case studies, 150 past proposals."
    },
    {
      id: "marcus_vance_analyst",
      name: "Marcus Vance",
      domain: "Lead Data Analyst & BI",
      rate: "$65/hr",
      desc: "Snowflake, dbt, PowerBI, Tableau, Python ETL automation & cohort modeling. 20 case studies, 150 past proposals."
    }
  ];

  return (
    <div id="onboarding-screen" className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold text-slate-100 mb-2">Welcome to GigBid</h1>
        <p className="text-slate-400 text-sm max-w-xl mx-auto">
          The multi-agent freelancer copilot. Ground proposals in verified portfolio evidence,
          defend against scam posts, and approve every proposal before submission.
        </p>
      </div>

      {/* Persona Selection */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3">
          1. Choose Freelancer Persona or Profile
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {personas.map((p) => {
            const isSelected = currentPersona === p.id;
            return (
              <div
                key={p.id}
                id={`persona-card-${p.id}`}
                onClick={() => onSelectPersona(p.id)}
                className={`cursor-pointer rounded-xl p-5 border transition ${
                  isSelected
                    ? "bg-emerald-950/30 border-emerald-500 shadow-lg shadow-emerald-500/10"
                    : "bg-slate-800/60 border-slate-700 hover:border-slate-600"
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-slate-100">{p.name}</h3>
                  <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-mono font-medium">
                    {p.rate}
                  </span>
                </div>
                <div className="text-xs font-medium text-emerald-400 mb-2">{p.domain}</div>
                <p className="text-xs text-slate-400 leading-relaxed">{p.desc}</p>
                {isSelected && (
                  <div className="mt-3 text-[11px] text-emerald-400 font-semibold flex items-center space-x-1">
                    <span>✓</span>
                    <span>Active Selected Persona</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Connected Marketplace Accounts */}
      <div className="mb-8 bg-slate-800/50 border border-slate-700/80 rounded-xl p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4">
          2. Connect Marketplace Accounts & Adapters
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-900/60 border border-emerald-500/40 rounded-lg p-4 flex items-center justify-between">
            <div>
              <div className="font-bold text-slate-200 text-sm">GigSim Marketplace Simulator</div>
              <div className="text-xs text-slate-400">REST API & Grading Stand-in (1,500 historical jobs)</div>
            </div>
            <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2.5 py-1 rounded-full font-medium">
              Connected (Local)
            </span>
          </div>

          <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-4 flex items-center justify-between">
            <div>
              <div className="font-bold text-slate-200 text-sm">Upwork Official MCP Server</div>
              <div className="text-xs text-slate-400">Streamable HTTP with OAuth 2.1</div>
            </div>
            <button
              id="connect-upwork-btn"
              onClick={() => setUpworkConnected(!upworkConnected)}
              className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition ${
                upworkConnected
                  ? "bg-emerald-600 text-white"
                  : "bg-slate-700 hover:bg-slate-600 text-slate-200"
              }`}
            >
              {upworkConnected ? "OAuth Active" : "Connect Upwork"}
            </button>
          </div>
        </div>
      </div>

      {/* Rate Floor & Budget Settings */}
      <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-800/50 border border-slate-700/80 rounded-xl p-5">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Freelancer Hourly Rate Floor ($/hr)
          </label>
          <input
            id="hourly-rate-input"
            type="number"
            value={hourlyRate}
            onChange={(e) => setHourlyRate(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 font-mono"
          />
        </div>

        <div className="bg-slate-800/50 border border-slate-700/80 rounded-xl p-5">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Weekly Connects Budget
          </label>
          <input
            id="weekly-budget-input"
            type="number"
            value={weeklyBudget}
            onChange={(e) => setWeeklyBudget(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 font-mono"
          />
        </div>
      </div>

      <div className="text-center">
        <button
          id="finish-onboarding-btn"
          onClick={onContinue}
          className="px-8 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/20 text-sm transition"
        >
          Launch GigBid Discovery Feed →
        </button>
      </div>
    </div>
  );
};
