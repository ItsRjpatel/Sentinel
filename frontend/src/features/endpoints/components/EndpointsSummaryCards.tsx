import React from "react";
import { Monitor, Activity, WifiOff, Laptop, Server, RefreshCw, AlertCircle } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useEndpointsSummary } from "../api/endpointsApi";

interface EndpointsSummaryCardsProps {
  params?: { status?: string; os?: string };
  onParamsChange?: (newParams: { status?: string; os?: string; page?: number }) => void;
}

export const EndpointsSummaryCards = React.memo(function EndpointsSummaryCards({
  params,
  onParamsChange,
}: EndpointsSummaryCardsProps) {
  const { data, isLoading, isError, refetch } = useEndpointsSummary();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <LoadingSkeleton key={i} height={90} />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <Card className="p-4 bg-error/10 border border-error/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-error" />
          <span className="text-body-sm font-semibold text-on-surface">Failed to load endpoints summary</span>
        </div>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-error text-on-error rounded-md text-xs font-bold flex items-center gap-1.5 hover:opacity-90 transition-opacity"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </Card>
    );
  }

  const cards = [
    { label: "Total Endpoints", count: data.total_endpoints, icon: Monitor, color: "text-primary bg-primary/10", border: "hover:border-primary/40", filter: { status: "all", os: "all", page: 1 }, active: params?.status === "all" && params?.os === "all" },
    { label: "Online", count: data.online_count, icon: Activity, color: "text-success bg-success/10", border: "hover:border-success/40", filter: { status: "online", os: "all", page: 1 }, active: params?.status === "online" },
    { label: "Offline", count: data.offline_count, icon: WifiOff, color: "text-on-surface-variant bg-on-surface-variant/10", border: "hover:border-on-surface-variant/40", filter: { status: "offline", os: "all", page: 1 }, active: params?.status === "offline" },
    { label: "Windows", count: data.windows_count, icon: Laptop, color: "text-primary bg-primary/10", border: "hover:border-primary/40", filter: { status: "all", os: "windows", page: 1 }, active: params?.os === "windows" },
    { label: "Linux", count: data.linux_count, icon: Server, color: "text-warning bg-warning/10", border: "hover:border-warning/40", filter: { status: "all", os: "linux", page: 1 }, active: params?.os === "linux" },
    { label: "macOS", count: data.macos_count, icon: Laptop, color: "text-tertiary bg-tertiary/10", border: "hover:border-tertiary/40", filter: { status: "all", os: "macos", page: 1 }, active: params?.os === "macos" },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((c) => {
        const Icon = c.icon;
        return (
          <Card
            key={c.label}
            onClick={() => onParamsChange?.(c.filter)}
            className={`flex flex-col justify-between p-3.5 bg-surface-container-low border-outline-variant ${c.border} transition-all cursor-pointer ${
              c.active ? "ring-2 ring-primary/60 bg-surface-container-high/60" : ""
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
                {c.label}
              </span>
              <div className={`p-1.5 rounded-md ${c.color}`}>
                <Icon className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-2">
              <div className="text-2xl font-black text-on-surface tracking-tight">
                {c.count.toLocaleString()}
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
});

