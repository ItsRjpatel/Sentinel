import { ExecutiveKpiCards } from "../components/ExecutiveKpiCards";
import { FleetHealthCard } from "../components/FleetHealthCard";
import { ComplianceOverviewCard } from "../components/ComplianceOverviewCard";
import { ThreatDistributionCard } from "../components/ThreatDistributionCard";
import { OsDistributionCard } from "../components/OsDistributionCard";
import { PerformanceAnalyticsCard } from "../components/PerformanceAnalyticsCard";
import { RecentAlertsCard } from "../components/RecentAlertsCard";
import { ActiveCommandsCard } from "../components/ActiveCommandsCard";
import { FleetPreviewTable } from "../components/FleetPreviewTable";
import { TopConsumersCard } from "../components/TopConsumersCard";
import { AgentActivitiesCard } from "../components/AgentActivitiesCard";
import { SystemHealthCard } from "../components/SystemHealthCard";

export function DashboardPage() {
  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Info & Real-time Live Telemetry Indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-outline-variant/40 pb-3">
        <div>
          <h1 className="text-2xl font-black text-on-surface tracking-tight">
            Enterprise Security Operations Center (SOC)
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5 font-medium">
            Real-time endpoint telemetry, threat distribution, performance analytics, and fleet policy SLA
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1 bg-surface-container-high rounded-full border border-outline-variant/40">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
            </span>
            <span className="text-[11px] font-extrabold text-on-surface">Live Backend Telemetry</span>
          </div>
        </div>
      </div>

      {/* ROW 1: Executive Overview (8 Isolated KPI Cards) */}
      <ExecutiveKpiCards />

      {/* ROW 2: Fleet Health, Compliance Overview, Threat Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-3">
        <div className="lg:col-span-4">
          <FleetHealthCard />
        </div>
        <div className="lg:col-span-4">
          <ComplianceOverviewCard />
        </div>
        <div className="lg:col-span-4">
          <ThreatDistributionCard />
        </div>
      </div>

      {/* ROW 3: Performance Telemetry & OS Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div className="lg:col-span-8">
          <PerformanceAnalyticsCard />
        </div>
        <div className="lg:col-span-4">
          <OsDistributionCard />
        </div>
      </div>

      {/* ROW 4: Recent Security Alerts & Running Remote Commands */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div className="lg:col-span-6">
          <RecentAlertsCard />
        </div>
        <div className="lg:col-span-6">
          <ActiveCommandsCard />
        </div>
      </div>

      {/* ROW 5: Fleet Preview Table */}
      <div className="w-full">
        <FleetPreviewTable />
      </div>

      {/* ROW 6: Top Resource Consumers, Agent Activity Timeline, System Health */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-12 gap-3">
        <div className="lg:col-span-4">
          <TopConsumersCard />
        </div>
        <div className="lg:col-span-4">
          <AgentActivitiesCard />
        </div>
        <div className="lg:col-span-4">
          <SystemHealthCard />
        </div>
      </div>
    </div>
  );
}
