import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";
import type { RoleItem, PermissionItem, CreateRolePayload } from "../types/rbacTypes";

export const fetchRolesList = async (): Promise<RoleItem[]> => {
  const res = await apiClient.get("/roles");
  return res.data.data;
};

export const fetchPermissionsList = async (): Promise<PermissionItem[]> => {
  const res = await apiClient.get("/permissions");
  return res.data.data;
};

export const postCreateRole = async (payload: CreateRolePayload): Promise<RoleItem> => {
  const res = await apiClient.post("/roles", payload);
  return res.data.data;
};

export const deleteRoleApi = async (id: string) => {
  const res = await apiClient.delete(`/roles/${id}`);
  return res.data;
};

// --- Custom TanStack Query Hooks ---

export const useRolesList = () =>
  useQuery({
    queryKey: ["roles", "list"],
    queryFn: fetchRolesList,
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const usePermissionsList = () =>
  useQuery({
    queryKey: ["permissions", "list"],
    queryFn: fetchPermissionsList,
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useCreateRole = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postCreateRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
    },
  });
};

export const useDeleteRole = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteRoleApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
    },
  });
};
