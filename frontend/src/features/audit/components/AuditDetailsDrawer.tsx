import React from "react";
import { X, FileText, Copy, Download, Code } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useAuditDetails } from "../api/auditApi";
import type { AuditLogItem } from "../types/auditTypes";

interface AuditDetailsDrawerProps {
  logId: string | null;
  onClose: () => void;
}

export const AuditDetailsDrawer = React.memo(function AuditDetailsDrawer({
  logId,
  onClose,
}: AuditDetailsDrawerProps) {
  const { data: log, isLoading } = useAuditDetails(logId || "");

  if (!logId) return null;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Audit log JSON copied to clipboard!");
  };

  const downloadJson = (item: AuditLogItem) => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(item, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `audit-log-${item.id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex justify-end transition-opacity">
      <div className="w-full max-w-2xl bg-surface-container-low border-l border-outline-variant shadow-2xl flex flex-col h-full overflow-y-auto scrollbar-none">
        {/* Header */}
        <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between bg-surface-container-high/60 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            <div>
              <h3 className="text-body-md font-black text-on-surface">Audit Event Metadata</h3>
              <p className="text-[11px] font-mono text-on-surface-variant">ID: {logId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-surface-container-highest text-on-surface-variant">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        {isLoading || !log ? (
          <div className="p-6">
            <LoadingSkeleton height={400} />
          </div>
        ) : (
          <div className="p-6 space-y-6 text-xs">
            {/* Metadata Summary Card */}
            <Card className="p-4 bg-surface-container border-outline-variant/50 space-y-3">
              <h4 className="font-black uppercase text-on-surface border-b border-outline-variant/40 pb-2">
                Event Execution Context
              </h4>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <span className="text-on-surface-variant">Action Event:</span>
                  <p className="font-mono font-extrabold text-primary">{log.action}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Module:</span>
                  <p className="font-bold text-on-surface">{log.module}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Actor:</span>
                  <p className="font-bold text-on-surface">{log.actor} ({log.actor_type})</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Severity & Status:</span>
                  <p className="font-bold text-on-surface">{log.severity} / {log.status}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Target Host:</span>
                  <p className="font-bold text-on-surface">{log.endpoint_hostname || "System Wide"}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Client IP Address:</span>
                  <p className="font-mono text-on-surface">{log.ip_address || "Internal"}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Timestamp:</span>
                  <p className="font-mono text-on-surface">{new Date(log.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Correlation ID:</span>
                  <p className="font-mono text-primary font-bold">{log.correlation_id || "N/A"}</p>
                </div>
              </div>
            </Card>

            {/* Target Resource */}
            {log.resource && (
              <div className="p-3 bg-surface-container-high rounded-xl border border-outline-variant/40 space-y-1">
                <span className="font-bold text-on-surface uppercase text-[10px]">Target Resource</span>
                <p className="font-mono font-extrabold text-on-surface">{log.resource}</p>
              </div>
            )}

            {/* JSON Payload Inspector */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-black uppercase text-on-surface flex items-center gap-1.5">
                  <Code className="h-4 w-4 text-primary" /> Full Event Details JSON
                </h4>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => copyToClipboard(JSON.stringify(log, null, 2))}
                    className="p-1 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-on-surface-variant flex items-center gap-1 text-[11px] font-bold"
                  >
                    <Copy className="h-3 w-3" /> Copy JSON
                  </button>
                  <button
                    onClick={() => downloadJson(log)}
                    className="p-1 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded text-on-surface-variant flex items-center gap-1 text-[11px] font-bold"
                  >
                    <Download className="h-3 w-3" /> Download
                  </button>
                </div>
              </div>

              <pre className="p-3 bg-surface-container-highest rounded-xl text-xs font-mono text-on-surface overflow-x-auto border border-outline-variant/40 max-h-72">
                {JSON.stringify(log.details || {}, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});
