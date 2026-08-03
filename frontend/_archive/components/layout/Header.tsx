import { Moon, Sun, Bell, Search, Settings, User, LogOut } from "lucide-react";
import { useTheme } from "../../contexts/ThemeContext";
import { useAuth } from "../../contexts/AuthContext";
import { useState } from "react";
import { cn } from "../../utils/cn";

export function Header() {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-40 bg-surface border-b border-outline-variant h-14 flex justify-between items-center px-gutter">
      <div className="flex items-center gap-6">
        {/* Only show title on larger screens or hide sidebar placeholder logic */}
        <span className="text-headline-md font-headline-md font-bold text-primary hidden md:inline-block">
          Sentinel Endpoint Management
        </span>
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-surface-container-high rounded-lg w-64 border border-outline-variant/30">
          <Search className="h-4 w-4 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Search resources..."
            className="bg-transparent border-none focus:ring-0 text-body-sm w-full placeholder:text-on-surface-variant outline-none"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 text-on-surface-variant hover:bg-surface-container-high transition-colors duration-200 rounded-full">
          <Bell className="h-5 w-5" />
        </button>
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-2 text-on-surface-variant hover:bg-surface-container-high transition-colors duration-200 rounded-full relative overflow-hidden w-9 h-9 flex items-center justify-center"
          title="Toggle Theme"
        >
          <Sun className={cn("absolute h-5 w-5 transition-all duration-500", theme === "dark" ? "opacity-100 rotate-0 scale-100" : "opacity-0 -rotate-90 scale-0")} />
          <Moon className={cn("absolute h-5 w-5 transition-all duration-500", theme === "dark" ? "opacity-0 rotate-90 scale-0" : "opacity-100 rotate-0 scale-100")} />
        </button>
        <button className="p-2 text-on-surface-variant hover:bg-surface-container-high transition-colors duration-200 rounded-full">
          <Settings className="h-5 w-5" />
        </button>
        
        {/* User Dropdown */}
        <div className="relative">
          <button 
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="h-8 w-8 rounded-full overflow-hidden border border-outline-variant bg-surface-container-high flex items-center justify-center text-primary"
          >
            <User className="h-5 w-5" />
          </button>

          {dropdownOpen && (
            <>
              <div 
                className="fixed inset-0 z-10" 
                onClick={() => setDropdownOpen(false)} 
              />
              <div className="absolute right-0 mt-2 w-48 bg-surface-container-highest rounded-md shadow-lg border border-outline-variant py-1 z-20">
                <div className="px-4 py-2 border-b border-outline-variant">
                  <p className="text-body-sm font-medium text-on-surface">{user?.username || "Admin"}</p>
                  <p className="text-label-sm text-on-surface-variant truncate">Administrator</p>
                </div>
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    logout();
                  }}
                  className="w-full text-left flex items-center gap-2 px-4 py-2 text-body-sm text-error hover:bg-surface-container transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
