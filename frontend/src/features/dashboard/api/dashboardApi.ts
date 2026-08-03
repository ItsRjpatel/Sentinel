import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";

// --- Interfaces matching backend data structures ---

export interface ComplianceItem {
  label: string;
  percentage: number;
  colorClass: string;
}

export interface StatusBreakdown {
  total: number;
  online: number;
  healthy: number;
  offline: number;
  warning?: number;
  critical?: number;
  unknown?: number;
}

export interface ExecutiveKpiData {
  total_endpoints: number;
  online_endpoints: number;
  offline_endpoints: number;
  healthy_endpoints: number;
  critical_alerts: number;
  warning_alerts: number;
  running_commands: number;
  compliance_score: number;
  security_score: number;
  last_sync: string;
  total_trend: string;
  online_trend: string;
  alerts_trend: string;
  commands_trend: string;
  status_breakdown: StatusBreakdown;
  compliance_overview: ComplianceItem[];
}

export interface FleetHealthData {
  online: number;
  offline: number;
  inactive: number;
  pending: number;
  isolated: number;
  needs_attention: number;
  healthy: number;
  warning: number;
  critical: number;
  unknown: number;
  total: number;
}

export interface ThreatDistributionData {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
  total_threats: number;
}

export interface OsDistributionItem {
  name: string;
  count: number;
  percentage: number;
}

export interface TelemetryPoint {
  time: string;
  value: number;
}

export interface PerformanceTelemetryData {
  cpu_history: TelemetryPoint[];
  memory_history: TelemetryPoint[];
  disk_history: TelemetryPoint[];
  network_history: TelemetryPoint[];
  fleet_average: number;
  peak_demand: number;
}

export interface TopConsumerItem {
  hostname: string;
  cpu: number;
  memory: number;
  disk: number;
  status: string;
  os: string;
  agent_version: string;
  last_seen: string;
}

export interface AgentActivityItem {
  id: string;
  activity_type: string;
  title: string;
  endpoint_name: string;
  timestamp: string;
  details: string;
  status: string;
}

export interface SystemServiceHealth {
  service: string;
  status: string;
  latency_ms: number;
  last_checked: string;
  details: string;
}

export interface ApiAlert {
  id: string;
  title: string;
  severity: "Critical" | "High" | "Medium" | "Low";
  description: string;
  endpoint_name: string;
  status: string;
  created_at: string;
}

export interface ApiCommand {
  id: string;
  command_type: string;
  status: string;
  endpoint_id: string;
  created_by: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface ApiEndpoint {
  id: string;
  hostname: string;
  os_version: string;
  hardware_hash: string;
  mac_addresses: string[];
  ip_addresses: string[];
  status: string;
  is_online: boolean;
  last_seen: string;
  current_user?: string;
  security_score?: number;
  config_version?: string;
}

// --- Fetcher Functions ---

export const fetchDashboardSummary = async (): Promise<ExecutiveKpiData> => {
  const res = await apiClient.get("/dashboard/summary");
  return res.data?.data ?? {};
};

export const fetchFleetHealth = async (): Promise<FleetHealthData> => {
  const res = await apiClient.get("/dashboard/fleet-health");
  return res.data?.data ?? {};
};

export const fetchThreatDistribution = async (): Promise<ThreatDistributionData> => {
  const res = await apiClient.get("/dashboard/threat-distribution");
  return res.data?.data ?? {};
};

export const fetchOsDistribution = async (): Promise<OsDistributionItem[]> => {
  const res = await apiClient.get("/dashboard/os-distribution");
  const payload = res.data?.data;
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.items)) return payload.items;
  return [];
};

export const fetchPerformance = async (timeRange: string = "1h"): Promise<PerformanceTelemetryData> => {
  const res = await apiClient.get(`/dashboard/performance?time_range=${timeRange}`);
  return res.data?.data ?? {};
};

export const fetchTopConsumers = async (): Promise<TopConsumerItem[]> => {
  const res = await apiClient.get("/dashboard/top-consumers");
  const payload = res.data?.data;
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.items)) return payload.items;
  return [];
};

export const fetchActivities = async (): Promise<AgentActivityItem[]> => {
  const res = await apiClient.get("/dashboard/activities");
  const payload = res.data?.data;
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.items)) return payload.items;
  return [];
};

export const fetchSystemHealth = async (): Promise<SystemServiceHealth[]> => {
  const res = await apiClient.get("/dashboard/system-health");
  const payload = res.data?.data;
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.items)) return payload.items;
  return [];
};

export const fetchRecentAlerts = async (): Promise<ApiAlert[]> => {
  const res = await apiClient.get("/alerts?limit=5");
  const payload = res.data?.data;
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.items)) return payload.items;
  if (payload && Array.isArray(payload.alerts)) return payload.alerts;
  return [];
};

export const fetchRecentCommands = async (): Promise<ApiCommand[]> => {
  const res = await apiClient.get("/commands?page_size=5");
  const payload = res.data?.data;
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.items)) return payload.items;
  if (payload && Array.isArray(payload.commands)) return payload.commands;
  return [];
};

export const fetchFleetPreview = async (): Promise<ApiEndpoint[]> => {
  const res = await apiClient.get("/endpoints?page_size=5");
  const payload = res.data?.data;
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.items)) return payload.items;
  if (payload && Array.isArray(payload.endpoints)) return payload.endpoints;
  return [];
};


// --- Isolated Custom Hooks ---

export const useSummary = () =>
  useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: fetchDashboardSummary,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useFleetHealth = () =>
  useQuery({
    queryKey: ["dashboard", "fleet-health"],
    queryFn: fetchFleetHealth,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useThreatDistribution = () =>
  useQuery({
    queryKey: ["dashboard", "threat-distribution"],
    queryFn: fetchThreatDistribution,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useOsDistribution = () =>
  useQuery({
    queryKey: ["dashboard", "os-distribution"],
    queryFn: fetchOsDistribution,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const usePerformance = (timeRange: string = "1h") =>
  useQuery({
    queryKey: ["dashboard", "performance", timeRange],
    queryFn: () => fetchPerformance(timeRange),
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useTopConsumers = () =>
  useQuery({
    queryKey: ["dashboard", "top-consumers"],
    queryFn: fetchTopConsumers,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useActivities = () =>
  useQuery({
    queryKey: ["dashboard", "activities"],
    queryFn: fetchActivities,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useSystemHealth = () =>
  useQuery({
    queryKey: ["dashboard", "system-health"],
    queryFn: fetchSystemHealth,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useAlerts = () =>
  useQuery({
    queryKey: ["dashboard", "alerts"],
    queryFn: fetchRecentAlerts,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useCommands = () =>
  useQuery({
    queryKey: ["dashboard", "commands"],
    queryFn: fetchRecentCommands,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useFleetPreview = () =>
  useQuery({
    queryKey: ["dashboard", "fleet-preview"],
    queryFn: fetchFleetPreview,
    refetchInterval: 30000,
    staleTime: 20000,
  });
