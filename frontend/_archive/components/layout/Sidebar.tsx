import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  Laptop, 
  Settings2,
  Shield, 
  ShieldAlert, 
  HelpCircle,
  Plus,
  LogOut,
  ChevronLeft
} from "lucide-react";
import { cn } from "../../utils/cn";
import { useAuth } from "../../contexts/AuthContext";

type NavItem = {
  name: string;
  path: string;
  icon: React.ElementType;
};

type NavSection = {
  title: string;
  items: NavItem[];
};

const navigation: NavSection[] = [
  {
    title: "",
    items: [{ name: "Dashboard", path: "/", icon: LayoutDashboard }],
  },
  {
    title: "Fleet",
    items: [
      { name: "Endpoint Management", path: "/endpoints", icon: Laptop },
      { name: "Operations", path: "/operations", icon: Settings2 }, 
    ],
  },
  {
    title: "Shield",
    items: [
      { name: "Security", path: "/alerts", icon: Shield },
    ],
  },
  {
    title: "System",
    items: [
      { name: "Administration", path: "/admin", icon: ShieldAlert },
      { name: "Help", path: "/help", icon: HelpCircle },
    ],
  },
];

interface SidebarProps {
  isPinned: boolean;
  setIsPinned: (pinned: boolean) => void;
}

export function Sidebar({ isPinned, setIsPinned }: SidebarProps) {
  const isExpanded = isPinned;

  const { logout } = useAuth();

  return (
    <aside
      className={cn(
        "fixed top-0 left-0 h-screen bg-sidebar border-r border-border transition-all duration-300 ease-in-out z-20 flex flex-col hidden md:flex",
        isExpanded ? "w-[280px]" : "w-[72px]"
      )}
    >
      <div className={cn("p-6 flex flex-col justify-center h-20 border-b border-border transition-all", isExpanded ? "" : "items-center px-0")}>
        <div className="flex items-center gap-3 mb-1">
          <div className="h-8 w-8 bg-primary-container rounded flex items-center justify-center flex-shrink-0">
            <Shield className="h-5 w-5 text-on-primary-container" />
          </div>
          <div className={cn("transition-opacity duration-300 whitespace-nowrap", isExpanded ? "opacity-100 w-auto" : "opacity-0 w-0 overflow-hidden")}>
            <h2 className="text-body-lg font-headline-md font-bold text-on-surface">Sentinel Ops</h2>
            <p className="text-body-sm text-on-surface-variant opacity-70">Enterprise Console</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-2 overflow-x-hidden scrollbar-hide">
        {navigation.map((section, idx) => (
          <div key={idx} className="mb-4">
            {section.title && (
              <div 
                className={cn(
                  "px-5 text-label-sm text-on-surface-variant uppercase tracking-wider opacity-50 mb-1 transition-all duration-300",
                  isExpanded ? "opacity-100 h-auto" : "opacity-0 h-0 overflow-hidden m-0 p-0"
                )}
              >
                {section.title}
              </div>
            )}
            
            <nav className="space-y-1 mt-1">
              {section.items.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 mx-2 px-3 py-2 rounded-lg transition-all duration-150 group relative border-l-4",
                      isActive
                        ? "bg-secondary-container text-on-secondary-container border-primary"
                        : "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface border-transparent"
                    )
                  }
                >
                  <item.icon className="h-5 w-5 flex-shrink-0 transition-transform duration-200 group-hover:scale-110" />
                  
                  {isExpanded && (
                    <span className="text-label-md font-label-md whitespace-nowrap">
                      {item.name}
                    </span>
                  )}

                  {/* Floating tooltip for collapsed state */}
                  {!isExpanded && (
                    <div className="absolute left-full ml-4 px-2 py-1 bg-surface-container-highest border border-border text-on-surface text-label-md rounded-md shadow-lg opacity-0 -translate-x-2 invisible group-hover:visible group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200 z-50 whitespace-nowrap flex items-center">
                      <div className="absolute left-0 -translate-x-1/2 top-1/2 -translate-y-1/2 w-2 h-2 bg-surface-container-highest border-l border-b border-border rotate-45" />
                      {item.name}
                    </div>
                  )}
                </NavLink>
              ))}
            </nav>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-border flex flex-col gap-4">
        {isExpanded ? (
          <button className="w-full flex items-center justify-center gap-2 py-2.5 bg-primary text-on-primary rounded-lg font-label-md hover:opacity-90 transition-all active:scale-95">
            <Plus className="h-4 w-4" />
            New Deployment
          </button>
        ) : (
          <button className="w-full flex items-center justify-center py-2.5 bg-primary text-on-primary rounded-lg hover:opacity-90 transition-all active:scale-95 group relative">
            <Plus className="h-5 w-5" />
            <div className="absolute left-full ml-4 px-2 py-1 bg-surface-container-highest border border-border text-on-surface text-label-md rounded-md shadow-lg opacity-0 -translate-x-2 invisible group-hover:visible group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200 z-50 whitespace-nowrap flex items-center">
              <div className="absolute left-0 -translate-x-1/2 top-1/2 -translate-y-1/2 w-2 h-2 bg-surface-container-highest border-l border-b border-border rotate-45" />
              New Deployment
            </div>
          </button>
        )}

        <div className="flex items-center justify-between mt-2">
          <button 
            onClick={() => logout()}
            className="flex items-center gap-3 text-on-surface-variant hover:text-primary transition-all px-2 py-2 group relative"
          >
            <LogOut className="h-5 w-5 flex-shrink-0 group-hover:scale-110 transition-transform" />
            {isExpanded && <span className="text-label-md font-label-md whitespace-nowrap">Logout</span>}
            
            {!isExpanded && (
              <div className="absolute left-full ml-4 px-2 py-1 bg-surface-container-highest border border-border text-on-surface text-label-md rounded-md shadow-lg opacity-0 -translate-x-2 invisible group-hover:visible group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200 z-50 whitespace-nowrap flex items-center">
                <div className="absolute left-0 -translate-x-1/2 top-1/2 -translate-y-1/2 w-2 h-2 bg-surface-container-highest border-l border-b border-border rotate-45" />
                Logout
              </div>
            )}
          </button>

          {isExpanded && (
            <button
              onClick={() => setIsPinned(!isPinned)}
              className="p-2 rounded-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors focus:outline-none"
              title="Collapse Sidebar"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}
