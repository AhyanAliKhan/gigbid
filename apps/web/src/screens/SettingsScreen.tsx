import React, { useState } from 'react';

export const SettingsScreen: React.FC = () => {
  const [autonomy, setAutonomy] = useState("semi_autonomous");
  const [rateFloor, setRateFloor] = useState(40);
  const [weeklyConnects, setWeeklyConnects] = useState(120);

  const [memoryRules, setMemoryRules] = useState([
    {
      id: "style-001",
      rule: "Never open with formal greetings like 'Dear Sir/Madam' or 'I am passionate'. Start immediately with technical deliverables.",
      source: "Learned from user edit diffs on 3 consecutive drafts."
    },
    {
      id: "style-002",
      rule: "Always state explicit latency or throughput improvements before discussing project timeline.",
      source: "Promoted after user added benchmark metrics to drafts."
    }
  ]);

  const handleDeleteRule = (id: string) => {
    setMemoryRules(memoryRules.filter(r => r.id !== id));
  };

  return (
    <div id="settings-screen" className="max-w-4xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Settings & Memory Management</h1>
        <p className="text-slate-400 text-xs mt-1">
          Configure autonomy parameters and inspect/delete knowledge promoted to Long-Term Memory.
        </p>
      </div>

      {/* Autonomy Level */}
      <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-6">
        <h3 className="text-sm font-bold text-slate-200 mb-3">Autonomy Policy Gate</h3>
        <div className="space-y-3">
          {[
            { id: "conservative", title: "Conservative (Manual Human Approval on Every Action)", desc: "Requires human confirmation on all bids, messages, and skips." },
            { id: "semi_autonomous", title: "Semi-Autonomous (Auto-Skip Low Fit, Human Approve All Proposals)", desc: "System auto-skips low-fit jobs and scams. High-fit proposals always require human approval before sending." },
            { id: "aggressive", title: "High Throughput (Autonomous Screening)", desc: "Autonomous queueing and background analysis with final sign-off." }
          ].map((opt) => (
            <label
              key={opt.id}
              className={`flex items-start space-x-3 p-3.5 rounded-lg border cursor-pointer transition ${
                autonomy === opt.id
                  ? "bg-emerald-950/20 border-emerald-500/60 text-slate-200"
                  : "bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-300"
              }`}
            >
              <input
                type="radio"
                name="autonomy"
                value={opt.id}
                checked={autonomy === opt.id}
                onChange={() => setAutonomy(opt.id)}
                className="mt-1 accent-emerald-500"
              />
              <div>
                <div className="text-xs font-bold text-slate-200">{opt.title}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">{opt.desc}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Budget Safeguards */}
      <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-6">
        <h3 className="text-sm font-bold text-slate-200 mb-4">Budget & Safety Constraints</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Weekly Connects Hard Cap
            </label>
            <input
              type="number"
              value={weeklyConnects}
              onChange={(e) => setWeeklyConnects(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm font-mono text-slate-200"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Minimum Project Rate Floor ($/hr)
            </label>
            <input
              type="number"
              value={rateFloor}
              onChange={(e) => setRateFloor(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm font-mono text-slate-200"
            />
          </div>
        </div>
      </div>

      {/* Long-Term Memory Viewer */}
      <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-200">Long-Term Style & Outcome Memory</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Rules promoted from user edits to drafts. You can inspect or permanently delete any learned preference.
            </p>
          </div>
          <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded font-mono">
            {memoryRules.length} Active Rules
          </span>
        </div>

        <div className="space-y-3">
          {memoryRules.map((r) => (
            <div
              key={r.id}
              id={`memory-rule-${r.id}`}
              className="bg-slate-900/80 border border-slate-800 rounded-lg p-3.5 flex items-start justify-between gap-4"
            >
              <div>
                <div className="text-xs font-semibold text-slate-200 mb-1">{r.rule}</div>
                <div className="text-[11px] text-emerald-400/90 font-mono">{r.source}</div>
              </div>
              <button
                id={`delete-rule-${r.id}`}
                onClick={() => handleDeleteRule(r.id)}
                className="text-xs text-rose-400 hover:text-rose-300 font-semibold px-2 py-1 rounded bg-rose-500/10 hover:bg-rose-500/20 transition"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
