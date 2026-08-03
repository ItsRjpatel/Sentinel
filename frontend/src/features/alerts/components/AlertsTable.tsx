import React from "react";
import { Link } from "react-router-dom";
import {
  Monitor,
  AlertOctagon,
  AlertTriangle,
  Info,
  CheckCircle2,
  Eye,
  UserPlus,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Clock,
} from "lucide-react";
import { Card, Badge, LoadingSkeleton, EmptyState } from "../../../components/ui";
import type { AlertItem } from "../types/alertsTypes";

interface AlertsTableProps {
  items: AlertItem[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (p: number) => void;
  isLoading: boolean;
  onViewDetails: (id: string) => void;
  onAcknowledge: (id: string) => void;
  onResolve: (id: string) => void;
  onReopen: (id: string) => void;
  onAssign: (id: string) => void;
  isMutating: boolean;
}

export const AlertsTable = React.memo(function AlertsTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
  onViewDetails,
  onAcknowledge,
  onResolve,
  onReopen,
  onAssign,
  isMutating,
}: AlertsTableProps) {
  if (isLoading) {
    return <LoadingSkeleton height={400} />;
  }

  const totalPages = Math.ceil(total / pageSize) || 1;

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return (
          <Badge variant="error" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <AlertOctagon className="h-3 w-3" /> Critical
          </Badge>
        );
      case "high":
        return (
          <Badge variant="warning" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <AlertTriangle className="h-3 w-3" /> High
          </Badge>
        );
      case "medium":
        return (
          <Badge variant="info" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <Info className="h-3 w-3" /> Medium
          </Badge>
        );
      default:
        return <Badge variant="default" size="sm">{severity}</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return (
          <Badge variant="error" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <Clock className="h-3 w-3 animate-pulse" /> Active
          </Badge>
        );
      case "acknowledged":
        return (
          <Badge variant="warning" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <Eye className="h-3 w-3" /> Acknowledged
          </Badge>
        );
      case "resolved":
        return (
          <Badge variant="success" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <CheckCircle2 className="h-3 w-3" /> Resolved
          </Badge>
        );
      default:
        return <Badge variant="default" size="sm">{status}</Badge>;
    }
  };

  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
      {items.length === 0 ? (
        <div className="py-16 flex items-center justify-center">
          <EmptyState
            title="No Security Alerts Found"
            description="All systems are operating within safe baseline parameters."
            className="border-none bg-transparent"
          />
        </div>
      ) : (
        <>
          <div className="overflow-x-auto scrollbar-none">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
              <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase sticky top-0">
                <tr>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3">Alert Title</th>
                  <th className="px-4 py-3">Target Endpoint</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Assigned To</th>
                  <th className="px-4 py-3">Created</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 font-medium">
                {items.map((alert) => {
                  const statusLower = alert.status.toLowerCase();
                  return (
                    <tr key={alert.id} className="hover:bg-surface-container-high/40 transition-colors">
                      <td className="px-4 py-3">{getSeverityBadge(alert.severity)}</td>
                      <td className="px-4 py-3 font-bold text-on-surface">
                        <button
                          onClick={() => onViewDetails(alert.id)}
                          className="hover:underline text-left text-primary font-bold"
                        >
                          {alert.title}
                        </button>
                      </td>
                      <td className="px-4 py-3 font-bold text-on-surface">
                        <div className="flex items-center gap-1.5">
                          <Monitor className="h-3.5 w-3.5 text-on-surface-variant" />
                          {alert.endpoint_id ? (
                            <Link to={`/endpoints/${alert.endpoint_id}`} className="hover:underline text-primary">
                              {alert.endpoint_name}
                            </Link>
                          ) : (
                            <span>{alert.endpoint_name}</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 font-mono font-bold text-on-surface-variant">{alert.category}</td>
                      <td className="px-4 py-3">{getStatusBadge(alert.status)}</td>
                      <td className="px-4 py-3 font-semibold text-on-surface">
                        {alert.assigned_analyst || <span className="text-on-surface-variant/50">Unassigned</span>}
                      </td>
                      <td className="px-4 py-3 font-mono text-on-surface-variant text-[11px]">
                        {new Date(alert.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1">
                          {/* View Details */}
                          <button
                            onClick={() => onViewDetails(alert.id)}
                            className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-primary"
                            title="View Alert Details"
                          >
                            <Eye className="h-3.5 w-3.5" />
                          </button>

                          {/* Acknowledge (if active) */}
                          {statusLower === "active" && (
                            <button
                              onClick={() => onAcknowledge(alert.id)}
                              disabled={isMutating}
                              className="p-1.5 bg-warning/15 hover:bg-warning/25 border border-warning/30 rounded text-warning"
                              title="Acknowledge Alert"
                            >
                              <Eye className="h-3.5 w-3.5" />
                            </button>
                          )}

                          {/* Resolve (if active or acknowledged) */}
                          {statusLower !== "resolved" && (
                            <button
                              onClick={() => onResolve(alert.id)}
                              disabled={isMutating}
                              className="p-1.5 bg-success/15 hover:bg-success/25 border border-success/30 rounded text-success"
                              title="Resolve Alert"
                            >
                              <CheckCircle2 className="h-3.5 w-3.5" />
                            </button>
                          )}

                          {/* Reopen (if resolved) */}
                          {statusLower === "resolved" && (
                            <button
                              onClick={() => onReopen(alert.id)}
                              disabled={isMutating}
                              className="p-1.5 bg-error/15 hover:bg-error/25 border border-error/30 rounded text-error"
                              title="Reopen Alert"
                            >
                              <RotateCcw className="h-3.5 w-3.5" />
                            </button>
                          )}

                          {/* Assign Analyst */}
                          <button
                            onClick={() => onAssign(alert.id)}
                            disabled={isMutating}
                            className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-on-surface-variant"
                            title="Assign Analyst"
                          >
                            <UserPlus className="h-3.5 w-3.5" />
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
              Showing <strong className="text-on-surface">{items.length}</strong> of <strong className="text-on-surface">{total}</strong> alerts
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
