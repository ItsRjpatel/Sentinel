import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";
import type { ReportSummaryData, ReportTemplate } from "../types/reportsTypes";

export const fetchReportsSummary = async (): Promise<ReportSummaryData> => {
  const res = await apiClient.get("/reports/summary");
  return res.data.data;
};

export const fetchReportTemplates = async (): Promise<ReportTemplate[]> => {
  const res = await apiClient.get("/reports/templates");
  return res.data.data;
};

export const useReportsSummary = () =>
  useQuery({
    queryKey: ["reports", "summary"],
    queryFn: fetchReportsSummary,
    staleTime: 10000,
  });

export const useReportTemplates = () =>
  useQuery({
    queryKey: ["reports", "templates"],
    queryFn: fetchReportTemplates,
    staleTime: 10000,
  });
