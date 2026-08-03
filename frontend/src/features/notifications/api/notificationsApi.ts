import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  severity: "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  category: "SYSTEM" | "SECURITY" | "COMMAND" | "COMPLIANCE";
  is_read: boolean;
  user_id?: string;
  link?: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  email_address?: string;
  webhook_enabled: boolean;
  webhook_url?: string;
  slack_enabled: boolean;
  slack_webhook_url?: string;
  teams_enabled: boolean;
  teams_webhook_url?: string;
  min_severity: string;
}

export const fetchNotificationsList = async (unread_only?: boolean): Promise<NotificationItem[]> => {
  const res = await apiClient.get("/notifications", { params: { unread_only } });
  return res.data?.data || res.data || [];
};

export const markNotificationReadApi = async (id: string) => {
  const res = await apiClient.patch(`/notifications/${id}/read`);
  return res.data;
};

export const markAllNotificationsReadApi = async () => {
  const res = await apiClient.post("/notifications/read-all");
  return res.data;
};

export const fetchNotificationPreferences = async (): Promise<NotificationPreferences> => {
  const res = await apiClient.get("/notifications/preferences");
  return res.data?.data || res.data;
};

export const saveNotificationPreferences = async (payload: NotificationPreferences): Promise<NotificationPreferences> => {
  const res = await apiClient.post("/notifications/preferences", payload);
  return res.data?.data || res.data;
};

// Hooks
export const useNotificationsList = (unread_only?: boolean) =>
  useQuery({
    queryKey: ["notifications", "list", unread_only],
    queryFn: () => fetchNotificationsList(unread_only),
    staleTime: 5000,
    refetchInterval: 15000,
  });

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: markNotificationReadApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};

export const useMarkAllNotificationsRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: markAllNotificationsReadApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};

export const useNotificationPreferences = () =>
  useQuery({
    queryKey: ["notifications", "preferences"],
    queryFn: fetchNotificationPreferences,
  });

export const useSaveNotificationPreferences = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: saveNotificationPreferences,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications", "preferences"] });
    },
  });
};
