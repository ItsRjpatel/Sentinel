import React, { useState } from "react";
import { Users } from "lucide-react";
import { UsersSummaryCards } from "../components/UsersSummaryCards";
import { UsersToolbar } from "../components/UsersToolbar";
import { UsersTable } from "../components/UsersTable";
import { UserDetailsDrawer } from "../components/UserDetailsDrawer";
import { CreateUserModal } from "../components/CreateUserModal";
import {
  useUsersList,
  useEnableUser,
  useDisableUser,
  useUnlockUser,
  useResetPassword,
  useDeleteUser,
} from "../api/usersApi";
import type { UserItem } from "../types/usersTypes";

export const UsersPage = React.memo(function UsersPage() {
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [page, setPage] = useState(1);
  const [selectedDetailsId, setSelectedDetailsId] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const { data, isLoading, isFetching, refetch } = useUsersList({
    search,
    role: roleFilter,
    status: statusFilter,
    page,
    page_size: 20,
  });

  const enableMutation = useEnableUser();
  const disableMutation = useDisableUser();
  const unlockMutation = useUnlockUser();
  const resetPassMutation = useResetPassword();
  const deleteMutation = useDeleteUser();

  const handleToggleStatus = async (user: UserItem) => {
    try {
      if (user.is_active) {
        await disableMutation.mutateAsync(user.id);
      } else {
        await enableMutation.mutateAsync(user.id);
      }
    } catch (err: any) {
      alert(`Status toggle failed: ${err.message || "Unknown error"}`);
    }
  };

  const handleUnlockUser = async (id: string) => {
    try {
      await unlockMutation.mutateAsync(id);
      alert("Account unlocked successfully!");
    } catch (err: any) {
      alert(`Unlock failed: ${err.message || "Unknown error"}`);
    }
  };

  const handleResetPassword = async (user: UserItem) => {
    const newPass = prompt(`Enter new password for ${user.username}:`);
    if (!newPass) return;
    try {
      await resetPassMutation.mutateAsync({ id: user.id, newPassword: newPass });
      alert("Password reset successfully!");
    } catch (err: any) {
      alert(`Password reset failed: ${err.message || "Unknown error"}`);
    }
  };

  const handleDeleteUser = async (id: string) => {
    if (!confirm("Are you sure you want to delete this user account?")) return;
    try {
      await deleteMutation.mutateAsync(id);
      alert("User deleted successfully!");
    } catch (err: any) {
      alert(`Delete failed: ${err.message || "Unknown error"}`);
    }
  };

  const isMutating =
    enableMutation.isPending ||
    disableMutation.isPending ||
    unlockMutation.isPending ||
    resetPassMutation.isPending ||
    deleteMutation.isPending;

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <Users className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise User Management Center</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Console Operator Provisioning, Identity Governance & Access Control
            </p>
          </div>
        </div>
      </div>

      {/* Row 1: Summary Metric Cards */}
      <UsersSummaryCards />

      {/* Row 2: Enterprise Toolbar */}
      <UsersToolbar
        search={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        roleFilter={roleFilter}
        onRoleFilterChange={(v) => { setRoleFilter(v); setPage(1); }}
        statusFilter={statusFilter}
        onStatusFilterChange={(v) => { setStatusFilter(v); setPage(1); }}
        onRefresh={() => refetch()}
        onOpenCreateModal={() => setIsCreateModalOpen(true)}
        isFetching={isFetching}
        items={data?.items || []}
      />

      {/* Row 3: Enterprise Users Table */}
      <UsersTable
        items={data?.items || []}
        total={data?.total || 0}
        page={page}
        pageSize={20}
        onPageChange={setPage}
        isLoading={isLoading}
        onViewDetails={setSelectedDetailsId}
        onEditUser={(u) => setSelectedDetailsId(u.id)}
        onToggleStatus={handleToggleStatus}
        onUnlockUser={handleUnlockUser}
        onResetPassword={handleResetPassword}
        onDeleteUser={handleDeleteUser}
        isMutating={isMutating}
      />

      {/* Drawer Overlay */}
      <UserDetailsDrawer
        userId={selectedDetailsId}
        onClose={() => setSelectedDetailsId(null)}
      />

      {/* Create Modal */}
      <CreateUserModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
});
