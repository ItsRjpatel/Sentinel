import React, { useState } from "react";
import { Settings, ShieldAlert, Cpu, Mail, Globe } from "lucide-react";
// 
export const SettingsPage = React.memo(function SettingsPage() {
        const [activeTab, setActiveTab] = useState("general");
  
  const sections = [
    { id: "general", label: "General Settings", icon: Globe },
    { id: "security", label: "Security & Auth", icon: ShieldAlert },
    { id: "agent", label: "Agent Config", icon: Cpu },
    { id: "smtp", label: "Integrations & Email", icon: Mail },
  ];

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <Settings className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise System Settings</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Global Platform Engine Parameters, Agent Heartbeats, and Security Policies
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-outline-variant/40 pb-2 overflow-x-auto scrollbar-none">
        {sections.map((sec) => {
          const Icon = sec.icon;
          const isActive = activeTab === sec.id;
          return (
            <button
              key={sec.id}
              onClick={() => setActiveTab(sec.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 border ${
                isActive
                  ? "bg-primary text-on-primary border-primary shadow-xs"
                  : "bg-surface-container-low text-on-surface-variant border-outline-variant/40 hover:bg-surface-container-high"
              }`}
            >
              <Icon className="h-4 w-4" /> {sec.label}
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      {/* Coming Soon Panel */}
      <div className="flex justify-center py-20">
        <div className="text-center bg-surface-container border border-outline-variant/60 rounded-xl p-10 max-w-lg">
          <Settings className="h-12 w-12 text-primary/40 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-on-surface mb-2">Feature Planned for Future Release</h2>
          <p className="text-sm text-on-surface-variant">
            The Enterprise System Settings module is currently in development.
          </p>
        </div>
      </div>
    </div>
  );
});

