import React from "react";
import { useNavigate } from "react-router-dom";
import { Activity, RefreshCw, AlertCircle, CheckCircle2, ShieldAlert, Terminal } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useActivities } from "../api/dashboardApi";

export const AgentActivitiesCard = React.memo(function AgentActivitiesCard() {
  const { data: rawData, isLoading, isError, refetch } = useActivities();
  const navigate = useNavigate();

  const activities = Array.isArray(rawData)
    ? rawData
    : (rawData as any)?.items || [];

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Latest Agent Activity</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load agent activity</p>
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

  const getIcon = (type: string) => {
    if (type.includes("Alert")) return <ShieldAlert className="h-3.5 w-3.5 text-error" />;
    if (type.includes("Command")) return <Terminal className="h-3.5 w-3.5 text-primary" />;
    return <CheckCircle2 className="h-3.5 w-3.5 text-success" />;
  };

  const handleActivityClick = (type: string) => {
    if (type.includes("Alert")) {
      navigate("/alerts");
    } else if (type.includes("Command")) {
      navigate("/commands");
    } else {
      navigate("/audit");
    }
  };

  return (
    <Card className="flex flex-col h-full bg-surface-container-low border-outline-variant p-4">
      <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3 mb-3">
        <div>
          <h3 className="text-body-md font-bold text-on-surface">Latest Agent Activity</h3>
          <p className="text-[11px] text-on-surface-variant">Real-time timeline of 10 latest agent events</p>
        </div>
        <div className="p-1.5 bg-primary/10 text-primary rounded-md">
          <Activity className="h-4 w-4" />
        </div>
      </div>

      <div className="space-y-2.5 flex-1 overflow-y-auto max-h-[300px] pr-1 scrollbar-none">
        {activities.map((act: any) => (
          <div
            key={act.id}
            onClick={() => handleActivityClick(act.activity_type || "")}
            className="flex items-start gap-2.5 p-2 rounded-md bg-surface-container-high/60 hover:bg-surface-container-highest transition-colors border border-outline-variant/20 cursor-pointer"
          >
            <div className="mt-0.5 p-1 bg-surface-container-low rounded border border-outline-variant/30">
              {getIcon(act.activity_type)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-on-surface truncate">{act.title}</span>
                <span className="text-[10px] font-mono text-on-surface-variant/80">{act.timestamp}</span>
              </div>
              <p className="text-[11px] text-on-surface-variant truncate mt-0.5">{act.details}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
});
