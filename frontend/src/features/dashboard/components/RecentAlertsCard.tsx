import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldAlert, ArrowRight, RefreshCw, AlertCircle } from "lucide-react";
import { Card, Badge, EmptyState, LoadingSkeleton } from "../../../components/ui";
import { useAlerts } from "../api/dashboardApi";

export const RecentAlertsCard = React.memo(function RecentAlertsCard() {
  const { data: rawData, isLoading, isError, refetch } = useAlerts();

  const alerts = Array.isArray(rawData)
    ? rawData
    : (rawData as any)?.items || (rawData as any)?.alerts || [];

  const navigate = useNavigate();

  const getBadgeVariant = (severity: string) => {
    switch (severity) {
      case "Critical":
        return "error";
      case "High":
        return "warning";
      case "Medium":
        return "info";
      default:
        return "default";
    }
  };

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Recent Security Alerts</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load recent alerts</p>
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
    <Card className="flex flex-col h-full bg-surface-container-low border-outline-variant p-0 overflow-hidden">
      <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-error" />
          <h3 className="text-body-md font-bold text-on-surface">Recent Security Alerts</h3>
        </div>
        <Link
          to="/alerts"
          className="text-label-sm font-bold text-primary hover:underline flex items-center gap-1"
        >
          View All <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      {alerts.length === 0 ? (
        <div className="p-6 flex-1 flex items-center justify-center">
          <EmptyState
            title="No Active Threat Alerts"
            description="All fleet endpoints are reporting clean security scans."
            className="border-none bg-transparent py-4"
          />
        </div>
      ) : (
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left border-collapse">
            <thead className="bg-surface-container-high text-label-sm text-on-surface-variant uppercase">
              <tr>
                <th className="px-4 py-2.5">Severity</th>
                <th className="px-4 py-2.5">Alert Title</th>
                <th className="px-4 py-2.5">Endpoint</th>
                <th className="px-4 py-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 text-body-sm">
              {alerts.map((alert: any) => (
                <tr
                  key={alert.id}
                  onClick={() => navigate("/alerts")}
                  className="hover:bg-surface-container-high/60 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-2.5">
                    <Badge variant={getBadgeVariant(alert.severity)} size="sm">
                      {alert.severity}
                    </Badge>
                  </td>
                  <td className="px-4 py-2.5 font-medium text-on-surface max-w-[220px] truncate">
                    {alert.title}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-on-surface-variant text-xs">
                    {alert.endpoint_name}
                  </td>
                  <td className="px-4 py-2.5 text-on-surface-variant capitalize text-xs">
                    <span className="inline-flex items-center gap-1.5 font-semibold">
                      <span className="h-1.5 w-1.5 rounded-full bg-error" />
                      {alert.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
});
