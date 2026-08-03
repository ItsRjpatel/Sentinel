import React from "react";
import { Search, RefreshCw, Filter, ShieldAlert, Download, FileSpreadsheet } from "lucide-react";
import type { AuditLogItem } from "../types/auditTypes";

interface AuditToolbarProps {
  search: string;
  onSearchChange: (v: string) => void;
  severityFilter: string;
  onSeverityFilterChange: (v: string) => void;
  moduleFilter: string;
  onModuleFilterChange: (v: string) => void;
  statusFilter: string;
  onStatusFilterChange: (v: string) => void;
  onRefresh: () => void;
  isFetching: boolean;
  items: AuditLogItem[];
}

const SEVERITY_OPTIONS = [
  { value: "ALL", label: "All Severities" },
  { value: "CRITICAL", label: "Critical" },
  { value: "WARNING", label: "Warning" },
  { value: "INFORMATION", label: "Information" },
];

const MODULE_OPTIONS = [
  { value: "ALL", label: "All Modules" },
  { value: "AUTHENTICATION", label: "AUTHENTICATION" },
  { value: "REMOTE_COMMANDS", label: "REMOTE_COMMANDS" },
  { value: "SECURITY_ALERTS", label: "SECURITY_ALERTS" },
  { value: "ENDPOINT_MANAGEMENT", label: "ENDPOINT_MANAGEMENT" },
];

const STATUS_OPTIONS = [
  { value: "ALL", label: "All Statuses" },
  { value: "SUCCESS", label: "SUCCESS" },
  { value: "FAILED", label: "FAILED" },
];

export const AuditToolbar = React.memo(function AuditToolbar({
  search,
  onSearchChange,
  severityFilter,
  onSeverityFilterChange,
  moduleFilter,
  onModuleFilterChange,
  statusFilter,
  onStatusFilterChange,
  onRefresh,
  isFetching,
  items,
}: AuditToolbarProps) {
  const exportCsv = () => {
    if (items.length === 0) {
      alert("No data available to export.");
      return;
    }
    const headers = ["ID", "Timestamp", "Actor", "ActorType", "Module", "Action", "Resource", "Severity", "Status", "IPAddress", "CorrelationID"];
    const rows = items.map((l) => [
      l.id,
      l.timestamp,
      l.actor,
      l.actor_type,
      l.module,
      l.action,
      l.resource || "",
      l.severity,
      l.status,
      l.ip_address || "",
      l.correlation_id || "",
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", `audit-logs-${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const exportJson = () => {
    if (items.length === 0) {
      alert("No data available to export.");
      return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(items, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", dataStr);
    link.setAttribute("download", `audit-logs-${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="bg-surface-container-low border border-outline-variant/60 rounded-xl p-3 flex flex-col lg:flex-row lg:items-center justify-between gap-3 shadow-xs">
      {/* Left Inputs */}
      <div className="flex flex-wrap items-center gap-2 flex-1">
        {/* Search */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-high rounded-lg border border-outline-variant/40 focus-within:border-primary transition-colors min-w-[240px] flex-1 max-w-sm">
          <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search action, actor, module, correlation ID..."
            className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>

        {/* Severity */}
        <div className="flex items-center gap-1.5 bg-surface-container-high px-2 py-1 rounded-lg border border-outline-variant/40 text-xs font-bold text-on-surface-variant">
          <ShieldAlert className="h-3.5 w-3.5" />
          <select
            value={severityFilter}
            onChange={(e) => onSeverityFilterChange(e.target.value)}
            className="bg-transparent text-on-surface focus:outline-none cursor-pointer font-bold"
          >
            {SEVERITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-surface-container-low text-on-surface">
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Module */}
        <div className="flex items-center gap-1.5 bg-surface-container-high px-2 py-1 rounded-lg border border-outline-variant/40 text-xs font-bold text-on-surface-variant">
          <Filter className="h-3.5 w-3.5" />
          <select
            value={moduleFilter}
            onChange={(e) => onModuleFilterChange(e.target.value)}
            className="bg-transparent text-on-surface focus:outline-none cursor-pointer font-bold"
          >
            {MODULE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-surface-container-low text-on-surface">
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Status */}
        <div className="flex items-center gap-1.5 bg-surface-container-high px-2 py-1 rounded-lg border border-outline-variant/40 text-xs font-bold text-on-surface-variant">
          <Filter className="h-3.5 w-3.5" />
          <select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="bg-transparent text-on-surface focus:outline-none cursor-pointer font-bold"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-surface-container-low text-on-surface">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={onRefresh}
          disabled={isFetching}
          className="p-2 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors disabled:opacity-50"
          title="Refresh Logs"
        >
          <RefreshCw className={`h-4 w-4 ${isFetching ? "animate-spin text-primary" : ""}`} />
        </button>

        <button
          onClick={exportCsv}
          className="px-3 py-1.5 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors flex items-center gap-1"
          title="Export as CSV"
        >
          <FileSpreadsheet className="h-3.5 w-3.5 text-success" /> CSV
        </button>

        <button
          onClick={exportJson}
          className="px-3 py-1.5 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors flex items-center gap-1"
          title="Export as JSON"
        >
          <Download className="h-3.5 w-3.5 text-primary" /> JSON
        </button>
      </div>
    </div>
  );
});
