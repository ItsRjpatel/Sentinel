import React, { useState } from "react";
import { X, Terminal, Calendar, Clock, ShieldCheck, AlertTriangle } from "lucide-react";
import { Button } from "../../../components/ui";
import { useBulkQueueCommands } from "../api/commandsApi";

interface BulkCommandModalProps {
  isOpen: boolean;
  onClose: () => void;
  availableEndpoints: { id: string; hostname: string }[];
}

const PREDEFINED_COMMAND_TYPES = [
  "PING",
  "RUN_INVENTORY",
  "REFRESH_POLICY",
  "RESTART_SERVICE",
  "RESTART_AGENT",
  "SYNC_NOW",
  "SYSTEM_SCAN",
  "AGENT_UPDATE",
  "PATCH_INSTALL",
  "PROCESS_KILL",
];

const HELPER_TEXTS: Record<string, string> = {
  POWERSHELL: "Runs PowerShell commands on selected endpoints.",
  CMD: "Runs Windows Command Prompt commands.",
  BATCH: "Runs Batch (.bat) commands.",
};

const PLACEHOLDERS: Record<string, string> = {
  POWERSHELL: "Get-Service",
  CMD: "ipconfig /all",
  BATCH: "net start",
};

export const BulkCommandModal = React.memo(function BulkCommandModal({
  isOpen,
  onClose,
  availableEndpoints,
}: BulkCommandModalProps) {
  // Existing state
  const [selectedEndpointIds, setSelectedEndpointIds] = useState<string[]>([]);
  const [commandType, setCommandType] = useState("PING");
  const [payloadJson, setPayloadJson] = useState("{}");
  const [executionMode, setExecutionMode] = useState<"NOW" | "SCHEDULED">("NOW");
  const [scheduledDateTime, setScheduledDateTime] = useState("");
  const [timezone, setTimezone] = useState("UTC");

  // New state for Enterprise Command vs Custom Console Command
  const [commandMode, setCommandMode] = useState<"ENTERPRISE" | "CUSTOM">("ENTERPRISE");
  const [consoleType, setConsoleType] = useState<"POWERSHELL" | "CMD" | "BATCH">("POWERSHELL");
  const [customScript, setCustomScript] = useState("");
  const [captureOutput, setCaptureOutput] = useState(true);
  const [runAsSystem, setRunAsSystem] = useState(true);
  const [stopOnError, setStopOnError] = useState(true);
  const [executionTimeout, setExecutionTimeout] = useState(300);

  const bulkMutation = useBulkQueueCommands();

  if (!isOpen) return null;

  const handleToggleSelectAll = () => {
    if (selectedEndpointIds.length === availableEndpoints.length) {
      setSelectedEndpointIds([]);
    } else {
      setSelectedEndpointIds(availableEndpoints.map((ep) => ep.id));
    }
  };

  const handleToggleEndpoint = (id: string) => {
    if (selectedEndpointIds.includes(id)) {
      setSelectedEndpointIds(selectedEndpointIds.filter((item) => item !== id));
    } else {
      setSelectedEndpointIds([...selectedEndpointIds, id]);
    }
  };

  const isCustomEmpty = commandMode === "CUSTOM" && !customScript.trim();
  const isSubmitDisabled = selectedEndpointIds.length === 0 || isCustomEmpty || bulkMutation.isPending;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedEndpointIds.length === 0) {
      alert("Please select at least one endpoint.");
      return;
    }

    let finalCommandType = commandType;
    let finalPayload: Record<string, any> = {};

    if (commandMode === "ENTERPRISE") {
      try {
        finalPayload = JSON.parse(payloadJson);
      } catch {
        alert("Invalid JSON payload format.");
        return;
      }
    } else {
      if (!customScript.trim()) {
        alert("Enter a command to execute.");
        return;
      }
      finalCommandType = "CUSTOM_SCRIPT";
      finalPayload = {
        shell: consoleType.toLowerCase(),
        script: customScript,
        capture_output: captureOutput,
        run_as_system: runAsSystem,
        stop_on_error: stopOnError,
        timeout: executionTimeout,
      };
    }

    let scheduledAtIso: string | undefined = undefined;
    if (executionMode === "SCHEDULED") {
      if (!scheduledDateTime) {
        alert("Please select a date and time for scheduled execution.");
        return;
      }
      scheduledAtIso = new Date(scheduledDateTime).toISOString();
    }

    try {
      await bulkMutation.mutateAsync({
        endpoint_ids: selectedEndpointIds,
        command_type: finalCommandType,
        payload: finalPayload,
        expires_in_seconds: 3600,
        scheduled_at: scheduledAtIso,
        timezone: executionMode === "SCHEDULED" ? timezone : undefined,
      });

      alert(`Successfully queued command for ${selectedEndpointIds.length} endpoints!`);
      onClose();
    } catch (err: any) {
      alert(`Bulk execution failed: ${err.message || "Unknown error"}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-surface-container-low border border-outline-variant/60 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between bg-surface-container-high/60">
          <div className="flex items-center gap-2">
            <Terminal className="h-5 w-5 text-primary" />
            <h3 className="text-body-md font-black text-on-surface">Run Enterprise Bulk Command</h3>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-surface-container-highest text-on-surface-variant">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto scrollbar-none flex-1 text-xs">
          {/* Execution Timing Selector (Run Now vs Schedule) */}
          <div className="space-y-2">
            <label className="font-bold text-on-surface uppercase">Execution Timing</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setExecutionMode("NOW")}
                className={`p-3 rounded-xl border font-extrabold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  executionMode === "NOW"
                    ? "bg-primary text-on-primary border-primary shadow-xs"
                    : "bg-surface-container-high text-on-surface-variant border-outline-variant/40 hover:bg-surface-container-highest"
                }`}
              >
                <Clock className="h-4 w-4" /> Run Instantly (Now)
              </button>

              <button
                type="button"
                onClick={() => setExecutionMode("SCHEDULED")}
                className={`p-3 rounded-xl border font-extrabold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  executionMode === "SCHEDULED"
                    ? "bg-primary text-on-primary border-primary shadow-xs"
                    : "bg-surface-container-high text-on-surface-variant border-outline-variant/40 hover:bg-surface-container-highest"
                }`}
              >
                <Calendar className="h-4 w-4" /> Schedule for Later
              </button>
            </div>
          </div>

          {/* Date / Time Picker if Scheduled */}
          {executionMode === "SCHEDULED" && (
            <div className="p-3 bg-surface-container-high rounded-xl border border-outline-variant/40 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-on-surface">Scheduled Date & Time</label>
                  <input
                    type="datetime-local"
                    value={scheduledDateTime}
                    onChange={(e) => setScheduledDateTime(e.target.value)}
                    className="w-full p-2 bg-surface-container-low border border-outline-variant/60 rounded-lg text-on-surface font-mono font-bold focus:outline-none focus:border-primary"
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-bold text-on-surface">Timezone</label>
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full p-2 bg-surface-container-low border border-outline-variant/60 rounded-lg text-on-surface font-bold focus:outline-none focus:border-primary"
                  >
                    <option value="UTC">UTC (Universal Coordinated Time)</option>
                    <option value="EST">EST (Eastern Standard Time)</option>
                    <option value="PST">PST (Pacific Standard Time)</option>
                    <option value="IST">IST (Indian Standard Time)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* NEW SECTION: Execution Mode (Enterprise Command vs Custom Console Command) */}
          <div className="space-y-2">
            <label className="font-bold text-on-surface uppercase">Execution Mode</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setCommandMode("ENTERPRISE")}
                className={`p-3 rounded-xl border font-extrabold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  commandMode === "ENTERPRISE"
                    ? "bg-primary text-on-primary border-primary shadow-xs"
                    : "bg-surface-container-high text-on-surface-variant border-outline-variant/40 hover:bg-surface-container-highest"
                }`}
              >
                <ShieldCheck className="h-4 w-4" /> Enterprise Command
              </button>

              <button
                type="button"
                onClick={() => setCommandMode("CUSTOM")}
                className={`p-3 rounded-xl border font-extrabold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  commandMode === "CUSTOM"
                    ? "bg-primary text-on-primary border-primary shadow-xs"
                    : "bg-surface-container-high text-on-surface-variant border-outline-variant/40 hover:bg-surface-container-highest"
                }`}
              >
                <Terminal className="h-4 w-4" /> Custom Console Command
              </button>
            </div>
          </div>

          {/* MODE 1: ENTERPRISE COMMAND */}
          {commandMode === "ENTERPRISE" && (
            <>
              <div className="space-y-1">
                <label className="font-bold text-on-surface uppercase">Command Type</label>
                <select
                  value={commandType}
                  onChange={(e) => setCommandType(e.target.value)}
                  className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface font-extrabold focus:outline-none focus:border-primary"
                >
                  {PREDEFINED_COMMAND_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-on-surface uppercase">Payload JSON (Optional)</label>
                <textarea
                  rows={3}
                  value={payloadJson}
                  onChange={(e) => setPayloadJson(e.target.value)}
                  className="w-full p-2.5 bg-surface-container-highest border border-outline-variant/50 rounded-xl text-on-surface font-mono text-xs focus:outline-none focus:border-primary"
                  placeholder="{}"
                />
              </div>
            </>
          )}

          {/* MODE 2: CUSTOM CONSOLE COMMAND */}
          {commandMode === "CUSTOM" && (
            <div className="space-y-4">
              {/* Console Type */}
              <div className="space-y-1">
                <label className="font-bold text-on-surface uppercase">Console Type</label>
                <select
                  value={consoleType}
                  onChange={(e) => setConsoleType(e.target.value as any)}
                  className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface font-extrabold focus:outline-none focus:border-primary"
                >
                  <option value="POWERSHELL">PowerShell</option>
                  <option value="CMD">CMD</option>
                  <option value="BATCH">Batch</option>
                </select>
                <p className="text-[11px] text-on-surface-variant font-medium pt-0.5">
                  {HELPER_TEXTS[consoleType]}
                </p>
              </div>

              {/* Custom Command Editor */}
              <div className="space-y-1">
                <label className="font-bold text-on-surface uppercase">Custom Command / Script</label>
                <div className="relative">
                  <textarea
                    rows={8}
                    value={customScript}
                    onChange={(e) => setCustomScript(e.target.value)}
                    className="w-full p-3 bg-surface-container-highest border border-outline-variant/50 rounded-xl text-on-surface font-mono text-xs min-h-[250px] resize-y focus:outline-none focus:border-primary scrollbar-none"
                    placeholder={`# Example script for ${consoleType}\n${PLACEHOLDERS[consoleType]}`}
                  />
                </div>
                {isCustomEmpty && (
                  <p className="text-[11px] text-error font-bold">Enter a command to execute.</p>
                )}
              </div>

              {/* Execution Options */}
              <div className="p-3 bg-surface-container-high rounded-xl border border-outline-variant/40 space-y-3">
                <label className="font-bold text-on-surface uppercase block border-b border-outline-variant/30 pb-1">
                  Execution Options
                </label>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={captureOutput}
                      onChange={(e) => setCaptureOutput(e.target.checked)}
                      className="rounded border-outline-variant text-primary focus:ring-0"
                    />
                    <span className="font-bold text-on-surface">Capture Output</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={runAsSystem}
                      onChange={(e) => setRunAsSystem(e.target.checked)}
                      className="rounded border-outline-variant text-primary focus:ring-0"
                    />
                    <span className="font-bold text-on-surface">Run as SYSTEM</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={stopOnError}
                      onChange={(e) => setStopOnError(e.target.checked)}
                      className="rounded border-outline-variant text-primary focus:ring-0"
                    />
                    <span className="font-bold text-on-surface">Stop on First Error</span>
                  </label>
                </div>

                <div className="space-y-1 pt-1">
                  <label className="font-bold text-on-surface">Execution Timeout (Seconds)</label>
                  <input
                    type="number"
                    value={executionTimeout}
                    onChange={(e) => setExecutionTimeout(Number(e.target.value) || 300)}
                    className="w-full sm:w-48 p-2 bg-surface-container-low border border-outline-variant/60 rounded-lg text-on-surface font-mono font-bold focus:outline-none focus:border-primary"
                    min={10}
                    max={3600}
                  />
                </div>
              </div>

              {/* Enterprise Security Warning Card */}
              <div className="p-3 bg-warning/15 border border-warning/30 rounded-xl flex items-start gap-2.5">
                <AlertTriangle className="h-4 w-4 text-warning flex-shrink-0 mt-0.5" />
                <p className="text-[11px] font-bold text-on-surface">
                  Custom commands execute directly on managed endpoints. Only Administrators should use this feature.
                </p>
              </div>
            </div>
          )}

          {/* Endpoint Selection Table */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="font-bold text-on-surface uppercase">Select Target Endpoints ({selectedEndpointIds.length} selected)</label>
              <button
                type="button"
                onClick={handleToggleSelectAll}
                className="text-xs font-bold text-primary hover:underline"
              >
                {selectedEndpointIds.length === availableEndpoints.length ? "Deselect All" : "Select All"}
              </button>
            </div>

            <div className="max-h-44 overflow-y-auto border border-outline-variant/50 rounded-xl bg-surface-container-high divide-y divide-outline-variant/30 scrollbar-none">
              {availableEndpoints.map((ep) => {
                const isSelected = selectedEndpointIds.includes(ep.id);
                return (
                  <label key={ep.id} className="flex items-center gap-3 p-2.5 hover:bg-surface-container-highest cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleToggleEndpoint(ep.id)}
                      className="rounded border-outline-variant text-primary focus:ring-0"
                    />
                    <span className="font-bold text-on-surface">{ep.hostname}</span>
                    <span className="font-mono text-on-surface-variant text-[11px]">({ep.id.slice(0, 8)}...)</span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Submit Action */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-outline-variant/40">
            <Button type="button" variant="outline" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={isSubmitDisabled} className="font-extrabold shadow-xs">
              {bulkMutation.isPending ? "Queuing Commands..." : executionMode === "SCHEDULED" ? "Schedule Batch Command" : "Dispatch Bulk Command"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
});
