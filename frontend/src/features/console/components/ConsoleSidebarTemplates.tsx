import React, { useState, useMemo } from "react";
import {
  Search,
  Star,
  ChevronRight,
  ChevronDown,
  Play,
  Clock,
  Sparkles,
  Network,
  Cpu,
  Settings,
  Activity,
  HardDrive,
  Shield,
  Key,
  Users,
  Code
} from "lucide-react";
import type { CommandTemplate } from "../types/consoleTypes";

interface ConsoleSidebarTemplatesProps {
  templates: CommandTemplate[];
  recentScripts: string[];
  onSelectTemplate: (template: CommandTemplate) => void;
  onExecuteScript: (script: string, shell: "powershell" | "cmd") => void;
}

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  Networking: Network,
  System: Cpu,
  Services: Settings,
  Processes: Activity,
  Storage: HardDrive,
  Windows: Sparkles,
  Registry: Key,
  Security: Shield,
  Users: Users,
  Custom: Code
};

export const ConsoleSidebarTemplates: React.FC<ConsoleSidebarTemplatesProps> = ({
  templates,
  recentScripts,
  onSelectTemplate,
  onExecuteScript
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [openCategories, setOpenCategories] = useState<Record<string, boolean>>({
    Networking: true,
    System: true,
    Services: false,
    Processes: false,
    Security: true
  });

  const categories = useMemo(() => {
    const map: Record<string, CommandTemplate[]> = {};
    templates.forEach((t) => {
      if (!map[t.category]) map[t.category] = [];
      map[t.category].push(t);
    });
    return map;
  }, [templates]);

  const favorites = useMemo(() => {
    return templates.filter((t) => t.isFavorite);
  }, [templates]);

  const filteredCategories = useMemo(() => {
    if (!searchTerm.trim()) return categories;
    const term = searchTerm.toLowerCase();
    const result: Record<string, CommandTemplate[]> = {};

    Object.entries(categories).forEach(([cat, list]) => {
      const matched = list.filter(
        (t) =>
          t.title.toLowerCase().includes(term) ||
          t.script.toLowerCase().includes(term) ||
          t.description.toLowerCase().includes(term)
      );
      if (matched.length > 0) {
        result[cat] = matched;
      }
    });
    return result;
  }, [categories, searchTerm]);

  const toggleCategory = (category: string) => {
    setOpenCategories((prev) => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  return (
    <div className="w-64 bg-[#161b22] border-r border-[#30363d] flex flex-col h-full select-none font-sans text-xs">
      {/* Sidebar Header & Search */}
      <div className="p-3 border-b border-[#30363d] space-y-2 bg-[#0d1117]/60">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="font-bold text-[#c9d1d9] text-xs uppercase tracking-wider">
            Command Library
          </span>
        </div>

        <div className="relative flex items-center">
          <Search className="h-3.5 w-3.5 absolute left-2.5 text-[#8b949e]" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-8 pr-2.5 py-1 bg-[#0d1117] border border-[#30363d] rounded text-xs text-[#c9d1d9] placeholder-[#484f58] focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Main Templates Scroll Area */}
      <div className="flex-1 overflow-y-auto p-2 space-y-3 scrollbar-thin scrollbar-thumb-[#30363d] scrollbar-track-[#161b22]">
        {/* Favorites Quick Section */}
        {!searchTerm && favorites.length > 0 && (
          <div className="space-y-1">
            <div className="px-2 text-[10px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1">
              <Star className="h-3 w-3 fill-amber-400" /> Favorites
            </div>

            <div className="space-y-1">
              {favorites.map((tmpl) => (
                <div
                  key={`fav-${tmpl.id}`}
                  onClick={() => onSelectTemplate(tmpl)}
                  className="group flex items-center justify-between p-2 bg-[#21262d]/60 hover:bg-[#21262d] rounded border border-amber-500/20 hover:border-amber-500/40 transition-all cursor-pointer"
                >
                  <div className="flex flex-col truncate pr-2">
                    <span className="font-semibold text-[#c9d1d9] text-xs truncate">
                      {tmpl.title}
                    </span>
                    <span className="font-mono text-[10px] text-[#8b949e] truncate">
                      {tmpl.script}
                    </span>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onExecuteScript(tmpl.script, tmpl.shell);
                    }}
                    title="Quick Run"
                    className="p-1 rounded bg-primary/20 hover:bg-primary text-primary hover:text-on-primary opacity-0 group-hover:opacity-100 transition-all cursor-pointer flex-shrink-0"
                  >
                    <Play className="h-3 w-3 fill-current" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Categorized Accordion Tree */}
        <div className="space-y-1">
          {Object.keys(filteredCategories).length === 0 ? (
            <div className="p-4 text-center text-[#8b949e] text-xs italic font-mono">
              No template found
            </div>
          ) : (
            Object.entries(filteredCategories).map(([catName, list]) => {
              const isOpen = searchTerm.trim() !== "" || !!openCategories[catName];
              const IconComp = CATEGORY_ICONS[catName] || Code;

              return (
                <div key={catName} className="rounded overflow-hidden">
                  {/* Category Accordion Header */}
                  <button
                    onClick={() => toggleCategory(catName)}
                    className="w-full px-2 py-1.5 flex items-center justify-between bg-[#21262d]/40 hover:bg-[#21262d] rounded text-[#c9d1d9] font-bold text-xs transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-2">
                      <IconComp className="h-3.5 w-3.5 text-primary" />
                      <span>{catName}</span>
                      <span className="text-[10px] text-[#8b949e] font-mono">
                        ({list.length})
                      </span>
                    </div>
                    {isOpen ? (
                      <ChevronDown className="h-3.5 w-3.5 text-[#8b949e]" />
                    ) : (
                      <ChevronRight className="h-3.5 w-3.5 text-[#8b949e]" />
                    )}
                  </button>

                  {/* Category Template Items */}
                  {isOpen && (
                    <div className="mt-1 ml-2 pl-2 border-l border-[#30363d] space-y-1">
                      {list.map((tmpl) => (
                        <div
                          key={tmpl.id}
                          onClick={() => onSelectTemplate(tmpl)}
                          className="group flex items-center justify-between p-1.5 hover:bg-[#21262d] rounded text-xs transition-all cursor-pointer"
                        >
                          <div className="flex flex-col truncate pr-2">
                            <div className="flex items-center gap-1.5">
                              <span className="px-1 py-0.2 bg-[#0d1117] text-[#8b949e] font-mono text-[9px] uppercase rounded border border-[#30363d]">
                                {tmpl.shell}
                              </span>
                              <span className="font-medium text-[#c9d1d9] truncate">
                                {tmpl.title}
                              </span>
                            </div>
                            <span className="font-mono text-[10px] text-[#8b949e] truncate mt-0.5">
                              {tmpl.script}
                            </span>
                          </div>

                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onExecuteScript(tmpl.script, tmpl.shell);
                            }}
                            title="Execute Script"
                            className="p-1 rounded bg-primary/20 hover:bg-primary text-primary hover:text-on-primary opacity-0 group-hover:opacity-100 transition-all cursor-pointer flex-shrink-0"
                          >
                            <Play className="h-3 w-3 fill-current" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Recent Executed Scripts */}
        {!searchTerm && recentScripts.length > 0 && (
          <div className="pt-2 border-t border-[#30363d] space-y-1">
            <div className="px-2 text-[10px] font-bold uppercase tracking-wider text-[#8b949e] flex items-center gap-1">
              <Clock className="h-3 w-3" /> Recent Scripts
            </div>

            <div className="space-y-0.5">
              {recentScripts.slice(0, 5).map((script, idx) => (
                <button
                  key={`recent-${idx}`}
                  onClick={() => onExecuteScript(script, "powershell")}
                  className="w-full text-left p-1.5 hover:bg-[#21262d] rounded text-xs font-mono text-[#8b949e] hover:text-[#c9d1d9] truncate transition-colors cursor-pointer block"
                  title={script}
                >
                  {script}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
