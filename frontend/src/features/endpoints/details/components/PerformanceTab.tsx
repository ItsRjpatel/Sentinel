import React, { useState, useEffect, useRef } from "react";
import { Cpu, HardDrive, Server, Network, RefreshCw, AlertCircle, Clock, Maximize2, X, Download, Activity } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../../components/ui";
import { cn } from "../../../../utils/cn";
import { usePerformance, useHardware } from "../api/detailsApi";
import type { MetricPoint } from "../api/detailsApi";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

type MetricType = "cpu" | "memory" | "disk" | "network";
type TimeRange = "60s" | "30m" | "1h" | "6h" | "24h";

// Calculate 95th percentile
const calculatePercentile = (data: number[], percentile: number) => {
  if (data.length === 0) return 0;
  const sorted = [...data].sort((a, b) => a - b);
  const index = Math.ceil((percentile / 100) * sorted.length) - 1;
  return sorted[index];
};

export const PerformanceTab = React.memo(function PerformanceTab({ endpointId }: { endpointId: string }) {
  const [range, setRange] = useState<TimeRange>("1h");
  const [activeMetric, setActiveMetric] = useState<MetricType>("cpu");
  const [isExpanded, setIsExpanded] = useState(false);

  const { data, isLoading, isError, refetch } = usePerformance(endpointId, range);
  const { data: hwData } = useHardware(endpointId);

  // chartData strictly mirrors backend telemetry
  const [chartData, setChartData] = useState({
    cpu: [] as MetricPoint[],
    memory: [] as MetricPoint[],
    disk: [] as MetricPoint[],
    network: [] as MetricPoint[],
  });

  const latestSeenTimestamp = useRef("");
  const currentRangeRef = useRef(range);

  useEffect(() => {
    if (!data) return;

    const newestPoint = data.cpu_history[0];
    const hasNewData = newestPoint && newestPoint.timestamp !== latestSeenTimestamp.current;
    const hasRangeChanged = range !== currentRangeRef.current;

    // Only rebuild and trigger animation if we have genuinely new data OR the user changed the time range.
    if (hasNewData || hasRangeChanged) {
      if (newestPoint) {
        latestSeenTimestamp.current = newestPoint.timestamp;
      }
      currentRangeRef.current = range;

      // Log for verification as requested
      console.log("=== PERFORMANCE TAB DIAGNOSTICS ===");
      console.log("Raw API Data (first 5):");
      console.table(data.cpu_history.slice(0, 5));

      const sliceSize = range === "60s" ? -60 : undefined;
      const newCpu = [...data.cpu_history].reverse().slice(sliceSize);
      const newMem = [...data.memory_history].reverse().slice(sliceSize);
      const newDisk = [...data.disk_history].reverse().slice(sliceSize);
      const newNet = [...data.network_history].reverse().slice(sliceSize);

      console.log("Chart Data (rebuilt):");
      console.table(newCpu);

      setChartData({
        cpu: newCpu,
        memory: newMem,
        disk: newDisk,
        network: newNet,
      });
    }
  }, [data, range]);

  if (isLoading) {
    return <LoadingSkeleton height={500} />;
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

  // Active dataset
  let activeData: MetricPoint[] = chartData.cpu;
  let activeUnit = "%";
  let activeTitle = "CPU Utilization";
  let activeIcon = <Cpu className="w-5 h-5" />;
  let activeColor = "#3b82f6";
  let activeSubtext = hwData ? hwData.cpu_name : "CPU";

  if (activeMetric === "cpu") {
    activeData = chartData.cpu;
    activeUnit = "%";
    activeTitle = "CPU Utilization";
    activeIcon = <Cpu className="w-5 h-5" />;
    activeColor = "#10b981"; 
  } else if (activeMetric === "memory") {
    activeData = chartData.memory;
    activeUnit = "%";
    activeTitle = "Memory Usage";
    activeIcon = <Server className="w-5 h-5" />;
    activeColor = "#3b82f6"; 
    activeSubtext = hwData ? `${hwData.installed_ram_gb} GB Total` : "RAM";
  } else if (activeMetric === "disk") {
    activeData = chartData.disk;
    activeUnit = "%";
    activeTitle = "Disk Activity";
    activeIcon = <HardDrive className="w-5 h-5" />;
    activeColor = "#8b5cf6"; 
    activeSubtext = "System Drive";
  } else if (activeMetric === "network") {
    activeData = chartData.network;
    activeUnit = " MB/s";
    activeTitle = "Network Traffic";
    activeIcon = <Network className="w-5 h-5" />;
    activeColor = "#06b6d4"; 
    activeSubtext = "Primary Adapter";
  }

  // All stats calculated strictly from the chartData passed to Recharts
  const rawValues = activeData.map((d) => d.value);
  const current = rawValues.length > 0 ? rawValues[rawValues.length - 1] : 0;
  const peak = rawValues.length > 0 ? Math.max(...rawValues) : 0;
  const avg = rawValues.length > 0 ? rawValues.reduce((a, b) => a + b, 0) / rawValues.length : 0;
  const min = rawValues.length > 0 ? Math.min(...rawValues) : 0;
  const p95 = calculatePercentile(rawValues, 95);
  const lastUpdated = activeData.length > 0 ? activeData[activeData.length - 1].timestamp : "N/A";

  const renderSparkline = (metricData: MetricPoint[], color: string) => (
    <div className="w-20 h-10 ml-auto pointer-events-none">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={metricData}>
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  const getMetricCurrent = (metricData: MetricPoint[]) => 
    metricData.length > 0 ? metricData[metricData.length - 1].value : 0;

  const cpuStops = (
    <>
      <stop offset="0%" stopColor="#ef4444" stopOpacity={0.8} />     
      <stop offset="20%" stopColor="#f97316" stopOpacity={0.6} />    
      <stop offset="40%" stopColor="#eab308" stopOpacity={0.4} />    
      <stop offset="100%" stopColor="#10b981" stopOpacity={0.1} />   
    </>
  );

  const stdStops = (
    <>
      <stop offset="0%" stopColor={activeColor} stopOpacity={0.4} />
      <stop offset="100%" stopColor={activeColor} stopOpacity={0.0} />
    </>
  );

  const renderChartContent = (expanded = false) => (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className={cn("font-bold text-on-surface flex items-center gap-2", expanded ? "text-2xl" : "text-xl")}>
            {activeIcon}
            {activeTitle}
          </h2>
          <p className="text-on-surface-variant text-sm mt-1">{activeSubtext}</p>
        </div>
        <div className="text-right flex flex-col items-end">
          <div className={cn("font-black font-mono text-primary", expanded ? "text-4xl" : "text-3xl")}>
            {current.toFixed(activeMetric === "network" ? 2 : 1)}{activeUnit}
          </div>
          <div className="flex items-center gap-2 mt-1">
            {range === "60s" && (
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-surface-container-highest border border-outline-variant/30">
                <div className={cn("w-2 h-2 rounded-full animate-pulse", isError ? "bg-error" : "bg-success")} />
                <span className={cn("text-[10px] font-bold uppercase", isError ? "text-error" : "text-success")}>
                  {isError ? "Connection Lost" : "LIVE"}
                </span>
              </div>
            )}
            {!expanded && (
              <button
                onClick={() => setIsExpanded(true)}
                className="text-xs font-bold text-on-surface-variant hover:text-primary transition-colors inline-flex items-center gap-1"
              >
                <Maximize2 className="w-3 h-3" /> Expand
              </button>
            )}
          </div>
        </div>
      </div>

      <div className={cn("w-full flex-1 min-h-[250px]", expanded ? "h-[450px]" : "h-64")}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={activeData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorMetric" x1="0" y1="0" x2="0" y2="1">
                {activeMetric === "cpu" ? cpuStops : stdStops}
              </linearGradient>
              <linearGradient id="strokeMetric" x1="0" y1="0" x2="0" y2="1">
                {activeMetric === "cpu" ? (
                  <>
                    <stop offset="0%" stopColor="#ef4444" />
                    <stop offset="20%" stopColor="#f97316" />
                    <stop offset="40%" stopColor="#eab308" />
                    <stop offset="100%" stopColor="#10b981" />
                  </>
                ) : (
                  <stop offset="0%" stopColor={activeColor} />
                )}
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" strokeOpacity={0.1} />
            <XAxis
              dataKey="timestamp"
              tick={range === "60s" ? false : { fontSize: 10, fill: "var(--color-on-surface-variant)" }}
              tickMargin={10}
              minTickGap={30}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[0, activeMetric === "network" ? "auto" : 100]}
              tick={{ fontSize: 10, fill: "var(--color-on-surface-variant)" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--color-surface-container-high)",
                borderColor: "var(--color-outline-variant)",
                borderRadius: "8px",
                color: "var(--color-on-surface)",
                fontSize: "12px",
                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
              }}
              itemStyle={{ color: "var(--color-primary)", fontWeight: "bold" }}
              labelStyle={{ color: "var(--color-on-surface-variant)", marginBottom: "4px" }}
              formatter={(val: any) => [`${(val != null ? Number(val) : 0).toFixed(activeMetric === "network" ? 2 : 1)}${activeUnit}`, activeTitle]}
              labelFormatter={(label) => `Time: ${label}`}
              isAnimationActive={false}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={activeMetric === "cpu" ? "url(#strokeMetric)" : activeColor}
              strokeWidth={expanded ? 3 : 2}
              fillOpacity={1}
              fill="url(#colorMetric)"
              isAnimationActive={true}
              animationDuration={800}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
        {range === "60s" && (
          <div className="flex justify-between text-[10px] font-medium text-on-surface-variant px-1 mt-1 select-none">
            <span>60 seconds</span>
            <span>Now</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-6 gap-4 mt-6 border-t border-outline-variant/30 pt-4">
        <div>
          <div className="text-[10px] uppercase font-bold text-on-surface-variant">Current</div>
          <div className="text-sm font-mono font-bold text-on-surface">{current.toFixed(1)}{activeUnit}</div>
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-on-surface-variant">Peak</div>
          <div className="text-sm font-mono font-bold text-on-surface">{peak.toFixed(1)}{activeUnit}</div>
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-on-surface-variant">Average</div>
          <div className="text-sm font-mono font-bold text-on-surface">{avg.toFixed(1)}{activeUnit}</div>
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-on-surface-variant">Minimum</div>
          <div className="text-sm font-mono font-bold text-on-surface">{min.toFixed(1)}{activeUnit}</div>
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-on-surface-variant">95th Pctl</div>
          <div className="text-sm font-mono font-bold text-on-surface">{p95.toFixed(1)}{activeUnit}</div>
        </div>
        <div>
          <div className="text-[10px] uppercase font-bold text-on-surface-variant flex items-center gap-1">
            <Clock className="w-3 h-3" /> {range === "60s" && !isError ? "Live" : "Updated"}
          </div>
          <div className="text-xs font-mono font-medium text-on-surface mt-0.5 truncate">{lastUpdated}</div>
        </div>
      </div>
    </div>
  );

  const getMetricClass = (metric: MetricType) => cn(
    "flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all border",
    activeMetric === metric
      ? "bg-surface-container-high border-outline-variant shadow-sm relative overflow-hidden before:absolute before:left-0 before:top-0 before:h-full before:w-1 before:bg-primary"
      : "bg-transparent border-transparent hover:bg-surface-container hover:border-outline-variant/30"
  );

  return (
    <div className="space-y-6">
      {/* Top Toolbar */}
      <Card className="p-4 bg-surface-container-low border-outline-variant flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-on-surface">System Performance</h3>
          <p className="text-xs text-on-surface-variant">Real-time endpoint telemetry monitoring</p>
        </div>
        <div className="flex items-center gap-1 bg-surface-container-high p-1 rounded-md border border-outline-variant/30 text-xs">
          {(["60s", "30m", "1h", "6h", "24h"] as const).map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={cn(
                "px-3 py-1.5 rounded font-extrabold transition-colors flex items-center gap-1",
                range === r ? "bg-primary text-on-primary shadow-xs" : "text-on-surface-variant hover:text-on-surface"
              )}
            >
              {r === "60s" && <Activity className={cn("w-3 h-3", range === "60s" ? "text-on-primary" : "text-success")} />} 
              {r === "60s" ? "60s Live" : r}
            </button>
          ))}
        </div>
      </Card>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Left Column: Metric Navigator */}
        <div className="xl:col-span-1 space-y-2">
          <div
            className={getMetricClass("cpu")}
            onClick={() => setActiveMetric("cpu")}
          >
            <div className="p-2 bg-surface-container-highest rounded text-on-surface">
              <Cpu className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-bold uppercase text-on-surface-variant">CPU</div>
              <div className="text-sm font-mono font-black text-on-surface truncate">
                {getMetricCurrent(chartData.cpu).toFixed(1)}%
              </div>
            </div>
            {renderSparkline(chartData.cpu, "#10b981")}
          </div>

          <div
            className={getMetricClass("memory")}
            onClick={() => setActiveMetric("memory")}
          >
            <div className="p-2 bg-surface-container-highest rounded text-on-surface">
              <Server className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-bold uppercase text-on-surface-variant">Memory</div>
              <div className="text-sm font-mono font-black text-on-surface truncate">
                {getMetricCurrent(chartData.memory).toFixed(1)}%
              </div>
            </div>
            {renderSparkline(chartData.memory, "#3b82f6")}
          </div>

          <div
            className={getMetricClass("disk")}
            onClick={() => setActiveMetric("disk")}
          >
            <div className="p-2 bg-surface-container-highest rounded text-on-surface">
              <HardDrive className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-bold uppercase text-on-surface-variant">Disk</div>
              <div className="text-sm font-mono font-black text-on-surface truncate">
                {getMetricCurrent(chartData.disk).toFixed(1)}%
              </div>
            </div>
            {renderSparkline(chartData.disk, "#8b5cf6")}
          </div>

          <div
            className={getMetricClass("network")}
            onClick={() => setActiveMetric("network")}
          >
            <div className="p-2 bg-surface-container-highest rounded text-on-surface">
              <Network className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-bold uppercase text-on-surface-variant">Network</div>
              <div className="text-sm font-mono font-black text-on-surface truncate">
                {getMetricCurrent(chartData.network).toFixed(1)} <span className="text-[10px] text-on-surface-variant font-sans">MB/s</span>
              </div>
            </div>
            {renderSparkline(chartData.network, "#06b6d4")}
          </div>
        </div>

        {/* Right Column: Main Chart */}
        <div className="xl:col-span-3">
          <Card className="p-5 bg-surface-container-low border-outline-variant h-full">
            {renderChartContent(false)}
          </Card>
        </div>
      </div>

      {/* Telemetry Table */}
      <Card className="overflow-hidden border border-outline-variant bg-surface-container-low">
        <div className="p-4 border-b border-outline-variant bg-surface-container-lowest flex items-center justify-between">
          <h3 className="text-sm font-bold text-on-surface">Raw Telemetry Data</h3>
          <div className="text-xs font-mono text-on-surface-variant">
            {Math.max(data.cpu_history.length, data.memory_history.length, data.disk_history.length, data.network_history.length)} Records
          </div>
        </div>
        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-left text-sm text-on-surface">
            <thead className="bg-surface-container-high sticky top-0 z-10 text-xs uppercase text-on-surface-variant">
              <tr>
                <th className="px-4 py-3 font-bold border-b border-outline-variant">Timestamp</th>
                <th className="px-4 py-3 font-bold border-b border-outline-variant text-right">CPU %</th>
                <th className="px-4 py-3 font-bold border-b border-outline-variant text-right">Memory %</th>
                <th className="px-4 py-3 font-bold border-b border-outline-variant text-right">Disk %</th>
                <th className="px-4 py-3 font-bold border-b border-outline-variant text-right">Network MB/s</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/50">
              {Array.from({ length: Math.max(data.cpu_history.length, data.memory_history.length) }).map((_, i) => (
                <tr key={i} className="hover:bg-surface-container-high/50 transition-colors">
                  <td className="px-4 py-2 font-mono text-xs text-on-surface-variant whitespace-nowrap">
                    {data.cpu_history[i]?.timestamp || data.memory_history[i]?.timestamp || ""}
                  </td>
                  <td className="px-4 py-2 text-right font-mono">{data.cpu_history[i]?.value != null ? data.cpu_history[i].value.toFixed(1) : "-"}</td>
                  <td className="px-4 py-2 text-right font-mono">{data.memory_history[i]?.value != null ? data.memory_history[i].value.toFixed(1) : "-"}</td>
                  <td className="px-4 py-2 text-right font-mono">{data.disk_history[i]?.value != null ? data.disk_history[i].value.toFixed(1) : "-"}</td>
                  <td className="px-4 py-2 text-right font-mono">{data.network_history[i]?.value != null ? data.network_history[i].value.toFixed(2) : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Expanded Modal */}
      {isExpanded && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <Card className="w-full max-w-6xl h-full max-h-[800px] bg-surface-container border-outline-variant shadow-2xl flex flex-col relative">
            <div className="flex items-center justify-between p-4 border-b border-outline-variant bg-surface-container-low">
              <h2 className="text-lg font-bold text-on-surface">Detailed Performance Analysis</h2>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-bold bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded transition-colors border border-outline-variant/50">
                  <Download className="w-3.5 h-3.5" /> Export PNG
                </button>
                <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-bold bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded transition-colors border border-outline-variant/50">
                  <Download className="w-3.5 h-3.5" /> Export CSV
                </button>
                <button
                  onClick={() => setIsExpanded(false)}
                  className="p-2 hover:bg-outline-variant/30 text-on-surface rounded-full transition-colors ml-2"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="p-6 flex-1 flex flex-col min-h-0 bg-surface-container-lowest">
              {renderChartContent(true)}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
});
