import React from 'react';

export const AnalyticsScreen: React.FC = () => {
  return (
    <div id="analytics-screen" className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Performance & Outcome Analytics</h1>
        <p className="text-slate-400 text-xs mt-1">
          Measured reply rates, Connects ROI, and latency metrics across 600 development jobs.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-5">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Reply Rate</div>
          <div className="text-3xl font-extrabold text-emerald-400 font-mono">46.8%</div>
          <div className="text-[11px] text-emerald-500 mt-1">↑ +27.3% vs V0 baseline</div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-5">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Hire Rate</div>
          <div className="text-3xl font-extrabold text-sky-400 font-mono">23.8%</div>
          <div className="text-[11px] text-sky-500 mt-1">25 verified contract wins</div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-5">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">p95 Latency</div>
          <div className="text-3xl font-extrabold text-indigo-400 font-mono">2.45s</div>
          <div className="text-[11px] text-slate-400 mt-1">Target budget: &lt;5.0s</div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-5">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Cost / Proposal</div>
          <div className="text-3xl font-extrabold text-amber-400 font-mono">$0.0014</div>
          <div className="text-[11px] text-slate-400 mt-1">Target budget: &lt;$0.05</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Reply Rate by Category */}
        <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-6">
          <h3 className="text-sm font-bold text-slate-200 mb-4">Reply & Hire Rate by Persona Domain</h3>
          <div className="space-y-4">
            {[
              { cat: "AI/ML (Alex Chen)", reply: "48.2%", hire: "24.1%", color: "bg-emerald-500" },
              { cat: "Full-Stack Web (Sarah Jenkins)", reply: "45.4%", hire: "22.8%", color: "bg-sky-500" },
              { cat: "Data Analytics (Marcus Vance)", reply: "46.0%", hire: "23.5%", color: "bg-purple-500" }
            ].map((item, idx) => (
              <div key={idx} className="space-y-1.5 text-xs">
                <div className="flex justify-between font-medium">
                  <span className="text-slate-300">{item.cat}</span>
                  <span className="text-slate-400">Reply: {item.reply} | Hire: {item.hire}</span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-2">
                  <div className={`${item.color} h-2 rounded-full`} style={{ width: item.reply }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Rejection Reasons */}
        <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-6">
          <h3 className="text-sm font-bold text-slate-200 mb-4">Top Auto-Skip & Scam Defense Triggers</h3>
          <div className="space-y-3">
            {[
              { reason: "Off-platform communication ask (Telegram / WhatsApp)", pct: "42.4%", count: 28 },
              { reason: "Unpaid production test work disguised as trial", pct: "27.3%", count: 18 },
              { reason: "Technical skill mismatch (Legacy stack)", pct: "18.2%", count: 12 },
              { reason: "Budget below minimum project floor ($300)", pct: "12.1%", count: 8 }
            ].map((r, i) => (
              <div key={i} className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded-lg text-xs">
                <span className="text-slate-300">{r.reason}</span>
                <span className="font-mono text-rose-400 font-semibold">{r.pct} ({r.count})</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
