import React from "react";
import {
  User,
  CheckCircle2,
  XCircle,
  Lock,
  Eye,
  Edit,
  UserCheck,
  UserX,
  KeyRound,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Unlock,
} from "lucide-react";
import { Card, Badge, LoadingSkeleton, EmptyState } from "../../../components/ui";
import type { UserItem } from "../types/usersTypes";

interface UsersTableProps {
  items: UserItem[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (p: number) => void;
  isLoading: boolean;
  onViewDetails: (id: string) => void;
  onEditUser: (user: UserItem) => void;
  onToggleStatus: (user: UserItem) => void;
  onUnlockUser: (id: string) => void;
  onResetPassword: (user: UserItem) => void;
  onDeleteUser: (id: string) => void;
  isMutating: boolean;
}

export const UsersTable = React.memo(function UsersTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
  onViewDetails,
  onEditUser,
  onToggleStatus,
  onUnlockUser,
  onResetPassword,
  onDeleteUser,
  isMutating,
}: UsersTableProps) {
  if (isLoading) {
    return <LoadingSkeleton height={400} />;
  }

  const totalPages = Math.ceil(total / pageSize) || 1;

  const getStatusBadge = (user: UserItem) => {
    if (user.is_locked) {
      return (
        <Badge variant="warning" size="sm" className="font-bold flex items-center gap-1 w-fit">
          <Lock className="h-3 w-3" /> Locked
        </Badge>
      );
    }
    if (user.is_active) {
      return (
        <Badge variant="success" size="sm" className="font-bold flex items-center gap-1 w-fit">
          <CheckCircle2 className="h-3 w-3" /> Active
        </Badge>
      );
    }
    return (
      <Badge variant="error" size="sm" className="font-bold flex items-center gap-1 w-fit">
        <XCircle className="h-3 w-3" /> Disabled
      </Badge>
    );
  };

  return (
    <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
      {items.length === 0 ? (
        <div className="py-16 flex items-center justify-center">
          <EmptyState
            title="No Operator Accounts Found"
            description="Use 'Create User' to provision console operator and analyst accounts."
            className="border-none bg-transparent"
          />
        </div>
      ) : (
        <>
          <div className="overflow-x-auto scrollbar-none">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
              <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase sticky top-0">
                <tr>
                  <th className="px-4 py-3">Username</th>
                  <th className="px-4 py-3">Email Address</th>
                  <th className="px-4 py-3">Full Name</th>
                  <th className="px-4 py-3">Assigned Roles</th>
                  <th className="px-4 py-3">Account Status</th>
                  <th className="px-4 py-3">Last Login</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 font-medium">
                {items.map((u) => (
                  <tr key={u.id} className="hover:bg-surface-container-high/40 transition-colors">
                    <td className="px-4 py-3 font-bold text-on-surface">
                      <div className="flex items-center gap-1.5">
                        <User className="h-3.5 w-3.5 text-primary" />
                        <button
                          onClick={() => onViewDetails(u.id)}
                          className="hover:underline text-primary text-left font-bold"
                        >
                          {u.username}
                        </button>
                      </div>
                    </td>
                    <td className="px-4 py-3 font-mono text-on-surface">{u.email}</td>
                    <td className="px-4 py-3 font-semibold text-on-surface">
                      {u.first_name || u.last_name ? `${u.first_name || ""} ${u.last_name || ""}`.trim() : "N/A"}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1 flex-wrap">
                        {u.roles.map((r) => (
                          <Badge key={r} variant="outline" size="sm" className="font-bold">
                            {r}
                          </Badge>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3">{getStatusBadge(u)}</td>
                    <td className="px-4 py-3 font-mono text-on-surface-variant text-[11px]">
                      {u.last_login ? new Date(u.last_login).toLocaleString() : "Never"}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-1">
                        {/* View */}
                        <button
                          onClick={() => onViewDetails(u.id)}
                          className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-primary"
                          title="View User Details"
                        >
                          <Eye className="h-3.5 w-3.5" />
                        </button>

                        {/* Edit */}
                        <button
                          onClick={() => onEditUser(u)}
                          className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-on-surface"
                          title="Edit User Info"
                        >
                          <Edit className="h-3.5 w-3.5" />
                        </button>

                        {/* Unlock if locked */}
                        {u.is_locked && (
                          <button
                            onClick={() => onUnlockUser(u.id)}
                            disabled={isMutating}
                            className="p-1.5 bg-warning/15 hover:bg-warning/25 border border-warning/30 rounded text-warning"
                            title="Unlock Account"
                          >
                            <Unlock className="h-3.5 w-3.5" />
                          </button>
                        )}

                        {/* Toggle Enable / Disable */}
                        <button
                          onClick={() => onToggleStatus(u)}
                          disabled={isMutating}
                          className={`p-1.5 rounded border transition-colors ${
                            u.is_active
                              ? "bg-error/15 hover:bg-error/25 border-error/30 text-error"
                              : "bg-success/15 hover:bg-success/25 border-success/30 text-success"
                          }`}
                          title={u.is_active ? "Disable Account" : "Enable Account"}
                        >
                          {u.is_active ? <UserX className="h-3.5 w-3.5" /> : <UserCheck className="h-3.5 w-3.5" />}
                        </button>

                        {/* Reset Password */}
                        <button
                          onClick={() => onResetPassword(u)}
                          className="p-1.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-warning"
                          title="Reset User Password"
                        >
                          <KeyRound className="h-3.5 w-3.5" />
                        </button>

                        {/* Delete */}
                        <button
                          onClick={() => onDeleteUser(u.id)}
                          disabled={isMutating}
                          className="p-1.5 bg-surface-container-high hover:bg-error/20 border border-outline-variant/40 rounded text-error"
                          title="Delete User"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-surface-container-high/60 border-t border-outline-variant/40 text-xs">
            <span className="text-on-surface-variant font-medium">
              Showing <strong className="text-on-surface">{items.length}</strong> of <strong className="text-on-surface">{total}</strong> users
            </span>

            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => onPageChange(page - 1)}
                className="p-1.5 bg-surface-container-low border border-outline-variant/40 rounded hover:bg-surface-container-highest disabled:opacity-40 text-on-surface"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="font-bold text-on-surface">Page {page} of {totalPages}</span>
              <button
                disabled={page >= totalPages}
                onClick={() => onPageChange(page + 1)}
                className="p-1.5 bg-surface-container-low border border-outline-variant/40 rounded hover:bg-surface-container-highest disabled:opacity-40 text-on-surface"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </Card>
  );
});
