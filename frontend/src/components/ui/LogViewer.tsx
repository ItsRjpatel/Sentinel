import React, { useState, useMemo, useRef } from "react";
import {
  Copy,
  Check,
  Search,
  Maximize2,
  Minimize2,
  ListOrdered,
  WrapText,
  FileText,
  FileCode
} from "lucide-react";
import { cn } from "../../utils/cn";

interface LogViewerProps {
  content: string | object | null | undefined;
  title?: string;
  maxHeight?: string; // Default: '400px'
  className?: string;
  showSearch?: boolean;
  showLineNumbers?: boolean;
}

export const LogViewer: React.FC<LogViewerProps> = ({
  content,
  title = "Output Log",
  maxHeight = "400px",
  className,
  showSearch = true,
  showLineNumbers: initialLineNumbers = true
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showLineNumbers, setShowLineNumbers] = useState(initialLineNumbers);
  const [wordWrap, setWordWrap] = useState(true);
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Normalize content to string
  const rawText = useMemo(() => {
    if (!content) return "No output recorded.";
    if (typeof content === "string") return content;
    try {
      return JSON.stringify(content, null, 2);
    } catch {
      return String(content);
    }
  }, [content]);

  // Process lines and search filter
  const lines = useMemo(() => {
    return rawText.split("\n");
  }, [rawText]);

  const filteredLineIndices = useMemo(() => {
    if (!searchTerm.trim()) return null;
    const term = searchTerm.toLowerCase();
    const indices: number[] = [];
    lines.forEach((line, idx) => {
      if (line.toLowerCase().includes(term)) {
        indices.push(idx);
      }
    });
    return indices;
  }, [lines, searchTerm]);

  const displayLines = useMemo(() => {
    if (filteredLineIndices === null) {
      return lines.map((text, idx) => ({ lineNum: idx + 1, text }));
    }
    return filteredLineIndices.map((idx) => ({ lineNum: idx + 1, text: lines[idx] }));
  }, [lines, filteredLineIndices]);

  const handleCopy = () => {
    navigator.clipboard.writeText(rawText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (format: "txt" | "json") => {
    const filename = `command_output_${Date.now()}.${format}`;
    let fileContent = rawText;
    let mimeType = "text/plain";

    if (format === "json") {
      mimeType = "application/json";
      if (typeof content === "object" && content !== null) {
        fileContent = JSON.stringify(content, null, 2);
      } else {
        try {
          const parsed = JSON.parse(rawText);
          fileContent = JSON.stringify(parsed, null, 2);
        } catch {
          fileContent = JSON.stringify({ raw_output: rawText }, null, 2);
        }
      }
    }

    const blob = new Blob([fileContent], { type: `${mimeType};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      ref={containerRef}
      className={cn(
        "rounded-lg border border-outline-variant/80 bg-[#0d1117] text-[#e6edf3] font-mono text-xs flex flex-col overflow-hidden shadow-md transition-all",
        isFullscreen ? "fixed inset-4 z-50 max-h-none border-primary/40 shadow-2xl" : "",
        className
      )}
    >
      {/* Sticky Top Toolbar */}
      <div className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-2 px-3 py-2 bg-[#161b22] border-b border-[#30363d] select-none">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-primary/80 inline-block" />
          <span className="font-sans text-xs font-semibold text-[#c9d1d9] tracking-wide">
            {title}
          </span>
          <span className="text-[11px] text-[#8b949e] font-sans">
            ({lines.length.toLocaleString()} {lines.length === 1 ? "line" : "lines"})
          </span>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {/* Search Box */}
          {showSearch && (
            <div className="relative flex items-center">
              <Search className="h-3.5 w-3.5 absolute left-2 text-[#8b949e]" />
              <input
                type="text"
                placeholder="Search log..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-7 pr-2 py-1 bg-[#0d1117] border border-[#30363d] rounded text-[11px] text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-primary/70 w-32 focus:w-44 transition-all"
              />
              {searchTerm && (
                <span className="text-[10px] text-primary ml-1.5 font-sans font-medium">
                  {filteredLineIndices ? `${filteredLineIndices.length} matches` : ""}
                </span>
              )}
            </div>
          )}

          {/* Toggle Line Numbers */}
          <button
            onClick={() => setShowLineNumbers(!showLineNumbers)}
            title="Toggle line numbers"
            className={cn(
              "p-1.5 rounded text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-colors cursor-pointer",
              showLineNumbers && "bg-[#21262d] text-primary"
            )}
          >
            <ListOrdered className="h-3.5 w-3.5" />
          </button>

          {/* Toggle Word Wrap */}
          <button
            onClick={() => setWordWrap(!wordWrap)}
            title="Toggle word wrap"
            className={cn(
              "p-1.5 rounded text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-colors cursor-pointer",
              wordWrap && "bg-[#21262d] text-primary"
            )}
          >
            <WrapText className="h-3.5 w-3.5" />
          </button>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            title="Copy output to clipboard"
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

          {/* Download TXT */}
          <button
            onClick={() => handleDownload("txt")}
            title="Download log file (.txt)"
            className="flex items-center gap-1 px-2 py-1 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] rounded text-[11px] font-sans font-medium transition-colors cursor-pointer"
          >
            <FileText className="h-3.5 w-3.5 text-blue-400" />
            <span>TXT</span>
          </button>

          {/* Download JSON */}
          <button
            onClick={() => handleDownload("json")}
            title="Download JSON structure (.json)"
            className="flex items-center gap-1 px-2 py-1 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] rounded text-[11px] font-sans font-medium transition-colors cursor-pointer"
          >
            <FileCode className="h-3.5 w-3.5 text-amber-400" />
            <span>JSON</span>
          </button>

          {/* Fullscreen Expand/Collapse */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            title={isFullscreen ? "Exit Fullscreen" : "Expand Fullscreen"}
            className="p-1.5 rounded text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-colors cursor-pointer"
          >
            {isFullscreen ? (
              <Minimize2 className="h-3.5 w-3.5 text-amber-400" />
            ) : (
              <Maximize2 className="h-3.5 w-3.5" />
            )}
          </button>
        </div>
      </div>

      {/* Main Terminal Output Body */}
      <div
        className="flex-1 overflow-y-auto overflow-x-hidden p-3 font-mono leading-relaxed select-text scrollbar-thin scrollbar-thumb-[#30363d] scrollbar-track-[#0d1117]"
        style={{
          maxHeight: isFullscreen ? "calc(100vh - 80px)" : maxHeight,
          wordBreak: wordWrap ? "break-word" : "normal",
          whiteSpace: wordWrap ? "pre-wrap" : "pre",
          overflowWrap: wordWrap ? "anywhere" : "normal"
        }}
      >
        {displayLines.length === 0 ? (
          <div className="text-[#8b949e] italic text-center py-6 font-sans">
            No lines match search filter "{searchTerm}"
          </div>
        ) : (
          <div className="table w-full border-collapse">
            {displayLines.map(({ lineNum, text }) => {
              const isError =
                text.toLowerCase().includes("error") ||
                text.toLowerCase().includes("failed") ||
                text.toLowerCase().includes("exception");
              const isSuccess =
                text.toLowerCase().includes("success") ||
                text.toLowerCase().includes("completed");
              const isHighlight =
                searchTerm.trim() !== "" &&
                text.toLowerCase().includes(searchTerm.toLowerCase());

              return (
                <div
                  key={lineNum}
                  className={cn(
                    "table-row hover:bg-[#161b22]/80 transition-colors group",
                    isHighlight && "bg-amber-500/15"
                  )}
                >
                  {/* Line Number Column */}
                  {showLineNumbers && (
                    <div className="table-cell pr-4 text-right text-[#484f58] select-none w-10 font-sans text-[11px] align-top group-hover:text-[#8b949e]">
                      {lineNum}
                    </div>
                  )}

                  {/* Line Text Content */}
                  <div
                    className={cn(
                      "table-cell align-top text-[#c9d1d9]",
                      isError && "text-red-400 font-semibold",
                      isSuccess && "text-emerald-400",
                      isHighlight && "text-amber-200"
                    )}
                  >
                    {text || " "}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
