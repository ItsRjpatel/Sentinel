import React from "react";
import { Server, RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useSystemHealth } from "../api/dashboardApi";

export const SystemHealthCard = React.memo(function SystemHealthCard() {
  const { data: rawData, isLoading, isError, refetch } = useSystemHealth();

  const services = Array.isArray(rawData)
    ? rawData
    : (rawData as any)?.items || [];

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">System Health</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load system health</p>
          <button
            onClick={() => refetch()}
            className="px-3 py-1 bg-primary text-on-primary rounded text-xs font-bold inline-flex items-center gap-1.5"
          >
            <RefreshCw className="h-3 w-3" /> Retry
          </button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col h-full bg-surface-container-low border-outline-variant p-4">
      <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3 mb-3">
        <div>
          <h3 className="text-body-md font-bold text-on-surface">System Health</h3>
          <p className="text-[11px] text-on-surface-variant">Core backend infrastructure & query latency</p>
        </div>
        <div className="p-1.5 bg-success/10 text-success rounded-md">
          <Server className="h-4 w-4" />
        </div>
      </div>

      <div className="space-y-2 flex-1">
        {services.map((svc: any) => (
          <div key={svc.service} className="p-2 bg-surface-container-high rounded-md border border-outline-variant/30 flex items-center justify-between">
            <div className="flex items-center gap-2 truncate">
              <CheckCircle2 className="h-3.5 w-3.5 text-success flex-shrink-0" />
              <div className="truncate">
                <p className="text-xs font-bold text-on-surface truncate">{svc.service}</p>
                <p className="text-[10px] text-on-surface-variant font-medium truncate">{svc.details}</p>
              </div>
            </div>
            <div className="text-right flex-shrink-0 pl-2">
              <span className="px-2 py-0.5 bg-success/10 text-success text-[10px] font-black rounded uppercase">
                {svc.status}
              </span>
              <p className="text-[10px] font-mono text-on-surface-variant font-bold mt-0.5">{svc.latency_ms} ms</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
});
