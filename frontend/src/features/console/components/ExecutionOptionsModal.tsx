import React, { useState } from "react";
import { X, Sliders, Shield, Terminal, Clock, Check } from "lucide-react";
import type { ExecutionOptions, ShellType, ExecutionContext, ExecutionPolicy } from "../types/consoleTypes";

interface ExecutionOptionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  options: ExecutionOptions;
  onSaveOptions: (newOptions: ExecutionOptions) => void;
}

export const ExecutionOptionsModal: React.FC<ExecutionOptionsModalProps> = ({
  isOpen,
  onClose,
  options,
  onSaveOptions
}) => {
  const [shell, setShell] = useState<ShellType>(options.shell);
  const [runAs, setRunAs] = useState<ExecutionContext>(options.runAs);
  const [timeout, setTimeoutVal] = useState<number>(options.timeout);
  const [captureOutput, setCaptureOutput] = useState<boolean>(options.captureOutput);
  const [stopOnError, setStopOnError] = useState<boolean>(options.stopOnError);
  const [executionPolicy, setExecutionPolicy] = useState<ExecutionPolicy>(options.executionPolicy);

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveOptions({
      shell,
      runAs,
      timeout,
      captureOutput,
      stopOnError,
      executionPolicy
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#161b22] border border-[#30363d] rounded-xl shadow-2xl overflow-hidden font-sans text-xs text-[#c9d1d9] select-none">
        {/* Header */}
        <div className="p-4 border-b border-[#30363d] flex items-center justify-between bg-[#0d1117]">
          <div className="flex items-center gap-2">
            <Sliders className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-bold text-[#c9d1d9]">Execution Engine Configuration</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4">
          {/* Shell Environment */}
          <div className="space-y-1.5">
            <label className="font-bold text-[#c9d1d9] flex items-center gap-1.5">
              <Terminal className="h-3.5 w-3.5 text-primary" /> Target Execution Shell
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setShell("powershell")}
                className={`p-2.5 rounded-lg border text-left font-semibold transition-all cursor-pointer ${
                  shell === "powershell"
                    ? "bg-primary/10 border-primary text-primary"
                    : "bg-[#21262d] border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
                }`}
              >
                PowerShell 7+
              </button>
              <button
                type="button"
                onClick={() => setShell("cmd")}
                className={`p-2.5 rounded-lg border text-left font-semibold transition-all cursor-pointer ${
                  shell === "cmd"
                    ? "bg-primary/10 border-primary text-primary"
                    : "bg-[#21262d] border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
                }`}
              >
                Command Prompt (CMD)
              </button>
            </div>
          </div>

          {/* Execution Context (SYSTEM vs User) */}
          <div className="space-y-1.5">
            <label className="font-bold text-[#c9d1d9] flex items-center gap-1.5">
              <Shield className="h-3.5 w-3.5 text-amber-400" /> Privilege Execution Context
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setRunAs("SYSTEM")}
                className={`p-2.5 rounded-lg border text-left font-semibold transition-all cursor-pointer ${
                  runAs === "SYSTEM"
                    ? "bg-amber-500/10 border-amber-500 text-amber-400"
                    : "bg-[#21262d] border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
                }`}
              >
                NT AUTHORITY\SYSTEM
              </button>
              <button
                type="button"
                onClick={() => setRunAs("User")}
                className={`p-2.5 rounded-lg border text-left font-semibold transition-all cursor-pointer ${
                  runAs === "User"
                    ? "bg-amber-500/10 border-amber-500 text-amber-400"
                    : "bg-[#21262d] border-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
                }`}
              >
                Interactive Logged-In User
              </button>
            </div>
          </div>

          {/* Execution Policy (for PowerShell) */}
          {shell === "powershell" && (
            <div className="space-y-1.5">
              <label className="font-bold text-[#c9d1d9]">PowerShell Execution Policy</label>
              <select
                value={executionPolicy}
                onChange={(e) => setExecutionPolicy(e.target.value as ExecutionPolicy)}
                className="w-full p-2 bg-[#21262d] border border-[#30363d] rounded-lg text-xs text-[#c9d1d9] focus:outline-none focus:border-primary"
              >
                <option value="Bypass">Bypass (Recommended for admin automation)</option>
                <option value="RemoteSigned">RemoteSigned</option>
                <option value="Unrestricted">Unrestricted</option>
                <option value="Default">Default</option>
              </select>
            </div>
          )}

          {/* Timeout (seconds) */}
          <div className="space-y-1.5">
            <label className="font-bold text-[#c9d1d9] flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5 text-blue-400" /> Command Execution Timeout (Seconds)
            </label>
            <input
              type="number"
              min={10}
              max={3600}
              value={timeout}
              onChange={(e) => setTimeoutVal(Number(e.target.value))}
              className="w-full p-2 bg-[#21262d] border border-[#30363d] rounded-lg text-xs text-[#c9d1d9] font-mono focus:outline-none focus:border-primary"
            />
          </div>

          {/* Toggles */}
          <div className="space-y-2 pt-2 border-t border-[#30363d]">
            <label className="flex items-center justify-between cursor-pointer p-2 hover:bg-[#21262d] rounded">
              <span className="font-medium">Capture Standard Output (stdout & stderr)</span>
              <input
                type="checkbox"
                checked={captureOutput}
                onChange={(e) => setCaptureOutput(e.target.checked)}
                className="accent-primary h-4 w-4"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer p-2 hover:bg-[#21262d] rounded">
              <span className="font-medium">Stop Script Execution on Command Error</span>
              <input
                type="checkbox"
                checked={stopOnError}
                onChange={(e) => setStopOnError(e.target.checked)}
                className="accent-primary h-4 w-4"
              />
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#30363d] bg-[#0d1117] flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-3 py-1.5 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] rounded font-semibold transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-1.5 bg-primary text-on-primary hover:opacity-90 rounded font-bold transition-all cursor-pointer flex items-center gap-1 shadow-xs"
          >
            <Check className="h-3.5 w-3.5" />
            <span>Save Configuration</span>
          </button>
        </div>
      </div>
    </div>
  );
};
