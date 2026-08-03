import React from "react";
import { Laptop, Cpu, HardDrive, ShieldCheck, RefreshCw, AlertCircle } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../../components/ui";
import { useOverview } from "../api/detailsApi";

export const OverviewTab = React.memo(function OverviewTab({ endpointId }: { endpointId: string }) {
  const { data, isLoading, isError, refetch } = useOverview(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load endpoint overview</p>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-error text-on-error rounded text-xs font-bold inline-flex items-center gap-1.5"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        <Card className="p-4 bg-surface-container-low border-outline-variant space-y-2">
          <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Device Model</span>
          <div className="flex items-center justify-between">
            <span className="text-lg font-black text-on-surface">{data.manufacturer}</span>
            <Laptop className="h-5 w-5 text-primary" />
          </div>
          <p className="text-xs text-on-surface-variant font-mono">{data.model}</p>
        </Card>

        <Card className="p-4 bg-surface-container-low border-outline-variant space-y-2">
          <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Operating System</span>
          <div className="flex items-center justify-between">
            <span className="text-lg font-black text-on-surface">{data.operating_system}</span>
            <Cpu className="h-5 w-5 text-tertiary" />
          </div>
          <p className="text-xs text-on-surface-variant font-mono">{data.architecture}</p>
        </Card>

        <Card className="p-4 bg-surface-container-low border-outline-variant space-y-2">
          <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Primary IP</span>
          <div className="flex items-center justify-between">
            <span className="text-lg font-black text-on-surface font-mono">
              {Array.isArray(data.ip_addresses) && data.ip_addresses[0] ? data.ip_addresses[0] : "No data available"}
            </span>
            <HardDrive className="h-5 w-5 text-success" />
          </div>
          <p className="text-xs text-on-surface-variant font-mono">
            MAC: {Array.isArray(data.mac_addresses) && data.mac_addresses[0] ? data.mac_addresses[0] : "No data available"}
          </p>
        </Card>

        <Card className="p-4 bg-surface-container-low border-outline-variant space-y-2">
          <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Security Rating</span>
          <div className="flex items-center justify-between">
            <span className="text-lg font-black text-success">{data.security_score}/100</span>
            <ShieldCheck className="h-5 w-5 text-success" />
          </div>
          <p className="text-xs text-on-surface-variant">Health: <strong className="text-success">{data.health}</strong></p>
        </Card>
      </div>

      {/* System Property Grid */}
      <Card className="p-5 bg-surface-container-low border-outline-variant space-y-4">
        <h3 className="text-body-md font-extrabold text-on-surface border-b border-outline-variant/40 pb-2">
          System Inventory Properties
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          <div>
            <span className="text-on-surface-variant font-medium">Agent ID:</span>
            <p className="font-mono font-bold text-on-surface truncate">{data.id}</p>
          </div>
          <div>
            <span className="text-on-surface-variant font-medium">Serial Number:</span>
            <p className="font-mono font-bold text-on-surface">{data.serial_number}</p>
          </div>
          <div>
            <span className="text-on-surface-variant font-medium">Endpoint Classification:</span>
            <p className="font-bold text-on-surface">{data.endpoint_type}</p>
          </div>
          <div>
            <span className="text-on-surface-variant font-medium">Enrollment Date:</span>
            <p className="font-bold text-on-surface">{new Date(data.enrolled_date).toLocaleDateString()}</p>
          </div>
          <div>
            <span className="text-on-surface-variant font-medium">Config Version:</span>
            <p className="font-mono font-bold text-on-surface">v{data.agent_version}</p>
          </div>
          <div>
            <span className="text-on-surface-variant font-medium">Active Logged-in User:</span>
            <p className="font-bold text-on-surface">{data.current_user}</p>
          </div>
        </div>
      </Card>
    </div>
  );
});
