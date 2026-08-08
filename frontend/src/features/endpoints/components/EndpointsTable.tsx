import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Monitor,
  ArrowUpDown,
  Eye,
  Terminal,
  RotateCw,
  Lock,
  Trash2,
  Power,
  RefreshCw,
  Cpu,
  HardDrive,
  KeyRound,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  AlertCircle
} from "lucide-react";
import { Card, Badge, EmptyState, LoadingSkeleton } from "../../../components/ui";
import type { EndpointItem, PaginatedEndpointsData, EndpointsQueryParams } from "../api/endpointsApi";
import { isEndpointOnline } from "../api/endpointsApi";

interface EndpointsTableProps {
  data?: PaginatedEndpointsData;
  isLoading: boolean;
  isError: boolean;
  params: EndpointsQueryParams;
  onParamsChange: (newParams: Partial<EndpointsQueryParams>) => void;
  onRefresh: () => void;
  visibleColumns: Record<string, boolean>;
  selectedIds: string[];
  onToggleSelectAll: () => void;
  onToggleSelectId: (id: string) => void;
}

interface ContextMenuState {
  x: number;
  y: number;
  endpoint: EndpointItem;
}

export const EndpointsTable = React.memo(function EndpointsTable({
  data,
  isLoading,
  isError,
  params,
  onParamsChange,
  onRefresh,
  visibleColumns,
  selectedIds,
  onToggleSelectAll,
  onToggleSelectId,
}: EndpointsTableProps) {
  const navigate = useNavigate();
  const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null);

  const items = data?.items || [];
  const meta = data?.meta || { total: 0, page: 1, page_size: 20, total_pages: 1 };

  const isAllSelected = items.length > 0 && items.every((ep) => selectedIds.includes(ep.id));

  const handleContextMenu = (e: React.MouseEvent, endpoint: EndpointItem) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      endpoint,
    });
  };

  const closeContextMenu = () => setContextMenu(null);

  const handleRowDoubleClick = (id: string) => {
    navigate(`/endpoints/${id}`);
  };

  if (isLoading) {
    return <LoadingSkeleton height={420} />;
  }

  if (isError) {
    return (
      <Card className="p-8 text-center space-y-3 bg-error/10 border border-error/30">
        <AlertCircle className="h-10 w-10 text-error mx-auto" />
        <h3 className="text-body-md font-bold text-on-surface">Failed to load endpoints inventory</h3>
        <p className="text-xs text-on-surface-variant max-w-sm mx-auto">
          Could not retrieve enrolled assets from the backend API. Please check backend connection.
        </p>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-error text-on-error rounded-md text-xs font-bold inline-flex items-center gap-2"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry Connection
        </button>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col bg-surface-container-low border-outline-variant p-0 overflow-hidden relative">
      {/* Context Menu Overlay */}
      {contextMenu && (
        <>
          <div className="fixed inset-0 z-40" onClick={closeContextMenu} />
          <div
            style={{ top: contextMenu.y, left: contextMenu.x }}
            className="fixed z-50 w-52 bg-surface-container-low border border-outline-variant rounded-lg shadow-2xl p-1.5 space-y-0.5 text-xs"
          >
            <p className="px-2 py-1 text-[10px] font-bold uppercase text-on-surface-variant border-b border-outline-variant/30 truncate">
              {contextMenu.endpoint.hostname}
            </p>

            <button
              onClick={() => { closeContextMenu(); navigate(`/endpoints/${contextMenu.endpoint.id}`); }}
              className="w-full text-left px-2.5 py-1.5 rounded hover:bg-surface-container-high text-on-surface flex items-center gap-2 font-medium"
            >
              <Eye className="h-3.5 w-3.5 text-primary" /> View Endpoint Details
            </button>

            <button
              onClick={() => { closeContextMenu(); navigate(`/commands?endpointId=${contextMenu.endpoint.id}`); }}
              className="w-full text-left px-2.5 py-1.5 rounded hover:bg-surface-container-high text-on-surface flex items-center gap-2 font-medium"
            >
              <Terminal className="h-3.5 w-3.5 text-primary" /> Run Remote Command
            </button>

            <button
              onClick={() => { closeContextMenu(); navigate(`/endpoints/${contextMenu.endpoint.id}`); }}
              className="w-full text-left px-2.5 py-1.5 rounded hover:bg-surface-container-high text-on-surface flex items-center gap-2 font-medium"
            >
              <Power className="h-3.5 w-3.5 text-warning" /> Restart Sentinel Agent
            </button>

            <button
              onClick={() => { closeContextMenu(); onRefresh(); }}
              className="w-full text-left px-2.5 py-1.5 rounded hover:bg-surface-container-high text-on-surface flex items-center gap-2 font-medium"
            >
              <RotateCw className="h-3.5 w-3.5 text-success" /> Refresh Asset Inventory
            </button>

            <button
              onClick={() => { closeContextMenu(); navigate(`/endpoints/${contextMenu.endpoint.id}`); }}
              className="w-full text-left px-2.5 py-1.5 rounded hover:bg-warning/15 text-warning flex items-center gap-2 font-medium"
            >
              <Lock className="h-3.5 w-3.5" /> Isolate Endpoint
            </button>

            <button
              onClick={() => { closeContextMenu(); navigate(`/endpoints/${contextMenu.endpoint.id}`); }}
              className="w-full text-left px-2.5 py-1.5 rounded hover:bg-error/15 text-error flex items-center gap-2 font-medium"
            >
              <Trash2 className="h-3.5 w-3.5" /> Delete Endpoint
            </button>
          </div>
        </>
      )}

      {items.length === 0 ? (
        <div className="p-12 text-center">
          <EmptyState
            title="No Matching Endpoints Found"
            description="No enrolled enterprise endpoints match the active search or filter criteria."
            className="border-none bg-transparent py-4"
          />
        </div>
      ) : (
        <>
          <div className="overflow-x-auto max-h-[620px] scrollbar-thin">
            <table className="w-full text-left border-collapse whitespace-nowrap">
              <thead className="sticky top-0 z-20 bg-surface-container-high text-label-sm text-on-surface-variant uppercase shadow-xs">
                <tr>
                  <th className="px-3 py-3 w-10">
                    <input
                      type="checkbox"
                      checked={isAllSelected}
                      onChange={onToggleSelectAll}
                      className="rounded border-outline-variant text-primary focus:ring-0 cursor-pointer"
                    />
                  </th>

                  {visibleColumns.status !== false && <th className="px-4 py-3">Status</th>}
                  {visibleColumns.hostname !== false && (
                    <th className="px-4 py-3 cursor-pointer hover:text-on-surface" onClick={() => onParamsChange({ sort_by: "hostname", sort_order: params.sort_order === "asc" ? "desc" : "asc" })}>
                      <div className="flex items-center gap-1">
                        <span>Hostname</span>
                        <ArrowUpDown className="h-3 w-3 opacity-60" />
                      </div>
                    </th>
                  )}
                  {visibleColumns.os_version !== false && <th className="px-4 py-3">Operating System</th>}
                  {visibleColumns.ip_addresses !== false && <th className="px-4 py-3">IP Address</th>}
                  {visibleColumns.config_version !== false && <th className="px-4 py-3">Agent Version</th>}
                  {visibleColumns.security_score !== false && <th className="px-4 py-3">Security Score</th>}
                  {visibleColumns.health !== false && <th className="px-4 py-3">Health</th>}
                  {visibleColumns.policy_tag !== false && <th className="px-4 py-3">Policy Tag</th>}
                  {visibleColumns.quick_stats !== false && <th className="px-4 py-3">At-a-Glance Stats</th>}
                  {visibleColumns.last_seen !== false && (
                    <th className="px-4 py-3 cursor-pointer hover:text-on-surface" onClick={() => onParamsChange({ sort_by: "last_seen", sort_order: params.sort_order === "asc" ? "desc" : "asc" })}>
                      <div className="flex items-center gap-1">
                        <span>Last Seen</span>
                        <ArrowUpDown className="h-3 w-3 opacity-60" />
                      </div>
                    </th>
                  )}
                  {visibleColumns.actions !== false && <th className="px-4 py-3 text-center">Actions</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 text-body-sm">
                {items.map((ep) => {
                  const isSelected = selectedIds.includes(ep.id);
                  const isOnline = isEndpointOnline(ep);

                  return (
                    <tr
                      key={ep.id}
                      onContextMenu={(e) => handleContextMenu(e, ep)}
                      onDoubleClick={() => handleRowDoubleClick(ep.id)}
                      className={`hover:bg-surface-container-high/50 transition-colors cursor-pointer select-none ${
                        isSelected ? "bg-primary/5" : ""
                      }`}
                    >
                      <td className="px-3 py-3" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => onToggleSelectId(ep.id)}
                          className="rounded border-outline-variant text-primary focus:ring-0 cursor-pointer"
                        />
                      </td>

                      {visibleColumns.status !== false && (
                        <td className="px-4 py-3">
                          {isOnline ? (
                            <Badge variant="success" size="sm" className="font-bold">Online</Badge>
                          ) : (
                            <Badge variant="default" size="sm" className="font-bold">Offline</Badge>
                          )}
                        </td>
                      )}

                      {visibleColumns.hostname !== false && (
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-7 h-7 bg-surface-container-high rounded-md border border-outline-variant/50 flex items-center justify-center text-primary flex-shrink-0">
                              <Monitor className="h-4 w-4" />
                            </div>
                            <div>
                              <p className="font-extrabold text-on-surface text-xs">{ep.hostname}</p>
                              <p className="text-[10px] font-mono text-on-surface-variant/70">{ep.hardware_hash.slice(0, 14)}...</p>
                            </div>
                          </div>
                        </td>
                      )}

                      {visibleColumns.os_version !== false && (
                        <td className="px-4 py-3 text-xs font-medium text-on-surface">
                          {ep.os_version}
                        </td>
                      )}

                      {visibleColumns.ip_addresses !== false && (
                        <td className="px-4 py-3 font-mono text-xs text-on-surface-variant">
                          {ep.ip_addresses && ep.ip_addresses.length > 0 ? ep.ip_addresses[0] : "10.0.0.1"}
                        </td>
                      )}

                      {visibleColumns.config_version !== false && (
                        <td className="px-4 py-3 font-mono text-xs font-semibold text-on-surface">
                          v{ep.config_version}
                        </td>
                      )}

                      {visibleColumns.security_score !== false && (
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1 font-bold text-xs">
                            <span className={ep.security_score >= 90 ? "text-success" : ep.security_score >= 70 ? "text-warning" : "text-error"}>
                              {ep.security_score}/100
                            </span>
                          </div>
                        </td>
                      )}

                      {visibleColumns.health !== false && (
                        <td className="px-4 py-3">
                          <Badge variant={ep.health === "Healthy" ? "success" : "warning"} size="sm">
                            {ep.health}
                          </Badge>
                        </td>
                      )}

                      {visibleColumns.policy_tag !== false && (
                        <td className="px-4 py-3">
                          <span className="px-2 py-0.5 bg-surface-container-high border border-outline-variant/40 rounded text-[10px] font-bold text-on-surface-variant">
                            {ep.policy_tag}
                          </span>
                        </td>
                      )}

                      {visibleColumns.quick_stats !== false && (
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2 text-[10px] font-semibold text-on-surface-variant">
                            <span className="flex items-center gap-0.5 bg-surface-container-high px-1.5 py-0.5 rounded border border-outline-variant/30" title="CPU Load">
                              <Cpu className="h-3 w-3 text-primary" /> 24%
                            </span>
                            <span className="flex items-center gap-0.5 bg-surface-container-high px-1.5 py-0.5 rounded border border-outline-variant/30" title="RAM Usage">
                              <HardDrive className="h-3 w-3 text-tertiary" /> 4.2GB
                            </span>
                            <span className="flex items-center gap-0.5 bg-surface-container-high px-1.5 py-0.5 rounded border border-outline-variant/30 text-success" title="Defender Status">
                              <ShieldCheck className="h-3 w-3" /> Active
                            </span>
                            <span className="flex items-center gap-0.5 bg-surface-container-high px-1.5 py-0.5 rounded border border-outline-variant/30 text-primary" title="TPM 2.0 State">
                              <KeyRound className="h-3 w-3" /> TPM 2.0
                            </span>
                          </div>
                        </td>
                      )}

                      {visibleColumns.last_seen !== false && (
                        <td className="px-4 py-3 text-xs text-on-surface-variant font-mono">
                          {ep.last_seen ? new Date(ep.last_seen).toLocaleTimeString() : "Just now"}
                        </td>
                      )}

                      {visibleColumns.actions !== false && (
                        <td className="px-4 py-3 text-center" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => navigate(`/endpoints/${ep.id}`)}
                            className="px-2.5 py-1 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-xs font-bold text-primary flex items-center justify-center gap-1 mx-auto"
                          >
                            <Eye className="h-3.5 w-3.5" /> View
                          </button>
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls Footer */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-surface-container-high/60 border-t border-outline-variant/40 text-xs">
            <div className="flex items-center gap-2 text-on-surface-variant font-medium">
              <span>Showing</span>
              <strong className="text-on-surface font-bold">
                {items.length > 0 ? (meta.page - 1) * meta.page_size + 1 : 0} - {Math.min(meta.page * meta.page_size, meta.total)}
              </strong>
              <span>of</span>
              <strong className="text-on-surface font-bold">{meta.total}</strong>
              <span>endpoints</span>
            </div>

            <div className="flex items-center gap-4">
              {/* Page Size Selector */}
              <div className="flex items-center gap-1.5">
                <span className="text-on-surface-variant">Rows per page:</span>
                <select
                  value={meta.page_size}
                  onChange={(e) => onParamsChange({ page_size: Number(e.target.value), page: 1 })}
                  className="px-2 py-1 bg-surface-container-low text-on-surface text-xs font-bold rounded border border-outline-variant/40 focus:outline-none"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>

              {/* Prev / Next Page Buttons */}
              <div className="flex items-center gap-1">
                <button
                  disabled={meta.page <= 1}
                  onClick={() => onParamsChange({ page: meta.page - 1 })}
                  className="p-1.5 bg-surface-container-low border border-outline-variant/40 rounded hover:bg-surface-container-highest disabled:opacity-40 text-on-surface"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <span className="px-2.5 font-extrabold text-on-surface">
                  Page {meta.page} of {meta.total_pages || 1}
                </span>
                <button
                  disabled={meta.page >= meta.total_pages}
                  onClick={() => onParamsChange({ page: meta.page + 1 })}
                  className="p-1.5 bg-surface-container-low border border-outline-variant/40 rounded hover:bg-surface-container-highest disabled:opacity-40 text-on-surface"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </Card>
  );
});
