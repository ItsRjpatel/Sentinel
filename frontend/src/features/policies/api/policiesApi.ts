import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/api";

export interface PolicyItem {
  id: string;
  name: string;
  description?: string;
  category: "Defender" | "Firewall" | "BitLocker" | "USB" | "Password" | "WindowsUpdate" | "RDP" | "Power";
  version: number;
  status: "DRAFT" | "ACTIVE" | "ARCHIVED";
  settings: Record<string, any>;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface PolicyVersionItem {
  id: string;
  policy_id: string;
  version: number;
  settings: Record<string, any>;
  change_summary?: string;
  created_by?: string;
  created_at: string;
}

export interface PolicyCreatePayload {
  name: string;
  description?: string;
  category: string;
  settings: Record<string, any>;
  status?: string;
}

export const fetchPoliciesList = async (category?: string): Promise<PolicyItem[]> => {
  const res = await apiClient.get("/policies", { params: { category } });
  return res.data?.data || res.data || [];
};

export const fetchPolicyDetails = async (id: string): Promise<PolicyItem> => {
  const res = await apiClient.get(`/policies/${id}`);
  return res.data?.data || res.data;
};

export const fetchPolicyVersions = async (id: string): Promise<PolicyVersionItem[]> => {
  const res = await apiClient.get(`/policies/${id}/versions`);
  return res.data?.data || res.data || [];
};

export const postCreatePolicy = async (payload: PolicyCreatePayload): Promise<PolicyItem> => {
  const res = await apiClient.post("/policies", payload);
  return res.data?.data || res.data;
};

export const postRollbackPolicy = async ({ id, version }: { id: string; version: number }): Promise<PolicyItem> => {
  const res = await apiClient.post(`/policies/${id}/rollback/${version}`);
  return res.data?.data || res.data;
};

export const postClonePolicy = async ({ id, newName }: { id: string; newName: string }): Promise<PolicyItem> => {
  const res = await apiClient.post(`/policies/${id}/clone`, null, { params: { new_name: newName } });
  return res.data?.data || res.data;
};

export const deletePolicyApi = async (id: string) => {
  const res = await apiClient.delete(`/policies/${id}`);
  return res.data;
};

// Hooks
export const usePoliciesList = (category?: string) =>
  useQuery({
    queryKey: ["policies", "list", category],
    queryFn: () => fetchPoliciesList(category),
    staleTime: 10000,
  });

export const usePolicyDetails = (id: string) =>
  useQuery({
    queryKey: ["policies", "detail", id],
    queryFn: () => fetchPolicyDetails(id),
    enabled: Boolean(id),
  });

export const usePolicyVersions = (id: string) =>
  useQuery({
    queryKey: ["policies", "versions", id],
    queryFn: () => fetchPolicyVersions(id),
    enabled: Boolean(id),
  });

export const useCreatePolicy = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postCreatePolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
    },
  });
};

export const useRollbackPolicy = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postRollbackPolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
    },
  });
};

export const useClonePolicy = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postClonePolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
    },
  });
};

export const useDeletePolicy = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deletePolicyApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
    },
  });
};
