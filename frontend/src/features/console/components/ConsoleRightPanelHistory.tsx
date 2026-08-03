import React, { useState } from "react";
import {
  History,
  CheckCircle2,
  XCircle,
  Loader2,
  User,
  ExternalLink
} from "lucide-react";
import type { ConsoleCommandRecord } from "../types/consoleTypes";
import { cn } from "../../../utils/cn";

interface ConsoleRightPanelHistoryProps {
  history: ConsoleCommandRecord[];
  onReopenCommand: (cmd: ConsoleCommandRecord) => void;
}

export const ConsoleRightPanelHistory: React.FC<ConsoleRightPanelHistoryProps> = ({
  history,
  onReopenCommand
}) => {
  const [selectedCmd, setSelectedCmd] = useState<ConsoleCommandRecord | null>(null);

  return (
    <div className="w-72 bg-[#161b22] border-l border-[#30363d] flex flex-col h-full select-none font-sans text-xs">
      {/* Panel Header */}
      <div className="p-3 border-b border-[#30363d] flex items-center justify-between bg-[#0d1117]/60">
        <div className="flex items-center gap-2">
          <History className="h-4 w-4 text-primary" />
          <span className="font-bold text-[#c9d1d9] text-xs uppercase tracking-wider">
            Execution Log
          </span>
        </div>
        <span className="px-1.5 py-0.5 bg-[#21262d] text-[#8b949e] font-mono text-[10px] rounded border border-[#30363d]">
          {history.length} {history.length === 1 ? "entry" : "entries"}
        </span>
      </div>

      {/* History Items List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2 scrollbar-thin scrollbar-thumb-[#30363d] scrollbar-track-[#161b22]">
        {history.length === 0 ? (
          <div className="p-6 text-center text-[#8b949e] text-xs italic font-mono">
            No command executions recorded for this session yet.
          </div>
        ) : (
          history.map((record) => {
            const isSuccess = record.status === "SUCCESS";
            const isFailed = record.status === "FAILED";
            const isPending = record.status === "PENDING" || record.status === "SENT" || record.status === "RUNNING";

            return (
              <div
                key={record.id}
                onDoubleClick={() => onReopenCommand(record)}
                onClick={() => setSelectedCmd(record)}
                className={cn(
                  "p-2.5 bg-[#21262d]/50 hover:bg-[#21262d] rounded-lg border border-[#30363d] transition-all cursor-pointer space-y-1.5 group",
                  selectedCmd?.id === record.id && "border-primary bg-[#21262d]"
                )}
              >
                {/* Header Row */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    {isSuccess && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
                    {isFailed && <XCircle className="h-3.5 w-3.5 text-red-400" />}
                    {isPending && <Loader2 className="h-3.5 w-3.5 text-amber-400 animate-spin" />}

                    <span className="font-bold text-[#c9d1d9] text-xs">
                      {record.commandType}
                    </span>
                  </div>

                  <span className="text-[10px] text-[#8b949e] font-mono">
                    {record.requestedAt}
                  </span>
                </div>

                {/* Command Script Preview */}
                <p className="font-mono text-[11px] text-[#8b949e] group-hover:text-[#c9d1d9] truncate">
                  {record.commandText}
                </p>

                {/* Metadata Footer */}
                <div className="flex items-center justify-between text-[10px] text-[#8b949e] font-sans pt-1 border-t border-[#30363d]/50">
                  <div className="flex items-center gap-1">
                    <User className="h-3 w-3 text-[#484f58]" />
                    <span>{record.user || "admin"}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="font-mono">
                      {record.durationMs !== undefined ? `${record.durationMs}ms` : "In progress"}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onReopenCommand(record);
                      }}
                      title="Inspect full output"
                      className="p-0.5 hover:text-primary transition-colors"
                    >
                      <ExternalLink className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Selected Command Preview Drawer / Modal Trigger */}
      {selectedCmd && (
        <div className="p-3 border-t border-[#30363d] bg-[#0d1117] space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-xs text-[#c9d1d9] truncate">
              {selectedCmd.commandType} Output
            </span>
            <button
              onClick={() => onReopenCommand(selectedCmd)}
              className="text-[11px] text-primary hover:underline font-medium"
            >
              Open Full Log
            </button>
          </div>
          <p className="text-[11px] font-mono text-[#8b949e] truncate">
            {selectedCmd.commandText}
          </p>
        </div>
      )}
    </div>
  );
};
