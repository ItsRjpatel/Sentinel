import React from "react";
import { FileText, AlertOctagon, AlertTriangle, Info, CheckCircle2, XCircle, Calendar, RefreshCw } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useAuditSummary } from "../api/auditApi";

export const AuditSummaryCards = React.memo(function AuditSummaryCards() {
  const { data, isLoading, isError, refetch } = useAuditSummary();

  if (isLoading) {
    return <LoadingSkeleton height={100} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-4 bg-error/10 border border-error/30 text-center space-y-2">
        <p className="text-xs font-medium text-on-surface-variant">Failed to load audit metrics</p>
        <button onClick={() => refetch()} className="px-3 py-1 bg-error text-on-error text-xs font-bold rounded inline-flex items-center gap-1">
          <RefreshCw className="h-3 w-3" /> Retry
        </button>
      </Card>
    );
  }

  const items = [
    { label: "Total Audit Events", count: data.total, icon: FileText, color: "text-primary", bg: "bg-primary/10" },
    { label: "Critical Severity", count: data.critical, icon: AlertOctagon, color: "text-error", bg: "bg-error/10" },
    { label: "Warning Events", count: data.warning, icon: AlertTriangle, color: "text-warning", bg: "bg-warning/10" },
    { label: "Information", count: data.information, icon: Info, color: "text-tertiary", bg: "bg-tertiary/10" },
    { label: "Success Status", count: data.success, icon: CheckCircle2, color: "text-success", bg: "bg-success/10" },
    { label: "Failed Status", count: data.failed, icon: XCircle, color: "text-error", bg: "bg-error/10" },
    { label: "Today's Events", count: data.today, icon: Calendar, color: "text-primary", bg: "bg-primary/10" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5">
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
