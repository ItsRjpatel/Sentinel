import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { apiClient } from "../../services/api";
import {
  Search,
  Sun,
  Moon,
  User,
  LogOut,
  ChevronRight,
  Settings,
  Command,
  FileText,
  Users as UsersIcon,
} from "lucide-react";
import { useTheme } from "../../contexts/ThemeContext";
import { useAuth } from "../../contexts/AuthContext";
import { cn } from "../../utils/cn";
import { DropdownMenu } from "../ui/DropdownMenu";
import { NotificationBell } from "./NotificationBell";

const routeTitles: Record<string, string> = {
  "/": "Dashboard",
  "/endpoints": "Endpoints Inventory",
  "/commands": "Remote Commands",
  "/alerts": "Security Alerts",
  "/admin/users": "User Management",
  "/admin/roles": "Roles & RBAC",
  "/admin/permissions": "Permissions",
  "/admin/settings": "System Settings",
  "/admin/audit": "Audit Logs",
  "/docs": "Documentation",
  "/notifications": "Notifications Center",
  "/reports": "Security Reports",
  "/software": "Software Inventory",
};



export function Header() {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const searchInputRef = useRef<HTMLInputElement>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const currentTitle = routeTitles[location.pathname] || "Overview";

  // Ctrl+K / Cmd+K global keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
        setIsSearchOpen(true);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);



  // Debounced global search effect
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setIsSearchOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await apiClient.get(`/dashboard/search?q=${encodeURIComponent(searchQuery)}`);
        const items = res.data?.data?.results || [];
        setSearchResults(items);
        setIsSearchOpen(true);
      } catch (err) {
        console.error("Global search error:", err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);


  const userMenuItems = [
    {
      label: user?.username || "Admin Context",
      disabled: true,
      onClick: () => {},
    },
    {
      label: "User Management",
      icon: <UsersIcon className="h-4 w-4" />,
      onClick: () => navigate("/admin/users"),
    },
    {
      label: "System Settings",
      icon: <Settings className="h-4 w-4" />,
      onClick: () => navigate("/admin/settings"),
    },
    {
      label: "Audit Logs",
      icon: <FileText className="h-4 w-4" />,
      onClick: () => navigate("/admin/audit"),
    },
    {
      label: "Sign out",
      icon: <LogOut className="h-4 w-4" />,
      danger: true,
      onClick: logout,
    },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-30 h-12 bg-surface-container-low border-b border-outline-variant flex items-center px-4 transition-all duration-300">
      {/* Container aligned with page content (offset by sidebar width 240px) */}
      <div className="w-full flex items-center justify-between md:pl-[240px]">
        {/* Left Section: Breadcrumbs + Search Bar */}
        <div className="flex items-center gap-6 flex-1 max-w-[650px] relative">
          {/* Breadcrumb */}
          <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-label-md flex-shrink-0">
            <Link to="/" className="text-on-surface-variant/70 font-medium hover:text-primary transition-colors">
              Console
            </Link>
            <ChevronRight className="h-3.5 w-3.5 text-on-surface-variant/40" />
            <span className="text-on-surface font-semibold truncate">{currentTitle}</span>
          </nav>

          {/* Search Bar */}
          <div className="relative hidden sm:flex items-center gap-2 px-3 py-1 bg-surface-container-high rounded-md w-full max-w-[420px] border border-outline-variant/40 focus-within:border-primary transition-colors">
            <Search className="h-3.5 w-3.5 text-on-surface-variant flex-shrink-0" />
            <input
              ref={searchInputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => searchQuery.trim() && setIsSearchOpen(true)}
              placeholder="Search resources, endpoints, alerts... (Ctrl+K)"
              className="bg-transparent border-none focus:outline-none text-body-sm w-full text-on-surface placeholder:text-on-surface-variant/60"
            />
            <kbd className="hidden md:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-mono text-on-surface-variant bg-surface-container-highest rounded border border-outline-variant/60">
              <Command className="h-2.5 w-2.5" />K
            </kbd>

            {/* Search Dropdown Overlay */}
            {isSearchOpen && (
              <div
                className="absolute top-full left-0 right-0 mt-2 bg-surface-container-high border border-outline-variant rounded-lg shadow-xl z-50 overflow-hidden max-h-[320px] overflow-y-auto"
                onMouseLeave={() => setIsSearchOpen(false)}
              >
                {isSearching ? (
                  <div className="p-4 text-center text-xs text-on-surface-variant font-medium">
                    Searching resources...
                  </div>
                ) : searchResults.length === 0 ? (
                  <div className="p-4 text-center text-xs text-on-surface-variant font-medium">
                    No matching results found
                  </div>
                ) : (
                  <div className="divide-y divide-outline-variant/30">
                    {searchResults.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => {
                          setIsSearchOpen(false);
                          setSearchQuery("");
                          navigate(item.url);
                        }}
                        className="w-full text-left p-3 hover:bg-surface-container-highest transition-colors flex items-center justify-between group"
                      >
                        <div>
                          <p className="text-xs font-bold text-on-surface group-hover:text-primary transition-colors">
                            {item.title}
                          </p>
                          <p className="text-[10px] text-on-surface-variant font-medium">
                            {item.subtitle}
                          </p>
                        </div>
                        <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-primary/10 text-primary">
                          {item.type}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Section: Notifications, Theme Toggle, Settings, User Profile */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Notification Bell */}
          <NotificationBell />

          {/* Theme Toggle */}
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="relative p-1.5 rounded-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors focus:outline-none overflow-hidden"
            title={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            aria-label="Toggle Theme"
          >
            <Sun className={cn("h-4 w-4 transition-all duration-300", theme === "dark" ? "opacity-100 rotate-0 scale-100" : "opacity-0 -rotate-90 scale-0 absolute")} />
            <Moon className={cn("h-4 w-4 transition-all duration-300", theme === "dark" ? "opacity-0 rotate-90 scale-0 absolute" : "opacity-100 rotate-0 scale-100")} />
          </button>

          {/* Settings Button */}
          <button
            onClick={() => navigate("/admin/settings")}
            className="p-1.5 rounded-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors focus:outline-none"
            title="System Settings"
            aria-label="Settings"
          >
            <Settings className="h-4 w-4" />
          </button>

          {/* Vertical Separator */}
          <div className="h-4 w-px bg-outline-variant/60 mx-1" />

          {/* User Profile Dropdown */}
          <DropdownMenu
            trigger={
              <button className="flex items-center gap-2 p-1 rounded-md hover:bg-surface-container-high transition-colors focus:outline-none">
                <div className="w-6 h-6 rounded-md bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                  <User className="h-3.5 w-3.5" />
                </div>
                <span className="text-body-sm font-semibold text-on-surface hidden md:inline-block">
                  {user?.username || "Admin"}
                </span>
              </button>
            }
            items={userMenuItems}
            align="right"
          />
        </div>
      </div>
    </header>
  );
}
