export interface UserItem {
  id: string;
  username: string;
  email: string;
  first_name?: string | null;
  last_name?: string | null;
  phone?: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  last_login?: string | null;
  created_at: string;
  roles: string[];
}

export interface UsersSummaryData {
  total: number;
  online: number;
  disabled: number;
  locked: number;
  administrators: number;
  analysts: number;
  agents: number;
  guests: number;
}

export interface PaginatedUsersResponse {
  items: UserItem[];
  total: number;
  page: number;
  size: number;
}

export interface UserQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  role?: string;
  status?: string;
}
