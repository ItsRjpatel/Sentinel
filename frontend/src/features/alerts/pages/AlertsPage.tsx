import React, { useState } from "react";
import { ShieldAlert } from "lucide-react";
import { AlertsSummaryCards } from "../components/AlertsSummaryCards";
import { AlertsToolbar } from "../components/AlertsToolbar";
import { AlertsTable } from "../components/AlertsTable";
import { AlertDetailsDrawer } from "../components/AlertDetailsDrawer";
import {
  useAlertsList,
  useAcknowledgeAlert,
  useResolveAlert,
  useReopenAlert,
  useAssignAlert,
} from "../api/alertsApi";

export const AlertsPage = React.memo(function AlertsPage() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [page, setPage] = useState(1);
  const [selectedDetailsId, setSelectedDetailsId] = useState<string | null>(null);

  const { data, isLoading, isFetching, refetch } = useAlertsList({
    severity: severityFilter,
    status: statusFilter,
    search,
    page,
    page_size: 20,
  });

  const ackMutation = useAcknowledgeAlert();
  const resolveMutation = useResolveAlert();
  const reopenMutation = useReopenAlert();
  const assignMutation = useAssignAlert();

  const handleAcknowledge = async (id: string) => {
    try {
      await ackMutation.mutateAsync(id);
    } catch (err: any) {
      alert(`Failed to acknowledge alert: ${err.message || "Unknown error"}`);
    }
  };

  const handleResolve = async (id: string) => {
    const notes = prompt("Enter resolution notes (optional):");
    try {
      await resolveMutation.mutateAsync({ id, resolutionNotes: notes || undefined });
    } catch (err: any) {
      alert(`Failed to resolve alert: ${err.message || "Unknown error"}`);
    }
  };

  const handleReopen = async (id: string) => {
    try {
      await reopenMutation.mutateAsync(id);
    } catch (err: any) {
      alert(`Failed to reopen alert: ${err.message || "Unknown error"}`);
    }
  };

  const handleAssign = async (id: string) => {
    const analyst = prompt("Enter analyst username to assign:");
    if (!analyst) return;
    try {
      await assignMutation.mutateAsync({ id, analyst });
    } catch (err: any) {
      alert(`Failed to assign alert: ${err.message || "Unknown error"}`);
    }
  };

  const isMutating =
    ackMutation.isPending || resolveMutation.isPending || reopenMutation.isPending || assignMutation.isPending;

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-error/10 border border-error/30 rounded-xl flex items-center justify-center text-error flex-shrink-0">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Security Alerts Center</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Real-time Threat Detection, Triage & Resolution Operations
            </p>
          </div>
        </div>
      </div>

      {/* Row 1: Summary Metric Cards */}
      <AlertsSummaryCards />

      {/* Row 2: Enterprise Toolbar */}
      <AlertsToolbar
        search={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        severityFilter={severityFilter}
        onSeverityFilterChange={(v) => { setSeverityFilter(v); setPage(1); }}
        statusFilter={statusFilter}
        onStatusFilterChange={(v) => { setStatusFilter(v); setPage(1); }}
        onRefresh={() => refetch()}
        isFetching={isFetching}
      />

      {/* Row 3: Enterprise Alerts Table */}
      <AlertsTable
        items={data?.items || []}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        onPageChange={setPage}
        isLoading={isLoading}
        onViewDetails={setSelectedDetailsId}
        onAcknowledge={handleAcknowledge}
        onResolve={handleResolve}
        onReopen={handleReopen}
        onAssign={handleAssign}
        isMutating={isMutating}
      />

      {/* Drawer Overlay */}
      <AlertDetailsDrawer
        alertId={selectedDetailsId}
        onClose={() => setSelectedDetailsId(null)}
      />
    </div>
  );
});
