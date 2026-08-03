import React from "react";
import { X, User, ShieldCheck } from "lucide-react";
import { Card, Badge, LoadingSkeleton } from "../../../components/ui";
import { useUserDetails } from "../api/usersApi";

interface UserDetailsDrawerProps {
  userId: string | null;
  onClose: () => void;
}

export const UserDetailsDrawer = React.memo(function UserDetailsDrawer({
  userId,
  onClose,
}: UserDetailsDrawerProps) {
  const { data: user, isLoading } = useUserDetails(userId || "");

  if (!userId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex justify-end transition-opacity">
      <div className="w-full max-w-2xl bg-surface-container-low border-l border-outline-variant shadow-2xl flex flex-col h-full overflow-y-auto scrollbar-none">
        {/* Header */}
        <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between bg-surface-container-high/60 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <User className="h-5 w-5 text-primary" />
            <div>
              <h3 className="text-body-md font-black text-on-surface">Operator Account Details</h3>
              <p className="text-[11px] font-mono text-on-surface-variant">ID: {userId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-surface-container-highest text-on-surface-variant">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        {isLoading || !user ? (
          <div className="p-6">
            <LoadingSkeleton height={400} />
          </div>
        ) : (
          <div className="p-6 space-y-6 text-xs">
            {/* Metadata Summary Card */}
            <Card className="p-4 bg-surface-container border-outline-variant/50 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-body-md font-black text-on-surface">{user.username}</h4>
                  <p className="text-on-surface-variant font-medium">{user.email}</p>
                </div>
                <Badge variant={user.is_active ? "success" : "error"}>
                  {user.is_active ? "Active" : "Disabled"}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2 border-t border-outline-variant/30 font-medium">
                <div>
                  <span className="text-on-surface-variant">Full Name:</span>
                  <p className="font-bold text-on-surface">
                    {user.first_name || user.last_name ? `${user.first_name || ""} ${user.last_name || ""}`.trim() : "N/A"}
                  </p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Phone:</span>
                  <p className="font-bold text-on-surface">{user.phone || "N/A"}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Account Verified:</span>
                  <p className="font-bold text-on-surface">{user.is_verified ? "Yes" : "No"}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Account Lock Status:</span>
                  <p className="font-bold text-on-surface">{user.is_locked ? "Locked" : "Unlocked"}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Created Date:</span>
                  <p className="font-mono text-on-surface">{new Date(user.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Last Login:</span>
                  <p className="font-mono text-on-surface">{user.last_login ? new Date(user.last_login).toLocaleString() : "Never"}</p>
                </div>
              </div>
            </Card>

            {/* Roles Card */}
            <div className="space-y-2">
              <h4 className="font-black uppercase text-on-surface flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-primary" /> Assigned Enterprise Roles
              </h4>
              <div className="p-3 bg-surface-container-high rounded-xl border border-outline-variant/40 flex items-center gap-2 flex-wrap">
                {user.roles.map((r) => (
                  <Badge key={r} variant="info" size="sm" className="font-extrabold">
                    {r}
                  </Badge>
                ))}
              </div>
            </div>

            {/* JSON Metadata Inspector */}
            <div className="space-y-2">
              <h4 className="font-black uppercase text-on-surface flex items-center gap-1.5">
                Account DTO Object
              </h4>
              <pre className="p-3 bg-surface-container-highest rounded-xl text-xs font-mono text-on-surface overflow-x-auto border border-outline-variant/40 max-h-60">
                {JSON.stringify(user, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});
