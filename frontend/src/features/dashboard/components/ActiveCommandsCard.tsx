import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Terminal, ArrowRight, Loader2, RefreshCw, AlertCircle } from "lucide-react";
import { Card, Badge, EmptyState, LoadingSkeleton } from "../../../components/ui";
import { useCommands } from "../api/dashboardApi";

export const ActiveCommandsCard = React.memo(function ActiveCommandsCard() {
  const { data: rawData, isLoading, isError, refetch } = useCommands();
  const navigate = useNavigate();

  const commands = Array.isArray(rawData)
    ? rawData
    : (rawData as any)?.items || (rawData as any)?.commands || [];

  const getBadgeVariant = (status: string) => {
    const s = (status || "").toLowerCase();
    if (s === "running" || s === "pending" || s === "sent") return "info";
    if (s === "success" || s === "completed") return "success";
    if (s === "failed" || s === "timeout") return "error";
    return "default";
  };

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Active Remote Commands</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load remote commands</p>
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
    <Card className="flex flex-col h-full bg-surface-container-low border-outline-variant p-0 overflow-hidden">
      <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="h-4 w-4 text-primary" />
          <h3 className="text-body-md font-bold text-on-surface">Running & Recent Commands</h3>
        </div>
        <Link
          to="/commands"
          className="text-label-sm font-bold text-primary hover:underline flex items-center gap-1"
        >
          View All <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      {!Array.isArray(commands) || commands.length === 0 ? (
        <div className="p-6 flex-1 flex items-center justify-center">
          <EmptyState
            title="No Commands Queued"
            description="Command dispatcher queue is empty."
            className="border-none bg-transparent py-4"
          />
        </div>
      ) : (
        <div className="overflow-x-auto flex-1 scrollbar-none">
          <table className="w-full text-left border-collapse">
            <thead className="bg-surface-container-high text-label-sm text-on-surface-variant uppercase">
              <tr>
                <th className="px-4 py-2.5">Command Type</th>
                <th className="px-4 py-2.5">Endpoint ID</th>
                <th className="px-4 py-2.5">Operator</th>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5">Progress</th>
                <th className="px-4 py-2.5">Queued At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 text-body-sm">
              {commands.map((cmd, idx) => {
                const statusLower = (cmd.status || "").toLowerCase();
                const isRunning = statusLower === "running" || statusLower === "pending" || statusLower === "sent";

                return (
                  <tr
                    key={cmd.id || `cmd-${idx}`}
                    onClick={() => navigate("/commands")}
                    className="hover:bg-surface-container-high/60 transition-colors cursor-pointer"
                  >
                    <td className="px-4 py-2.5 font-bold font-mono text-on-surface text-xs">
                      {cmd.command_type}
                    </td>
                    <td className="px-4 py-2.5 font-mono text-on-surface-variant text-xs">
                      {cmd.endpoint_id ? cmd.endpoint_id.slice(0, 13) + "..." : "System"}
                    </td>
                    <td className="px-4 py-2.5 text-on-surface font-medium text-xs">
                      {cmd.created_by || "admin"}
                    </td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-1.5">
                        {isRunning && <Loader2 className="h-3.5 w-3.5 text-primary animate-spin" />}
                        <Badge variant={getBadgeVariant(cmd.status)} size="sm">
                          {cmd.status}
                        </Badge>
                      </div>
                    </td>
                    <td className="px-4 py-2.5 text-xs font-semibold">
                      <div className="flex items-center gap-2 max-w-[100px]">
                        <div className="h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden">
                          <div
                            style={{ width: isRunning ? "65%" : "100%" }}
                            className={`h-full ${isRunning ? "bg-primary" : "bg-success"}`}
                          />
                        </div>
                        <span className="text-[10px] text-on-surface-variant">{isRunning ? "65%" : "100%"}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2.5 text-on-surface-variant text-xs">
                      {cmd.created_at ? new Date(cmd.created_at).toLocaleTimeString() : "Just now"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
});
