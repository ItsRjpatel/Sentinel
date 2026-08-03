import React from "react";
import { RefreshCw, AlertCircle } from "lucide-react";
import { Card, Badge, LoadingSkeleton } from "../../../../components/ui";
import { useUpdates } from "../api/detailsApi";

export const UpdatesTab = React.memo(function UpdatesTab({ endpointId }: { endpointId: string }) {
  const { data = [], isLoading, isError, refetch } = useUpdates(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load Windows Updates</p>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-error text-on-error rounded text-xs font-bold inline-flex items-center gap-1.5"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </Card>
    );
  }

  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
      <div className="p-4 border-b border-outline-variant/40 flex items-center justify-between">
        <div>
          <h3 className="text-body-md font-extrabold text-on-surface">Installed Windows Patches & Updates</h3>
          <p className="text-xs text-on-surface-variant">Total patches: {data.length}</p>
        </div>
      </div>

      <div className="overflow-x-auto max-h-[500px] scrollbar-none">
        <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
          <thead className="sticky top-0 bg-surface-container-high text-on-surface-variant font-bold uppercase shadow-xs">
            <tr>
              <th className="px-4 py-3">KB Patch</th>
              <th className="px-4 py-3">Title / Description</th>
              <th className="px-4 py-3">Installed Date</th>
              <th className="px-4 py-3">Security Update</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/30 font-medium">
            {data.map((upd, idx) => (
              <tr key={idx} className="hover:bg-surface-container-high/40 transition-colors">
                <td className="px-4 py-3 font-mono font-bold text-primary">{upd.kb_number}</td>
                <td className="px-4 py-3 font-bold text-on-surface truncate max-w-md">{upd.title}</td>
                <td className="px-4 py-3 text-on-surface-variant font-mono">{upd.installed_on}</td>
                <td className="px-4 py-3">
                  <Badge variant={upd.is_security_update ? "success" : "default"} size="sm">
                    {upd.is_security_update ? "Security Patch" : "Feature Patch"}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <Badge variant="success" size="sm">{upd.installed_state}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
});
