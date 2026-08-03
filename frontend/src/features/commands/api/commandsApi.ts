import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";

export interface CommandSummaryData {
  pending: number;
  running: number;
  success: number;
  failed: number;
  timed_out: number;
  cancelled: number;
  scheduled: number;
  total: number;
}

export interface CommandItem {
  id: string;
  endpoint_id: string;
  endpoint_hostname?: string;
  endpoint_type?: string;
  command_type: string;
  status: string;
  payload?: Record<string, any>;
  created_by?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: Record<string, any>;
  error_message?: string;
  retry_count: number;
  expires_at?: string;
  scheduled_at?: string;
  recurring?: string;
  timezone?: string;
}

export interface PaginatedCommandsResponse {
  items: CommandItem[];
  total: number;
  page: number;
  size: number;
}

export interface CommandQueryParams {
  status?: string;
  command_type?: string;
  endpoint_id?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface BulkCommandPayload {
  endpoint_ids: string[];
  command_type: string;
  payload?: Record<string, any>;
  expires_in_seconds?: number;
  scheduled_at?: string;
  timezone?: string;
}

export const fetchCommandsSummary = async (): Promise<CommandSummaryData> => {
  const res = await apiClient.get("/commands/summary");
  return res.data.data;
};

export const fetchCommandsList = async (params: CommandQueryParams): Promise<PaginatedCommandsResponse> => {
  const query = new URLSearchParams();
  if (params.status && params.status !== "ALL") query.append("status", params.status);
  if (params.command_type && params.command_type !== "ALL") query.append("command_type", params.command_type);
  if (params.endpoint_id) query.append("endpoint_id", params.endpoint_id);
  if (params.search) query.append("search", params.search);
  if (params.page) query.append("page", params.page.toString());
  if (params.page_size) query.append("page_size", params.page_size.toString());

  const res = await apiClient.get(`/commands?${query.toString()}`);
  const payload = res.data?.data || res.data || {};
  const items = Array.isArray(payload) ? payload : Array.isArray(payload.items) ? payload.items : [];
  return {
    items,
    total: payload.total ?? items.length,
    page: payload.page ?? params.page ?? 1,
    size: payload.size ?? payload.page_size ?? params.page_size ?? 20,
  };
};

export const fetchCommandDetails = async (id: string): Promise<CommandItem> => {
  const res = await apiClient.get(`/commands/${id}`);
  return res.data?.data || res.data;
};

export interface SingleCommandPayload {
  endpoint_id: string;
  command_type: string;
  payload?: Record<string, any>;
  expires_in_seconds?: number;
  scheduled_at?: string;
  recurring?: string;
  timezone?: string;
  created_by?: string;
}

export const postQueueSingleCommand = async (payload: SingleCommandPayload) => {
  const res = await apiClient.post("/commands", payload);
  return res.data?.data || res.data;
};

export const postQueueBulkCommands = async (payload: BulkCommandPayload) => {
  const res = await apiClient.post("/commands/bulk", payload);
  return res.data?.data || res.data;
};

export const postRetryCommand = async (id: string): Promise<CommandItem> => {
  const res = await apiClient.post(`/commands/${id}/retry`);
  return res.data?.data || res.data;
};

export const patchCancelCommand = async (id: string): Promise<CommandItem> => {
  const res = await apiClient.patch(`/commands/${id}/cancel`);
  return res.data?.data || res.data;
};

// --- Custom TanStack Query Hooks ---

export const useCommandsSummary = () =>
  useQuery({
    queryKey: ["commands", "summary"],
    queryFn: fetchCommandsSummary,
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useCommandsList = (params: CommandQueryParams) =>
  useQuery({
    queryKey: ["commands", "list", params],
    queryFn: () => fetchCommandsList(params),
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useCommandDetails = (id: string) =>
  useQuery({
    queryKey: ["commands", "detail", id],
    queryFn: () => fetchCommandDetails(id),
    enabled: Boolean(id),
    staleTime: 10000,
  });

export const useBulkQueueCommands = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postQueueBulkCommands,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commands"] });
    },
  });
};

export const useRetryCommand = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postRetryCommand,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commands"] });
    },
  });
};

export const useCancelCommand = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchCancelCommand,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commands"] });
    },
  });
};
