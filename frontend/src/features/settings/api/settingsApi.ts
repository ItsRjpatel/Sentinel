import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";
import type { SettingItem } from "../types/settingsTypes";

export const fetchSettingsList = async (): Promise<SettingItem[]> => {
  const res = await apiClient.get("/settings");
  return res.data.data;
};

export const putUpdateSetting = async ({ key, value }: { key: string; value: Record<string, any> }): Promise<SettingItem> => {
  const res = await apiClient.put(`/settings/${key}`, { value });
  return res.data.data;
};

export const useSettingsList = () =>
  useQuery({
    queryKey: ["settings", "list"],
    queryFn: fetchSettingsList,
    staleTime: 10000,
  });

export const useUpdateSetting = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: putUpdateSetting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
  });
};
