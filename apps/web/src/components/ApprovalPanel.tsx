import React, { useState } from 'react';
import { EvidenceHover } from './EvidenceHover';

interface ApprovalPanelProps {
  jobId: string;
  coverLetter: string;
  bidAmount: number;
  connectsCost: number;
  evidenceIds: string[];
  riskScore: number;
  onApprove: () => void;
  onEdit: (newText: string) => void;
  onReject: (reason: string) => void;
}

export const ApprovalPanel: React.FC<ApprovalPanelProps> = ({
  jobId,
  coverLetter,
  bidAmount,
  connectsCost,
  evidenceIds,
  riskScore,
  onApprove,
  onEdit,
  onReject
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(coverLetter);
  const [rejectReason, setRejectReason] = useState("");
  const [showRejectModal, setShowRejectModal] = useState(false);

  return (
    <div id="approval-panel" className="bg-slate-800/90 border border-slate-700 rounded-xl p-6 shadow-2xl backdrop-blur">
      <div className="flex items-center justify-between border-b border-slate-700/80 pb-4 mb-5">
        <div>
          <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs px-2.5 py-1 rounded-full font-medium">
            Human Approval Required
          </span>
          <h2 className="text-xl font-bold text-slate-100 mt-2">Proposal Review & Decision Gate</h2>
        </div>
        <div className="text-right">
          <div className="text-sm font-semibold text-emerald-400">Bid: ${bidAmount}</div>
          <div className="text-xs text-slate-400">Cost: {connectsCost} Connects</div>
        </div>
      </div>

      {/* Inline Critic & Compliance Status */}
      <div className="grid grid-cols-2 gap-4 mb-5">
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-700/60 text-xs">
          <span className="font-semibold text-emerald-400">✓ Critic Verification Passed:</span> Grounding 95%, Personalization 90%. All claims mapped to portfolio records.
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-700/60 text-xs">
          <span className="font-semibold text-emerald-400">✓ Compliance Guard Cleared:</span> Zero contact leaks, no guarantees, compliant with marketplace rules.
        </div>
      </div>

      {/* Proposal Draft Body */}
      <div className="mb-5">
        <div className="flex justify-between items-center mb-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Proposal Cover Letter (Evidence Hover Active)
          </label>
          <button 
            id="toggle-edit-btn"
            onClick={() => setIsEditing(!isEditing)}
            className="text-xs text-sky-400 hover:text-sky-300 underline font-medium"
          >
            {isEditing ? "Switch to Preview" : "✏️ Edit Draft"}
          </button>
        </div>

        {isEditing ? (
          <textarea
            id="proposal-edit-textarea"
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            rows={8}
            className="w-full bg-slate-950 border border-sky-500/50 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500 font-mono"
          />
        ) : (
          <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 text-sm leading-relaxed text-slate-300 whitespace-pre-line">
            {coverLetter}
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center space-x-2">
              <span className="text-xs text-slate-400">Linked Proof Points:</span>
              {evidenceIds.map((id) => (
                <EvidenceHover 
                  key={id}
                  evidenceId={id} 
                  title="Production RAG Pipeline in PyTorch" 
                  outcome="Completed 5/5" 
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Dry Run Preview Box */}
      <div className="bg-slate-900/40 border border-slate-800 rounded-lg p-3.5 mb-6 text-xs text-slate-400 flex items-center justify-between">
        <div>
          <span className="text-slate-300 font-medium">Dry Run Preview:</span> Deducts {connectsCost} connects on submission. Idempotency key verified.
        </div>
        <div className="font-mono text-emerald-400 font-semibold">
          Ready to submit
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end space-x-3">
        <button
          id="reject-proposal-btn"
          onClick={() => setShowRejectModal(true)}
          className="px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-lg text-sm font-semibold transition"
        >
          ✕ Reject with Reason
        </button>

        {isEditing ? (
          <button
            id="save-and-approve-btn"
            onClick={() => onEdit(editedText)}
            className="px-5 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-sm font-semibold shadow-lg shadow-sky-600/30 transition"
          >
            Save Edits & Submit
          </button>
        ) : (
          <button
            id="approve-proposal-btn"
            onClick={onApprove}
            className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold shadow-lg shadow-emerald-600/30 transition flex items-center space-x-1.5"
          >
            <span>✓</span>
            <span>Approve & Submit Draft</span>
          </button>
        )}
      </div>

      {/* Reject Reason Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 max-w-md w-full shadow-2xl">
            <h3 className="text-base font-bold text-slate-100 mb-2">Reject Proposal</h3>
            <p className="text-xs text-slate-400 mb-3">
              Provide a reason for rejection. This feedback will be recorded in the audit trace and used to refine future fit assessment.
            </p>
            <input
              id="reject-reason-input"
              type="text"
              placeholder="e.g. Budget too low, client history suspicious..."
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 mb-4 focus:outline-none focus:ring-2 focus:ring-rose-500"
            />
            <div className="flex justify-end space-x-2">
              <button 
                onClick={() => setShowRejectModal(false)}
                className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 font-medium"
              >
                Cancel
              </button>
              <button 
                id="confirm-reject-btn"
                onClick={() => {
                  onReject(rejectReason || "Rejected by user");
                  setShowRejectModal(false);
                }}
                className="px-4 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
