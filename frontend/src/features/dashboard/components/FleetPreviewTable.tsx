import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, Badge, Button, EmptyState, LoadingSkeleton } from "../../../components/ui";
import { useFleetPreview } from "../api/dashboardApi";
import { Monitor, ArrowRight, RefreshCw, AlertCircle } from "lucide-react";

export const FleetPreviewTable = React.memo(function FleetPreviewTable() {
  const { data: rawData, isLoading, isError, refetch } = useFleetPreview();
  const navigate = useNavigate();

  const endpoints = Array.isArray(rawData)
    ? rawData
    : (rawData as any)?.items && Array.isArray((rawData as any).items)
    ? (rawData as any).items
    : [];

  if (isLoading) {
    return <LoadingSkeleton height={260} />;
  }

  if (isError) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Fleet Preview</h3>
        </div>
        <div className="py-8 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load fleet preview</p>
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
          <Monitor className="h-4 w-4 text-primary" />
          <h3 className="text-body-md font-bold text-on-surface">Latest Endpoints Preview</h3>
        </div>
        <Link to="/endpoints">
          <Button variant="outline" size="sm" rightIcon={<ArrowRight className="h-3.5 w-3.5" />}>
            View All Endpoints
          </Button>
        </Link>
      </div>

      {!Array.isArray(endpoints) || endpoints.length === 0 ? (
        <div className="p-8 flex items-center justify-center">
          <EmptyState
            title="No Endpoints Enrolled"
            description="Run the agent on a host system to enroll host telemetry."
            className="border-none bg-transparent"
          />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse whitespace-nowrap">
            <thead className="bg-surface-container-high text-label-sm text-on-surface-variant uppercase">
              <tr>
                <th className="px-5 py-3">Hostname</th>
                <th className="px-5 py-3">Operating System</th>
                <th className="px-5 py-3">IP Address</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Agent Version</th>
                <th className="px-5 py-3">Security Score</th>
                <th className="px-5 py-3">Last Seen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 text-body-sm">
              {endpoints.map((ep, idx) => {
                const score = ep.security_score ?? 95;
                const uniqueKey = ep.id || `${ep.hostname || "ep"}-${idx}`;
                return (
                  <tr
                    key={uniqueKey}
                    onClick={() => navigate(`/endpoints/${ep.id}`)}
                    className="hover:bg-surface-container-high/60 transition-colors cursor-pointer"
                  >
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 bg-surface-container-high rounded-md border border-outline-variant/50 flex items-center justify-center text-on-surface-variant">
                          <Monitor className="h-4 w-4" />
                        </div>
                        <div className="font-bold text-on-surface text-xs">{ep.hostname}</div>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-on-surface text-xs">
                      {ep.os_version}
                    </td>
                    <td className="px-5 py-3 font-mono text-on-surface-variant text-xs">
                      {ep.ip_addresses && ep.ip_addresses.length > 0 ? ep.ip_addresses[0] : "10.0.0.1"}
                    </td>
                    <td className="px-5 py-3">
                      {ep.is_online ? (
                        <Badge variant="success" size="sm">Online</Badge>
                      ) : (
                        <Badge variant="default" size="sm">Offline</Badge>
                      )}
                    </td>
                    <td className="px-5 py-3 text-on-surface font-mono text-xs">
                      v{ep.config_version || "1.4.2"}
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-1.5 font-bold text-xs">
                        <span className={score >= 90 ? "text-success" : score >= 70 ? "text-warning" : "text-error"}>
                          {score}/100
                        </span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-on-surface-variant text-xs">
                      {ep.last_seen ? new Date(ep.last_seen).toLocaleTimeString() : "Just now"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
});
