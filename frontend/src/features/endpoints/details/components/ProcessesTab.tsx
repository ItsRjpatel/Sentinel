import React, { useState } from "react";
import { Search, RefreshCw, AlertCircle, Cpu, HardDrive } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../../components/ui";
import { useProcesses } from "../api/detailsApi";

export const ProcessesTab = React.memo(function ProcessesTab({ endpointId }: { endpointId: string }) {
  const [search, setSearch] = useState("");
  const { data = [], isLoading, isError, refetch } = useProcesses(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load running processes</p>
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
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.user.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
      {/* Header & Search */}
      <div className="p-4 border-b border-outline-variant/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-body-md font-extrabold text-on-surface">Active Running Processes</h3>
          <p className="text-xs text-on-surface-variant font-medium">Active process count: {data.length}</p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-high rounded-md border border-outline-variant/40 focus-within:border-primary transition-colors min-w-[240px]">
          <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search process name or user..."
            className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>
      </div>

      {/* Processes Table */}
      <div className="overflow-x-auto max-h-[500px] scrollbar-none">
        <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
          <thead className="sticky top-0 bg-surface-container-high text-on-surface-variant font-bold uppercase shadow-xs">
            <tr>
              <th className="px-4 py-3">PID</th>
              <th className="px-4 py-3">Process Name</th>
              <th className="px-4 py-3">CPU Load</th>
              <th className="px-4 py-3">Memory Usage</th>
              <th className="px-4 py-3">Account Context</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/30 font-medium">
            {filtered.map((proc) => (
              <tr key={proc.pid} className="hover:bg-surface-container-high/40 transition-colors">
                <td className="px-4 py-3 font-mono font-bold text-primary">{proc.pid}</td>
                <td className="px-4 py-3 font-bold text-on-surface">{proc.name}</td>
                <td className="px-4 py-3 font-mono font-bold text-on-surface">
                  <span className="flex items-center gap-1">
                    <Cpu className="h-3 w-3 text-primary" /> {proc.cpu_percent}%
                  </span>
                </td>
                <td className="px-4 py-3 font-mono font-bold text-on-surface">
                  <span className="flex items-center gap-1">
                    <HardDrive className="h-3 w-3 text-tertiary" /> {proc.memory_mb} MB
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-on-surface-variant">{proc.user}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
});
