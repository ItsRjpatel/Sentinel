import React, { useState } from "react";
import { Search, RotateCw, Columns, ChevronDown } from "lucide-react";
import type { EndpointsQueryParams } from "../api/endpointsApi";

interface EndpointsToolbarProps {
  params: EndpointsQueryParams;
  onParamsChange: (newParams: Partial<EndpointsQueryParams>) => void;
  onRefresh: () => void;
  visibleColumns: Record<string, boolean>;
  onColumnToggle: (columnKey: string) => void;
}

export const EndpointsToolbar = React.memo(function EndpointsToolbar({
  params,
  onParamsChange,
  onRefresh,
  visibleColumns,
  onColumnToggle,
}: EndpointsToolbarProps) {
  const [columnsOpen, setColumnsOpen] = useState(false);

  const columnLabels: Record<string, string> = {
    hostname: "Hostname",
    os_version: "Operating System",
    ip_addresses: "IP Address",
    status: "Status",
    health: "Health",
    security_score: "Security Score",
    config_version: "Agent Version",
    policy_tag: "Policy Tag",
    last_seen: "Last Seen",
    quick_stats: "Quick Stats (CPU/RAM/Disk/TPM)",
    actions: "Actions",
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 p-3 bg-surface-container-low border border-outline-variant rounded-xl">
      {/* Search Bar & Filters */}
      <div className="flex flex-wrap items-center gap-2 flex-1">
        {/* Search */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-high rounded-md border border-outline-variant/40 focus-within:border-primary transition-colors flex-1 min-w-[200px] max-w-[360px]">
          <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
          <input
            type="text"
            value={params.search || ""}
            onChange={(e) => onParamsChange({ search: e.target.value, page: 1 })}
            placeholder="Search hostname, IP, hardware..."
            className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>

        {/* Status Filter */}
        <select
          value={params.status || "all"}
          onChange={(e) => onParamsChange({ status: e.target.value, page: 1 })}
          className="px-2.5 py-1.5 bg-surface-container-high text-on-surface text-xs font-semibold rounded-md border border-outline-variant/40 focus:outline-none"
        >
          <option value="all">All Statuses</option>
          <option value="online">Online Only</option>
          <option value="offline">Offline Only</option>
        </select>

        {/* OS Filter */}
        <select
          value={params.os || "all"}
          onChange={(e) => onParamsChange({ os: e.target.value, page: 1 })}
          className="px-2.5 py-1.5 bg-surface-container-high text-on-surface text-xs font-semibold rounded-md border border-outline-variant/40 focus:outline-none"
        >
          <option value="all">All Platforms</option>
          <option value="windows">Windows</option>
          <option value="linux">Linux / Ubuntu</option>
          <option value="macos">macOS</option>
        </select>

        {/* Sort Selector */}
        <select
          value={`${params.sort_by || "last_seen"}_${params.sort_order || "desc"}`}
          onChange={(e) => {
            const [by, order] = e.target.value.split("_");
            onParamsChange({ sort_by: by, sort_order: order as "asc" | "desc" });
          }}
          className="px-2.5 py-1.5 bg-surface-container-high text-on-surface text-xs font-semibold rounded-md border border-outline-variant/40 focus:outline-none"
        >
          <option value="last_seen_desc">Sort: Last Seen (Newest)</option>
          <option value="last_seen_asc">Sort: Last Seen (Oldest)</option>
          <option value="hostname_asc">Sort: Hostname (A-Z)</option>
          <option value="hostname_desc">Sort: Hostname (Z-A)</option>
          <option value="security_score_desc">Sort: Security Rating (High)</option>
          <option value="security_score_asc">Sort: Security Rating (Low)</option>
        </select>
      </div>

      {/* Control Actions: Columns Toggle + Refresh */}
      <div className="flex items-center gap-2">
        {/* Columns Customizer Dropdown */}
        <div className="relative">
          <button
            onClick={() => setColumnsOpen(!columnsOpen)}
            className="px-3 py-1.5 bg-surface-container-high text-on-surface rounded-md text-xs font-bold flex items-center gap-1.5 border border-outline-variant/40 hover:bg-surface-container-highest transition-colors"
          >
            <Columns className="h-3.5 w-3.5" />
            <span>Columns</span>
            <ChevronDown className="h-3.5 w-3.5 opacity-60" />
          </button>

          {columnsOpen && (
            <div className="absolute right-0 mt-1 w-56 bg-surface-container-low border border-outline-variant rounded-lg shadow-xl p-2 z-50 space-y-1">
              <p className="px-2 py-1 text-[10px] font-bold uppercase text-on-surface-variant border-b border-outline-variant/30">
                Toggle Columns
              </p>
              {Object.keys(columnLabels).map((colKey) => (
                <label key={colKey} className="flex items-center gap-2 px-2 py-1 hover:bg-surface-container-high rounded text-xs font-medium text-on-surface cursor-pointer">
                  <input
                    type="checkbox"
                    checked={visibleColumns[colKey] !== false}
                    onChange={() => onColumnToggle(colKey)}
                    className="rounded border-outline-variant text-primary focus:ring-0"
                  />
                  <span>{columnLabels[colKey]}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Manual Refresh */}
        <button
          onClick={onRefresh}
          className="px-3 py-1.5 bg-primary text-on-primary rounded-md text-xs font-bold flex items-center gap-1.5 hover:opacity-90 transition-opacity"
        >
          <RotateCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>
    </div>
  );
});
