export interface AuditLogItem {
  id: string;
  timestamp: string;
  actor: string;
  actor_type: string;
  endpoint_id?: string | null;
  endpoint_hostname?: string | null;
  action: string;
  module: string;
  resource?: string | null;
  severity: string;
  ip_address?: string | null;
  user_agent?: string | null;
  status: string;
  details?: Record<string, any> | null;
  correlation_id?: string | null;
}

export interface AuditSummaryData {
  total: number;
  critical: number;
  warning: number;
  information: number;
  success: number;
  failed: number;
  today: number;
}

export interface PaginatedAuditResponse {
  items: AuditLogItem[];
  total: number;
  page: number;
  size: number;
}

export interface AuditQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  severity?: string;
  module?: string;
  actor?: string;
  endpoint_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  sort_by?: string;
  sort_order?: string;
}
