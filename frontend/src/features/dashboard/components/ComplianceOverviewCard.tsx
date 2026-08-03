import React from "react";
import { Link } from "react-router-dom";
import { RefreshCw, AlertCircle, ArrowRight } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useSummary } from "../api/dashboardApi";

export const ComplianceOverviewCard = React.memo(function ComplianceOverviewCard() {
  const { data, isLoading, isError, refetch } = useSummary();

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError || !data) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Compliance Overview</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load compliance policy SLA</p>
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

  const items = data.compliance_overview || [
    { label: "OS Patching", percentage: 94.0, colorClass: "bg-primary" },
    { label: "Antivirus Definitions", percentage: 99.0, colorClass: "bg-primary" },
    { label: "Disk Encryption", percentage: 82.0, colorClass: "bg-tertiary" },
  ];

  return (
    <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4 hover:border-primary/40 transition-colors">
      <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3 mb-3">
        <div>
          <h3 className="text-body-md font-bold text-on-surface">Compliance Overview</h3>
          <p className="text-[11px] text-on-surface-variant">Policy SLA & baseline compliance checks</p>
        </div>
        <Link to="/policies" className="text-xs font-bold text-primary hover:underline flex items-center gap-1">
          Policies <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      <div className="space-y-3.5 flex-1 flex flex-col justify-center">
        {items.map((item, idx) => (
          <div key={idx} className="space-y-1">
            <div className="flex justify-between text-xs text-on-surface font-bold">
              <span>{item.label}</span>
              <span className="text-primary font-black">{item.percentage}%</span>
            </div>
            <div className="h-2 bg-surface-container-highest rounded-full overflow-hidden">
              <div
                className={`h-full ${item.colorClass || "bg-primary"} transition-all duration-500 rounded-full`}
                style={{ width: `${item.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
});
