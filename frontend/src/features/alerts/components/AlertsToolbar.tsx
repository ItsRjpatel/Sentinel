import React from "react";
import { Search, RefreshCw, Filter, ShieldAlert } from "lucide-react";

interface AlertsToolbarProps {
  search: string;
  onSearchChange: (v: string) => void;
  severityFilter: string;
  onSeverityFilterChange: (v: string) => void;
  statusFilter: string;
  onStatusFilterChange: (v: string) => void;
  onRefresh: () => void;
  isFetching: boolean;
}

const SEVERITY_OPTIONS = [
  { value: "ALL", label: "All Severities" },
  { value: "CRITICAL", label: "Critical" },
  { value: "HIGH", label: "High" },
  { value: "MEDIUM", label: "Medium" },
  { value: "LOW", label: "Low" },
];

const STATUS_OPTIONS = [
  { value: "ALL", label: "All Statuses" },
  { value: "ACTIVE", label: "Active" },
  { value: "ACKNOWLEDGED", label: "Acknowledged" },
  { value: "RESOLVED", label: "Resolved" },
];

export const AlertsToolbar = React.memo(function AlertsToolbar({
  search,
  onSearchChange,
  severityFilter,
  onSeverityFilterChange,
  statusFilter,
  onStatusFilterChange,
  onRefresh,
  isFetching,
}: AlertsToolbarProps) {
  return (
    <div className="bg-surface-container-low border border-outline-variant/60 rounded-xl p-3 flex flex-col lg:flex-row lg:items-center justify-between gap-3 shadow-xs">
      {/* Left Search & Filter inputs */}
      <div className="flex flex-wrap items-center gap-2 flex-1">
        {/* Search */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-high rounded-lg border border-outline-variant/40 focus-within:border-primary transition-colors min-w-[240px] flex-1 max-w-sm">
          <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search title, category, description, endpoint..."
            className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>

        {/* Severity Dropdown */}
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

        {/* Status Dropdown */}
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

      {/* Right Refresh */}
      <button
        onClick={onRefresh}
        disabled={isFetching}
        className="p-2 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors disabled:opacity-50 flex items-center gap-1.5"
        title="Refresh Alerts"
      >
        <RefreshCw className={`h-4 w-4 ${isFetching ? "animate-spin text-primary" : ""}`} />
        <span>Refresh</span>
      </button>
    </div>
  );
});
