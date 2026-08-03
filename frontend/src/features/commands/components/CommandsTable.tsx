import React from "react";
import { Link } from "react-router-dom";
import {
  Monitor,
  Clock,
  Play,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Ban,
  Calendar,
  RotateCw,
  Eye,
  Copy,
  Download,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Card, Badge, LoadingSkeleton, EmptyState } from "../../../components/ui";
import type { CommandItem } from "../api/commandsApi";

interface CommandsTableProps {
  items: CommandItem[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (p: number) => void;
  isLoading: boolean;
  onViewDetails: (id: string) => void;
  onRetryCommand: (id: string) => void;
  onCancelCommand: (id: string) => void;
  isRetrying: boolean;
  isCancelling: boolean;
}

export const CommandsTable = React.memo(function CommandsTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
  onViewDetails,
  onRetryCommand,
  onCancelCommand,
  isRetrying,
  isCancelling,
}: CommandsTableProps) {
  if (isLoading) {
    return <LoadingSkeleton height={400} />;
  }

  const totalPages = Math.ceil(total / pageSize) || 1;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Command JSON copied to clipboard!");
  };

  const downloadJson = (item: CommandItem) => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(item, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `command-${item.id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const getStatusBadge = (item: CommandItem) => {
    const isScheduled = item.scheduled_at && new Date(item.scheduled_at) > new Date();
    if (isScheduled && item.status.toUpperCase() === "PENDING") {
      return (
        <Badge variant="warning" size="sm" className="font-bold flex items-center gap-1 w-fit">
          <Calendar className="h-3 w-3" /> Scheduled
        </Badge>
      );
    }

    switch (item.status.toUpperCase()) {
      case "PENDING":
        return (
          <Badge variant="warning" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <Clock className="h-3 w-3" /> Pending
          </Badge>
        );
      case "SENT":
      case "RUNNING":
        return (
          <Badge variant="info" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <Play className="h-3 w-3 animate-pulse" /> Running
          </Badge>
        );
      case "SUCCESS":
      case "COMPLETED":
        return (
          <Badge variant="success" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <CheckCircle2 className="h-3 w-3" /> Success
          </Badge>
        );
      case "FAILED":
        return (
          <Badge variant="error" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <XCircle className="h-3 w-3" /> Failed
          </Badge>
        );
      case "TIMEOUT":
        return (
          <Badge variant="warning" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <AlertTriangle className="h-3 w-3" /> Timed Out
          </Badge>
        );
      case "CANCELLED":
        return (
          <Badge variant="default" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <Ban className="h-3 w-3" /> Cancelled
          </Badge>
        );
      default:
        return <Badge variant="default" size="sm">{item.status}</Badge>;
    }
  };

  const calculateDuration = (item: CommandItem) => {
    if (!item.started_at || !item.completed_at) return "N/A";
    const start = new Date(item.started_at).getTime();
    const end = new Date(item.completed_at).getTime();
    const diffMs = Math.max(0, end - start);
    if (diffMs < 1000) return `${diffMs}ms`;
    return `${(diffMs / 1000).toFixed(2)}s`;
  };

  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
      {items.length === 0 ? (
        <div className="py-16 flex items-center justify-center">
          <EmptyState
            title="No Commands Dispatched"
            description="Use 'Run Bulk Command' to queue execution across your fleet endpoints."
            className="border-none bg-transparent"
          />
        </div>
      ) : (
        <>
          <div className="overflow-x-auto scrollbar-none">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
              <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase">
                <tr>
                  <th className="px-4 py-3">Command ID</th>
                  <th className="px-4 py-3">Endpoint Host</th>
                  <th className="px-4 py-3">Command Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Requested By</th>
                  <th className="px-4 py-3">Created</th>
                  <th className="px-4 py-3">Completed</th>
                  <th className="px-4 py-3">Duration</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 font-medium">
                {items.map((cmd) => {
                  const statusUpper = cmd.status.toUpperCase();
                  const canRetry = statusUpper === "FAILED" || statusUpper === "TIMEOUT";
                  const canCancel = statusUpper === "PENDING";

                  return (
                    <tr key={cmd.id} className="hover:bg-surface-container-high/40 transition-colors">
                      <td className="px-4 py-3 font-mono font-bold text-primary">{cmd.id.slice(0, 8)}...</td>
                      <td className="px-4 py-3 font-bold text-on-surface">
                        <div className="flex items-center gap-2">
                          <Monitor className="h-3.5 w-3.5 text-on-surface-variant" />
                          <Link to={`/endpoints/${cmd.endpoint_id}`} className="hover:underline text-primary">
                            {cmd.endpoint_hostname || cmd.endpoint_id.slice(0, 8)}
                          </Link>
                        </div>
                      </td>
                      <td className="px-4 py-3 font-mono font-extrabold text-on-surface">{cmd.command_type}</td>
                      <td className="px-4 py-3">{getStatusBadge(cmd)}</td>
                      <td className="px-4 py-3 font-semibold text-on-surface-variant">{cmd.created_by || "system"}</td>
                      <td className="px-4 py-3 font-mono text-on-surface-variant text-[11px]">
                        {new Date(cmd.created_at).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-3 font-mono text-on-surface-variant text-[11px]">
                        {cmd.completed_at ? new Date(cmd.completed_at).toLocaleTimeString() : "In Progress"}
                      </td>
                      <td className="px-4 py-3 font-mono text-on-surface-variant">{calculateDuration(cmd)}</td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1">
                          {/* View Details */}
                          <button
                            onClick={() => onViewDetails(cmd.id)}
                            className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-primary"
                            title="View Command Details & Logs"
                          >
                            <Eye className="h-3.5 w-3.5" />
                          </button>

                          {/* Retry (Only FAILED or TIMEOUT) */}
                          <button
                            onClick={() => canRetry && onRetryCommand(cmd.id)}
                            disabled={!canRetry || isRetrying}
                            className={`p-1.5 rounded border transition-colors ${
                              canRetry
                                ? "bg-warning/15 hover:bg-warning/25 border-warning/30 text-warning cursor-pointer"
                                : "bg-surface-container-high border-outline-variant/30 text-on-surface-variant/40 cursor-not-allowed opacity-40"
                            }`}
                            title={canRetry ? "Retry Failed Command" : "Retry is only available for FAILED or TIMEOUT commands"}
                          >
                            <RotateCw className="h-3.5 w-3.5" />
                          </button>

                          {/* Cancel (Only PENDING) */}
                          <button
                            onClick={() => canCancel && onCancelCommand(cmd.id)}
                            disabled={!canCancel || isCancelling}
                            className={`p-1.5 rounded border transition-colors ${
                              canCancel
                                ? "bg-error/15 hover:bg-error/25 border-error/30 text-error cursor-pointer"
                                : "bg-surface-container-high border-outline-variant/30 text-on-surface-variant/40 cursor-not-allowed opacity-40"
                            }`}
                            title={canCancel ? "Cancel Pending Command" : "Cancel is only available for PENDING commands"}
                          >
                            <Ban className="h-3.5 w-3.5" />
                          </button>

                          {/* Copy Result JSON */}
                          <button
                            onClick={() => copyToClipboard(JSON.stringify(cmd, null, 2))}
                            className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-on-surface-variant"
                            title="Copy Command JSON"
                          >
                            <Copy className="h-3.5 w-3.5" />
                          </button>

                          {/* Download JSON */}
                          <button
                            onClick={() => downloadJson(cmd)}
                            className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-on-surface-variant"
                            title="Download Result JSON File"
                          >
                            <Download className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-surface-container-high/60 border-t border-outline-variant/40 text-xs">
            <span className="text-on-surface-variant font-medium">
              Showing <strong className="text-on-surface">{items.length}</strong> of <strong className="text-on-surface">{total}</strong> commands
            </span>

            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => onPageChange(page - 1)}
                className="p-1.5 bg-surface-container-low border border-outline-variant/40 rounded hover:bg-surface-container-highest disabled:opacity-40 text-on-surface"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="font-bold text-on-surface">Page {page} of {totalPages}</span>
              <button
                disabled={page >= totalPages}
                onClick={() => onPageChange(page + 1)}
                className="p-1.5 bg-surface-container-low border border-outline-variant/40 rounded hover:bg-surface-container-highest disabled:opacity-40 text-on-surface"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </Card>
  );
});
