import React from "react";
import { Search, RefreshCw, Filter, UserPlus, FileSpreadsheet, Download, ShieldCheck } from "lucide-react";
import { Button } from "../../../components/ui";
import type { UserItem } from "../types/usersTypes";

interface UsersToolbarProps {
  search: string;
  onSearchChange: (v: string) => void;
  roleFilter: string;
  onRoleFilterChange: (v: string) => void;
  statusFilter: string;
  onStatusFilterChange: (v: string) => void;
  onRefresh: () => void;
  onOpenCreateModal: () => void;
  isFetching: boolean;
  items: UserItem[];
}

const ROLE_OPTIONS = [
  { value: "ALL", label: "All Roles" },
  { value: "ADMIN", label: "Administrator" },
  { value: "ANALYST", label: "Analyst" },
  { value: "OPERATOR", label: "Operator" },
];

const STATUS_OPTIONS = [
  { value: "ALL", label: "All Statuses" },
  { value: "ACTIVE", label: "Active" },
  { value: "DISABLED", label: "Disabled" },
  { value: "LOCKED", label: "Locked" },
];

export const UsersToolbar = React.memo(function UsersToolbar({
  search,
  onSearchChange,
  roleFilter,
  onRoleFilterChange,
  statusFilter,
  onStatusFilterChange,
  onRefresh,
  onOpenCreateModal,
  isFetching,
  items,
}: UsersToolbarProps) {
  const exportCsv = () => {
    if (items.length === 0) return alert("No data available to export.");
    const headers = ["ID", "Username", "Email", "FirstName", "LastName", "Phone", "Active", "Verified", "Locked", "LastLogin", "Roles"];
    const rows = items.map((u) => [
      u.id,
      u.username,
      u.email,
      u.first_name || "",
      u.last_name || "",
      u.phone || "",
      u.is_active ? "TRUE" : "FALSE",
      u.is_verified ? "TRUE" : "FALSE",
      u.is_locked ? "TRUE" : "FALSE",
      u.last_login || "",
      u.roles.join(";"),
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", `user-directory-${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const exportJson = () => {
    if (items.length === 0) return alert("No data available to export.");
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(items, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", dataStr);
    link.setAttribute("download", `user-directory-${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="bg-surface-container-low border border-outline-variant/60 rounded-xl p-3 flex flex-col lg:flex-row lg:items-center justify-between gap-3 shadow-xs">
      {/* Left Search & Filter inputs */}
      <div className="flex flex-wrap items-center gap-2 flex-1">
        {/* Search */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-high rounded-lg border border-outline-variant/40 focus-within:border-primary transition-colors min-w-[240px] flex-1 max-w-sm">
          <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search username, email, first or last name..."
            className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>

        {/* Role Dropdown */}
        <div className="flex items-center gap-1.5 bg-surface-container-high px-2 py-1 rounded-lg border border-outline-variant/40 text-xs font-bold text-on-surface-variant">
          <ShieldCheck className="h-3.5 w-3.5" />
          <select
            value={roleFilter}
            onChange={(e) => onRoleFilterChange(e.target.value)}
            className="bg-transparent text-on-surface focus:outline-none cursor-pointer font-bold"
          >
            {ROLE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-surface-container-low text-on-surface">
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Status Dropdown */}
        <div className="flex items-center gap-1.5 bg-surface-container-high px-2 py-1 rounded-lg border border-outline-variant/40 text-xs font-bold text-on-surface-variant">
          <Filter className="h-3.5 w-3.5" />
          <select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="bg-transparent text-on-surface focus:outline-none cursor-pointer font-bold"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-surface-container-low text-on-surface">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Right Action buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={onRefresh}
          disabled={isFetching}
          className="p-2 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors disabled:opacity-50"
          title="Refresh User List"
        >
          <RefreshCw className={`h-4 w-4 ${isFetching ? "animate-spin text-primary" : ""}`} />
        </button>

        <button
          onClick={exportCsv}
          className="px-3 py-1.5 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors flex items-center gap-1"
        >
          <FileSpreadsheet className="h-3.5 w-3.5 text-success" /> CSV
        </button>

        <button
          onClick={exportJson}
          className="px-3 py-1.5 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors flex items-center gap-1"
        >
          <Download className="h-3.5 w-3.5 text-primary" /> JSON
        </button>

        <Button
          onClick={onOpenCreateModal}
          variant="primary"
          size="sm"
          leftIcon={<UserPlus className="h-4 w-4" />}
          className="font-extrabold shadow-xs"
        >
          Create User
        </Button>
      </div>
    </div>
  );
});
