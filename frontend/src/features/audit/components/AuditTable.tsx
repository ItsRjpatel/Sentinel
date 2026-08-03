import React from "react";
import { Link } from "react-router-dom";
import {
  Monitor,
  AlertOctagon,
  AlertTriangle,
  Info,
  CheckCircle2,
  XCircle,
  Eye,
  ChevronLeft,
  ChevronRight,
  User,
  Globe,
} from "lucide-react";
import { Card, Badge, LoadingSkeleton, EmptyState } from "../../../components/ui";
import type { AuditLogItem } from "../types/auditTypes";

interface AuditTableProps {
  items: AuditLogItem[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (p: number) => void;
  isLoading: boolean;
  onViewDetails: (id: string) => void;
}

export const AuditTable = React.memo(function AuditTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
  onViewDetails,
}: AuditTableProps) {
  if (isLoading) {
    return <LoadingSkeleton height={400} />;
  }

  const totalPages = Math.ceil(total / pageSize) || 1;

  const getSeverityBadge = (sev: string) => {
    switch (sev.toUpperCase()) {
      case "CRITICAL":
        return (
          <Badge variant="error" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <AlertOctagon className="h-3 w-3" /> Critical
          </Badge>
        );
      case "WARNING":
        return (
          <Badge variant="warning" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <AlertTriangle className="h-3 w-3" /> Warning
          </Badge>
        );
      default:
        return (
          <Badge variant="info" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <Info className="h-3 w-3" /> Info
          </Badge>
        );
    }
  };

  const getStatusBadge = (stat: string) => {
    switch (stat.toUpperCase()) {
      case "SUCCESS":
        return (
          <Badge variant="success" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <CheckCircle2 className="h-3 w-3" /> Success
          </Badge>
        );
      case "FAILED":
      case "DENIED":
        return (
          <Badge variant="error" size="sm" className="font-bold flex items-center gap-1 w-fit">
            <XCircle className="h-3 w-3" /> Failed
          </Badge>
        );
      default:
        return <Badge variant="default" size="sm">{stat}</Badge>;
    }
  };

  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
      {items.length === 0 ? (
        <div className="py-16 flex items-center justify-center">
          <EmptyState
            title="No Audit Logs Found"
            description="No system audit records match the selected search or filter criteria."
            className="border-none bg-transparent"
          />
        </div>
      ) : (
        <>
          <div className="overflow-x-auto scrollbar-none">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
              <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase sticky top-0">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3">Actor</th>
                  <th className="px-4 py-3">Module</th>
                  <th className="px-4 py-3">Action</th>
                  <th className="px-4 py-3">Target Endpoint</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">IP Address</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 font-medium">
                {items.map((log) => (
                  <tr key={log.id} className="hover:bg-surface-container-high/40 transition-colors">
                    <td className="px-4 py-3 font-mono text-on-surface-variant text-[11px]">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">{getSeverityBadge(log.severity)}</td>
                    <td className="px-4 py-3 font-bold text-on-surface">
                      <div className="flex items-center gap-1.5">
                        <User className="h-3.5 w-3.5 text-primary" />
                        <span>{log.actor}</span>
                        <span className="text-[10px] text-on-surface-variant/70 uppercase font-mono">({log.actor_type})</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 font-mono font-bold text-on-surface">{log.module}</td>
                    <td className="px-4 py-3 font-extrabold text-primary font-mono">{log.action}</td>
                    <td className="px-4 py-3 font-bold text-on-surface">
                      {log.endpoint_hostname ? (
                        <div className="flex items-center gap-1.5">
                          <Monitor className="h-3.5 w-3.5 text-on-surface-variant" />
                          {log.endpoint_id ? (
                            <Link to={`/endpoints/${log.endpoint_id}`} className="hover:underline text-primary">
                              {log.endpoint_hostname}
                            </Link>
                          ) : (
                            <span>{log.endpoint_hostname}</span>
                          )}
                        </div>
                      ) : (
                        <span className="text-on-surface-variant/50">System Wide</span>
                      )}
                    </td>
                    <td className="px-4 py-3">{getStatusBadge(log.status)}</td>
                    <td className="px-4 py-3 font-mono text-on-surface-variant">
                      <div className="flex items-center gap-1">
                        <Globe className="h-3 w-3 text-on-surface-variant/60" />
                        {log.ip_address || "Internal"}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => onViewDetails(log.id)}
                        className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-primary"
                        title="View Full Audit Event Details"
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-surface-container-high/60 border-t border-outline-variant/40 text-xs">
            <span className="text-on-surface-variant font-medium">
              Showing <strong className="text-on-surface">{items.length}</strong> of <strong className="text-on-surface">{total}</strong> audit events
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
