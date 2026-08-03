export interface AlertNote {
  author: string;
  timestamp: string;
  content: string;
}

export interface AlertItem {
  id: string;
  title: string;
  severity: string;
  category: string;
  description: string;
  endpoint_id?: string | null;
  endpoint_name: string;
  status: string;
  assigned_analyst?: string | null;
  resolution_notes?: string | null;
  notes: { author: string; timestamp: string; content: string }[];
  created_at: string;
  updated_at?: string | null;
}

export interface AlertSummaryData {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  informational: number;
  active: number;
  acknowledged: number;
  resolved: number;
}

export interface PaginatedAlertsResponse {
  items: AlertItem[];
  total: number;
  page: number;
  size: number;
}

export interface AlertQueryParams {
  page?: number;
  page_size?: number;
  severity?: string;
  status?: string;
  endpoint_id?: string;
  search?: string;
}
