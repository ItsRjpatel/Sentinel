import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";
import type { AlertItem, AlertSummaryData, PaginatedAlertsResponse, AlertQueryParams } from "../types/alertsTypes";

export const fetchAlertsSummary = async (): Promise<AlertSummaryData> => {
  const res = await apiClient.get("/alerts/summary");
  return res.data.data;
};

export const fetchAlertsList = async (params: AlertQueryParams): Promise<PaginatedAlertsResponse> => {
  const query = new URLSearchParams();
  if (params.page) query.append("page", params.page.toString());
  if (params.page_size) query.append("page_size", params.page_size.toString());
  if (params.severity && params.severity !== "ALL") query.append("severity", params.severity);
  if (params.status && params.status !== "ALL") query.append("status", params.status);
  if (params.endpoint_id) query.append("endpoint_id", params.endpoint_id);
  if (params.search) query.append("search", params.search);

  const res = await apiClient.get(`/alerts?${query.toString()}`);
  return res.data.data;
};

export const fetchAlertDetails = async (id: string): Promise<AlertItem> => {
  const res = await apiClient.get(`/alerts/${id}`);
  return res.data.data;
};

export const patchAcknowledgeAlert = async (id: string): Promise<AlertItem> => {
  const res = await apiClient.patch(`/alerts/${id}/acknowledge`);
  return res.data.data;
};

export const patchResolveAlert = async ({ id, resolutionNotes }: { id: string; resolutionNotes?: string }): Promise<AlertItem> => {
  const res = await apiClient.patch(`/alerts/${id}/resolve`, { resolution_notes: resolutionNotes });
  return res.data.data;
};

export const patchReopenAlert = async (id: string): Promise<AlertItem> => {
  const res = await apiClient.patch(`/alerts/${id}/reopen`);
  return res.data.data;
};

export const patchAssignAlert = async ({ id, analyst }: { id: string; analyst: string }): Promise<AlertItem> => {
  const res = await apiClient.patch(`/alerts/${id}/assign`, { analyst });
  return res.data.data;
};

export const postAddNote = async ({ id, note }: { id: string; note: string }): Promise<AlertItem> => {
  const res = await apiClient.post(`/alerts/${id}/notes`, { note });
  return res.data.data;
};

// --- Custom TanStack Query Hooks with 30s auto-refresh ---

export const useAlertsSummary = () =>
  useQuery({
    queryKey: ["alerts", "summary"],
    queryFn: fetchAlertsSummary,
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useAlertsList = (params: AlertQueryParams) =>
  useQuery({
    queryKey: ["alerts", "list", params],
    queryFn: () => fetchAlertsList(params),
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useAlertDetails = (id: string) =>
  useQuery({
    queryKey: ["alerts", "detail", id],
    queryFn: () => fetchAlertDetails(id),
    enabled: Boolean(id),
    staleTime: 10000,
  });

export const useAcknowledgeAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchAcknowledgeAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
};

export const useResolveAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchResolveAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
};

export const useReopenAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchReopenAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
};

export const useAssignAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchAssignAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
};

export const useAddNote = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postAddNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
};
