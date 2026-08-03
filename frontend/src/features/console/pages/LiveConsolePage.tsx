import React, { useState, useEffect } from "react";
import { ConsoleTopBar } from "../components/ConsoleTopBar";
import { ConsoleSidebarTemplates } from "../components/ConsoleSidebarTemplates";
import { InteractiveTerminal } from "../components/InteractiveTerminal";
import { ConsoleRightPanelHistory } from "../components/ConsoleRightPanelHistory";
import { ExecutionOptionsModal } from "../components/ExecutionOptionsModal";
import { LogViewer } from "../../../components/ui/LogViewer";
import { DEFAULT_COMMAND_TEMPLATES } from "../data/commandTemplates";
import type {
  EndpointSession,
  ExecutionOptions,
  TerminalLine,
  ConsoleCommandRecord
} from "../types/consoleTypes";
import { useEndpoints } from "../../endpoints/api/endpointsApi";
import { postQueueSingleCommand, fetchCommandDetails } from "../../commands/api/commandsApi";
import { useAuth } from "../../../contexts/AuthContext";
import { X, Monitor } from "lucide-react";

export const LiveConsolePage: React.FC = () => {
  const { data: endpointsResponse, refetch: refetchEndpoints } = useEndpoints();
  const { user } = useAuth();

  const endpoints = React.useMemo(() => {
    const rawData: any = endpointsResponse;
    if (Array.isArray(rawData)) return rawData;
    if (Array.isArray(rawData?.items)) return rawData.items;
    return [];
  }, [endpointsResponse]);

  // Multi-session state map keyed by endpointId
  const [sessions, setSessions] = useState<Record<string, EndpointSession>>({});
  const [activeEndpointId, setActiveEndpointId] = useState<string | null>(null);

  // Modals state
  const [isOptionsOpen, setIsOptionsOpen] = useState(false);
  const [inspectedCommand, setInspectedCommand] = useState<ConsoleCommandRecord | null>(null);

  // Default execution options
  const defaultOptions: ExecutionOptions = {
    shell: "powershell",
    runAs: "SYSTEM",
    timeout: 300,
    captureOutput: true,
    stopOnError: true,
    executionPolicy: "Bypass"
  };

  // Auto-initialize first online endpoint on load
  useEffect(() => {
    if (endpoints.length > 0 && !activeEndpointId) {
      const firstEp = endpoints[0];
      createOrActivateSession(firstEp);
    }
  }, [endpoints]);

  const createOrActivateSession = (ep: any) => {
    const epId = ep.id;
    if (!sessions[epId]) {
      const isOnline = ep.status === "healthy" || ep.status === "online";
      const newSession: EndpointSession = {
        endpointId: epId,
        hostname: ep.hostname || epId,
        osVersion: ep.os_version || "Windows Workstation",
        ipAddress: ep.ip_address || "127.0.0.1",
        status: isOnline ? "online" : "offline",
        lastSeen: ep.last_seen,
        options: { ...defaultOptions },
        terminalBuffer: [
          {
            id: `sys-init-${Date.now()}`,
            timestamp: new Date().toLocaleTimeString(),
            type: "system",
            text: `Connected to endpoint [${ep.hostname || epId}] (${ep.os_version || "Windows"}). Ready for remote command execution.`
          }
        ],
        history: []
      };
      setSessions((prev) => ({ ...prev, [epId]: newSession }));
    }
    setActiveEndpointId(epId);
  };

  const activeSession = activeEndpointId ? sessions[activeEndpointId] || null : null;

  // Handle switching endpoint from dropdown
  const handleSelectEndpoint = (epId: string) => {
    const targetEp = endpoints.find((e: any) => e.id === epId);
    if (targetEp) {
      createOrActivateSession(targetEp);
    } else {
      setActiveEndpointId(epId);
    }
  };

  const handleCloseSessionTab = (epId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSessions((prev) => {
      const copy = { ...prev };
      delete copy[epId];
      return copy;
    });
    if (activeEndpointId === epId) {
      const remainingIds = Object.keys(sessions).filter((id) => id !== epId);
      setActiveEndpointId(remainingIds.length > 0 ? remainingIds[0] : null);
    }
  };

  // Execute Command Handler
  const handleExecuteCommand = async (scriptText: string, customShell?: "powershell" | "cmd") => {
    if (!activeSession || !activeEndpointId) return;

    const shellToUse = customShell || activeSession.options.shell;
    const timestamp = new Date().toLocaleTimeString();

    // 1. Append Input to Terminal Buffer
    const inputLine: TerminalLine = {
      id: `in-${Date.now()}`,
      timestamp,
      type: "input",
      text: scriptText
    };

    setSessions((prev) => {
      const current = prev[activeEndpointId];
      if (!current) return prev;
      return {
        ...prev,
        [activeEndpointId]: {
          ...current,
          terminalBuffer: [...current.terminalBuffer, inputLine]
        }
      };
    });

    // 2. Queue backend command API
    try {
      const payloadData = {
        shell: shellToUse,
        script: scriptText,
        run_as: activeSession.options.runAs,
        timeout: activeSession.options.timeout,
        capture_output: activeSession.options.captureOutput,
        stop_on_error: activeSession.options.stopOnError,
        execution_policy: activeSession.options.executionPolicy
      };

      const res = await postQueueSingleCommand({
        endpoint_id: activeEndpointId,
        command_type: "CUSTOM_SCRIPT",
        payload: payloadData,
        created_by: user?.username || "Admin_Console"
      });

      const cmdId = res.command_id || res.id;

      const newRecord: ConsoleCommandRecord = {
        id: cmdId,
        commandType: "CUSTOM_SCRIPT",
        commandText: scriptText,
        shell: shellToUse,
        status: "RUNNING",
        requestedAt: timestamp,
        user: user?.username || "Admin"
      };

      // Append command record to history
      setSessions((prev) => {
        const current = prev[activeEndpointId];
        if (!current) return prev;
        return {
          ...prev,
          [activeEndpointId]: {
            ...current,
            history: [newRecord, ...current.history],
            activeCommandId: cmdId
          }
        };
      });

      // 3. Poll for result
      pollCommandCompletion(activeEndpointId, cmdId);
    } catch (err: any) {
      const errLine: TerminalLine = {
        id: `err-${Date.now()}`,
        timestamp: new Date().toLocaleTimeString(),
        type: "error",
        text: `Failed to queue command: ${err.message || "Network Error"}`
      };

      setSessions((prev) => {
        const current = prev[activeEndpointId];
        if (!current) return prev;
        return {
          ...prev,
          [activeEndpointId]: {
            ...current,
            terminalBuffer: [...current.terminalBuffer, errLine]
          }
        };
      });
    }
  };

  // Poll Command Completion (Incremental WebSocket / Polling)
  const pollCommandCompletion = (epId: string, cmdId: string) => {
    let attempts = 0;
    const maxAttempts = 30;

    const interval = setInterval(async () => {
      attempts++;
      try {
        const details = await fetchCommandDetails(cmdId);
        const status = details.status;

        if (status === "SUCCESS" || status === "FAILED" || status === "TIMEOUT" || attempts >= maxAttempts) {
          clearInterval(interval);

          const resultObj = details.result || {};
          const stdoutText =
            typeof resultObj === "object"
              ? resultObj.stdout || resultObj.message || JSON.stringify(resultObj, null, 2)
              : String(resultObj);
          const stderrText = details.error_message || resultObj.stderr || "";

          // Create Terminal Output Lines
          const outputLines: TerminalLine[] = [];
          if (stdoutText) {
            outputLines.push({
              id: `out-${Date.now()}-1`,
              timestamp: new Date().toLocaleTimeString(),
              type: status === "SUCCESS" ? "output" : "error",
              text: stdoutText,
              commandId: cmdId
            });
          }

          if (stderrText && status !== "SUCCESS") {
            outputLines.push({
              id: `out-${Date.now()}-2`,
              timestamp: new Date().toLocaleTimeString(),
              type: "error",
              text: `STDERR: ${stderrText}`,
              commandId: cmdId
            });
          }

          // Update Session Buffer and History Record
          setSessions((prev) => {
            const current = prev[epId];
            if (!current) return prev;

            const updatedHistory = current.history.map((rec) => {
              if (rec.id === cmdId) {
                return {
                  ...rec,
                  status: status as any,
                  completedAt: new Date().toLocaleTimeString(),
                  stdout: stdoutText,
                  stderr: stderrText,
                  result: resultObj
                };
              }
              return rec;
            });

            return {
              ...prev,
              [epId]: {
                ...current,
                terminalBuffer: [...current.terminalBuffer, ...outputLines],
                history: updatedHistory,
                activeCommandId: undefined
              }
            };
          });
        }
      } catch {
        if (attempts >= maxAttempts) clearInterval(interval);
      }
    }, 1500);
  };

  const handleClearTerminal = () => {
    if (!activeEndpointId) return;
    setSessions((prev) => {
      const current = prev[activeEndpointId];
      if (!current) return prev;
      return {
        ...prev,
        [activeEndpointId]: {
          ...current,
          terminalBuffer: []
        }
      };
    });
  };

  const handleSaveOptions = (newOptions: ExecutionOptions) => {
    if (!activeEndpointId) return;
    setSessions((prev) => {
      const current = prev[activeEndpointId];
      if (!current) return prev;
      return {
        ...prev,
        [activeEndpointId]: {
          ...current,
          options: newOptions
        }
      };
    });
  };

  const activeSessionList = Object.values(sessions);
  const recentScriptsList = activeSession
    ? activeSession.history.map((h) => h.commandText).filter(Boolean)
    : [];

  return (
    <div className="flex flex-col h-[calc(100vh-48px)] bg-[#0d1117] text-[#c9d1d9] overflow-hidden">
      {/* Top Bar Header */}
      <ConsoleTopBar
        endpoints={endpoints}
        activeSession={activeSession}
        onSelectEndpoint={handleSelectEndpoint}
        onRefreshEndpoints={refetchEndpoints}
        onReconnectSession={() => {
          if (activeEndpointId && activeSession) {
            setSessions((prev) => ({
              ...prev,
              [activeEndpointId]: {
                ...activeSession,
                terminalBuffer: [
                  ...activeSession.terminalBuffer,
                  {
                    id: `sys-rec-${Date.now()}`,
                    timestamp: new Date().toLocaleTimeString(),
                    type: "system",
                    text: `Session reconnected to endpoint [${activeSession.hostname}]. WebSocket transport synchronized.`
                  }
                ]
              }
            }));
          }
        }}
        onDisconnectSession={() => {
          if (activeEndpointId && activeSession) {
            setSessions((prev) => ({
              ...prev,
              [activeEndpointId]: {
                ...activeSession,
                status: "offline",
                terminalBuffer: [
                  ...activeSession.terminalBuffer,
                  {
                    id: `sys-disc-${Date.now()}`,
                    timestamp: new Date().toLocaleTimeString(),
                    type: "system",
                    text: `Session disconnected from endpoint [${activeSession.hostname}].`
                  }
                ]
              }
            }));
          }
        }}
        onClearTerminal={handleClearTerminal}
        onOpenOptions={() => setIsOptionsOpen(true)}
      />

      {/* Multi-Endpoint Sessions Tab Bar */}
      {activeSessionList.length > 0 && (
        <div className="bg-[#161b22] px-3 border-b border-[#30363d] flex items-center gap-1 overflow-x-auto select-none scrollbar-none">
          {activeSessionList.map((sess) => {
            const isActive = sess.endpointId === activeEndpointId;
            return (
              <div
                key={sess.endpointId}
                onClick={() => setActiveEndpointId(sess.endpointId)}
                className={`flex items-center gap-2 px-3 py-1.5 border-t-2 text-xs font-semibold rounded-t transition-all cursor-pointer ${
                  isActive
                    ? "bg-[#0d1117] border-primary text-primary"
                    : "bg-[#21262d]/40 border-transparent text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d]"
                }`}
              >
                <Monitor className="h-3.5 w-3.5" />
                <span className="truncate max-w-[120px]">{sess.hostname}</span>
                <button
                  onClick={(e) => handleCloseSessionTab(sess.endpointId, e)}
                  className="p-0.5 rounded hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Main Console Workspace Layout (Sidebar + Terminal + History Panel) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Command Templates */}
        <ConsoleSidebarTemplates
          templates={DEFAULT_COMMAND_TEMPLATES}
          recentScripts={recentScriptsList}
          onSelectTemplate={(tmpl) => {
            handleExecuteCommand(tmpl.script, tmpl.shell);
          }}
          onExecuteScript={(script, shell) => {
            handleExecuteCommand(script, shell);
          }}
        />

        {/* Center: Interactive Terminal */}
        {activeSession ? (
          <InteractiveTerminal
            buffer={activeSession.terminalBuffer}
            shell={activeSession.options.shell}
            isRunning={!!activeSession.activeCommandId}
            onExecuteCommand={(cmd) => handleExecuteCommand(cmd)}
            onClearBuffer={handleClearTerminal}
            hostname={activeSession.hostname}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center p-8 text-center text-[#8b949e]">
            <div>
              <Monitor className="h-10 w-10 text-primary mx-auto mb-3 opacity-60" />
              <h3 className="text-sm font-bold text-[#c9d1d9] mb-1">No Active Session Selected</h3>
              <p className="text-xs max-w-sm mx-auto">
                Select an endpoint from the top bar dropdown or deploy a Windows Agent to open a live remote operations console.
              </p>
            </div>
          </div>
        )}

        {/* Right Panel: Session Execution Log */}
        <ConsoleRightPanelHistory
          history={activeSession?.history || []}
          onReopenCommand={(record) => setInspectedCommand(record)}
        />
      </div>

      {/* Execution Options Modal */}
      {activeSession && (
        <ExecutionOptionsModal
          isOpen={isOptionsOpen}
          onClose={() => setIsOptionsOpen(false)}
          options={activeSession.options}
          onSaveOptions={handleSaveOptions}
        />
      )}

      {/* Command Inspection LogViewer Modal */}
      {inspectedCommand && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-3xl bg-[#161b22] border border-[#30363d] rounded-xl shadow-2xl overflow-hidden">
            <div className="p-3 border-b border-[#30363d] flex items-center justify-between bg-[#0d1117]">
              <span className="font-bold text-xs text-[#c9d1d9]">
                {inspectedCommand.commandType} Output – ID: {inspectedCommand.id}
              </span>
              <button
                onClick={() => setInspectedCommand(null)}
                className="p-1 text-[#8b949e] hover:text-[#c9d1d9]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-4">
              <LogViewer
                content={inspectedCommand.stdout || inspectedCommand.result || inspectedCommand.stderr || "No log output."}
                title={`Command: ${inspectedCommand.commandText}`}
                maxHeight="500px"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
