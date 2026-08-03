export interface RoleItem {
  id: string;
  name: string;
  description?: string | null;
  permissions?: PermissionItem[];
}

export interface PermissionItem {
  id: string;
  name: string;
  description?: string | null;
}

export interface CreateRolePayload {
  name: string;
  description?: string;
  permissions?: string[];
}
