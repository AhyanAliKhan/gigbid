import React, { useState, useEffect } from 'react';
import { DegradedBanner } from './components/DegradedBanner';
import { OnboardingScreen } from './screens/OnboardingScreen';
import { InboxScreen } from './screens/InboxScreen';
import { JobDetailScreen } from './screens/JobDetailScreen';
import { ProposalStudioScreen } from './screens/ProposalStudioScreen';
import { PipelineScreen } from './screens/PipelineScreen';
import { MessagesScreen } from './screens/MessagesScreen';
import { RunViewerScreen } from './screens/RunViewerScreen';
import { AnalyticsScreen } from './screens/AnalyticsScreen';
import { SettingsScreen } from './screens/SettingsScreen';

export const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<string>("inbox");
  const [activePersona, setActivePersona] = useState<string>("alex_chen_aiml");
  const [selectedJobId, setSelectedJobId] = useState<string>("job-0001");
  const [isDegraded, setIsDegraded] = useState<boolean>(false);
  const [queuedCount, setQueuedCount] = useState<number>(0);

  // Poll API health to detect degraded mode
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("/health");
        if (res.ok) {
          const data = await res.json();
          setIsDegraded(Boolean(data.degraded_mode));
          setQueuedCount(data.queued_operations || 0);
        }
      } catch (err) {
        // If API unreachable, set degraded mode banner
        setIsDegraded(true);
        setQueuedCount(1);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const sampleJobs = [
    {
      job_id: "job-0001",
      title: "Production RAG Pipeline with Hybrid Search for Enterprise Knowledge Base",
      category: "AI/ML",
      description: "Build an enterprise-grade retrieval pipeline in PyTorch using hybrid dense + BM25 search, cross-encoder reranking, and sub-second latency.",
      budget: { min: 500, max: 900 },
      connects_cost: 8,
      required_skills: ["Python", "PyTorch", "vLLM", "Vector Databases", "FastAPI"],
      fit_score: 0.94,
      risk_score: 0.12,
      recommended_action: "BID",
      badge: "Strong Fit",
      is_scam: false,
      client_tier: "Enterprise ($125k+ spend)"
    },
    {
      job_id: "job-0002",
      title: "Unpaid Trial: Complete Full Analytics Dashboard on Free Test",
      category: "Full-Stack Web",
      description: "Complete full production dashboard for free as test. Contact hiring manager directly on Telegram @scam_recruiter to get repo credentials.",
      budget: { min: 0, max: 0 },
      connects_cost: 10,
      required_skills: ["React", "Python"],
      fit_score: 0.15,
      risk_score: 0.98,
      recommended_action: "SKIP",
      badge: "Scam Detected",
      is_scam: true,
      client_tier: "Unverified ($0 spend)"
    },
    {
      job_id: "job-0003",
      title: "Next.js 15 SaaS Dashboard with TailwindCSS & TypeScript",
      category: "Full-Stack Web",
      description: "Looking for an expert React / Next.js developer to refactor our multi-tenant SaaS analytics portal with TypeScript and Playwright tests.",
      budget: { min: 600, max: 1200 },
      connects_cost: 6,
      required_skills: ["TypeScript", "Next.js", "React", "TailwindCSS"],
      fit_score: 0.91,
      risk_score: 0.10,
      recommended_action: "BID",
      badge: "Strong Fit",
      is_scam: false,
      client_tier: "Enterprise ($85k+ spend)"
    },
    {
      job_id: "job-0004",
      title: "Snowflake & dbt Enterprise Data Warehouse Modeling",
      category: "Data Analytics",
      description: "Build modular dbt transformation pipelines and executive PowerBI dashboards tracking ARR and customer churn analytics.",
      budget: { min: 450, max: 800 },
      connects_cost: 8,
      required_skills: ["SQL", "Snowflake", "dbt", "PowerBI"],
      fit_score: 0.89,
      risk_score: 0.14,
      recommended_action: "BID",
      badge: "Strong Fit",
      is_scam: false,
      client_tier: "Mid-Market"
    }
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-900 text-slate-100">
      {/* Degraded Mode Banner */}
      <DegradedBanner isDegraded={isDegraded} queuedCount={queuedCount} />

      {/* Navigation Bar */}
      <header className="bg-slate-950/90 border-b border-slate-800 sticky top-0 z-40 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentScreen("inbox")}>
            <div className="w-7 h-7 rounded-lg bg-emerald-600 flex items-center justify-center font-bold text-white shadow-md">
              ⚡
            </div>
            <span className="font-bold text-lg tracking-tight text-white">GigBid</span>
            <span className="text-[10px] font-mono bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30">
              Copilot v1.0
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {[
              { id: "inbox", label: "Inbox" },
              { id: "studio", label: "Proposal Studio" },
              { id: "pipeline", label: "Pipeline" },
              { id: "messages", label: "Messages" },
              { id: "runs", label: "Run Viewer" },
              { id: "analytics", label: "Analytics" },
              { id: "settings", label: "Settings" }
            ].map((tab) => (
              <button
                key={tab.id}
                id={`nav-${tab.id}`}
                onClick={() => setCurrentScreen(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  currentScreen === tab.id
                    ? "bg-slate-800 text-emerald-400 border border-slate-700"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          {/* Persona Switcher Pill */}
          <div className="flex items-center space-x-3">
            <button
              id="onboarding-nav-btn"
              onClick={() => setCurrentScreen("onboarding")}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-lg border border-slate-700 transition"
            >
              👤 Switch Persona
            </button>
            <div className="text-right hidden sm:block">
              <div className="text-[11px] font-bold text-slate-200">
                {activePersona === "alex_chen_aiml" ? "Alex Chen (AI/ML)" : activePersona === "sarah_jenkins_fullstack" ? "Sarah Jenkins (Web)" : "Marcus Vance (BI)"}
              </div>
              <div className="text-[10px] text-emerald-400 font-mono">100% JSS · Top Rated</div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1">
        {currentScreen === "onboarding" && (
          <OnboardingScreen
            currentPersona={activePersona}
            onSelectPersona={(id) => setActivePersona(id)}
            onContinue={() => setCurrentScreen("inbox")}
          />
        )}

        {currentScreen === "inbox" && (
          <InboxScreen
            jobs={sampleJobs}
            onSelectJob={(id) => {
              setSelectedJobId(id);
              setCurrentScreen("detail");
            }}
            onSkipJob={(id) => alert(`Skipped ${id}`)}
          />
        )}

        {currentScreen === "detail" && (
          <JobDetailScreen
            jobId={selectedJobId}
            onProceedToStudio={() => setCurrentScreen("studio")}
            onBackToInbox={() => setCurrentScreen("inbox")}
          />
        )}

        {currentScreen === "studio" && (
          <ProposalStudioScreen
            jobId={selectedJobId}
            onSubmitted={() => setCurrentScreen("pipeline")}
          />
        )}

        {currentScreen === "pipeline" && <PipelineScreen />}
        {currentScreen === "messages" && <MessagesScreen />}
        {currentScreen === "runs" && <RunViewerScreen />}
        {currentScreen === "analytics" && <AnalyticsScreen />}
        {currentScreen === "settings" && <SettingsScreen />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500">
        AI-4016 R&D Assignment: GigBid Multi-Agent Freelancer Copilot · FAST School of Computing, FAST-NUCES Islamabad
      </footer>
    </div>
  );
};
