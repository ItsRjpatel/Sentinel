import React from "react";
import { Search, RefreshCw, Terminal, Filter } from "lucide-react";
import { Button } from "../../../components/ui";

interface CommandsToolbarProps {
  search: string;
  onSearchChange: (v: string) => void;
  statusFilter: string;
  onStatusFilterChange: (v: string) => void;
  typeFilter: string;
  onTypeFilterChange: (v: string) => void;
  onRefresh: () => void;
  onOpenBulkModal: () => void;
  isFetching: boolean;
}

const STATUS_OPTIONS = [
  { value: "ALL", label: "All Statuses" },
  { value: "PENDING", label: "Pending" },
  { value: "RUNNING", label: "Running" },
  { value: "SCHEDULED", label: "Scheduled" },
  { value: "SUCCESS", label: "Success" },
  { value: "FAILED", label: "Failed" },
  { value: "TIMEOUT", label: "Timed Out" },
  { value: "CANCELLED", label: "Cancelled" },
];

const TYPE_OPTIONS = [
  { value: "ALL", label: "All Types" },
  { value: "PING", label: "PING" },
  { value: "RUN_INVENTORY", label: "RUN_INVENTORY" },
  { value: "REFRESH_POLICY", label: "REFRESH_POLICY" },
  { value: "RESTART_SERVICE", label: "RESTART_SERVICE" },
  { value: "RESTART_AGENT", label: "RESTART_AGENT" },
  { value: "SYNC_NOW", label: "SYNC_NOW" },
  { value: "SYSTEM_SCAN", label: "SYSTEM_SCAN" },
  { value: "AGENT_UPDATE", label: "AGENT_UPDATE" },
  { value: "PATCH_INSTALL", label: "PATCH_INSTALL" },
  { value: "PROCESS_KILL", label: "PROCESS_KILL" },
];

export const CommandsToolbar = React.memo(function CommandsToolbar({
  search,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  typeFilter,
  onTypeFilterChange,
  onRefresh,
  onOpenBulkModal,
  isFetching,
}: CommandsToolbarProps) {
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
            placeholder="Search command type, host, creator..."
            className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface placeholder:text-on-surface-variant/60"
          />
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

        {/* Command Type Dropdown */}
        <div className="flex items-center gap-1.5 bg-surface-container-high px-2 py-1 rounded-lg border border-outline-variant/40 text-xs font-bold text-on-surface-variant">
          <Terminal className="h-3.5 w-3.5" />
          <select
            value={typeFilter}
            onChange={(e) => onTypeFilterChange(e.target.value)}
            className="bg-transparent text-on-surface focus:outline-none cursor-pointer font-bold"
          >
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-surface-container-low text-on-surface">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Right Action buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={onRefresh}
          disabled={isFetching}
          className="p-2 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors disabled:opacity-50"
          title="Refresh Commands"
        >
          <RefreshCw className={`h-4 w-4 ${isFetching ? "animate-spin text-primary" : ""}`} />
        </button>

        <Button
          onClick={onOpenBulkModal}
          variant="primary"
          size="sm"
          leftIcon={<Terminal className="h-4 w-4" />}
          className="font-extrabold shadow-xs"
        >
          Run Bulk Command
        </Button>
      </div>
    </div>
  );
});
