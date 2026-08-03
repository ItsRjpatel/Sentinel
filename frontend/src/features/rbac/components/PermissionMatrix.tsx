import React from "react";
import { CheckCircle2, Key } from "lucide-react";
import { Card } from "../../../components/ui";
import type { RoleItem, PermissionItem } from "../types/rbacTypes";

interface PermissionMatrixProps {
  roles: RoleItem[];
  permissions: PermissionItem[];
}

export const PermissionMatrix = React.memo(function PermissionMatrix({
  roles,
  permissions,
}: PermissionMatrixProps) {
  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
      <div className="p-4 bg-surface-container-high/60 border-b border-outline-variant/60">
        <h3 className="text-body-md font-black text-on-surface flex items-center gap-2">
          <Key className="h-5 w-5 text-primary" /> Enterprise Role & Capability Permission Matrix
        </h3>
        <p className="text-xs text-on-surface-variant font-medium">
          Comprehensive mapping of granular capabilities against enterprise RBAC roles.
        </p>
      </div>

      <div className="overflow-x-auto scrollbar-none">
        <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
          <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase sticky top-0">
            <tr>
              <th className="px-4 py-3 min-w-[200px]">Permission Capability</th>
              <th className="px-4 py-3">Description</th>
              {roles.map((r) => (
                <th key={r.id} className="px-4 py-3 text-center min-w-[120px]">
                  {r.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/30 font-medium">
            {permissions.map((p) => (
              <tr key={p.id} className="hover:bg-surface-container-high/40 transition-colors">
                <td className="px-4 py-3 font-mono font-extrabold text-primary">{p.name}</td>
                <td className="px-4 py-3 text-on-surface-variant">{p.description || "System permission target"}</td>
                {roles.map((r) => {
                  const hasPerm = r.name.toLowerCase() === "admin" || (r.permissions && r.permissions.some((rp) => rp.name === p.name));
                  return (
                    <td key={r.id} className="px-4 py-3 text-center">
                      {hasPerm ? (
                        <CheckCircle2 className="h-4 w-4 text-success inline-block" />
                      ) : (
                        <span className="text-on-surface-variant/30 font-mono text-[10px]">—</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
});
