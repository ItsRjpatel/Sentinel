import React, { useState } from "react";
import { ShieldAlert } from "lucide-react";
import { AlertsSummaryCards } from "../components/AlertsSummaryCards";
import { AlertsToolbar } from "../components/AlertsToolbar";
import { AlertDetailsDrawer } from "../components/AlertDetailsDrawer";
// import {
//   useAlertsList,
//   useAcknowledgeAlert,
//   useResolveAlert,
//   useReopenAlert,
//   useAssignAlert,
// } from "../api/alertsApi";

export const AlertsPage = React.memo(function AlertsPage() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
    const [selectedDetailsId, setSelectedDetailsId] = useState<string | null>(null);

      const isFetching = false;
  const refetch = () => {};


  
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
        onSearchChange={(v) => { setSearch(v); {}; }}
        severityFilter={severityFilter}
        onSeverityFilterChange={(v) => { setSeverityFilter(v); {}; }}
        statusFilter={statusFilter}
        onStatusFilterChange={(v) => { setStatusFilter(v); {}; }}
        onRefresh={() => refetch()}
        isFetching={isFetching}
      />

      {/* Enterprise Alerts Table */}
      <div className="flex justify-center py-20">
        <div className="text-center bg-surface-container border border-outline-variant/60 rounded-xl p-10 max-w-lg">
          <ShieldAlert className="h-12 w-12 text-primary/40 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-on-surface mb-2">Feature Planned for Future Release</h2>
          <p className="text-sm text-on-surface-variant">
            The advanced Security Alerts Center is currently in development and will be available in an upcoming update.
          </p>
        </div>
      </div>

      {/* Drawer Overlay */}
      <AlertDetailsDrawer
        alertId={selectedDetailsId}
        onClose={() => setSelectedDetailsId(null)}
      />
    </div>
  );
});

