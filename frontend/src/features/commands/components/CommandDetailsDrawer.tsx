import React from "react";
import { X, AlertTriangle, Terminal, Code, FileText } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { LogViewer } from "../../../components/ui/LogViewer";
import { useCommandDetails } from "../api/commandsApi";

interface CommandDetailsDrawerProps {
  commandId: string | null;
  onClose: () => void;
}

export const CommandDetailsDrawer = React.memo(function CommandDetailsDrawer({
  commandId,
  onClose,
}: CommandDetailsDrawerProps) {
  const { data: cmd, isLoading } = useCommandDetails(commandId || "");

  if (!commandId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex justify-end transition-opacity">
      <div className="w-full max-w-2xl bg-surface-container-low border-l border-outline-variant shadow-2xl flex flex-col h-full overflow-y-auto scrollbar-none">
        {/* Header */}
        <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between bg-surface-container-high/60 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <Terminal className="h-5 w-5 text-primary" />
            <div>
              <h3 className="text-body-md font-black text-on-surface">Command Orchestration Details</h3>
              <p className="text-[11px] font-mono text-on-surface-variant">ID: {commandId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-surface-container-highest text-on-surface-variant">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        {isLoading || !cmd ? (
          <div className="p-6">
            <LoadingSkeleton height={400} />
          </div>
        ) : (
          <div className="p-6 space-y-6">
            {/* Metadata Summary Card */}
            <Card className="p-4 bg-surface-container border-outline-variant/50 space-y-3">
              <h4 className="text-xs font-black uppercase text-on-surface border-b border-outline-variant/40 pb-2">
                Execution Metadata
              </h4>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-on-surface-variant">Command Type:</span>
                  <p className="font-mono font-extrabold text-primary">{cmd.command_type}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Status:</span>
                  <p className="font-bold text-on-surface">{cmd.status}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Target Endpoint:</span>
                  <p className="font-bold text-on-surface">{cmd.endpoint_hostname || cmd.endpoint_id}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Dispatched By:</span>
                  <p className="font-bold text-on-surface">{cmd.created_by || "system"}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Retry Count:</span>
                  <p className="font-bold text-on-surface">{cmd.retry_count}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Expiration:</span>
                  <p className="font-mono text-on-surface-variant">{cmd.expires_at ? new Date(cmd.expires_at).toLocaleString() : "Never"}</p>
                </div>
              </div>

            </Card>

            {/* Execution Timeline */}
            <div className="space-y-3">
              <h4 className="text-xs font-black uppercase text-on-surface">Execution Phase Timeline</h4>
              <div className="grid grid-cols-4 gap-2 text-center text-xs">
                <div className="p-2 bg-surface-container-high rounded border border-outline-variant/30">
                  <p className="text-[10px] text-on-surface-variant uppercase font-bold">Queued</p>
                  <p className="font-mono text-[11px] font-bold text-on-surface">{new Date(cmd.created_at).toLocaleTimeString()}</p>
                </div>
                <div className="p-2 bg-surface-container-high rounded border border-outline-variant/30">
                  <p className="text-[10px] text-on-surface-variant uppercase font-bold">Dispatched</p>
                  <p className="font-mono text-[11px] font-bold text-on-surface">{cmd.started_at ? new Date(cmd.started_at).toLocaleTimeString() : "Pending"}</p>
                </div>
                <div className="p-2 bg-surface-container-high rounded border border-outline-variant/30">
                  <p className="text-[10px] text-on-surface-variant uppercase font-bold">Completed</p>
                  <p className="font-mono text-[11px] font-bold text-on-surface">{cmd.completed_at ? new Date(cmd.completed_at).toLocaleTimeString() : "In Progress"}</p>
                </div>
                <div className="p-2 bg-surface-container-high rounded border border-outline-variant/30">
                  <p className="text-[10px] text-on-surface-variant uppercase font-bold">Final Status</p>
                  <p className="font-bold text-primary">{cmd.status}</p>
                </div>
              </div>
            </div>

            {/* Payload Inspector */}
            <div className="space-y-2">
              <h4 className="text-xs font-black uppercase text-on-surface flex items-center gap-1.5">
                <Code className="h-4 w-4 text-primary" /> Command Payload Parameters
              </h4>
              <pre className="p-3 bg-surface-container-highest rounded-xl text-xs font-mono text-on-surface overflow-x-auto border border-outline-variant/40">
                {JSON.stringify(cmd.payload || {}, null, 2)}
              </pre>
            </div>

            {/* Execution Output Log */}
            <div className="space-y-2">
              <h4 className="text-xs font-black uppercase text-on-surface flex items-center gap-1.5">
                <FileText className="h-4 w-4 text-primary" /> Execution Log Output
              </h4>
              <LogViewer
                content={cmd.result || (cmd.error_message ? { error: cmd.error_message } : "No execution output recorded.")}
                title={`${cmd.command_type} Execution Log`}
                maxHeight="400px"
              />
            </div>

            {/* Error Message Traceback */}
            {cmd.error_message && (
              <div className="p-3 bg-error/15 border border-error/30 rounded-xl space-y-1">
                <h4 className="text-xs font-bold text-error flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4" /> Error Execution Traceback
                </h4>
                <p className="text-xs font-mono text-on-surface">{cmd.error_message}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

