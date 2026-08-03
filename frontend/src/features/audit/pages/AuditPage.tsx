import React, { useState } from "react";
import { FileText } from "lucide-react";
import { AuditSummaryCards } from "../components/AuditSummaryCards";
import { AuditToolbar } from "../components/AuditToolbar";
import { AuditTable } from "../components/AuditTable";
import { AuditDetailsDrawer } from "../components/AuditDetailsDrawer";
import { useAuditLogs } from "../api/auditApi";

export const AuditPage = React.memo(function AuditPage() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [moduleFilter, setModuleFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [page, setPage] = useState(1);
  const [selectedDetailsId, setSelectedDetailsId] = useState<string | null>(null);

  const { data, isLoading, isFetching, refetch } = useAuditLogs({
    search,
    severity: severityFilter,
    module: moduleFilter,
    status: statusFilter,
    page,
    page_size: 20,
  });

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Audit Logs Center</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Immutable Governance & Operational Security Audit Trail
            </p>
          </div>
        </div>
      </div>

      {/* Row 1: Summary Metric Cards */}
      <AuditSummaryCards />

      {/* Row 2: Enterprise Toolbar */}
      <AuditToolbar
        search={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        severityFilter={severityFilter}
        onSeverityFilterChange={(v) => { setSeverityFilter(v); setPage(1); }}
        moduleFilter={moduleFilter}
        onModuleFilterChange={(v) => { setModuleFilter(v); setPage(1); }}
        statusFilter={statusFilter}
        onStatusFilterChange={(v) => { setStatusFilter(v); setPage(1); }}
        onRefresh={() => refetch()}
        isFetching={isFetching}
        items={data?.items || []}
      />

      {/* Row 3: Enterprise Audit Table */}
      <AuditTable
        items={data?.items || []}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        onPageChange={setPage}
        isLoading={isLoading}
        onViewDetails={setSelectedDetailsId}
      />

      {/* Drawer Overlay */}
      <AuditDetailsDrawer
        logId={selectedDetailsId}
        onClose={() => setSelectedDetailsId(null)}
      />
    </div>
  );
});
