import React from 'react';

interface DegradedBannerProps {
  isDegraded: boolean;
  queuedCount: number;
}

export const DegradedBanner: React.FC<DegradedBannerProps> = ({ isDegraded, queuedCount }) => {
  if (!isDegraded) return null;

  return (
    <div id="degraded-mode-banner" className="bg-amber-500/20 border-b border-amber-500/40 px-4 py-2 text-amber-300 text-sm flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <span className="animate-pulse text-lg">⚠️</span>
        <span className="font-medium">Marketplace Simulator Offline — System Operating in DEGRADED MODE</span>
      </div>
      <div className="text-xs bg-amber-950/60 px-2 py-1 rounded border border-amber-600/30">
        Queued Operations: <span className="font-bold text-amber-200">{queuedCount}</span> (will auto-retry on reconnect)
      </div>
    </div>
  );
};
