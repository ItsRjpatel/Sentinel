import { useMemo } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import {
  LayoutDashboard,
  ShieldCheck,
  Activity,
  Cpu,
  HardDrive,
  Network,
  Package,
  FileCheck,
  PlaySquare,
  Terminal,
  Users,
  Clock,
} from "lucide-react";
import { cn } from "../../../../utils/cn";
import { useOverview } from "../api/detailsApi";
import { EndpointDetailsHeader } from "../components/EndpointDetailsHeader";
import { OverviewTab } from "../components/OverviewTab";
import { SecurityTab } from "../components/SecurityTab";
import { PerformanceTab } from "../components/PerformanceTab";
import { HardwareTab } from "../components/HardwareTab";
import { StorageTab } from "../components/StorageTab";
import { NetworkTab } from "../components/NetworkTab";
import { SoftwareTab } from "../components/SoftwareTab";
import { UpdatesTab } from "../components/UpdatesTab";
import { ServicesTab } from "../components/ServicesTab";
import { ProcessesTab } from "../components/ProcessesTab";
import { UsersTab } from "../components/UsersTab";
import { TimelineTab } from "../components/TimelineTab";

const TABS = [
  { key: "overview", label: "Overview", icon: LayoutDashboard },
  { key: "security", label: "Security", icon: ShieldCheck },
  { key: "performance", label: "Performance", icon: Activity },
  { key: "hardware", label: "Hardware", icon: Cpu },
  { key: "storage", label: "Storage", icon: HardDrive },
  { key: "network", label: "Network", icon: Network },
  { key: "software", label: "Installed Software", icon: Package },
  { key: "updates", label: "Windows Updates", icon: FileCheck },
  { key: "services", label: "Services", icon: PlaySquare },
  { key: "processes", label: "Processes", icon: Terminal },
  { key: "users", label: "Local Users", icon: Users },
  { key: "timeline", label: "Activity Timeline", icon: Clock },
] as const;

export function EndpointDetailsPage() {
  const { id = "" } = useParams<{ id: string }>();
  const [searchParams, setSearchParams] = useSearchParams();

  const activeTabKey = searchParams.get("tab") || "overview";

  const { data: overview } = useOverview(id);

  const handleTabChange = (key: string) => {
    setSearchParams({ tab: key }, { replace: false });
  };

  const activeTabComponent = useMemo(() => {
    switch (activeTabKey) {
      case "overview": return <OverviewTab endpointId={id} />;
      case "security": return <SecurityTab endpointId={id} />;
      case "performance": return <PerformanceTab endpointId={id} />;
      case "hardware": return <HardwareTab endpointId={id} />;
      case "storage": return <StorageTab endpointId={id} />;
      case "network": return <NetworkTab endpointId={id} />;
      case "software": return <SoftwareTab endpointId={id} />;
      case "updates": return <UpdatesTab endpointId={id} />;
      case "services": return <ServicesTab endpointId={id} />;
      case "processes": return <ProcessesTab endpointId={id} />;
      case "users": return <UsersTab endpointId={id} />;
      case "timeline": return <TimelineTab endpointId={id} />;
      default: return <OverviewTab endpointId={id} />;
    }
  }, [activeTabKey, id]);

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Sticky Header with Breadcrumbs & Actions */}
      <EndpointDetailsHeader overview={overview} />

      {/* Sticky 12-Tab Navigation Bar */}
      <div className="sticky top-12 z-20 bg-surface-container-low border-b border-outline-variant/60 py-1 overflow-x-auto scrollbar-none shadow-xs">
        <div className="flex items-center gap-1 min-w-max">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTabKey === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => handleTabChange(tab.key)}
                className={cn(
                  "px-3 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all cursor-pointer select-none",
                  isActive
                    ? "bg-primary text-on-primary shadow-xs"
                    : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
                )}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Active Tab View */}
      <div className="w-full min-h-[400px]">
        {activeTabComponent}
      </div>
    </div>
  );
}
