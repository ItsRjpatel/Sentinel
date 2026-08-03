import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Search, X, Monitor, ShieldAlert, ShieldCheck, ArrowRight } from "lucide-react";
import { apiClient } from "../../services/api";

export const GlobalSearchModal: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any>({
    endpoints: [],
    users: [],
    commands: [],
    alerts: [],
    policies: [],
    audit: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Shortcut Ctrl+K / Cmd+K listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  useEffect(() => {
    if (!query.trim()) {
      setResults({ endpoints: [], users: [], commands: [], alerts: [], policies: [], audit: [] });
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.get("/search", { params: { q: query } });
        setResults(res.data?.data || res.data || {});
      } catch {
        // Handle error silently
      } finally {
        setIsLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  const totalResults =
    (results.endpoints?.length || 0) +
    (results.users?.length || 0) +
    (results.commands?.length || 0) +
    (results.alerts?.length || 0) +
    (results.policies?.length || 0) +
    (results.audit?.length || 0);

  const handleNavigate = (link: string) => {
    setIsOpen(false);
    navigate(link);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-start justify-center pt-20 p-4">
      <div className="w-full max-w-2xl bg-surface-container-low border border-outline-variant rounded-2xl shadow-2xl overflow-hidden font-sans text-xs text-on-surface">
        {/* Search Bar Input Header */}
        <div className="p-3 border-b border-outline-variant/60 flex items-center gap-3 bg-surface-container-high">
          <Search className="h-5 w-5 text-primary flex-shrink-0" />
          <input
            type="text"
            placeholder="Search Endpoints, Users, Commands, Alerts, Policies, Audit Logs... (ESC to exit)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-body-md text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none"
            autoFocus
          />
          <button onClick={() => setIsOpen(false)} className="p-1 text-on-surface-variant hover:text-on-surface">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <p className="text-center text-on-surface-variant py-8">Searching enterprise database...</p>
          ) : query.trim() && totalResults === 0 ? (
            <p className="text-center text-on-surface-variant py-8">No results found for "{query}".</p>
          ) : !query.trim() ? (
            <div className="text-center text-on-surface-variant py-8 space-y-1">
              <p className="font-bold text-on-surface">Global Enterprise Search Ready</p>
              <p className="text-[11px]">Type hostname, IP, username, alert name, or policy title to instantly query across modules.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {results.endpoints?.length > 0 && (
                <div className="space-y-1">
                  <span className="text-[10px] font-bold uppercase text-primary tracking-wider flex items-center gap-1">
                    <Monitor className="h-3.5 w-3.5" /> Endpoints
                  </span>
                  {results.endpoints.map((item: any) => (
                    <div
                      key={item.id}
                      onClick={() => handleNavigate(item.link)}
                      className="p-2.5 bg-surface-container hover:bg-surface-container-high rounded-xl flex items-center justify-between cursor-pointer transition-colors"
                    >
                      <div>
                        <span className="font-bold text-on-surface">{item.title}</span>
                        <span className="text-[11px] text-on-surface-variant block">{item.subtitle}</span>
                      </div>
                      <ArrowRight className="h-4 w-4 text-on-surface-variant" />
                    </div>
                  ))}
                </div>
              )}

              {results.policies?.length > 0 && (
                <div className="space-y-1">
                  <span className="text-[10px] font-bold uppercase text-amber-400 tracking-wider flex items-center gap-1">
                    <ShieldCheck className="h-3.5 w-3.5" /> Security Policies
                  </span>
                  {results.policies.map((item: any) => (
                    <div
                      key={item.id}
                      onClick={() => handleNavigate(item.link)}
                      className="p-2.5 bg-surface-container hover:bg-surface-container-high rounded-xl flex items-center justify-between cursor-pointer transition-colors"
                    >
                      <div>
                        <span className="font-bold text-on-surface">{item.title}</span>
                        <span className="text-[11px] text-on-surface-variant block">{item.subtitle}</span>
                      </div>
                      <ArrowRight className="h-4 w-4 text-on-surface-variant" />
                    </div>
                  ))}
                </div>
              )}

              {results.alerts?.length > 0 && (
                <div className="space-y-1">
                  <span className="text-[10px] font-bold uppercase text-error tracking-wider flex items-center gap-1">
                    <ShieldAlert className="h-3.5 w-3.5" /> Security Alerts
                  </span>
                  {results.alerts.map((item: any) => (
                    <div
                      key={item.id}
                      onClick={() => handleNavigate(item.link)}
                      className="p-2.5 bg-surface-container hover:bg-surface-container-high rounded-xl flex items-center justify-between cursor-pointer transition-colors"
                    >
                      <div>
                        <span className="font-bold text-on-surface">{item.title}</span>
                        <span className="text-[11px] text-on-surface-variant block">{item.subtitle}</span>
                      </div>
                      <ArrowRight className="h-4 w-4 text-on-surface-variant" />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
