import React, { useState } from 'react';

export const MessagesScreen: React.FC = () => {
  const [selectedThread, setSelectedThread] = useState("thread-01");
  const [replyText, setReplyText] = useState(
    "Hi! Thank you for the positive feedback. I would be glad to meet with your team. " +
    "I have availability for a 30-minute introductory call tomorrow at 15:00 UTC or 17:00 UTC. " +
    "Looking forward to discussing the RAG deployment!"
  );
  const [sentNotice, setSentNotice] = useState(false);

  const threads = [
    {
      id: "thread-01",
      client: "Enterprise AI Labs",
      subject: "Production RAG Pipeline in PyTorch",
      preview: "Hi! We reviewed your proposal and were impressed by your case study benchmarks. Are you available for a 20-minute call?",
      time: "14:20 UTC",
      unread: true
    },
    {
      id: "thread-02",
      client: "Fintech Growth Co",
      subject: "vLLM Low Latency Cluster",
      preview: "Could you clarify your experience with TensorRT-LLM quantization?",
      time: "Yesterday",
      unread: false
    }
  ];

  const handleSend = () => {
    setSentNotice(true);
    setTimeout(() => setSentNotice(false), 2500);
  };

  return (
    <div id="messages-screen" className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Client Conversations & Liaison</h1>
        <p className="text-slate-400 text-xs mt-1">
          Intents classified by Client Liaison agent. Calendar slots sourced from Workspace MCP.
        </p>
      </div>

      {sentNotice && (
        <div className="mb-4 p-3 bg-emerald-500/20 border border-emerald-500/50 rounded-xl text-emerald-300 text-xs font-semibold">
          ✓ Approved reply transmitted to client thread on marketplace!
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-slate-800/60 border border-slate-700/80 rounded-xl overflow-hidden min-h-[500px]">
        {/* Threads List */}
        <div className="border-r border-slate-700/80 bg-slate-900/40 p-3 space-y-2">
          {threads.map((t) => (
            <div
              key={t.id}
              onClick={() => setSelectedThread(t.id)}
              className={`p-3 rounded-lg cursor-pointer transition ${
                selectedThread === t.id
                  ? "bg-slate-800 border border-emerald-500/40 text-slate-100"
                  : "bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-bold text-xs text-slate-200">{t.client}</span>
                <span className="text-[10px] text-slate-500">{t.time}</span>
              </div>
              <div className="text-[11px] font-medium text-emerald-400 mb-1">{t.subject}</div>
              <p className="text-[11px] text-slate-400 truncate">{t.preview}</p>
            </div>
          ))}
        </div>

        {/* Message Thread & Reply Gate */}
        <div className="md:col-span-2 p-6 flex flex-col justify-between">
          <div>
            <div className="border-b border-slate-700 pb-3 mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-100">Enterprise AI Labs</h3>
                <span className="text-xs text-emerald-400 font-medium">Intent Detected: Interview Request</span>
              </div>
              <span className="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded">
                Workspace Calendar Synced
              </span>
            </div>

            {/* Message Bubble */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span className="font-semibold text-slate-300">Client Message</span>
                <span>Today at 14:20 UTC</span>
              </div>
              <p className="text-sm text-slate-200 leading-relaxed">
                Hi Alex! We reviewed your proposal and were impressed by your case study benchmarks with hybrid BM25 search.
                Are you available for a brief 20-minute introductory call tomorrow to discuss deliverables and timeline?
              </p>
            </div>

            {/* Suggested Reply with Calendar Slots */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Suggested Reply (Client Liaison Draft + Calendar Slots)
                </label>
                <span className="text-[11px] text-amber-400 font-semibold">Approval Required</span>
              </div>
              <textarea
                id="message-reply-textarea"
                rows={4}
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-sans"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-slate-800">
            <button
              id="approve-send-message-btn"
              onClick={handleSend}
              className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg shadow-lg shadow-emerald-600/20 transition flex items-center space-x-1"
            >
              <span>✓ Approve & Send Reply</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
