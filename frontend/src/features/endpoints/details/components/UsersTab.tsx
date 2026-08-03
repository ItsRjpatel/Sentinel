import React from "react";
import { User, RefreshCw, AlertCircle } from "lucide-react";
import { Card, Badge, LoadingSkeleton } from "../../../../components/ui";
import { useUsers } from "../api/detailsApi";

export const UsersTab = React.memo(function UsersTab({ endpointId }: { endpointId: string }) {
  const { data = [], isLoading, isError, refetch } = useUsers(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load local user accounts</p>
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
          <h3 className="text-body-md font-extrabold text-on-surface">Local User Accounts</h3>
          <p className="text-xs text-on-surface-variant">Accounts configured on endpoint: {data.length}</p>
        </div>
      </div>

      <div className="overflow-x-auto scrollbar-none">
        <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
          <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase">
            <tr>
              <th className="px-4 py-3">Username</th>
              <th className="px-4 py-3">Privilege Level</th>
              <th className="px-4 py-3">Account State</th>
              <th className="px-4 py-3">Last Interactive Login</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/30 font-medium">
            {data.map((usr, idx) => (
              <tr key={idx} className="hover:bg-surface-container-high/40 transition-colors">
                <td className="px-4 py-3 font-bold text-on-surface flex items-center gap-2">
                  <User className="h-4 w-4 text-primary" />
                  <span>{usr.username}</span>
                </td>
                <td className="px-4 py-3">
                  <Badge variant={usr.is_admin ? "warning" : "default"} size="sm">
                    {usr.is_admin ? "Administrator" : "Standard User"}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <Badge variant={usr.is_disabled ? "default" : "success"} size="sm">
                    {usr.is_disabled ? "Disabled" : "Active"}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-on-surface-variant font-mono">{usr.last_login}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
});
