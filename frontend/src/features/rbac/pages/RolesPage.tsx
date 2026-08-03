import React, { useState } from "react";
import { ShieldCheck, Plus, RefreshCw } from "lucide-react";
import { Button, LoadingSkeleton } from "../../../components/ui";
import { RolesCards } from "../components/RolesCards";
import { PermissionMatrix } from "../components/PermissionMatrix";
import { CreateRoleModal } from "../components/CreateRoleModal";
import { useRolesList, usePermissionsList, useDeleteRole } from "../api/rbacApi";

export const RolesPage = React.memo(function RolesPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data: roles = [], isLoading: isLoadingRoles, refetch: refetchRoles } = useRolesList();
  const { data: permissions = [], isLoading: isLoadingPerms, refetch: refetchPerms } = usePermissionsList();
  const deleteMutation = useDeleteRole();

  const handleDeleteRole = async (id: string) => {
    if (!confirm("Are you sure you want to delete this RBAC role?")) return;
    try {
      await deleteMutation.mutateAsync(id);
      alert("Role deleted successfully!");
    } catch (err: any) {
      alert(`Failed to delete role: ${err.message || "Unknown error"}`);
    }
  };

  const isLoading = isLoadingRoles || isLoadingPerms;

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Role-Based Access Control (RBAC)</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Manage Security Roles, Access Scopes, and Capability Mapping
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => { refetchRoles(); refetchPerms(); }}
            className="p-2 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors"
            title="Refresh Roles & Matrix"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          <Button
            onClick={() => setIsCreateModalOpen(true)}
            variant="primary"
            size="sm"
            leftIcon={<Plus className="h-4 w-4" />}
            className="font-extrabold shadow-xs"
          >
            Create Role
          </Button>
        </div>
      </div>

      {isLoading ? (
        <LoadingSkeleton height={400} />
      ) : (
        <>
          {/* Row 1: Role Metric Cards */}
          <RolesCards roles={roles} onDeleteRole={handleDeleteRole} />

          {/* Row 2: Capability Permission Matrix */}
          <PermissionMatrix roles={roles} permissions={permissions} />
        </>
      )}

      {/* Modal */}
      <CreateRoleModal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} />
    </div>
  );
});
