import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";

export interface EndpointItem {
  id: string;
  hostname: string;
  os_version: string;
  hardware_hash: string;
  mac_addresses: string[];
  ip_addresses: string[];
  status: string;
  is_online: boolean;
  last_seen: string;
  current_user: string;
  security_score: number;
  health: string;
  config_version: string;
  tpm_enabled: boolean;
  defender_status: string;
  bitlocker_status: string;
  policy_tag: string;
}

export interface EndpointsSummary {
  total_endpoints: number;
  online_count: number;
  offline_count: number;
  windows_count: number;
  linux_count: number;
  macos_count: number;
}

export interface EndpointsPaginationMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginatedEndpointsData {
  items: EndpointItem[];
  meta: EndpointsPaginationMeta;
}

export interface EndpointsQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  os?: string;
  risk?: string;
  tag?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

// --- API Fetchers ---

export const fetchEndpointsSummary = async (): Promise<EndpointsSummary> => {
  const res = await apiClient.get("/endpoints/summary");
  return res.data.data;
};

export const fetchEndpoints = async (params: EndpointsQueryParams = {}): Promise<PaginatedEndpointsData> => {
  const query = new URLSearchParams();
  if (params.page) query.append("page", params.page.toString());
  if (params.page_size) query.append("page_size", params.page_size.toString());
  if (params.search) query.append("search", params.search);
  if (params.status && params.status !== "all") query.append("status", params.status);
  if (params.os && params.os !== "all") query.append("os", params.os);
  if (params.risk && params.risk !== "all") query.append("risk", params.risk);
  if (params.tag && params.tag !== "all") query.append("tag", params.tag);
  if (params.sort_by) query.append("sort_by", params.sort_by);
  if (params.sort_order) query.append("sort_order", params.sort_order);

  const res = await apiClient.get(`/endpoints?${query.toString()}`);
  return res.data.data;
};

export const fetchEndpointById = async (id: string): Promise<EndpointItem> => {
  const res = await apiClient.get(`/endpoints/${id}`);
  return res.data.data;
};

// --- Custom Query Hooks ---

export const useEndpointsSummary = () =>
  useQuery({
    queryKey: ["endpoints", "summary"],
    queryFn: fetchEndpointsSummary,
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useEndpoints = (params: EndpointsQueryParams = {}) =>
  useQuery({
    queryKey: ["endpoints", "list", params],
    queryFn: () => fetchEndpoints(params),
    refetchInterval: 30000,
    staleTime: 20000,
  });

export const useEndpointDetails = (id: string) =>
  useQuery({
    queryKey: ["endpoints", "detail", id],
    queryFn: () => fetchEndpointById(id),
    enabled: Boolean(id),
    staleTime: 30000,
  });
