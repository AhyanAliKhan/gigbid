import React, { useState } from 'react';
import { ApprovalPanel } from '../components/ApprovalPanel';

interface ProposalStudioScreenProps {
  jobId: string;
  onSubmitted: () => void;
}

export const ProposalStudioScreen: React.FC<ProposalStudioScreenProps> = ({
  jobId,
  onSubmitted
}) => {
  const [coverLetter, setCoverLetter] = useState(
    "Hi,\n\n" +
    "Regarding your project to build an enterprise RAG pipeline with hybrid search: I have extensive production experience implementing high-accuracy retrieval architectures. " +
    "In a previous engagement (CS-ALEX-001: Production RAG Pipeline for Fintech), I engineered a hybrid BM25 + dense search pipeline with cross-encoder reranking that achieved a 22% lift in Recall@5 and reduced p95 latency by 48%. " +
    "My architecture will ensure clean modularity, strict typing, and full Playwright / pytest regression suites. " +
    "I can deliver all deliverables within your 21-day timeline.\n\n" +
    "Best regards,\nAlex Chen"
  );

  const [notification, setNotification] = useState<string | null>(null);

  const handleApprove = () => {
    setNotification("✓ Proposal approved and submitted to GigSim marketplace! 8 Connects deducted.");
    setTimeout(() => {
      onSubmitted();
    }, 1500);
  };

  const handleEdit = (newText: string) => {
    setCoverLetter(newText);
    setNotification("✓ Edits saved, analyzed for style memory rules, and submitted to marketplace!");
    setTimeout(() => {
      onSubmitted();
    }, 1500);
  };

  const handleReject = (reason: string) => {
    setNotification(`✕ Proposal rejected: "${reason}". Thread finalized.`);
    setTimeout(() => {
      onSubmitted();
    }, 1500);
  };

  return (
    <div id="proposal-studio-screen" className="max-w-4xl mx-auto p-6">
      {notification && (
        <div className="mb-6 p-4 bg-emerald-500/20 border border-emerald-500/50 rounded-xl text-emerald-300 text-sm font-semibold flex items-center justify-between animate-fade-in">
          <span>{notification}</span>
        </div>
      )}

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Proposal Studio</h1>
        <p className="text-slate-400 text-xs mt-1">
          Ground every sentence in verifiable portfolio achievements. Critic & Compliance guards are active.
        </p>
      </div>

      <ApprovalPanel
        jobId={jobId}
        coverLetter={coverLetter}
        bidAmount={650.0}
        connectsCost={8}
        evidenceIds={["CS-ALEX-001"]}
        riskScore={0.12}
        onApprove={handleApprove}
        onEdit={handleEdit}
        onReject={handleReject}
      />
    </div>
  );
};
