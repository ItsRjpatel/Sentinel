import React from "react";
import { useNavigate } from "react-router-dom";
import { Terminal, RotateCw, Power, CheckSquare } from "lucide-react";

interface EndpointsBulkActionBarProps {
  selectedCount: number;
  onClearSelection: () => void;
}

export const EndpointsBulkActionBar = React.memo(function EndpointsBulkActionBar({
  selectedCount,
  onClearSelection,
}: EndpointsBulkActionBarProps) {
  const navigate = useNavigate();

  if (selectedCount === 0) return null;

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-primary/10 border border-primary/30 rounded-xl animate-fadeIn">
      <div className="flex items-center gap-2">
        <CheckSquare className="h-4 w-4 text-primary" />
        <span className="text-xs font-bold text-primary">
          {selectedCount} {selectedCount === 1 ? "endpoint" : "endpoints"} selected
        </span>
        <button
          onClick={onClearSelection}
          className="text-[11px] text-on-surface-variant hover:text-on-surface underline font-medium ml-2"
        >
          Deselect All
        </button>
      </div>

      {/* Action Buttons (UI triggers) */}
      <div className="flex flex-wrap items-center gap-1.5">
        <button
          onClick={() => navigate("/commands")}
          className="px-2.5 py-1 bg-surface-container-high text-on-surface rounded text-xs font-bold flex items-center gap-1 hover:bg-surface-container-highest border border-outline-variant/40"
        >
          <Terminal className="h-3.5 w-3.5 text-primary" /> Run Command
        </button>

        <button
          onClick={() => navigate("/commands")}
          className="px-2.5 py-1 bg-surface-container-high text-on-surface rounded text-xs font-bold flex items-center gap-1 hover:bg-surface-container-highest border border-outline-variant/40"
        >
          <RotateCw className="h-3.5 w-3.5 text-success" /> Refresh Inventory
        </button>

        <button
          onClick={() => navigate("/commands")}
          className="px-2.5 py-1 bg-surface-container-high text-on-surface rounded text-xs font-bold flex items-center gap-1 hover:bg-surface-container-highest border border-outline-variant/40"
        >
          <Power className="h-3.5 w-3.5 text-warning" /> Restart Agent
        </button>

      </div>
    </div>
  );
});

