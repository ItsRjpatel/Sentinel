import React from "react";
import { useNavigate } from "react-router-dom";
import { Monitor, RefreshCw, AlertCircle } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useOsDistribution } from "../api/dashboardApi";

export const OsDistributionCard = React.memo(function OsDistributionCard() {
  const { data: rawData, isLoading, isError, refetch } = useOsDistribution();
  const navigate = useNavigate();

  const data = Array.isArray(rawData)
    ? rawData
    : (rawData as any)?.items || [];

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError || !data) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Operating Systems</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load OS distribution</p>
          <button
            onClick={() => refetch()}
            className="px-3 py-1 bg-primary text-on-primary rounded text-xs font-bold inline-flex items-center gap-1.5"
          >
            <RefreshCw className="h-3 w-3" /> Retry
          </button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
      <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3">
        <div>
          <h3 className="text-body-md font-bold text-on-surface">Operating Systems</h3>
          <p className="text-[11px] text-on-surface-variant">OS platform breakdown across fleet</p>
        </div>
        <div className="p-1.5 bg-primary/10 text-primary rounded-md">
          <Monitor className="h-4 w-4" />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 my-3">
        {data.map((os: any, idx: number) => (
          <div
            key={`${os.name}-${idx}`}
            onClick={() => navigate(`/endpoints?search=${encodeURIComponent(os.name)}`)}
            className="p-2.5 bg-surface-container-high hover:bg-surface-container-highest transition-colors rounded-md border border-outline-variant/30 flex items-center justify-between cursor-pointer"
          >
            <div className="truncate pr-2">
              <p className="text-xs font-bold text-on-surface truncate">{os.name}</p>
              <p className="text-[10px] text-on-surface-variant font-medium">{os.percentage}% of fleet</p>
            </div>
            <span className="px-2 py-0.5 bg-primary/10 text-primary text-xs font-black rounded">
              {os.count}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
});
