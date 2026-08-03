import React from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  Monitor,
  CheckCircle2,
  XCircle
} from "lucide-react";
import { useGroupDetails, useGroupEndpoints } from "../api/groupsApi";
import { Card, LoadingSkeleton } from "../../../components/ui";

export const GroupDetailsPage: React.FC = () => {
  const { id = "" } = useParams<{ id: string }>();
  const { data: group, isLoading: groupLoading } = useGroupDetails(id);
  const { data: endpoints = [], isLoading: epLoading } = useGroupEndpoints(id);

  if (groupLoading) {
    return (
      <div className="p-6 space-y-4">
        <LoadingSkeleton height={120} />
        <LoadingSkeleton height={300} />
      </div>
    );
  }

  if (!group) {
    return (
      <div className="p-12 text-center text-on-surface-variant">
        <h3 className="text-body-md font-bold text-on-surface">Group Not Found</h3>
        <Link to="/groups" className="text-primary text-xs font-bold hover:underline mt-2 inline-block">
          Return to Groups List
        </Link>
      </div>
    );
  }

  const stats = group.stats || {
    endpoint_count: endpoints.length,
    online_count: endpoints.filter((e: any) => e.status === "healthy" || e.status === "online").length,
    offline_count: 0,
    compliance_percent: 100,
    health_percent: 100
  };

  return (
    <div className="p-6 space-y-6 bg-surface min-h-screen text-on-surface">
      {/* Top Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/groups"
          className="p-2 bg-surface-container hover:bg-surface-container-high rounded-xl text-on-surface-variant transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-primary/10 text-primary font-mono text-[10px] font-bold rounded uppercase border border-primary/20">
              {group.group_type}
            </span>
            <h1 className="text-body-lg font-black text-on-surface">{group.name}</h1>
          </div>
          <p className="text-xs text-on-surface-variant">{group.description || "No description provided."}</p>
        </div>
      </div>

      {/* Stats Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-surface-container border-outline-variant/50 space-y-1">
          <span className="text-[10px] font-bold uppercase text-on-surface-variant">Total Endpoints</span>
          <p className="text-body-lg font-black text-on-surface">{stats.endpoint_count}</p>
        </Card>
        <Card className="p-4 bg-surface-container border-outline-variant/50 space-y-1">
          <span className="text-[10px] font-bold uppercase text-emerald-400">Online Endpoints</span>
          <p className="text-body-lg font-black text-emerald-400">{stats.online_count}</p>
        </Card>
        <Card className="p-4 bg-surface-container border-outline-variant/50 space-y-1">
          <span className="text-[10px] font-bold uppercase text-primary">Compliance Rate</span>
          <p className="text-body-lg font-black text-primary">{stats.compliance_percent}%</p>
        </Card>
        <Card className="p-4 bg-surface-container border-outline-variant/50 space-y-1">
          <span className="text-[10px] font-bold uppercase text-amber-400">Health Index</span>
          <p className="text-body-lg font-black text-amber-400">{stats.health_percent}%</p>
        </Card>
      </div>

      {/* Member Endpoints List */}
      <Card className="p-5 border-outline-variant/60 space-y-4">
        <h3 className="text-body-md font-black text-on-surface flex items-center gap-2 border-b border-outline-variant/40 pb-3">
          <Monitor className="h-5 w-5 text-primary" /> Group Member Endpoints ({endpoints.length})
        </h3>

        {epLoading ? (
          <LoadingSkeleton height={150} />
        ) : endpoints.length === 0 ? (
          <p className="text-xs text-on-surface-variant text-center py-6">
            No endpoints currently assigned to this group.
          </p>
        ) : (
          <div className="divide-y divide-outline-variant/30">
            {endpoints.map((ep: any) => {
              const isOnline = ep.status === "healthy" || ep.status === "online";
              return (
                <div key={ep.id} className="py-3 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-3">
                    <Monitor className="h-4 w-4 text-primary" />
                    <div>
                      <Link to={`/endpoints/${ep.id}`} className="font-bold text-on-surface hover:text-primary transition-colors">
                        {ep.hostname || ep.id}
                      </Link>
                      <p className="text-[10px] font-mono text-on-surface-variant">{ep.os_version || "Windows"}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className="font-mono text-on-surface-variant">{ep.ip_address}</span>
                    <div className="flex items-center gap-1">
                      {isOnline ? (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          <span className="font-bold text-emerald-400 uppercase text-[10px]">Online</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="h-4 w-4 text-on-surface-variant" />
                          <span className="font-bold text-on-surface-variant uppercase text-[10px]">Offline</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
};
