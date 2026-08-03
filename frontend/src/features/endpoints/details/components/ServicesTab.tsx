import React, { useState } from "react";
import { Search, RefreshCw, AlertCircle, Play, Pause } from "lucide-react";
import { Card, Badge, LoadingSkeleton } from "../../../../components/ui";
import { useServices } from "../api/detailsApi";

export const ServicesTab = React.memo(function ServicesTab({ endpointId }: { endpointId: string }) {
  const [search, setSearch] = useState("");
  const { data = [], isLoading, isError, refetch } = useServices(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load Windows Services</p>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-error text-on-error rounded text-xs font-bold inline-flex items-center gap-1.5"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </Card>
    );
  }

  const filtered = data.filter(
    (s) =>
      s.service_name.toLowerCase().includes(search.toLowerCase()) ||
      s.display_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
      {/* Header & Search */}
      <div className="p-4 border-b border-outline-variant/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-body-md font-extrabold text-on-surface">Windows Services</h3>
          <p className="text-xs text-on-surface-variant">Total services: {data.length}</p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-high rounded-md border border-outline-variant/40 focus-within:border-primary transition-colors min-w-[240px]">
          <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search service name or display..."
            className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>
      </div>

      {/* Services Table */}
      <div className="overflow-x-auto max-h-[500px] scrollbar-none">
        <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
          <thead className="sticky top-0 bg-surface-container-high text-on-surface-variant font-bold uppercase shadow-xs">
            <tr>
              <th className="px-4 py-3">Service Name</th>
              <th className="px-4 py-3">Display Name</th>
              <th className="px-4 py-3">State</th>
              <th className="px-4 py-3">Startup Type</th>
              <th className="px-4 py-3">PID</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/30 font-medium">
            {filtered.map((svc, idx) => {
              const isRunning = svc.current_state.toLowerCase() === "running";
              return (
                <tr key={idx} className="hover:bg-surface-container-high/40 transition-colors">
                  <td className="px-4 py-3 font-mono font-bold text-primary">{svc.service_name}</td>
                  <td className="px-4 py-3 font-bold text-on-surface">{svc.display_name}</td>
                  <td className="px-4 py-3">
                    <Badge variant={isRunning ? "success" : "default"} size="sm" className="font-bold flex items-center gap-1 w-fit">
                      {isRunning ? <Play className="h-2.5 w-2.5" /> : <Pause className="h-2.5 w-2.5" />}
                      <span>{svc.current_state}</span>
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-on-surface-variant font-semibold">{svc.start_mode}</td>
                  <td className="px-4 py-3 font-mono font-bold text-on-surface">{svc.process_id || "N/A"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
});
