import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";
import type { UserItem, UsersSummaryData, PaginatedUsersResponse, UserQueryParams } from "../types/usersTypes";

export const fetchUsersSummary = async (): Promise<UsersSummaryData> => {
  const res = await apiClient.get("/users/summary");
  return res.data.data;
};

export const fetchUsersList = async (params: UserQueryParams): Promise<PaginatedUsersResponse> => {
  const query = new URLSearchParams();
  if (params.page) query.append("page", params.page.toString());
  if (params.page_size) query.append("page_size", params.page_size.toString());
  if (params.search) query.append("search", params.search);
  if (params.role && params.role !== "ALL") query.append("role", params.role);
  if (params.status && params.status !== "ALL") query.append("status", params.status);

  const res = await apiClient.get(`/users?${query.toString()}`);
  return res.data.data;
};

export const fetchUserDetails = async (id: string): Promise<UserItem> => {
  const res = await apiClient.get(`/users/${id}`);
  return res.data.data;
};

export const postCreateUser = async (payload: any): Promise<UserItem> => {
  const res = await apiClient.post("/users", payload);
  return res.data.data;
};

export const putUpdateUser = async ({ id, payload }: { id: string; payload: any }): Promise<UserItem> => {
  const res = await apiClient.put(`/users/${id}`, payload);
  return res.data.data;
};

export const patchEnableUser = async (id: string): Promise<UserItem> => {
  const res = await apiClient.patch(`/users/${id}/enable`);
  return res.data.data;
};

export const patchDisableUser = async (id: string): Promise<UserItem> => {
  const res = await apiClient.patch(`/users/${id}/disable`);
  return res.data.data;
};

export const patchUnlockUser = async (id: string): Promise<UserItem> => {
  const res = await apiClient.patch(`/users/${id}/unlock`);
  return res.data.data;
};

export const postResetPassword = async ({ id, newPassword }: { id: string; newPassword: string }): Promise<UserItem> => {
  const res = await apiClient.post(`/users/${id}/reset-password`, { new_password: newPassword });
  return res.data.data;
};

export const deleteUserApi = async (id: string) => {
  const res = await apiClient.delete(`/users/${id}`);
  return res.data.data;
};

// --- Custom TanStack Query Hooks ---

export const useUsersSummary = () =>
  useQuery({
    queryKey: ["users", "summary"],
    queryFn: fetchUsersSummary,
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useUsersList = (params: UserQueryParams) =>
  useQuery({
    queryKey: ["users", "list", params],
    queryFn: () => fetchUsersList(params),
    staleTime: 10000,
    refetchInterval: 30000,
  });

export const useUserDetails = (id: string) =>
  useQuery({
    queryKey: ["users", "detail", id],
    queryFn: () => fetchUserDetails(id),
    enabled: Boolean(id),
    staleTime: 10000,
  });

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postCreateUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: putUpdateUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};

export const useEnableUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchEnableUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};

export const useDisableUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchDisableUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};

export const useUnlockUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchUnlockUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};

export const useResetPassword = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postResetPassword,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteUserApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};
