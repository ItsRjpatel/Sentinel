import React from "react";
import { useNavigate } from "react-router-dom";
import { Cpu, RefreshCw, AlertCircle } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useTopConsumers } from "../api/dashboardApi";

export const TopConsumersCard = React.memo(function TopConsumersCard() {
  const { data: rawData, isLoading, isError, refetch } = useTopConsumers();
  const navigate = useNavigate();

  const consumers = Array.isArray(rawData)
    ? rawData
    : (rawData as any)?.items || [];

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Top Resource Consumers</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load top consumers</p>
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
          <h3 className="text-body-md font-bold text-on-surface">Top Resource Consumers</h3>
          <p className="text-[11px] text-on-surface-variant">Top 5 endpoints with highest CPU / RAM load</p>
        </div>
        <div className="p-1.5 bg-warning/10 text-warning rounded-md">
          <Cpu className="h-4 w-4" />
        </div>
      </div>

      <div className="space-y-3 flex-1">
        {consumers.map((item: any, idx: number) => (
          <div
            key={`${item.hostname}-${idx}`}
            onClick={() => navigate("/endpoints")}
            className="p-2 bg-surface-container-high hover:bg-surface-container-highest transition-colors rounded-md border border-outline-variant/30 space-y-1.5 cursor-pointer"
          >
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-on-surface truncate">{item.hostname}</span>
              <span className="text-primary font-mono text-[11px]">CPU: {item.cpu}%</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-[10px] text-on-surface-variant font-semibold">
              <div className="bg-surface-container-low p-1 rounded">RAM: <strong className="text-on-surface">{item.memory}%</strong></div>
              <div className="bg-surface-container-low p-1 rounded">Disk: <strong className="text-on-surface">{item.disk}%</strong></div>
              <div className="bg-surface-container-low p-1 rounded">Seen: <strong className="text-on-surface">{item.last_seen}</strong></div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
});
