import React from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, RefreshCw, CheckCircle2, ArrowRight } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useThreatDistribution } from "../api/dashboardApi";

export const ThreatDistributionCard = React.memo(function ThreatDistributionCard() {
  const { data, isLoading, isError, refetch } = useThreatDistribution();

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError || !data) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Threat Distribution</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertTriangle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load threat distribution</p>
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

  const items = [
    { label: "Critical", count: data.critical, color: "bg-error text-error", barColor: "bg-error" },
    { label: "High", count: data.high, color: "bg-warning text-warning", barColor: "bg-warning" },
    { label: "Medium", count: data.medium, color: "bg-tertiary text-tertiary", barColor: "bg-tertiary" },
    { label: "Low", count: data.low, color: "bg-primary text-primary", barColor: "bg-primary" },
    { label: "Info", count: data.info, color: "bg-on-surface-variant text-on-surface-variant", barColor: "bg-on-surface-variant/60" },
  ];

  const total = data.total_threats || 1;

  return (
    <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4 hover:border-error/40 transition-colors">
      <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3">
        <div>
          <h3 className="text-body-md font-bold text-on-surface">Threat Distribution</h3>
          <p className="text-[11px] text-on-surface-variant">Active alert counts by severity level</p>
        </div>
        <Link to="/alerts" className="text-xs font-bold text-error hover:underline flex items-center gap-1">
          Alerts <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      <div className="space-y-2.5 my-3">
        {items.map((item) => {
          const pct = Math.round((item.count / total) * 100);
          return (
            <div key={item.label} className="space-y-1">
              <div className="flex items-center justify-between text-xs font-medium">
                <span className="text-on-surface flex items-center gap-1.5 font-bold">
                  <span className={`h-2 w-2 rounded-full ${item.barColor}`} />
                  {item.label}
                </span>
                <span className="text-on-surface-variant font-bold">
                  {item.count} ({pct}%)
                </span>
              </div>
              <div className="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden">
                <div
                  style={{ width: `${pct}%` }}
                  className={`h-full ${item.barColor} transition-all duration-500`}
                />
              </div>
            </div>
          );
        })}
      </div>

      {data.total_threats === 0 && (
        <div className="p-3 bg-success/10 border border-success/30 rounded-md text-center flex items-center justify-center gap-2 text-xs font-bold text-success">
          <CheckCircle2 className="h-4 w-4" /> No Active Critical Threats
        </div>
      )}
    </Card>
  );
});
