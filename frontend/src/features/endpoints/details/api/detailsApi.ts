import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../../services/api";

export interface OverviewDetails {
  id: string;
  hostname: string;
  endpoint_type: string;
  is_online: boolean;
  status: string;
  last_heartbeat: string;
  operating_system: string;
  architecture: string;
  serial_number: string;
  manufacturer: string;
  model: string;
  enrolled_date: string;
  agent_version: string;
  ip_addresses: string[];
  mac_addresses: string[];
  current_user: string;
  security_score: number;
  health: string;
}

export interface HardwareDetails {
  cpu_name: string;
  cpu_cores: number;
  logical_processors: number;
  installed_ram_gb: number;
  motherboard: string;
  bios_version: string;
  bios_manufacturer: string;
  tpm_version: string;
  secure_boot_enabled: boolean;
  is_virtual: boolean;
  gpu_name: string;
}

export interface PhysicalDiskItem {
  model: string;
  manufacturer: string;
  serial_number: string;
  media_type: string;
  size_gb: number;
  health_status: string;
  is_boot_disk: boolean;
}

export interface LogicalVolumeItem {
  drive_letter: string;
  volume_name: string;
  file_system: string;
  capacity_gb: number;
  used_gb: number;
  free_gb: number;
  bitlocker_status: string;
}

export interface StorageDetails {
  physical_disks: PhysicalDiskItem[];
  logical_volumes: LogicalVolumeItem[];
  total_capacity_gb: number;
  total_used_gb: number;
  total_free_gb: number;
  drive_health: string;
  bitlocker_status: string;
}

export interface SecurityDetails {
  defender_status: string;
  firewall_status: string;
  bitlocker_status: string;
  tpm_version: string;
  secure_boot_enabled: boolean;
  antivirus_name: string;
  antivirus_status: string;
  security_score: number;
  compliance_score: number;
  risk_level: string;
}

export interface MetricPoint {
  timestamp: string;
  value: number;
}

export interface PerformanceDetails {
  range: string;
  cpu_history: MetricPoint[];
  memory_history: MetricPoint[];
  disk_history: MetricPoint[];
  network_history: MetricPoint[];
}

export interface NetworkAdapterItem {
  adapter_name: string;
  mac_address: string;
  ipv4: string;
  ipv6: string;
  gateway: string;
  dns_servers: string;
  dhcp_enabled: boolean;
  operational_status: string;
}

export interface NetworkDetails {
  hostname: string;
  domain_workgroup: string;
  primary_ipv4: string;
  primary_ipv6: string;
  primary_mac: string;
  primary_dns: string;
  primary_gateway: string;
  adapters: NetworkAdapterItem[];
}

export interface SoftwareItem {
  application_name: string;
  publisher: string;
  version: string;
  install_date: string;
  architecture: string;
}

export interface UpdateItem {
  kb_number: string;
  title: string;
  installed_on: string;
  installed_state: string;
  is_security_update: boolean;
}

export interface ServiceItem {
  service_name: string;
  display_name: string;
  current_state: string;
  start_mode: string;
  process_id: number;
  executable_path: string;
}

export interface ProcessItem {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_mb: number;
  user: string;
}

export interface UserAccountItem {
  username: string;
  is_admin: boolean;
  is_disabled: boolean;
  last_login: string;
}

export interface TimelineEventItem {
  id: string;
  event_type: string;
  title: string;
  timestamp: string;
  details: string;
}

// --- Fetchers ---
export const fetchOverview = async (id: string): Promise<OverviewDetails> => {
  const res = await apiClient.get(`/endpoints/${id}/overview`);
  return res.data.data;
};

export const fetchHardware = async (id: string): Promise<HardwareDetails> => {
  const res = await apiClient.get(`/endpoints/${id}/hardware`);
  return res.data.data;
};

export const fetchStorage = async (id: string): Promise<StorageDetails> => {
  const res = await apiClient.get(`/endpoints/${id}/storage`);
  return res.data.data;
};

export const fetchSecurity = async (id: string): Promise<SecurityDetails> => {
  const res = await apiClient.get(`/endpoints/${id}/security`);
  return res.data.data;
};

export const fetchPerformance = async (id: string, range: string): Promise<PerformanceDetails> => {
  const apiRange = range === "60s" ? "30m" : range;
  const res = await apiClient.get(`/endpoints/${id}/performance?range=${apiRange}`);
  return res.data.data;
};

export const fetchNetwork = async (id: string): Promise<NetworkDetails> => {
  const res = await apiClient.get(`/endpoints/${id}/network`);
  return res.data.data;
};

export const fetchSoftware = async (id: string): Promise<SoftwareItem[]> => {
  const res = await apiClient.get(`/endpoints/${id}/software`);
  const data = res.data.data;
  return Array.isArray(data) ? data : data?.items || [];
};

export const fetchUpdates = async (id: string): Promise<UpdateItem[]> => {
  const res = await apiClient.get(`/endpoints/${id}/updates`);
  const data = res.data.data;
  return Array.isArray(data) ? data : data?.items || [];
};

export const fetchServices = async (id: string): Promise<ServiceItem[]> => {
  const res = await apiClient.get(`/endpoints/${id}/services`);
  const data = res.data.data;
  return Array.isArray(data) ? data : data?.items || [];
};

export const fetchProcesses = async (id: string): Promise<ProcessItem[]> => {
  const res = await apiClient.get(`/endpoints/${id}/processes`);
  const data = res.data.data;
  return Array.isArray(data) ? data : data?.items || [];
};

export const fetchUsers = async (id: string): Promise<UserAccountItem[]> => {
  const res = await apiClient.get(`/endpoints/${id}/users`);
  const data = res.data.data;
  return Array.isArray(data) ? data : data?.items || [];
};

export const fetchTimeline = async (id: string): Promise<TimelineEventItem[]> => {
  const res = await apiClient.get(`/endpoints/${id}/timeline`);
  const data = res.data.data;
  return Array.isArray(data) ? data : data?.items || [];
};

// --- Custom Query Hooks ---

export const useOverview = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "overview"],
    queryFn: () => fetchOverview(id),
    enabled: Boolean(id),
    staleTime: 20000,
    refetchInterval: 30000,
  });

export const useHardware = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "hardware"],
    queryFn: () => fetchHardware(id),
    enabled: Boolean(id),
    staleTime: 30000,
    refetchInterval: 30000,
  });

export const useStorage = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "storage"],
    queryFn: () => fetchStorage(id),
    enabled: Boolean(id),
    staleTime: 30000,
    refetchInterval: 30000,
  });

export const useSecurity = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "security"],
    queryFn: () => fetchSecurity(id),
    enabled: Boolean(id),
    staleTime: 20000,
    refetchInterval: 30000,
  });

export const usePerformance = (id: string, range: string = "1h") => {
  return useQuery({
    queryKey: ["endpoint", id, "performance", range],
    queryFn: () => fetchPerformance(id, range),
    enabled: Boolean(id),
    staleTime: 15000,
    refetchInterval: 30000,
  });
};

export const useNetwork = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "network"],
    queryFn: () => fetchNetwork(id),
    enabled: Boolean(id),
    staleTime: 30000,
    refetchInterval: 30000,
  });

export const useSoftware = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "software"],
    queryFn: () => fetchSoftware(id),
    enabled: Boolean(id),
    staleTime: 60000,
    refetchInterval: 30000,
  });

export const useUpdates = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "updates"],
    queryFn: () => fetchUpdates(id),
    enabled: Boolean(id),
    staleTime: 60000,
    refetchInterval: 30000,
  });

export const useServices = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "services"],
    queryFn: () => fetchServices(id),
    enabled: Boolean(id),
    staleTime: 30000,
    refetchInterval: 30000,
  });

export const useProcesses = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "processes"],
    queryFn: () => fetchProcesses(id),
    enabled: Boolean(id),
    staleTime: 15000,
    refetchInterval: 30000,
  });

export const useUsers = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "users"],
    queryFn: () => fetchUsers(id),
    enabled: Boolean(id),
    staleTime: 60000,
    refetchInterval: 30000,
  });

export const useTimeline = (id: string) =>
  useQuery({
    queryKey: ["endpoint", id, "timeline"],
    queryFn: () => fetchTimeline(id),
    enabled: Boolean(id),
    staleTime: 20000,
    refetchInterval: 30000,
  });
