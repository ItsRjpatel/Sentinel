import React, { useState } from "react";
import { Settings, Save, ShieldAlert, Cpu, Mail, Globe } from "lucide-react";
import { Card, Button, LoadingSkeleton } from "../../../components/ui";
import { useSettingsList, useUpdateSetting } from "../api/settingsApi";

export const SettingsPage = React.memo(function SettingsPage() {
  const { data: settings = [], isLoading } = useSettingsList();
  const updateMutation = useUpdateSetting();

  const [activeTab, setActiveTab] = useState("general");

  if (isLoading) {
    return <LoadingSkeleton height={500} />;
  }

  const handleSaveCategory = async (key: string, currentVal: any) => {
    try {
      await updateMutation.mutateAsync({ key, value: currentVal });
      alert(`Settings for ${key} saved successfully!`);
    } catch (err: any) {
      alert(`Failed to save settings: ${err.message || "Unknown error"}`);
    }
  };

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
      {settings.map((item) => {
        if (item.key !== activeTab) return null;

        return (
          <Card key={item.key} className="p-6 bg-surface-container-low border-outline-variant space-y-6">
            <div className="flex items-center justify-between border-b border-outline-variant/40 pb-3">
              <div>
                <h3 className="text-body-lg font-black text-on-surface uppercase">{item.key} Configuration</h3>
                <p className="text-xs text-on-surface-variant">{item.description}</p>
              </div>
              <Button
                onClick={() => handleSaveCategory(item.key, item.value)}
                disabled={updateMutation.isPending}
                variant="primary"
                size="sm"
                leftIcon={<Save className="h-4 w-4" />}
                className="font-extrabold shadow-xs"
              >
                {updateMutation.isPending ? "Saving..." : "Save Settings"}
              </Button>
            </div>

            {/* Render KV Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-medium">
              {Object.entries(item.value).map(([subKey, subVal]) => (
                <div key={subKey} className="space-y-1 bg-surface-container-high p-3 rounded-xl border border-outline-variant/40">
                  <label className="font-bold text-on-surface uppercase text-[11px]">{subKey.replace(/_/g, " ")}</label>
                  {typeof subVal === "boolean" ? (
                    <div className="flex items-center gap-2 pt-1">
                      <input
                        type="checkbox"
                        checked={subVal}
                        onChange={(e) => {
                          item.value[subKey] = e.target.checked;
                        }}
                        className="w-4 h-4 text-primary rounded border-outline-variant focus:ring-primary"
                      />
                      <span className="text-on-surface font-bold">{subVal ? "Enabled" : "Disabled"}</span>
                    </div>
                  ) : (
                    <input
                      type={typeof subVal === "number" ? "number" : "text"}
                      defaultValue={String(subVal)}
                      onChange={(e) => {
                        item.value[subKey] = typeof subVal === "number" ? Number(e.target.value) : e.target.value;
                      }}
                      className="w-full p-2 bg-surface-container-low border border-outline-variant/50 rounded-lg text-on-surface font-bold focus:outline-none focus:border-primary"
                    />
                  )}
                </div>
              ))}
            </div>
          </Card>
        );
      })}
    </div>
  );
});
