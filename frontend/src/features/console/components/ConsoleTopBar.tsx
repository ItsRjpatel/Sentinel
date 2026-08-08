import React, { useState } from "react";
import {
  Monitor,
  Search,
  RotateCcw,
  WifiOff,
  Sliders,
  Trash2,
  ChevronDown,
  RefreshCw
} from "lucide-react";
import type { EndpointSession } from "../types/consoleTypes";
import { cn } from "../../../utils/cn";
import { isEndpointOnline } from "../../endpoints/api/endpointsApi";

interface ConsoleTopBarProps {
  endpoints: any[];
  activeSession: EndpointSession | null;
  onSelectEndpoint: (endpointId: string) => void;
  onRefreshEndpoints: () => void;
  onReconnectSession: () => void;
  onDisconnectSession: () => void;
  onClearTerminal: () => void;
  onOpenOptions: () => void;
}

export const ConsoleTopBar: React.FC<ConsoleTopBarProps> = ({
  endpoints,
  activeSession,
  onSelectEndpoint,
  onRefreshEndpoints,
  onReconnectSession,
  onDisconnectSession,
  onClearTerminal,
  onOpenOptions
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const filteredEndpoints = endpoints.filter((ep) => {
    const term = searchTerm.toLowerCase();
    const hostname = (ep.hostname || "").toLowerCase();
    const os = (ep.os_version || "").toLowerCase();
    const ip = (ep.ip_address || "").toLowerCase();
    return hostname.includes(term) || os.includes(term) || ip.includes(term);
  });

  const isOnline = activeSession?.status === "online";

  return (
    <div className="bg-[#161b22] border-b border-[#30363d] p-3 flex flex-wrap items-center justify-between gap-3 text-xs text-[#c9d1d9] select-none shadow-sm">
      {/* Left: Endpoint Selector & Active Badge */}
      <div className="flex items-center gap-3">
        {/* Endpoint Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 bg-[#21262d] hover:bg-[#30363d] border border-[#30363d] rounded-md text-xs font-semibold text-[#c9d1d9] transition-colors cursor-pointer min-w-[200px] justify-between shadow-xs"
          >
            <div className="flex items-center gap-2 truncate">
              <Monitor className="h-4 w-4 text-primary flex-shrink-0" />
              <span className="truncate">
                {activeSession ? activeSession.hostname : "Select Endpoint..."}
              </span>
            </div>
            <ChevronDown className="h-3.5 w-3.5 text-[#8b949e] flex-shrink-0" />
          </button>

          {dropdownOpen && (
            <div className="absolute left-0 top-full mt-1.5 w-72 bg-[#161b22] border border-[#30363d] rounded-md shadow-2xl z-50 overflow-hidden font-sans">
              <div className="p-2 border-b border-[#30363d] bg-[#0d1117] flex items-center gap-2">
                <Search className="h-3.5 w-3.5 text-[#8b949e]" />
                <input
                  type="text"
                  placeholder="Filter endpoints..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-transparent text-xs text-[#c9d1d9] placeholder-[#484f58] focus:outline-none"
                  autoFocus
                />
              </div>

              <div className="max-h-60 overflow-y-auto divide-y divide-[#21262d]">
                {filteredEndpoints.length === 0 ? (
                  <div className="p-3 text-center text-[#8b949e] text-xs">
                    No endpoints match "{searchTerm}"
                  </div>
                ) : (
                  filteredEndpoints.map((ep) => {
                    const isSelected = activeSession?.endpointId === ep.id;
                    const epOnline = isEndpointOnline(ep);

                    return (
                      <button
                        key={ep.id}
                        onClick={() => {
                          onSelectEndpoint(ep.id);
                          setDropdownOpen(false);
                        }}
                        className={cn(
                          "w-full p-2.5 text-left flex items-center justify-between hover:bg-[#21262d] transition-colors cursor-pointer",
                          isSelected && "bg-[#21262d] border-l-2 border-primary"
                        )}
                      >
                        <div className="flex flex-col truncate pr-2">
                          <span className="font-bold text-xs text-[#c9d1d9] truncate">
                            {ep.hostname || ep.id}
                          </span>
                          <span className="text-[10px] text-[#8b949e] truncate">
                            {ep.os_version || "Windows Workstation"}
                          </span>
                        </div>

                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          <span
                            className={cn(
                              "w-2 h-2 rounded-full",
                              epOnline ? "bg-emerald-400 animate-pulse" : "bg-zinc-500"
                            )}
                          />
                          <span className="text-[10px] uppercase font-bold text-[#8b949e]">
                            {epOnline ? "Online" : "Offline"}
                          </span>
                        </div>
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>

        {/* Active Session Endpoint Info Badge */}
        {activeSession && (
          <div className="flex items-center gap-3 px-3 py-1 bg-[#0d1117] border border-[#30363d] rounded-md">
            {/* Status Pulse */}
            <div className="flex items-center gap-1.5">
              <span
                className={cn(
                  "w-2.5 h-2.5 rounded-full inline-block",
                  isOnline ? "bg-emerald-400 animate-pulse shadow-sm" : "bg-red-500"
                )}
              />
              <span className="text-[11px] font-bold tracking-wide uppercase text-[#c9d1d9]">
                {isOnline ? "Online" : "Offline"}
              </span>
            </div>

            <span className="text-[#30363d]">|</span>

            {/* OS Badge */}
            <span className="text-[11px] text-[#8b949e] font-mono truncate max-w-[180px]">
              {activeSession.osVersion || "Windows 11"}
            </span>

            {/* Shell Format Badge */}
            <span className="px-1.5 py-0.5 bg-primary/10 text-primary text-[10px] font-mono font-bold rounded border border-primary/20 uppercase">
              {activeSession.options.shell}
            </span>
          </div>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Refresh List */}
        <button
          onClick={onRefreshEndpoints}
          title="Refresh endpoints list"
          className="p-1.5 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] rounded border border-[#30363d] transition-colors cursor-pointer"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </button>

        {/* Reconnect Session */}
        <button
          onClick={onReconnectSession}
          disabled={!activeSession}
          title="Reconnect terminal session"
          className="flex items-center gap-1 px-2.5 py-1 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] disabled:opacity-40 rounded border border-[#30363d] text-xs font-medium transition-colors cursor-pointer"
        >
          <RotateCcw className="h-3.5 w-3.5 text-primary" />
          <span>Reconnect</span>
        </button>

        {/* Disconnect Session */}
        <button
          onClick={onDisconnectSession}
          disabled={!activeSession}
          title="Disconnect session"
          className="flex items-center gap-1 px-2.5 py-1 bg-[#21262d] hover:bg-red-500/20 hover:text-red-400 text-[#8b949e] disabled:opacity-40 rounded border border-[#30363d] text-xs font-medium transition-colors cursor-pointer"
        >
          <WifiOff className="h-3.5 w-3.5" />
          <span>Disconnect</span>
        </button>

        {/* Clear Screen */}
        <button
          onClick={onClearTerminal}
          disabled={!activeSession}
          title="Clear screen buffer"
          className="flex items-center gap-1 px-2.5 py-1 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] disabled:opacity-40 rounded border border-[#30363d] text-xs font-medium transition-colors cursor-pointer"
        >
          <Trash2 className="h-3.5 w-3.5 text-amber-400" />
          <span>Clear</span>
        </button>

        {/* Options Modal Trigger */}
        <button
          onClick={onOpenOptions}
          disabled={!activeSession}
          title="Execution Options"
          className="flex items-center gap-1 px-3 py-1 bg-primary text-on-primary hover:opacity-90 disabled:opacity-40 rounded text-xs font-bold transition-all cursor-pointer shadow-sm"
        >
          <Sliders className="h-3.5 w-3.5" />
          <span>Options</span>
        </button>
      </div>
    </div>
  );
};
