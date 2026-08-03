import React from "react";
import { ShieldAlert, Terminal, RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../../components/ui";
import { useTimeline } from "../api/detailsApi";

export const TimelineTab = React.memo(function TimelineTab({ endpointId }: { endpointId: string }) {
  const { data = [], isLoading, isError, refetch } = useTimeline(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load activity timeline</p>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-error text-on-error rounded text-xs font-bold inline-flex items-center gap-1.5"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </Card>
    );
  }

  const getIcon = (type: string) => {
    if (type.includes("Alert")) return <ShieldAlert className="h-4 w-4 text-error" />;
    if (type.includes("Command")) return <Terminal className="h-4 w-4 text-primary" />;
    return <CheckCircle2 className="h-4 w-4 text-success" />;
  };

  return (
    <Card className="p-5 bg-surface-container-low border-outline-variant space-y-4">
      <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3">
        <h3 className="text-body-md font-extrabold text-on-surface">Endpoint Activity Timeline</h3>
        <span className="text-xs text-on-surface-variant font-medium">Merged EDR events (Newest First)</span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-outline-variant/50">
        {data.map((evt) => (
          <div key={evt.id} className="relative flex items-start gap-4">
            <div className="absolute -left-6 mt-0.5 p-1 bg-surface-container-low rounded-full border border-outline-variant/60 shadow-xs z-10">
              {getIcon(evt.event_type)}
            </div>

            <div className="flex-1 bg-surface-container-high/60 rounded-xl p-3.5 border border-outline-variant/30 space-y-1">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span className="text-xs font-extrabold text-on-surface">{evt.title}</span>
                <span className="text-[10px] font-mono text-on-surface-variant font-semibold">{evt.timestamp}</span>
              </div>
              <p className="text-xs text-on-surface-variant">{evt.details}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
});
