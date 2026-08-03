export interface ReportSummaryData {
  total_generated: number;
  scheduled: number;
  compliance_score: number;
  last_generated: string;
}

export interface ReportTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  format: string;
}
