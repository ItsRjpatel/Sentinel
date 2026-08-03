import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";
import type { AuditLogItem, AuditSummaryData, PaginatedAuditResponse, AuditQueryParams } from "../types/auditTypes";

export const fetchAuditSummary = async (): Promise<AuditSummaryData> => {
  const res = await apiClient.get("/audit/summary");
  return res.data.data;
};

export const fetchAuditLogsList = async (params: AuditQueryParams): Promise<PaginatedAuditResponse> => {
  const query = new URLSearchParams();
  if (params.page) query.append("page", params.page.toString());
  if (params.page_size) query.append("page_size", params.page_size.toString());
  if (params.search) query.append("search", params.search);
  if (params.severity && params.severity !== "ALL") query.append("severity", params.severity);
  if (params.module && params.module !== "ALL") query.append("module", params.module);
  if (params.actor && params.actor !== "ALL") query.append("actor", params.actor);
  if (params.endpoint_id) query.append("endpoint_id", params.endpoint_id);
  if (params.status && params.status !== "ALL") query.append("status", params.status);
  if (params.start_date) query.append("start_date", params.start_date);
  if (params.end_date) query.append("end_date", params.end_date);
  if (params.sort_by) query.append("sort_by", params.sort_by);
  if (params.sort_order) query.append("sort_order", params.sort_order);

  const res = await apiClient.get(`/audit?${query.toString()}`);
  return res.data.data;
};

export const fetchAuditDetails = async (id: string): Promise<AuditLogItem> => {
  const res = await apiClient.get(`/audit/${id}`);
  return res.data.data;
};

// --- Custom TanStack Query Hooks with 30s auto-refresh ---

export const useAuditSummary = () =>
  useQuery({
    queryKey: ["audit", "summary"],
    queryFn: fetchAuditSummary,
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useAuditLogs = (params: AuditQueryParams) =>
  useQuery({
    queryKey: ["audit", "list", params],
    queryFn: () => fetchAuditLogsList(params),
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useAuditDetails = (id: string) =>
  useQuery({
    queryKey: ["audit", "detail", id],
    queryFn: () => fetchAuditDetails(id),
    enabled: Boolean(id),
    staleTime: 10000,
  });
