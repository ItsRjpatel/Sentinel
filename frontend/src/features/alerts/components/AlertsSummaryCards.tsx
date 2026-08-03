import React from "react";
import { AlertOctagon, AlertTriangle, Info, CheckCircle2, ShieldAlert, RefreshCw, Eye } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useAlertsSummary } from "../api/alertsApi";

export const AlertsSummaryCards = React.memo(function AlertsSummaryCards() {
  const { data, isLoading, isError, refetch } = useAlertsSummary();

  if (isLoading) {
    return <LoadingSkeleton height={100} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-4 bg-error/10 border border-error/30 text-center space-y-2">
        <p className="text-xs font-medium text-on-surface-variant">Failed to load alerts summary metrics</p>
        <button onClick={() => refetch()} className="px-3 py-1 bg-error text-on-error text-xs font-bold rounded inline-flex items-center gap-1">
          <RefreshCw className="h-3 w-3" /> Retry
        </button>
      </Card>
    );
  }

  const items = [
    { label: "Total Security Alerts", count: data.total, icon: ShieldAlert, color: "text-primary", bg: "bg-primary/10" },
    { label: "Critical Severity", count: data.critical, icon: AlertOctagon, color: "text-error", bg: "bg-error/10" },
    { label: "High Severity", count: data.high, icon: AlertTriangle, color: "text-warning", bg: "bg-warning/10" },
    { label: "Medium Severity", count: data.medium, icon: Info, color: "text-tertiary", bg: "bg-tertiary/10" },
    { label: "Low Severity", count: data.low, icon: Info, color: "text-on-surface-variant", bg: "bg-surface-container-highest" },
    { label: "Active Triaging", count: data.active, icon: Eye, color: "text-error", bg: "bg-error/10" },
    { label: "Acknowledged", count: data.acknowledged, icon: Info, color: "text-warning", bg: "bg-warning/10" },
    { label: "Resolved", count: data.resolved, icon: CheckCircle2, color: "text-success", bg: "bg-success/10" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <Card key={item.label} className="p-3 bg-surface-container-low border-outline-variant space-y-1.5 flex flex-col justify-between">
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
