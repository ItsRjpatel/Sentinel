export interface SettingItem {
  id: string;
  key: string;
  category: string;
  value: Record<string, any>;
  description?: string | null;
}
