import { useState, useEffect, useCallback } from "react";
import { Plus, RotateCw, Laptop, X, Shield, Copy, Check } from "lucide-react";
import { EndpointsSummaryCards } from "../components/EndpointsSummaryCards";
import { EndpointsToolbar } from "../components/EndpointsToolbar";
import { EndpointsBulkActionBar } from "../components/EndpointsBulkActionBar";
import { EndpointsTable } from "../components/EndpointsTable";
import { useEndpoints } from "../api/endpointsApi";
import type { EndpointsQueryParams } from "../api/endpointsApi";

const LOCAL_STORAGE_KEY = "sentinel_endpoints_preferences_v1";

interface PersistedState {
  pageSize: number;
  sortBy: string;
  sortOrder: "asc" | "desc";
  statusFilter: string;
  osFilter: string;
  visibleColumns: Record<string, boolean>;
}

export function EndpointsPage() {
  // 1. Load initial state from LocalStorage or fallbacks
  const getInitialState = (): PersistedState => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.warn("Failed to load endpoints preferences from localStorage", e);
    }
    return {
      pageSize: 20,
      sortBy: "last_seen",
      sortOrder: "desc",
      statusFilter: "all",
      osFilter: "all",
      visibleColumns: {},
    };
  };

  const initial = getInitialState();

  const [queryParams, setQueryParams] = useState<EndpointsQueryParams>({
    page: 1,
    page_size: initial.pageSize,
    search: "",
    status: initial.statusFilter,
    os: initial.osFilter,
    sort_by: initial.sortBy,
    sort_order: initial.sortOrder,
  });

  const [visibleColumns, setVisibleColumns] = useState<Record<string, boolean>>(initial.visibleColumns);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [enrollModalOpen, setEnrollModalOpen] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);

  // 2. Persist state changes to LocalStorage
  useEffect(() => {
    const stateToSave: PersistedState = {
      pageSize: queryParams.page_size || 20,
      sortBy: queryParams.sort_by || "last_seen",
      sortOrder: queryParams.sort_order || "desc",
      statusFilter: queryParams.status || "all",
      osFilter: queryParams.os || "all",
      visibleColumns,
    };
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(stateToSave));
    } catch (e) {
      console.warn("Failed to save endpoints preferences to localStorage", e);
    }
  }, [queryParams, visibleColumns]);

  // 3. TanStack Query
  const { data, isLoading, isError, refetch } = useEndpoints(queryParams);

  const handleParamsChange = useCallback((newParams: Partial<EndpointsQueryParams>) => {
    setQueryParams((prev) => ({ ...prev, ...newParams }));
  }, []);

  const handleColumnToggle = useCallback((columnKey: string) => {
    setVisibleColumns((prev) => ({
      ...prev,
      [columnKey]: prev[columnKey] === false ? true : false,
    }));
  }, []);

  const handleToggleSelectAll = useCallback(() => {
    const items = data?.items || [];
    if (items.length === 0) return;

    const allCurrentIds = items.map((i) => i.id);
    const isAllSelected = allCurrentIds.every((id) => selectedIds.includes(id));

    if (isAllSelected) {
      setSelectedIds((prev) => prev.filter((id) => !allCurrentIds.includes(id)));
    } else {
      setSelectedIds((prev) => Array.from(new Set([...prev, ...allCurrentIds])));
    }
  }, [data, selectedIds]);

  const handleToggleSelectId = useCallback((id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  }, []);

  const handleCopyCommand = () => {
    navigator.clipboard.writeText("powershell -ExecutionPolicy Bypass -Command \"Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/agent/deploy.ps1' -OutFile 'install.ps1'; .\\install.ps1 -Server 'http://localhost:8000'\"");
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* HEADER SECTION */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-outline-variant/40 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <Laptop className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Endpoints</h1>
          </div>
          <p className="text-xs text-on-surface-variant mt-0.5 font-medium">
            Manage and monitor enrolled enterprise endpoints.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setEnrollModalOpen(true)}
            className="px-3.5 py-1.5 bg-primary text-on-primary rounded-md text-xs font-bold flex items-center gap-1.5 hover:opacity-90 transition-opacity shadow-sm"
          >
            <Plus className="h-4 w-4" />
            <span>+ Enroll Endpoint</span>
          </button>
          <button
            onClick={() => refetch()}
            className="px-3 py-1.5 bg-surface-container-high text-on-surface rounded-md text-xs font-bold flex items-center gap-1.5 border border-outline-variant/40 hover:bg-surface-container-highest transition-colors"
          >
            <RotateCw className="h-3.5 w-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* ROW 1: Summary Cards */}
      <EndpointsSummaryCards params={queryParams} onParamsChange={handleParamsChange} />

      {/* ROW 2: Enterprise Toolbar */}
      <EndpointsToolbar
        params={queryParams}
        onParamsChange={handleParamsChange}
        onRefresh={refetch}
        visibleColumns={visibleColumns}
        onColumnToggle={handleColumnToggle}
      />

      {/* Bulk Action Bar (Rendered if items selected) */}
      <EndpointsBulkActionBar
        selectedCount={selectedIds.length}
        onClearSelection={() => setSelectedIds([])}
      />

      {/* ROW 3: Enterprise Data Table */}
      <EndpointsTable
        data={data}
        isLoading={isLoading}
        isError={isError}
        params={queryParams}
        onParamsChange={handleParamsChange}
        onRefresh={refetch}
        visibleColumns={visibleColumns}
        selectedIds={selectedIds}
        onToggleSelectAll={handleToggleSelectAll}
        onToggleSelectId={handleToggleSelectId}
      />

      {/* Enroll Endpoint Modal */}
      {enrollModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-xs">
          <div className="bg-surface-container-low border border-outline-variant rounded-xl max-w-lg w-full p-5 space-y-4 shadow-2xl animate-scaleIn">
            <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                <h3 className="text-body-md font-extrabold text-on-surface">Enroll New Host Endpoint</h3>
              </div>
              <button
                onClick={() => setEnrollModalOpen(false)}
                className="p-1 rounded-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-on-surface-variant">
              <p>Run the following automated PowerShell deployment command on target host machines to enroll them into Sentinel X EDR:</p>
              
              <div className="p-3 bg-surface-container-high rounded-md border border-outline-variant/50 font-mono text-[11px] text-on-surface relative">
                <code>powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/agent/deploy.ps1' -OutFile 'install.ps1'; .\install.ps1 -Server 'http://localhost:8000'"</code>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  onClick={handleCopyCommand}
                  className="px-3 py-1.5 bg-primary text-on-primary rounded text-xs font-bold inline-flex items-center gap-1.5"
                >
                  {copiedKey ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                  <span>{copiedKey ? "Copied!" : "Copy Deployment Command"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
