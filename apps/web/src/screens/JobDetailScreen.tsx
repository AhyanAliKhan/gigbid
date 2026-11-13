import React from 'react';
import { EvidenceHover } from '../components/EvidenceHover';

interface JobDetailScreenProps {
  jobId: string;
  onProceedToStudio: () => void;
  onBackToInbox: () => void;
}

export const JobDetailScreen: React.FC<JobDetailScreenProps> = ({
  jobId,
  onProceedToStudio,
  onBackToInbox
}) => {
  return (
    <div id="job-detail-screen" className="max-w-5xl mx-auto p-6">
      <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
        <button
          onClick={onBackToInbox}
          className="text-xs text-slate-400 hover:text-slate-200 flex items-center space-x-1"
        >
          <span>← Back to Job Inbox</span>
        </button>
        <span className="text-xs bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full font-semibold">
          Recommended Action: BID
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Left Column: JobSpec & Risk */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-6">
            <h1 className="text-xl font-bold text-slate-100 mb-2">
              Production RAG Pipeline with Hybrid Search for Enterprise Knowledge Base
            </h1>
            <div className="flex flex-wrap gap-2 text-xs text-slate-400 mb-4">
              <span>Job ID: {jobId}</span>
              <span>•</span>
              <span>Category: AI/ML</span>
              <span>•</span>
              <span>Duration: 21 days</span>
            </div>

            <div className="text-sm text-slate-300 leading-relaxed mb-6">
              We are seeking an experienced AI/ML specialist to design and deploy a production-grade
              Retrieval-Augmented Generation (RAG) system with hybrid BM25 + dense search, cross-encoder reranking,
              and sub-second query latency. The candidate must provide verifiable case studies of past RAG deployments.
            </div>

            {/* Extracted Deliverables */}
            <div className="border-t border-slate-700/60 pt-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
                Extracted JobSpec Deliverables (Job Analyst Node)
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                <li className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>Hybrid vector + lexical retrieval pipeline with Reciprocal Rank Fusion</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>Cross-encoder reranking layer for high precision at top-5 results</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>FastAPI microservice endpoints with p95 latency under 1.5 seconds</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Requirement-to-Evidence Matrix */}
          <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">
              Requirement-to-Evidence Matrix (Fit Matcher Node)
            </h3>
            <div className="space-y-3">
              {[
                { req: "Hybrid Search (BM25 + Vector)", evId: "CS-ALEX-001", title: "Enterprise RAG Pipeline", metric: "22% Recall@5 lift over naive dense" },
                { req: "vLLM / Low Latency Serving", evId: "CS-ALEX-002", title: "vLLM Inference Cluster", metric: "p95 dropped from 820ms to 425ms" },
                { req: "FastAPI REST Integration", evId: "REPO-alex-toolkit", title: "Core ML Microservice Toolkit", metric: "Production-ready async endpoints" }
              ].map((item, idx) => (
                <div key={idx} className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 flex items-center justify-between text-xs">
                  <div>
                    <span className="text-slate-200 font-medium">{item.req}</span>
                    <div className="text-slate-400 text-[11px] mt-0.5">{item.metric}</div>
                  </div>
                  <EvidenceHover 
                    evidenceId={item.evId}
                    title={item.title}
                    outcome="Verified 5/5"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Risk & Pricing */}
        <div className="space-y-6">
          <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              Risk & Vetting Assessment
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Risk Score:</span>
                <span className="font-mono font-bold text-emerald-400">0.12 (Low Risk)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Scam Signals:</span>
                <span className="text-slate-300">None detected</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Prompt Injections:</span>
                <span className="text-slate-300">Zero injected text</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Client Tier:</span>
                <span className="text-slate-300 font-medium">Enterprise ($125,000+ spend)</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
              Pricing Strategist Quote
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Recommended Bid:</span>
                <span className="font-mono font-bold text-emerald-400 text-sm">$650.00</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Client Budget Band:</span>
                <span className="text-slate-300">$500 - $800</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Connects Required:</span>
                <span className="text-slate-300">8 Connects</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Projected ROI:</span>
                <span className="text-emerald-400 font-semibold">5.2x</span>
              </div>
            </div>
          </div>

          <button
            id="proceed-to-studio-btn"
            onClick={onProceedToStudio}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/20 text-xs transition"
          >
            Open Proposal Studio →
          </button>
        </div>
      </div>
    </div>
  );
};
