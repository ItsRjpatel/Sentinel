import React from "react";
import { Link } from "react-router-dom";
import { AlertCircle, RefreshCw, ShieldAlert, CheckCircle, WifiOff, ArrowRight } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useFleetHealth } from "../api/dashboardApi";

export const FleetHealthCard = React.memo(function FleetHealthCard() {
  const { data, isLoading, isError, refetch } = useFleetHealth();

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError || !data) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Fleet Health</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load fleet health</p>
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

  const total = data.total || 1;
  const healthyPct = Math.round((data.healthy / total) * 100);
  const warningPct = Math.round((data.warning / total) * 100);
  const offlinePct = Math.round((data.offline / total) * 100);

  return (
    <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4 hover:border-primary/40 transition-colors">
      <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3">
        <div>
          <h3 className="text-body-md font-bold text-on-surface">Fleet Health</h3>
          <p className="text-[11px] text-on-surface-variant">Real-time status breakdown across managed hosts</p>
        </div>
        <Link to="/endpoints" className="text-xs font-bold text-primary hover:underline flex items-center gap-1">
          View All <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      {/* Visual Multi-Segment Status Bar */}
      <div className="my-4">
        <div className="flex items-center justify-between text-xs font-semibold mb-1.5">
          <span className="text-on-surface">Fleet Distribution</span>
          <span className="text-on-surface-variant">{data.total} Managed Agents</span>
        </div>
        <div className="h-3 w-full bg-surface-container-highest rounded-full overflow-hidden flex gap-0.5">
          <div style={{ width: `${healthyPct}%` }} className="bg-success h-full transition-all duration-500" title="Healthy" />
          <div style={{ width: `${warningPct}%` }} className="bg-warning h-full transition-all duration-500" title="Warning" />
          <div style={{ width: `${offlinePct}%` }} className="bg-on-surface-variant/40 h-full transition-all duration-500" title="Offline" />
        </div>
      </div>

      {/* Metric Badges Grid */}
      <div className="grid grid-cols-3 gap-2">
        <div className="p-2 bg-surface-container-high rounded-md flex flex-col justify-center border border-outline-variant/30">
          <div className="flex items-center gap-1.5 text-[11px] font-bold text-success">
            <CheckCircle className="h-3.5 w-3.5" />
            <span>Healthy</span>
          </div>
          <span className="text-lg font-extrabold text-on-surface mt-0.5">{data.healthy}</span>
        </div>

        <div className="p-2 bg-surface-container-high rounded-md flex flex-col justify-center border border-outline-variant/30">
          <div className="flex items-center gap-1.5 text-[11px] font-bold text-warning">
            <ShieldAlert className="h-3.5 w-3.5" />
            <span>Warning</span>
          </div>
          <span className="text-lg font-extrabold text-on-surface mt-0.5">{data.warning}</span>
        </div>

        <div className="p-2 bg-surface-container-high rounded-md flex flex-col justify-center border border-outline-variant/30">
          <div className="flex items-center gap-1.5 text-[11px] font-bold text-on-surface-variant">
            <WifiOff className="h-3.5 w-3.5" />
            <span>Offline</span>
          </div>
          <span className="text-lg font-extrabold text-on-surface mt-0.5">{data.offline}</span>
        </div>

        <div className="p-2 bg-surface-container-high rounded-md flex flex-col justify-center border border-outline-variant/30">
          <span className="text-[10px] font-bold uppercase text-on-surface-variant">Inactive</span>
          <span className="text-sm font-bold text-on-surface mt-0.5">{data.inactive}</span>
        </div>

        <div className="p-2 bg-surface-container-high rounded-md flex flex-col justify-center border border-outline-variant/30">
          <span className="text-[10px] font-bold uppercase text-on-surface-variant">Pending</span>
          <span className="text-sm font-bold text-on-surface mt-0.5">{data.pending}</span>
        </div>

        <div className="p-2 bg-surface-container-high rounded-md flex flex-col justify-center border border-outline-variant/30">
          <span className="text-[10px] font-bold uppercase text-error">Attention</span>
          <span className="text-sm font-bold text-error mt-0.5">{data.needs_attention}</span>
        </div>
      </div>
    </Card>
  );
});
