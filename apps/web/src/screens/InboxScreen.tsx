import React, { useState } from 'react';

interface JobSummary {
  job_id: string;
  title: string;
  category: string;
  description: string;
  budget: { min: number; max: number };
  connects_cost: number;
  required_skills: string[];
  fit_score: number;
  risk_score: number;
  recommended_action: string;
  badge: string;
  is_scam: boolean;
  client_tier: string;
}

interface InboxScreenProps {
  jobs: JobSummary[];
  onSelectJob: (jobId: string) => void;
  onSkipJob: (jobId: string) => void;
}

export const InboxScreen: React.FC<InboxScreenProps> = ({
  jobs,
  onSelectJob,
  onSkipJob
}) => {
  const [filter, setFilter] = useState("all");

  const filteredJobs = jobs.filter(j => {
    if (filter === "bid") return j.recommended_action === "BID";
    if (filter === "skip") return j.recommended_action === "SKIP";
    return true;
  });

  return (
    <div id="inbox-screen" className="max-w-6xl mx-auto p-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 mb-6 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Job Discovery Feed</h1>
          <p className="text-slate-400 text-xs mt-1">
            Scouted from marketplace searches. Ranked by portfolio evidence alignment and security risk score.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center space-x-2">
          {["all", "bid", "skip"].map((f) => (
            <button
              key={f}
              id={`filter-btn-${f}`}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
                filter === f
                  ? "bg-emerald-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              {f === "all" ? "All Jobs" : f === "bid" ? "Recommended Bids" : "Skipped / Scams"}
            </button>
          ))}
        </div>
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {filteredJobs.map((job) => {
          const isBid = job.recommended_action === "BID";
          return (
            <div
              key={job.job_id}
              id={`job-card-${job.job_id}`}
              className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-5 hover:border-slate-600 transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
                    isBid 
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" 
                      : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                  }`}>
                    {job.badge}
                  </span>
                  <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
                    {job.category}
                  </span>
                  <span className="text-xs text-slate-400">
                    Client: {job.client_tier}
                  </span>
                </div>

                <h3 
                  onClick={() => onSelectJob(job.job_id)}
                  className="text-base font-bold text-slate-100 hover:text-emerald-400 cursor-pointer transition mb-1"
                >
                  {job.title}
                </h3>
                <p className="text-xs text-slate-400 mb-3">{job.description}</p>

                <div className="flex flex-wrap gap-1.5">
                  {job.required_skills.map((s, i) => (
                    <span key={i} className="text-[11px] bg-slate-900 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Stats & Actions */}
              <div className="flex md:flex-col items-center md:items-end justify-between w-full md:w-auto pt-3 md:pt-0 border-t md:border-t-0 border-slate-700/60 gap-3">
                <div className="text-right">
                  <div className="text-sm font-bold text-slate-200">
                    ${job.budget.min} - ${job.budget.max}
                  </div>
                  <div className="text-xs text-slate-400">
                    {job.connects_cost} Connects · Fit: {(job.fit_score * 100).toFixed(0)}%
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    id={`skip-btn-${job.job_id}`}
                    onClick={() => onSkipJob(job.job_id)}
                    className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-700 rounded-lg"
                  >
                    Skip
                  </button>
                  <button
                    id={`open-job-btn-${job.job_id}`}
                    onClick={() => onSelectJob(job.job_id)}
                    className="px-4 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow transition"
                  >
                    Open & Review
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
