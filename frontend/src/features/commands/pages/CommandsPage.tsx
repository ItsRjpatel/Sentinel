import { useState } from "react";
import { Terminal } from "lucide-react";
import { CommandsSummaryCards } from "../components/CommandsSummaryCards";
import { CommandsToolbar } from "../components/CommandsToolbar";
import { CommandsTable } from "../components/CommandsTable";
import { CommandDetailsDrawer } from "../components/CommandDetailsDrawer";
import { BulkCommandModal } from "../components/BulkCommandModal";
import { GlobalWebSocketProvider } from "../../../contexts/GlobalWebSocketProvider";
import { useCommandsList, useRetryCommand, useCancelCommand } from "../api/commandsApi";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";

function CommandsPageContent() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [page, setPage] = useState(1);
  const [selectedDetailsId, setSelectedDetailsId] = useState<string | null>(null);
  const [isBulkModalOpen, setIsBulkModalOpen] = useState(false);

  const { data, isLoading, isFetching, refetch } = useCommandsList({
    status: statusFilter,
    command_type: typeFilter,
    search,
    page,
    page_size: 20,
  });

  const retryMutation = useRetryCommand();
  const cancelMutation = useCancelCommand();

  // Fetch registered endpoints for bulk modal target selection
  const { data: endpointsData } = useQuery({
    queryKey: ["endpoints", "simple_list"],
    queryFn: async () => {
      const res = await apiClient.get("/endpoints?page_size=100");
      const payload = res.data?.data;
      if (Array.isArray(payload)) return payload;
      if (payload && Array.isArray(payload.items)) return payload.items;
      return [];
    },
  });

  const availableEndpoints = (endpointsData || []).map((ep: any) => ({
    id: ep.id,
    hostname: ep.hostname || "Endpoint Host",
  }));

  const handleRetryCommand = async (id: string) => {
    try {
      await retryMutation.mutateAsync(id);
      alert("Command retried successfully and queued for execution!");
    } catch (err: any) {
      alert(`Failed to retry command: ${err.message || "Unknown error"}`);
    }
  };

  const handleCancelCommand = async (id: string) => {
    try {
      await cancelMutation.mutateAsync(id);
      alert("Command cancelled successfully!");
    } catch (err: any) {
      alert(`Failed to cancel command: ${err.message || "Unknown error"}`);
    }
  };

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <Terminal className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Remote Command Center</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Real-time Task Orchestration Engine • WebSocket Live Updates Active
            </p>
          </div>
        </div>
      </div>

      {/* Row 1: Summary Metric Cards */}
      <CommandsSummaryCards
        currentStatus={statusFilter}
        onStatusChange={(v) => {
          setStatusFilter(v);
          setPage(1);
        }}
      />

      {/* Row 2: Enterprise Toolbar */}
      <CommandsToolbar
        search={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        statusFilter={statusFilter}
        onStatusFilterChange={(v) => { setStatusFilter(v); setPage(1); }}
        typeFilter={typeFilter}
        onTypeFilterChange={(v) => { setTypeFilter(v); setPage(1); }}
        onRefresh={() => refetch()}
        onOpenBulkModal={() => setIsBulkModalOpen(true)}
        isFetching={isFetching}
      />

      {/* Row 3: Enterprise Commands Table */}
      <CommandsTable
        items={data?.items || []}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        onPageChange={setPage}
        isLoading={isLoading}
        onViewDetails={setSelectedDetailsId}
        onRetryCommand={handleRetryCommand}
        onCancelCommand={handleCancelCommand}
        isRetrying={retryMutation.isPending}
        isCancelling={cancelMutation.isPending}
      />

      {/* Drawer Overlay */}
      <CommandDetailsDrawer
        commandId={selectedDetailsId}
        onClose={() => setSelectedDetailsId(null)}
      />

      {/* Bulk Dispatch Modal */}
      <BulkCommandModal
        isOpen={isBulkModalOpen}
        onClose={() => setIsBulkModalOpen(false)}
        availableEndpoints={availableEndpoints}
      />
    </div>
  );
}

export function CommandsPage() {
  return (
    <GlobalWebSocketProvider>
      <CommandsPageContent />
    </GlobalWebSocketProvider>
  );
}
