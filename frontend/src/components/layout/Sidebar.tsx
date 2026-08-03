import React from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Monitor,
  Terminal,
  Radio,
  ShieldAlert,
  Users,
  ShieldCheck,
  KeyRound,
  Settings,
  FileText,
  Shield,
  HelpCircle,
  Plus,
  LogOut,
  FolderKanban,
  Calendar,
} from "lucide-react";
import { cn } from "../../utils/cn";
import { useAuth } from "../../contexts/AuthContext";

export interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    title: "Overview",
    items: [
      { name: "Dashboard", path: "/", icon: LayoutDashboard },
    ],
  },
  {
    title: "Remote Operations",
    items: [
      { name: "Commands", path: "/commands", icon: Terminal },
      { name: "Live Console", path: "/console", icon: Radio },
      { name: "Scheduled Tasks", path: "/schedules", icon: Calendar },
    ],
  },
  {
    title: "Security",
    items: [
      { name: "Security Policies", path: "/policies", icon: ShieldCheck },
      { name: "Security Alerts", path: "/alerts", icon: ShieldAlert },
    ],
  },
  {
    title: "Management",
    items: [
      { name: "Endpoints", path: "/endpoints", icon: Monitor },
      { name: "Endpoint Groups", path: "/groups", icon: FolderKanban },
    ],
  },
  {
    title: "Administration",
    items: [
      { name: "User Management", path: "/admin/users", icon: Users },
      { name: "Roles & RBAC", path: "/admin/roles", icon: ShieldCheck },
      { name: "Permissions", path: "/admin/permissions", icon: KeyRound },
      { name: "System Settings", path: "/admin/settings", icon: Settings },
      { name: "Audit Logs", path: "/admin/audit", icon: FileText },
    ],
  },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  return (
    <aside
      className="fixed top-0 left-0 bottom-0 z-40 w-[240px] bg-surface-container-low border-r border-outline-variant flex flex-col select-none"
      aria-label="Main Navigation"
    >
      {/* Brand Header */}
      <div className="h-12 flex items-center px-4 border-b border-outline-variant/60 flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-primary/10 border border-primary/30 flex items-center justify-center text-primary flex-shrink-0">
            <Shield className="h-4 w-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-body-sm font-bold text-on-surface leading-none tracking-tight">
              Sentinel X
            </span>
            <span className="text-[10px] text-on-surface-variant uppercase tracking-widest font-semibold mt-0.5">
              EDR Platform
            </span>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="p-3 flex-shrink-0">
        <button
          onClick={() => navigate("/endpoints")}
          className="w-full py-1.5 px-3 bg-primary text-on-primary rounded-md text-label-md font-bold flex items-center justify-center gap-2 hover:opacity-90 active:scale-[0.98] transition-all shadow-sm cursor-pointer"
        >
          <Plus className="h-4 w-4" />
          <span>Deploy Agent</span>
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-1 space-y-4 scrollbar-none">
        {navSections.map((section, idx) => (
          <div key={idx} className="space-y-0.5">
            <div className="px-2.5 text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider mb-1">
              {section.title}
            </div>

            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-body-sm transition-colors group relative font-medium",
                    isActive
                      ? "bg-primary/10 text-primary font-semibold"
                      : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
                  )}
                >
                  {/* Active Indicator Line */}
                  {isActive && (
                    <span className="absolute left-0 top-1 bottom-1 w-1 bg-primary rounded-r" />
                  )}

                  <Icon
                    className={cn(
                      "h-4 w-4 flex-shrink-0 transition-colors",
                      isActive ? "text-primary" : "text-on-surface-variant group-hover:text-on-surface"
                    )}
                  />

                  <span className="truncate">{item.name}</span>
                </NavLink>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer Section */}
      <div className="p-2.5 border-t border-outline-variant/60 space-y-0.5 flex-shrink-0">
        <NavLink
          to="/docs"
          className={cn(
            "flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-body-sm transition-colors font-medium",
            location.pathname === "/docs"
              ? "bg-primary/10 text-primary font-semibold"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          )}
        >
          <HelpCircle className="h-4 w-4" />
          <span>Documentation</span>
        </NavLink>
        <button
          onClick={logout}
          className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-body-sm text-error hover:bg-error/10 transition-colors text-left font-medium cursor-pointer"
        >
          <LogOut className="h-4 w-4" />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}
