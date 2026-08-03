import React from "react";
import { FileBarChart2, Download, FileSpreadsheet, RefreshCw } from "lucide-react";
import { Card, Button, LoadingSkeleton } from "../../../components/ui";
import { useReportsSummary, useReportTemplates } from "../api/reportsApi";

export const ReportsPage = React.memo(function ReportsPage() {
  const { data: summary, isLoading: isLoadingSum, refetch: refetchSum } = useReportsSummary();
  const { data: templates = [], isLoading: isLoadingTpl, refetch: refetchTpl } = useReportTemplates();

  const handleGenerate = (name: string, format: string) => {
    alert(`Generating ${name} in ${format} format... Your download will start automatically.`);
  };

  const isLoading = isLoadingSum || isLoadingTpl;

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <FileBarChart2 className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Reports Center</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Executive Audits, Compliance Framework Reports & Automated PDF/CSV Generation
            </p>
          </div>
        </div>

        <button
          onClick={() => { refetchSum(); refetchTpl(); }}
          className="p-2 bg-surface-container-high text-on-surface hover:bg-surface-container-highest border border-outline-variant/40 rounded-lg text-xs font-bold transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {isLoading ? (
        <LoadingSkeleton height={400} />
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <Card className="p-4 bg-surface-container-low border-outline-variant space-y-1">
              <span className="text-[10px] font-bold text-on-surface-variant uppercase">Reports Generated</span>
              <p className="text-2xl font-black text-primary font-mono">{summary?.total_generated || 0}</p>
            </Card>

            <Card className="p-4 bg-surface-container-low border-outline-variant space-y-1">
              <span className="text-[10px] font-bold text-on-surface-variant uppercase">Scheduled Recurrent</span>
              <p className="text-2xl font-black text-tertiary font-mono">{summary?.scheduled || 0}</p>
            </Card>

            <Card className="p-4 bg-surface-container-low border-outline-variant space-y-1">
              <span className="text-[10px] font-bold text-on-surface-variant uppercase">Platform Compliance</span>
              <p className="text-2xl font-black text-success font-mono">{summary?.compliance_score || 0}%</p>
            </Card>

            <Card className="p-4 bg-surface-container-low border-outline-variant space-y-1">
              <span className="text-[10px] font-bold text-on-surface-variant uppercase">Last Report Run</span>
              <p className="text-xs font-bold text-on-surface font-mono truncate">{summary?.last_generated || "N/A"}</p>
            </Card>
          </div>

          {/* Templates Grid */}
          <div className="space-y-3">
            <h3 className="text-body-md font-black text-on-surface uppercase">Report Templates</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.map((tpl) => (
                <Card key={tpl.id} className="p-4 bg-surface-container-low border-outline-variant space-y-3 flex flex-col justify-between">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="px-2 py-0.5 rounded bg-primary/10 text-primary font-mono text-[10px] font-bold uppercase">
                        {tpl.category}
                      </span>
                      <span className="text-xs font-mono font-bold text-on-surface-variant">{tpl.format}</span>
                    </div>
                    <h4 className="text-body-md font-black text-on-surface">{tpl.name}</h4>
                    <p className="text-xs text-on-surface-variant">{tpl.description}</p>
                  </div>

                  <div className="pt-2 border-t border-outline-variant/30 flex items-center justify-end gap-2">
                    <Button
                      onClick={() => handleGenerate(tpl.name, "PDF")}
                      variant="outline"
                      size="sm"
                      leftIcon={<Download className="h-3.5 w-3.5" />}
                    >
                      Export PDF
                    </Button>
                    <Button
                      onClick={() => handleGenerate(tpl.name, "CSV")}
                      variant="primary"
                      size="sm"
                      leftIcon={<FileSpreadsheet className="h-3.5 w-3.5" />}
                    >
                      Export CSV
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
});
