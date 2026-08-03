import React from "react";
import { Clock, Play, CheckCircle2, XCircle, AlertTriangle, Ban, Calendar, Activity, RefreshCw } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useCommandsSummary } from "../api/commandsApi";

interface CommandsSummaryCardsProps {
  currentStatus?: string;
  onStatusChange?: (status: string) => void;
}

export const CommandsSummaryCards = React.memo(function CommandsSummaryCards({
  currentStatus,
  onStatusChange,
}: CommandsSummaryCardsProps) {
  const { data, isLoading, isError, refetch } = useCommandsSummary();

  if (isLoading) {
    return <LoadingSkeleton height={100} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-4 bg-error/10 border border-error/30 text-center space-y-2">
        <p className="text-xs font-medium text-on-surface-variant">Failed to load command summary metrics</p>
        <button onClick={() => refetch()} className="px-3 py-1 bg-error text-on-error text-xs font-bold rounded inline-flex items-center gap-1">
          <RefreshCw className="h-3 w-3" /> Retry
        </button>
      </Card>
    );
  }

  const items = [
    { label: "Pending Queue", status: "PENDING", count: data.pending, icon: Clock, color: "text-warning", bg: "bg-warning/10" },
    { label: "Active Running", status: "RUNNING", count: data.running, icon: Play, color: "text-primary", bg: "bg-primary/10" },
    { label: "Scheduled", status: "SCHEDULED", count: data.scheduled, icon: Calendar, color: "text-tertiary", bg: "bg-tertiary/10" },
    { label: "Successful", status: "SUCCESS", count: data.success, icon: CheckCircle2, color: "text-success", bg: "bg-success/10" },
    { label: "Failed", status: "FAILED", count: data.failed, icon: XCircle, color: "text-error", bg: "bg-error/10" },
    { label: "Timed Out", status: "TIMED_OUT", count: data.timed_out, icon: AlertTriangle, color: "text-warning", bg: "bg-warning/10" },
    { label: "Cancelled", status: "CANCELLED", count: data.cancelled, icon: Ban, color: "text-on-surface-variant", bg: "bg-surface-container-highest" },
    { label: "Total Dispatch", status: "ALL", count: data.total, icon: Activity, color: "text-primary", bg: "bg-primary/10" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = currentStatus === item.status;
        return (
          <Card
            key={item.label}
            onClick={() => onStatusChange?.(item.status)}
            className={`p-3 bg-surface-container-low border-outline-variant space-y-1.5 flex flex-col justify-between cursor-pointer transition-all hover:border-primary/40 ${
              isActive ? "ring-2 ring-primary/60 bg-surface-container-high/60" : ""
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider truncate">{item.label}</span>
              <div className={`p-1 rounded ${item.bg} ${item.color}`}>
                <Icon className="h-3.5 w-3.5" />
              </div>
            </div>
            <div className="text-xl font-black text-on-surface font-mono">{item.count}</div>
          </Card>
        );
      })}
    </div>
  );
});
