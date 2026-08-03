import React, { useState } from "react";
import { Cpu, HardDrive, Server, Network, RefreshCw, AlertCircle } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../../components/ui";
import { cn } from "../../../../utils/cn";
import { usePerformance } from "../api/detailsApi";
import type { MetricPoint } from "../api/detailsApi";

export const PerformanceTab = React.memo(function PerformanceTab({ endpointId }: { endpointId: string }) {
  const [range, setRange] = useState<"30m" | "1h" | "6h" | "24h">("1h");
  const [activeMetric, setActiveMetric] = useState<"cpu" | "memory" | "disk" | "network">("cpu");

  const { data, isLoading, isError, refetch } = usePerformance(endpointId, range);

  if (isLoading) {
    return <LoadingSkeleton height={360} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load performance telemetry</p>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-error text-on-error rounded text-xs font-bold inline-flex items-center gap-1.5"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </Card>
    );
  }

  const getMetricData = (): MetricPoint[] => {
    switch (activeMetric) {
      case "cpu": return data.cpu_history;
      case "memory": return data.memory_history;
      case "disk": return data.disk_history;
      case "network": return data.network_history;
    }
  };

  const metricPoints = getMetricData();
  const currentVal = metricPoints.length > 0 ? metricPoints[metricPoints.length - 1].value : 0;

  // Render SVG Path
  const width = 800;
  const height = 180;
  const padding = 20;

  const maxVal = Math.max(...metricPoints.map((p) => p.value), 100);
  const minVal = 0;

  const pointsString = metricPoints
    .map((p, idx) => {
      const x = padding + (idx / Math.max(metricPoints.length - 1, 1)) * (width - padding * 2);
      const y = height - padding - ((p.value - minVal) / (maxVal - minVal)) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(" ");

  const areaString = metricPoints.length > 0
    ? `${padding},${height - padding} ${pointsString} ${width - padding},${height - padding}`
    : "";

  return (
    <Card className="p-5 bg-surface-container-low border-outline-variant space-y-4">
      {/* Selector Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-outline-variant/40 pb-3">
        {/* Metric Tabs */}
        <div className="flex items-center gap-1.5 bg-surface-container-high p-1 rounded-lg border border-outline-variant/30">
          <button
            onClick={() => setActiveMetric("cpu")}
            className={cn(
              "px-3 py-1 rounded text-xs font-extrabold flex items-center gap-1.5 transition-colors",
              activeMetric === "cpu" ? "bg-primary text-on-primary shadow-xs" : "text-on-surface-variant hover:text-on-surface"
            )}
          >
            <Cpu className="h-3.5 w-3.5" /> CPU
          </button>
          <button
            onClick={() => setActiveMetric("memory")}
            className={cn(
              "px-3 py-1 rounded text-xs font-extrabold flex items-center gap-1.5 transition-colors",
              activeMetric === "memory" ? "bg-primary text-on-primary shadow-xs" : "text-on-surface-variant hover:text-on-surface"
            )}
          >
            <Server className="h-3.5 w-3.5" /> RAM
          </button>
          <button
            onClick={() => setActiveMetric("disk")}
            className={cn(
              "px-3 py-1 rounded text-xs font-extrabold flex items-center gap-1.5 transition-colors",
              activeMetric === "disk" ? "bg-primary text-on-primary shadow-xs" : "text-on-surface-variant hover:text-on-surface"
            )}
          >
            <HardDrive className="h-3.5 w-3.5" /> Disk
          </button>
          <button
            onClick={() => setActiveMetric("network")}
            className={cn(
              "px-3 py-1 rounded text-xs font-extrabold flex items-center gap-1.5 transition-colors",
              activeMetric === "network" ? "bg-primary text-on-primary shadow-xs" : "text-on-surface-variant hover:text-on-surface"
            )}
          >
            <Network className="h-3.5 w-3.5" /> Network
          </button>
        </div>

        {/* Time Selector */}
        <div className="flex items-center gap-1 bg-surface-container-high p-1 rounded-md border border-outline-variant/30 text-xs">
          {(["30m", "1h", "6h", "24h"] as const).map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={cn(
                "px-2.5 py-0.5 rounded font-extrabold transition-colors",
                range === r ? "bg-surface-container-low text-primary border border-outline-variant/40" : "text-on-surface-variant hover:text-on-surface"
              )}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Header Stat & Graph */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase text-on-surface-variant">
            Live {activeMetric.toUpperCase()} Utilization History
          </span>
          <span className="text-xl font-black text-primary font-mono">
            {currentVal}{activeMetric === "network" ? " MB/s" : "%"}
          </span>
        </div>

        {/* SVG Area Line Graph */}
        <div className="w-full bg-surface-container-high/60 rounded-xl p-3 border border-outline-variant/30">
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-44 overflow-visible">
            <defs>
              <linearGradient id="perfGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--color-primary, #3b82f6)" stopOpacity="0.35" />
                <stop offset="100%" stopColor="var(--color-primary, #3b82f6)" stopOpacity="0.0" />
              </linearGradient>
            </defs>

            {/* Grid lines */}
            <line x1={padding} y1={padding} x2={width - padding} y2={padding} stroke="currentColor" strokeOpacity="0.1" />
            <line x1={padding} y1={height / 2} x2={width - padding} y2={height / 2} stroke="currentColor" strokeOpacity="0.1" />
            <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="currentColor" strokeOpacity="0.1" />

            {/* Area Fill */}
            {areaString && <polygon points={areaString} fill="url(#perfGrad)" />}

            {/* Line Path */}
            {pointsString && (
              <polyline
                fill="none"
                stroke="var(--color-primary, #3b82f6)"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={pointsString}
              />
            )}
          </svg>

          {/* Time Labels */}
          <div className="flex justify-between text-[10px] font-mono text-on-surface-variant px-2 pt-1 border-t border-outline-variant/30">
            <span>{metricPoints[0]?.timestamp || "00:00"}</span>
            <span>{metricPoints[Math.floor(metricPoints.length / 2)]?.timestamp || "12:00"}</span>
            <span>{metricPoints[metricPoints.length - 1]?.timestamp || "23:59"}</span>
          </div>
        </div>
      </div>
    </Card>
  );
});
