import React from "react";
import { Users, UserCheck, UserX, Lock, ShieldCheck, UserCheck2, Bot, User, RefreshCw } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useUsersSummary } from "../api/usersApi";

export const UsersSummaryCards = React.memo(function UsersSummaryCards() {
  const { data, isLoading, isError, refetch } = useUsersSummary();

  if (isLoading) {
    return <LoadingSkeleton height={100} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-4 bg-error/10 border border-error/30 text-center space-y-2">
        <p className="text-xs font-medium text-on-surface-variant">Failed to load user summary metrics</p>
        <button onClick={() => refetch()} className="px-3 py-1 bg-error text-on-error text-xs font-bold rounded inline-flex items-center gap-1">
          <RefreshCw className="h-3 w-3" /> Retry
        </button>
      </Card>
    );
  }

  const items = [
    { label: "Total Users", count: data.total, icon: Users, color: "text-primary", bg: "bg-primary/10" },
    { label: "Online Now", count: data.online, icon: UserCheck, color: "text-success", bg: "bg-success/10" },
    { label: "Disabled Accounts", count: data.disabled, icon: UserX, color: "text-error", bg: "bg-error/10" },
    { label: "Locked Out", count: data.locked, icon: Lock, color: "text-warning", bg: "bg-warning/10" },
    { label: "Administrators", count: data.administrators, icon: ShieldCheck, color: "text-primary", bg: "bg-primary/10" },
    { label: "Analysts", count: data.analysts, icon: UserCheck2, color: "text-tertiary", bg: "bg-tertiary/10" },
    { label: "Agents / Services", count: data.agents, icon: Bot, color: "text-info", bg: "bg-info/10" },
    { label: "Guests / Others", count: data.guests, icon: User, color: "text-on-surface-variant", bg: "bg-surface-container-highest" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <Card key={item.label} className="p-3 bg-surface-container-low border-outline-variant space-y-1.5 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider truncate">{item.label}</span>
              <div className={`p-1 rounded ${item.bg} ${item.color}`}>
                <Icon className="h-3.5 w-3.5" />
              </div>
            </div>
            <div className="text-xl font-black text-on-surface font-mono">{item.count}</div>
          </Card>
        );
      })}
    </div>
  );
});
