import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";

export interface GroupStats {
  endpoint_count: number;
  online_count: number;
  offline_count: number;
  compliance_percent: number;
  health_percent: number;
}

export interface GroupItem {
  id: string;
  name: string;
  description?: string;
  group_type: "STATIC" | "DYNAMIC";
  criteria?: Record<string, any>;
  site?: string;
  location?: string;
  department?: string;
  tags?: string[];
  created_by?: string;
  created_at: string;
  updated_at: string;
  stats?: GroupStats;
}

export interface GroupCreatePayload {
  name: string;
  description?: string;
  group_type?: "STATIC" | "DYNAMIC";
  criteria?: Record<string, any>;
  site?: string;
  location?: string;
  department?: string;
  tags?: string[];
  endpoint_ids?: string[];
}

export const fetchGroupsList = async (search?: string): Promise<GroupItem[]> => {
  const res = await apiClient.get("/groups", { params: { search } });
  return res.data?.data || res.data || [];
};

export const fetchGroupDetails = async (id: string): Promise<GroupItem> => {
  const res = await apiClient.get(`/groups/${id}`);
  return res.data?.data || res.data;
};

export const fetchGroupEndpoints = async (id: string) => {
  const res = await apiClient.get(`/groups/${id}/endpoints`);
  return res.data?.data || res.data || [];
};

export const postCreateGroup = async (payload: GroupCreatePayload): Promise<GroupItem> => {
  const res = await apiClient.post("/groups", payload);
  return res.data?.data || res.data;
};

export const deleteGroupApi = async (id: string) => {
  const res = await apiClient.delete(`/groups/${id}`);
  return res.data;
};

export const assignEndpointsToGroupApi = async ({ id, endpoint_ids }: { id: string; endpoint_ids: string[] }) => {
  const res = await apiClient.post(`/groups/${id}/assign`, endpoint_ids);
  return res.data;
};

// Hooks
export const useGroupsList = (search?: string) =>
  useQuery({
    queryKey: ["groups", "list", search],
    queryFn: () => fetchGroupsList(search),
    staleTime: 10000,
  });

export const useGroupDetails = (id: string) =>
  useQuery({
    queryKey: ["groups", "detail", id],
    queryFn: () => fetchGroupDetails(id),
    enabled: Boolean(id),
  });

export const useGroupEndpoints = (id: string) =>
  useQuery({
    queryKey: ["groups", "endpoints", id],
    queryFn: () => fetchGroupEndpoints(id),
    enabled: Boolean(id),
  });

export const useCreateGroup = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postCreateGroup,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups"] });
    },
  });
};

export const useDeleteGroup = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteGroupApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups"] });
    },
  });
};
