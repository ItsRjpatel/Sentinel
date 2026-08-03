import React from "react";
import { Link } from "react-router-dom";
import {
  Monitor,
  Activity,
  AlertTriangle,
  Terminal,
  ShieldCheck,
  ShieldAlert,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  WifiOff,
  CheckCircle2
} from "lucide-react";
import { Card, Badge, LoadingSkeleton } from "../../../components/ui";
import { useSummary } from "../api/dashboardApi";

export const ExecutiveKpiCards = React.memo(function ExecutiveKpiCards() {
  const { data, isLoading, isError, refetch } = useSummary();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 xl:grid-cols-8 gap-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <LoadingSkeleton key={i} height={110} />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <Card className="p-4 bg-error/10 border border-error/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-error" />
          <span className="text-body-sm font-semibold text-on-surface">Failed to load Executive KPIs</span>
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

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 xl:grid-cols-8 gap-3">
      {/* 1. Total Endpoints */}
      <Link to="/endpoints" className="block">
        <Card className="flex flex-col justify-between p-3.5 bg-surface-container-low border-outline-variant hover:border-primary/40 transition-colors cursor-pointer h-full">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
              Total Endpoints
            </span>
            <div className="p-1.5 bg-primary/10 rounded-md text-primary">
              <Monitor className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-black text-on-surface tracking-tight">
              {data.total_endpoints.toLocaleString()}
            </div>
            <div className="flex items-center gap-1 text-[11px] text-primary font-semibold mt-1">
              <TrendingUp className="h-3 w-3" />
              <span>{data.total_trend} fleet</span>
            </div>
          </div>
        </Card>
      </Link>

      {/* 2. Online Endpoints */}
      <Link to="/endpoints?status=online" className="block">
        <Card className="flex flex-col justify-between p-3.5 bg-surface-container-low border-outline-variant hover:border-success/40 transition-colors cursor-pointer h-full">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
              Online
            </span>
            <div className="p-1.5 bg-success/10 rounded-md text-success">
              <Activity className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-black text-on-surface tracking-tight">
              {data.online_endpoints.toLocaleString()}
            </div>
            <div className="flex items-center gap-1 text-[11px] text-success font-semibold mt-1">
              <span>
                {data.total_endpoints > 0
                  ? `${Math.round((data.online_endpoints / data.total_endpoints) * 100)}% online`
                  : "0%"}
              </span>
            </div>
          </div>
        </Card>
      </Link>

      {/* 3. Offline Endpoints */}
      <Link to="/endpoints?status=offline" className="block">
        <Card className="flex flex-col justify-between p-3.5 bg-surface-container-low border-outline-variant hover:border-on-surface-variant/40 transition-colors cursor-pointer h-full">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
              Offline
            </span>
            <div className="p-1.5 bg-on-surface-variant/10 rounded-md text-on-surface-variant">
              <WifiOff className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-black text-on-surface tracking-tight">
              {data.offline_endpoints.toLocaleString()}
            </div>
            <div className="flex items-center gap-1 text-[11px] text-on-surface-variant font-semibold mt-1">
              <span>Disconnected</span>
            </div>
          </div>
        </Card>
      </Link>

      {/* 4. Healthy Endpoints */}
      <Link to="/endpoints?status=healthy" className="block">
        <Card className="flex flex-col justify-between p-3.5 bg-surface-container-low border-outline-variant hover:border-success/40 transition-colors cursor-pointer h-full">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
              Healthy
            </span>
            <div className="p-1.5 bg-success/10 rounded-md text-success">
              <CheckCircle2 className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-black text-on-surface tracking-tight">
              {data.healthy_endpoints.toLocaleString()}
            </div>
            <div className="flex items-center gap-1 text-[11px] text-success font-semibold mt-1">
              <span>Optimal State</span>
            </div>
          </div>
        </Card>
      </Link>

      {/* 5. Critical Alerts */}
      <Link to="/alerts?severity=Critical" className="block">
        <Card className="flex flex-col justify-between p-3.5 bg-surface-container-low border-outline-variant hover:border-error/40 transition-colors cursor-pointer h-full">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
              Critical Alerts
            </span>
            <div className="p-1.5 bg-error/10 rounded-md text-error">
              <AlertTriangle className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-black text-error tracking-tight">
              {data.critical_alerts.toLocaleString()}
            </div>
            <div className="flex items-center gap-1 text-[11px] text-error font-semibold mt-1">
              <TrendingDown className="h-3 w-3" />
              <span>Active Threats</span>
            </div>
          </div>
        </Card>
      </Link>

      {/* 6. Running Commands */}
      <Link to="/commands" className="block">
        <Card className="flex flex-col justify-between p-3.5 bg-surface-container-low border-outline-variant hover:border-primary/40 transition-colors cursor-pointer h-full">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
              Commands
            </span>
            <div className="p-1.5 bg-primary/10 rounded-md text-primary">
              <Terminal className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-black text-on-surface tracking-tight">
              {data.running_commands.toLocaleString()}
            </div>
            <div className="flex items-center gap-1 text-[11px] text-primary font-semibold mt-1">
              <span>Executing Tasks</span>
            </div>
          </div>
        </Card>
      </Link>

      {/* 7. Compliance Score */}
      <Link to="/policies" className="block">
        <Card className="flex flex-col justify-between p-3.5 bg-surface-container-low border-outline-variant hover:border-primary/40 transition-colors cursor-pointer h-full">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
              Compliance
            </span>
            <div className="p-1.5 bg-primary/10 rounded-md text-primary">
              <ShieldCheck className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-black text-on-surface tracking-tight">
              {data.compliance_score}%
            </div>
            <div className="flex items-center gap-1 text-[11px] text-primary font-semibold mt-1">
              <span>SLA Compliant</span>
            </div>
          </div>
        </Card>
      </Link>

      {/* 8. Security Score Hero Card */}
      <Link to="/alerts" className="block">
        <Card className="flex flex-col justify-between p-3.5 bg-gradient-to-br from-primary/15 via-surface-container-low to-surface-container-high border-2 border-primary/40 shadow-sm relative overflow-hidden cursor-pointer h-full">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-black text-primary uppercase tracking-wider">
              Security Score
            </span>
            <Badge variant="success" className="text-[10px] px-1.5 py-0">HERO</Badge>
          </div>
          <div className="mt-2">
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-black text-on-surface leading-none">
                {data.security_score}
              </span>
              <span className="text-xs font-bold text-on-surface-variant">/ 100</span>
            </div>
            <div className="flex items-center gap-1 text-[11px] text-primary font-bold mt-1">
              <ShieldAlert className="h-3 w-3" />
              <span>Optimal Defense</span>
            </div>
          </div>
        </Card>
      </Link>
    </div>
  );
});
