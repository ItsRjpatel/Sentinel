import React, { useState } from "react";
import { Search, RefreshCw, AlertCircle, Package } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../../components/ui";
import { useSoftware } from "../api/detailsApi";

export const SoftwareTab = React.memo(function SoftwareTab({ endpointId }: { endpointId: string }) {
  const [search, setSearch] = useState("");
  const { data = [], isLoading, isError, refetch } = useSoftware(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load software inventory</p>
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
      s.application_name.toLowerCase().includes(search.toLowerCase()) ||
      s.publisher.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden space-y-0">
      {/* Header & Search */}
      <div className="p-4 border-b border-outline-variant/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-body-md font-extrabold text-on-surface">Installed Applications</h3>
          <p className="text-xs text-on-surface-variant">Total applications: {data.length}</p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-high rounded-md border border-outline-variant/40 focus-within:border-primary transition-colors min-w-[240px]">
          <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search software or publisher..."
            className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>
      </div>

      {/* Software Table */}
      {filtered.length === 0 ? (
        <div className="p-6 text-center text-xs text-on-surface-variant font-medium">
          No data available
        </div>
      ) : (
        <div className="overflow-x-auto max-h-[500px] scrollbar-none">
          <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
            <thead className="sticky top-0 bg-surface-container-high text-on-surface-variant font-bold uppercase shadow-xs">
              <tr>
                <th className="px-4 py-3">Application Name</th>
                <th className="px-4 py-3">Publisher</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Install Date</th>
                <th className="px-4 py-3">Architecture</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 font-medium">
              {filtered.map((app, idx) => (
                <tr key={idx} className="hover:bg-surface-container-high/40 transition-colors">
                  <td className="px-4 py-3 font-bold text-on-surface flex items-center gap-2">
                    <Package className="h-4 w-4 text-primary" />
                    <span>{app.application_name}</span>
                  </td>
                  <td className="px-4 py-3 text-on-surface-variant">{app.publisher}</td>
                  <td className="px-4 py-3 font-mono font-bold text-on-surface">{app.version}</td>
                  <td className="px-4 py-3 text-on-surface-variant font-mono">{app.install_date}</td>
                  <td className="px-4 py-3 font-mono text-on-surface-variant">{app.architecture}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
});
