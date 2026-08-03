import React, { useState, useMemo } from "react";
import { RefreshCw, AlertCircle, Cpu, HardDrive, Server, Network } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { cn } from "../../../utils/cn";
import { usePerformance } from "../api/dashboardApi";

export const PerformanceAnalyticsCard = React.memo(function PerformanceAnalyticsCard() {
  const [timeRange, setTimeRange] = useState<"30m" | "1h" | "6h" | "24h">("1h");
  const [metricTab, setMetricTab] = useState<"CPU" | "Memory" | "Disk" | "Network">("CPU");

  const { data, isLoading, isError, refetch } = usePerformance(timeRange);

  const currentPoints = useMemo(() => {
    if (!data) return [];
    switch (metricTab) {
      case "Memory":
        return data.memory_history;
      case "Disk":
        return data.disk_history;
      case "Network":
        return data.network_history;
      default:
        return data.cpu_history;
    }
  }, [data, metricTab]);

  const svgPathData = useMemo(() => {
    if (!currentPoints || currentPoints.length === 0) return { linePath: "", areaPath: "" };
    const width = 500;
    const height = 120;
    const step = width / (currentPoints.length - 1 || 1);

    const points = currentPoints.map((pt, i) => {
      const x = i * step;
      const y = height - (pt.value / 100) * (height - 10);
      return { x, y };
    });

    const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
    const areaPath = `${linePath} L ${width} ${height} L 0 ${height} Z`;

    return { linePath, areaPath };
  }, [currentPoints]);

  if (isLoading) {
    return <LoadingSkeleton height={300} />;
  }

  if (isError || !data) {
    return (
      <Card className="flex flex-col justify-between h-full bg-surface-container-low border-outline-variant p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-body-md font-bold text-on-surface">Performance Analytics</h3>
        </div>
        <div className="py-12 text-center space-y-2">
          <AlertCircle className="h-8 w-8 text-error mx-auto" />
          <p className="text-xs text-on-surface-variant font-medium">Failed to load performance telemetry</p>
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

  const latestVal = currentPoints.length > 0 ? currentPoints[currentPoints.length - 1].value : 0;

  return (
    <Card className="flex flex-col h-full bg-surface-container-low border-outline-variant p-4">
      {/* Header with Metric & Time Range Selectors */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-outline-variant/40 pb-3">
        <div>
          <h3 className="text-body-md font-bold text-on-surface">Performance Telemetry</h3>
          <p className="text-[11px] text-on-surface-variant">Real-time resource utilization across active agents</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Time Range Selector */}
          <div className="flex gap-0.5 bg-surface-container-high p-0.5 rounded-md border border-outline-variant/40">
            {(["30m", "1h", "6h", "24h"] as const).map((tr) => (
              <button
                key={tr}
                onClick={() => setTimeRange(tr)}
                className={cn(
                  "px-2 py-0.5 text-[10px] font-bold rounded transition-colors",
                  timeRange === tr
                    ? "bg-primary text-on-primary shadow-xs"
                    : "text-on-surface-variant hover:text-on-surface"
                )}
              >
                {tr}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Metric Tabs */}
      <div className="flex items-center gap-2 mt-3 mb-2">
        {(
          [
            { key: "CPU", icon: Cpu, color: "text-primary" },
            { key: "Memory", icon: Server, color: "text-tertiary" },
            { key: "Disk", icon: HardDrive, color: "text-warning" },
            { key: "Network", icon: Network, color: "text-success" },
          ] as const
        ).map(({ key, icon: Icon, color }) => (
          <button
            key={key}
            onClick={() => setMetricTab(key)}
            className={cn(
              "flex-1 py-1.5 px-2 rounded-md border text-xs font-bold flex items-center justify-center gap-1.5 transition-all",
              metricTab === key
                ? "bg-surface-container-high border-primary/50 text-on-surface shadow-xs"
                : "border-outline-variant/30 text-on-surface-variant hover:border-outline-variant"
            )}
          >
            <Icon className={cn("h-3.5 w-3.5", color)} />
            <span>{key}</span>
          </button>
        ))}
      </div>

      {/* SVG Performance Telemetry Graph */}
      <div className="flex-1 min-h-[160px] relative flex items-end justify-between px-1 my-2">
        <svg
          className="absolute inset-0 w-full h-full overflow-visible"
          preserveAspectRatio="none"
          viewBox="0 0 500 120"
        >
          <defs>
            <linearGradient id="telemetryGrad" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="var(--color-primary)" stopOpacity="0.3" />
              <stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0.0" />
            </linearGradient>
          </defs>
          <path d={svgPathData.areaPath} fill="url(#telemetryGrad)" />
          <path
            d={svgPathData.linePath}
            fill="none"
            stroke="var(--color-primary)"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        </svg>

        {/* X-Axis Time Labels */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-between px-1 text-[10px] font-mono text-on-surface-variant/70">
          {currentPoints.map((pt, i) => (
            <span key={i}>{pt.time}</span>
          ))}
        </div>
      </div>

      {/* Footer Metrics */}
      <div className="flex items-center justify-around pt-3 border-t border-outline-variant/40 text-xs">
        <div className="flex items-center gap-1.5 font-semibold text-on-surface">
          <span className="h-2 w-2 rounded-full bg-primary" />
          <span>Current: <strong className="font-extrabold text-primary">{latestVal}%</strong></span>
        </div>
        <div className="flex items-center gap-1.5 font-semibold text-on-surface">
          <span className="h-2 w-2 rounded-full bg-tertiary" />
          <span>Fleet Avg: <strong className="font-extrabold">{data.fleet_average}%</strong></span>
        </div>
        <div className="flex items-center gap-1.5 font-semibold text-on-surface">
          <span className="h-2 w-2 rounded-full bg-warning" />
          <span>Peak Demand: <strong className="font-extrabold text-warning">{data.peak_demand}%</strong></span>
        </div>
      </div>
    </Card>
  );
});
