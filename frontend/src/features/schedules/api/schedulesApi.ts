import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";

export interface ScheduleItem {
  id: string;
  name: string;
  job_type: "INVENTORY" | "COMMAND" | "POLICY_REFRESH" | "HEARTBEAT_CHECK" | "CLEANUP";
  schedule_type: "RECURRING" | "ONE_TIME";
  cron_expression?: string;
  next_run_at?: string;
  last_run_at?: string;
  status: "ACTIVE" | "PAUSED" | "COMPLETED" | "EXPIRED";
  payload?: Record<string, any>;
  retry_count: number;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ScheduleCreatePayload {
  name: string;
  job_type: string;
  schedule_type?: string;
  cron_expression?: string;
  status?: string;
  payload?: Record<string, any>;
}

export const fetchSchedulesList = async (status?: string): Promise<ScheduleItem[]> => {
  const res = await apiClient.get("/schedules", { params: { status } });
  return res.data?.data || res.data || [];
};

export const postCreateSchedule = async (payload: ScheduleCreatePayload): Promise<ScheduleItem> => {
  const res = await apiClient.post("/schedules", payload);
  return res.data?.data || res.data;
};

export const postRunScheduleNow = async (id: string) => {
  const res = await apiClient.post(`/schedules/${id}/run-now`);
  return res.data?.data || res.data;
};

export const deleteScheduleApi = async (id: string) => {
  const res = await apiClient.delete(`/schedules/${id}`);
  return res.data;
};

// Hooks
export const useSchedulesList = (status?: string) =>
  useQuery({
    queryKey: ["schedules", "list", status],
    queryFn: () => fetchSchedulesList(status),
    staleTime: 10000,
  });

export const useCreateSchedule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postCreateSchedule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
    },
  });
};

export const useRunScheduleNow = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postRunScheduleNow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
    },
  });
};

export const useDeleteSchedule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteScheduleApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
    },
  });
};
