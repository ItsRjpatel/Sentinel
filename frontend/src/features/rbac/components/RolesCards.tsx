import React from "react";
import { ShieldCheck, Key, Trash2 } from "lucide-react";
import { Card, Badge } from "../../../components/ui";
import type { RoleItem } from "../types/rbacTypes";

interface RolesCardsProps {
  roles: RoleItem[];
  onDeleteRole: (id: string) => void;
}

export const RolesCards = React.memo(function RolesCards({
  roles,
  onDeleteRole,
}: RolesCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {roles.map((role) => (
        <Card key={role.id} className="p-4 bg-surface-container-low border-outline-variant space-y-3 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-primary" />
                <h3 className="text-body-md font-black text-on-surface">{role.name}</h3>
              </div>
              <Badge variant="outline" size="sm" className="font-mono text-[10px]">
                ID: {role.id.slice(0, 8)}
              </Badge>
            </div>
            <p className="text-xs text-on-surface-variant line-clamp-2">
              {role.description || "Custom enterprise RBAC role configuration."}
            </p>
          </div>

          <div className="pt-3 border-t border-outline-variant/30 flex items-center justify-between text-xs">
            <span className="font-bold text-on-surface flex items-center gap-1">
              <Key className="h-3.5 w-3.5 text-tertiary" /> {role.permissions?.length || 0} Permissions
            </span>
            <button
              onClick={() => onDeleteRole(role.id)}
              className="p-1 text-on-surface-variant hover:text-error transition-colors"
              title="Delete Role"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </Card>
      ))}
    </div>
  );
});
