import React from "react";
import { Key, ShieldCheck, RefreshCw } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { usePermissionsList } from "../api/rbacApi";

export const PermissionsPage = React.memo(function PermissionsPage() {
  const { data: permissions = [], isLoading, refetch } = usePermissionsList();

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <Key className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Permissions Center</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Granular System Capability Catalog & Security Scopes
            </p>
          </div>
        </div>

        <button
          onClick={() => refetch()}
          className="p-2 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors"
          title="Refresh Permissions"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {isLoading ? (
        <LoadingSkeleton height={400} />
      ) : (
        <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
          <div className="overflow-x-auto scrollbar-none">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
              <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase sticky top-0">
                <tr>
                  <th className="px-4 py-3">Permission Key</th>
                  <th className="px-4 py-3">Module / Scope</th>
                  <th className="px-4 py-3">Description</th>
                  <th className="px-4 py-3">ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 font-medium">
                {permissions.map((p) => {
                  const parts = p.name.split(".");
                  const category = parts[0]?.toUpperCase() || "SYSTEM";
                  return (
                    <tr key={p.id} className="hover:bg-surface-container-high/40 transition-colors">
                      <td className="px-4 py-3 font-mono font-extrabold text-primary flex items-center gap-1.5">
                        <ShieldCheck className="h-3.5 w-3.5 text-primary" /> {p.name}
                      </td>
                      <td className="px-4 py-3 font-bold text-on-surface">
                        <span className="px-2 py-0.5 rounded bg-surface-container-highest font-mono text-[10px]">
                          {category}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-on-surface-variant">{p.description || "System permission target"}</td>
                      <td className="px-4 py-3 font-mono text-on-surface-variant text-[11px]">{p.id}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
});
