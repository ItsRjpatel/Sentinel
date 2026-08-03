import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  ChevronRight,
  Monitor,
  Terminal,
  RotateCw,
  Power,
  Lock,
  Unlock,
  Trash2,
  Activity,
  WifiOff,
  Loader2,
} from "lucide-react";
import { Badge } from "../../../../components/ui";
import { apiClient } from "../../../../services/api";
import type { OverviewDetails } from "../api/detailsApi";

interface EndpointDetailsHeaderProps {
  overview?: OverviewDetails;
}

export const EndpointDetailsHeader = React.memo(function EndpointDetailsHeader({
  overview,
}: EndpointDetailsHeaderProps) {
  const hostname = overview?.hostname || "Endpoint Host";
  const isOnline = overview?.is_online || false;
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const dispatchCommand = async (commandType: string, actionLabel: string, payload: Record<string, any> = {}) => {
    if (!overview?.id) return;
    setLoadingAction(actionLabel);
    setActionMessage(null);
    try {
      await apiClient.post("/commands", {
        endpoint_id: overview.id,
        command_type: commandType,
        payload,
      });
      setActionMessage(`${actionLabel} command queued successfully.`);
    } catch (err: any) {
      setActionMessage(`Failed to dispatch ${actionLabel}: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className="space-y-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
      {/* Step 7 Breadcrumbs: Console > Endpoints > [HOSTNAME] */}
      <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-xs text-on-surface-variant">
        <span className="text-on-surface-variant/70 font-medium">Console</span>
        <ChevronRight className="h-3.5 w-3.5 opacity-50" />
        <Link to="/endpoints" className="font-semibold text-primary hover:underline">
          Endpoints
        </Link>
        <ChevronRight className="h-3.5 w-3.5 opacity-50" />
        <span className="font-extrabold text-on-surface truncate">{hostname}</span>
      </nav>

      {/* Main Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left Info Column */}
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0 mt-0.5">
            <Monitor className="h-6 w-6" />
          </div>

          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-2xl font-black text-on-surface tracking-tight">{hostname}</h1>

              {isOnline ? (
                <Badge variant="success" size="md" className="font-bold flex items-center gap-1">
                  <Activity className="h-3 w-3" /> Online
                </Badge>
              ) : (
                <Badge variant="default" size="md" className="font-bold flex items-center gap-1">
                  <WifiOff className="h-3 w-3" /> Offline
                </Badge>
              )}

              <span className="px-2.5 py-0.5 bg-primary/10 text-primary text-xs font-black rounded-full border border-primary/20">
                Score: {overview?.security_score ?? 0}/100
              </span>

              <span className="px-2.5 py-0.5 bg-surface-container-high text-on-surface-variant text-xs font-extrabold rounded-md border border-outline-variant/40">
                Health: {overview?.health || "Unknown"}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-on-surface-variant font-medium">
              <span>OS: <strong className="text-on-surface">{overview?.operating_system || "No data available"}</strong></span>
              <span>•</span>
              <span>Agent: <strong className="text-on-surface font-mono">{overview?.agent_version ? `v${overview.agent_version}` : "N/A"}</strong></span>
              <span>•</span>
              <span>Last Heartbeat: <strong className="text-on-surface">{overview?.last_heartbeat ? new Date(overview.last_heartbeat).toLocaleTimeString() : "No data available"}</strong></span>
            </div>
          </div>
        </div>

        {/* Right Quick Actions Buttons */}
        <div className="flex flex-wrap items-center gap-1.5 flex-shrink-0">
          <button
            onClick={() => dispatchCommand("SYSTEM_INFO", "Run Command")}
            disabled={loadingAction === "Run Command" || !overview?.id}
            className="px-3 py-1.5 bg-primary text-on-primary rounded-md text-xs font-bold flex items-center gap-1.5 hover:opacity-90 transition-opacity shadow-xs disabled:opacity-50"
          >
            {loadingAction === "Run Command" ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Terminal className="h-3.5 w-3.5" />}
            <span>Run Command</span>
          </button>

          <button
            onClick={() => dispatchCommand("SYSTEM_INFO", "Refresh Inventory", { collect: "all" })}
            disabled={loadingAction === "Refresh Inventory" || !overview?.id}
            className="px-3 py-1.5 bg-surface-container-high text-on-surface rounded-md text-xs font-bold flex items-center gap-1.5 border border-outline-variant/40 hover:bg-surface-container-highest transition-colors disabled:opacity-50"
          >
            {loadingAction === "Refresh Inventory" ? <Loader2 className="h-3.5 w-3.5 animate-spin text-success" /> : <RotateCw className="h-3.5 w-3.5 text-success" />}
            <span>Refresh Inventory</span>
          </button>

          <button
            onClick={() => dispatchCommand("RESTART_AGENT", "Restart Agent")}
            disabled={loadingAction === "Restart Agent" || !overview?.id}
            className="px-3 py-1.5 bg-surface-container-high text-on-surface rounded-md text-xs font-bold flex items-center gap-1.5 border border-outline-variant/40 hover:bg-surface-container-highest transition-colors disabled:opacity-50"
          >
            {loadingAction === "Restart Agent" ? <Loader2 className="h-3.5 w-3.5 animate-spin text-warning" /> : <Power className="h-3.5 w-3.5 text-warning" />}
            <span>Restart Agent</span>
          </button>

          <button
            onClick={() => dispatchCommand("ISOLATE_NETWORK", "Isolate")}
            disabled={loadingAction === "Isolate" || !overview?.id}
            className="px-3 py-1.5 bg-warning/15 text-warning rounded-md text-xs font-bold flex items-center gap-1.5 border border-warning/30 hover:bg-warning/20 transition-colors disabled:opacity-50"
          >
            {loadingAction === "Isolate" ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Lock className="h-3.5 w-3.5" />}
            <span>Isolate</span>
          </button>

          <button
            onClick={() => dispatchCommand("RESTORE_NETWORK", "Release")}
            disabled={loadingAction === "Release" || !overview?.id}
            className="px-3 py-1.5 bg-surface-container-high text-on-surface rounded-md text-xs font-bold flex items-center gap-1.5 border border-outline-variant/40 hover:bg-surface-container-highest transition-colors disabled:opacity-50"
          >
            {loadingAction === "Release" ? <Loader2 className="h-3.5 w-3.5 animate-spin text-success" /> : <Unlock className="h-3.5 w-3.5 text-success" />}
            <span>Release</span>
          </button>

          <button
            disabled
            title="Not implemented"
            className="px-3 py-1.5 bg-error/10 text-error/50 rounded-md text-xs font-bold flex items-center gap-1.5 border border-error/20 cursor-not-allowed opacity-60"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Delete</span>
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-2 text-xs font-semibold rounded bg-surface-container-high text-primary border border-primary/20 flex items-center justify-between">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="text-on-surface-variant hover:text-on-surface ml-2">×</button>
        </div>
      )}
    </div>
  );
});

