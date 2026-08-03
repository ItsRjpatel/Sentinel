import React, { useState, useRef, useEffect } from "react";
import {
  Terminal as TerminalIcon,
  Play,
  Copy,
  Check,
  Download,
  Trash2,
  Maximize2,
  Minimize2,
  Loader2
} from "lucide-react";
import type { TerminalLine, ShellType } from "../types/consoleTypes";
import { cn } from "../../../utils/cn";

interface InteractiveTerminalProps {
  buffer: TerminalLine[];
  shell: ShellType;
  isRunning: boolean;
  onExecuteCommand: (cmdText: string) => void;
  onClearBuffer: () => void;
  hostname?: string;
}

export const InteractiveTerminal: React.FC<InteractiveTerminalProps> = ({
  buffer,
  shell,
  isRunning,
  onExecuteCommand,
  onClearBuffer,
  hostname = "DESKTOP-JK4JV9R"
}) => {
  const [inputVal, setInputVal] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [historyIdx, setHistoryIdx] = useState<number>(-1);
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const terminalEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto scroll to bottom when buffer updates
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [buffer, isRunning]);

  // Prompt Prefix
  const promptPrefix = shell === "powershell" ? "PS C:\\>" : "C:\\>";

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const trimmed = inputVal.trim();
      if (!trimmed) return;

      // Handle local clear command
      if (trimmed.toLowerCase() === "clear" || trimmed.toLowerCase() === "cls") {
        onClearBuffer();
        setInputVal("");
        setHistoryIdx(-1);
        return;
      }

      // Append to history
      setHistory((prev) => [...prev, trimmed]);
      setHistoryIdx(-1);

      // Execute via parent
      onExecuteCommand(trimmed);
      setInputVal("");
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (history.length === 0) return;
      const nextIdx = historyIdx === -1 ? history.length - 1 : Math.max(0, historyIdx - 1);
      setHistoryIdx(nextIdx);
      setInputVal(history[nextIdx] || "");
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIdx === -1) return;
      const nextIdx = historyIdx + 1;
      if (nextIdx >= history.length) {
        setHistoryIdx(-1);
        setInputVal("");
      } else {
        setHistoryIdx(nextIdx);
        setInputVal(history[nextIdx] || "");
      }
    }
  };

  const handleCopyAll = () => {
    const fullText = buffer.map((b) => b.text).join("\n");
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadLog = () => {
    const text = buffer.map((b) => `[${b.timestamp}] ${b.text}`).join("\n");
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `terminal_session_${hostname}_${Date.now()}.log`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className={cn(
        "flex-1 bg-[#0d1117] flex flex-col font-mono text-xs overflow-hidden select-text transition-all",
        isFullscreen ? "fixed inset-0 z-50 rounded-none" : "rounded-none"
      )}
    >
      {/* Terminal Header Toolbar */}
      <div className="bg-[#161b22] px-4 py-2 border-b border-[#30363d] flex items-center justify-between select-none">
        <div className="flex items-center gap-2">
          <TerminalIcon className="h-4 w-4 text-emerald-400" />
          <span className="font-sans font-bold text-xs text-[#c9d1d9]">
            {hostname} – Live Console ({shell.toUpperCase()})
          </span>
          {isRunning && (
            <div className="flex items-center gap-1.5 px-2 py-0.5 bg-amber-500/10 border border-amber-500/30 rounded text-[10px] text-amber-400 font-sans font-semibold">
              <Loader2 className="h-3 w-3 animate-spin" />
              <span>Executing...</span>
            </div>
          )}
        </div>

        {/* Toolbar Buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleCopyAll}
            title="Copy Terminal Log"
            className="flex items-center gap-1 px-2 py-1 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] rounded text-[11px] font-sans font-medium transition-colors cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>

          <button
            onClick={handleDownloadLog}
            title="Download Log (.log)"
            className="flex items-center gap-1 px-2 py-1 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] rounded text-[11px] font-sans font-medium transition-colors cursor-pointer"
          >
            <Download className="h-3.5 w-3.5 text-blue-400" />
            <span>Export</span>
          </button>

          <button
            onClick={onClearBuffer}
            title="Clear Terminal Buffer"
            className="p-1.5 bg-[#21262d] hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] rounded transition-colors cursor-pointer"
          >
            <Trash2 className="h-3.5 w-3.5 text-amber-400" />
          </button>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            className="p-1.5 bg-[#21262d] hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] rounded transition-colors cursor-pointer"
          >
            {isFullscreen ? (
              <Minimize2 className="h-3.5 w-3.5 text-amber-400" />
            ) : (
              <Maximize2 className="h-3.5 w-3.5 text-[#c9d1d9]" />
            )}
          </button>
        </div>
      </div>

      {/* Terminal Output Log Canvas */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-1.5 scrollbar-thin scrollbar-thumb-[#30363d] scrollbar-track-[#0d1117]"
        onClick={() => inputRef.current?.focus()}
      >
        {buffer.length === 0 ? (
          <div className="text-[#8b949e] py-8 text-center font-sans">
            <p className="font-bold text-xs text-[#c9d1d9] mb-1">
              Interactive Remote Console Ready
            </p>
            <p className="text-[11px]">
              Type a command below or select a script template from the left sidebar to execute.
            </p>
          </div>
        ) : (
          buffer.map((line) => {
            const isInput = line.type === "input";
            const isError = line.type === "error";
            const isSystem = line.type === "system";
            const isInfo = line.type === "info";

            return (
              <div key={line.id} className="flex items-start gap-2 leading-relaxed">
                {/* Line Timestamp */}
                <span className="text-[10px] text-[#484f58] font-mono select-none pt-0.5 flex-shrink-0">
                  [{line.timestamp}]
                </span>

                {/* Line Content */}
                <div
                  className={cn(
                    "flex-1 font-mono text-xs whitespace-pre-wrap break-words overflow-wrap-anywhere",
                    isInput && "text-[#58a6ff] font-bold",
                    isError && "text-red-400 font-semibold",
                    isSystem && "text-amber-400 italic",
                    isInfo && "text-blue-300",
                    !isInput && !isError && !isSystem && !isInfo && "text-[#c9d1d9]"
                  )}
                >
                  {isInput && <span className="text-emerald-400 mr-1.5">{promptPrefix}</span>}
                  {line.text}
                </div>
              </div>
            );
          })
        )}

        <div ref={terminalEndRef} />
      </div>

      {/* Interactive Command Input Line */}
      <div className="p-3 bg-[#161b22] border-t border-[#30363d] flex items-center gap-2">
        <span className="font-mono font-bold text-emerald-400 text-xs select-none">
          {promptPrefix}
        </span>

        <input
          ref={inputRef}
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isRunning}
          placeholder={
            isRunning
              ? "Command executing on remote Windows endpoint..."
              : "Type Windows command or script here... (Up/Down arrow for history, Enter to run)"
          }
          className="flex-1 bg-transparent font-mono text-xs text-[#c9d1d9] placeholder-[#484f58] focus:outline-none disabled:opacity-50"
          autoFocus
        />

        <button
          onClick={() => {
            const trimmed = inputVal.trim();
            if (trimmed) {
              setHistory((prev) => [...prev, trimmed]);
              onExecuteCommand(trimmed);
              setInputVal("");
            }
          }}
          disabled={isRunning || !inputVal.trim()}
          title="Run Command"
          className="px-3 py-1 bg-primary text-on-primary hover:opacity-90 disabled:opacity-40 rounded text-xs font-bold font-sans transition-all cursor-pointer flex items-center gap-1 shadow-xs"
        >
          {isRunning ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Play className="h-3.5 w-3.5 fill-current" />
          )}
          <span>Run</span>
        </button>
      </div>
    </div>
  );
};
