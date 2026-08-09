import React, { useState } from "react";
import {
  Bell,
  CheckCheck,
  ShieldAlert,
  Info,
  AlertTriangle,
  Sliders,
  Mail,
  MessageSquare,
  Check
} from "lucide-react";
import {
  useNotificationsList,
  useMarkNotificationRead,
  useMarkAllNotificationsRead,
  useNotificationPreferences,
  useSaveNotificationPreferences
} from "../api/notificationsApi";
import { Card, LoadingSkeleton } from "../../../components/ui";
import { useNavigate } from "react-router-dom";

export const NotificationsPage: React.FC = () => {
  const [tab, setTab] = useState<"ALL" | "UNREAD" | "PREFERENCES">("ALL");
  const { data: notifications = [], isLoading } = useNotificationsList(tab === "UNREAD");
  const markReadMutation = useMarkNotificationRead();
  const markAllReadMutation = useMarkAllNotificationsRead();
  const navigate = useNavigate();

  const { data: prefs } = useNotificationPreferences();
  const savePrefsMutation = useSaveNotificationPreferences();

  const [emailEnabled, setEmailEnabled] = useState(false);
  const [emailAddr, setEmailAddr] = useState("");
  const [slackEnabled, setSlackEnabled] = useState(false);
  const [slackUrl, setSlackUrl] = useState("");

  React.useEffect(() => {
    if (prefs) {
      setEmailEnabled(prefs.email_enabled);
      setEmailAddr(prefs.email_address || "");
      setSlackEnabled(prefs.slack_enabled);
      setSlackUrl(prefs.slack_webhook_url || "");
    }
  }, [prefs]);

  const handleSavePrefs = async (e: React.FormEvent) => {
    e.preventDefault();
    await savePrefsMutation.mutateAsync({
      email_enabled: emailEnabled,
      email_address: emailAddr,
      webhook_enabled: false,
      slack_enabled: slackEnabled,
      slack_webhook_url: slackUrl,
      teams_enabled: false,
      min_severity: "INFO"
    });
  };

  return (
    <div className="p-6 space-y-6 bg-surface min-h-screen text-on-surface">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-body-lg font-black tracking-tight text-on-surface flex items-center gap-2">
            <Bell className="h-7 w-7 text-primary" /> Enterprise Notification Center
          </h1>
          <p className="text-xs text-on-surface-variant">
            Real-time security alert dispatches, multi-channel webhooks (Slack/Teams/Email), & user audit feeds.
          </p>
        </div>

        <button
          onClick={() => markAllReadMutation.mutate()}
          className="flex items-center gap-1.5 px-4 py-2 bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-bold text-xs rounded-xl border border-outline-variant/60 transition-all cursor-pointer"
        >
          <CheckCheck className="h-4 w-4 text-emerald-400" /> Mark All Read
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-outline-variant/40 pb-2">
        <button
          onClick={() => setTab("ALL")}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all cursor-pointer ${
            tab === "ALL" ? "bg-primary/10 text-primary border border-primary/30" : "text-on-surface-variant hover:text-on-surface"
          }`}
        >
          All Activity Log
        </button>
        <button
          onClick={() => setTab("UNREAD")}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all cursor-pointer ${
            tab === "UNREAD" ? "bg-primary/10 text-primary border border-primary/30" : "text-on-surface-variant hover:text-on-surface"
          }`}
        >
          Unread Notifications
        </button>
        <button
          onClick={() => setTab("PREFERENCES")}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center gap-1.5 ${
            tab === "PREFERENCES" ? "bg-primary/10 text-primary border border-primary/30" : "text-on-surface-variant hover:text-on-surface"
          }`}
        >
          <Sliders className="h-3.5 w-3.5" /> Channel Preferences
        </button>
      </div>

      {/* Content */}
      {tab === "PREFERENCES" ? (
        <form onSubmit={handleSavePrefs} className="max-w-xl space-y-4">
          <Card className="p-6 border-outline-variant/60 space-y-4">
            <h3 className="text-body-md font-black text-on-surface flex items-center gap-2">
              <Mail className="h-5 w-5 text-primary" /> Email Alerting Channel
            </h3>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-xs font-bold text-on-surface">Enable Email Notifications</span>
              <input
                type="checkbox"
                checked={emailEnabled}
                onChange={(e) => setEmailEnabled(e.target.checked)}
                className="accent-primary h-4 w-4"
              />
            </label>

            {emailEnabled && (
              <div className="space-y-1">
                <label className="text-xs font-bold text-on-surface">Target Email Address</label>
                <input
                  type="email"
                  value={emailAddr}
                  onChange={(e) => setEmailAddr(e.target.value)}
                  placeholder="admin@enterprise.com"
                  className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            )}
          </Card>

          <Card className="p-6 border-outline-variant/60 space-y-4">
            <h3 className="text-body-md font-black text-on-surface flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-amber-400" /> Slack & Teams Webhook Integration
            </h3>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-xs font-bold text-on-surface">Enable Slack Webhook Alerts</span>
              <input
                type="checkbox"
                checked={slackEnabled}
                onChange={(e) => setSlackEnabled(e.target.checked)}
                className="accent-primary h-4 w-4"
              />
            </label>

            {slackEnabled && (
              <div className="space-y-1">
                <label className="text-xs font-bold text-on-surface">Slack Incoming Webhook URL</label>
                <input
                  type="url"
                  value={slackUrl}
                  onChange={(e) => setSlackUrl(e.target.value)}
                  placeholder="https://hooks.slack.com/services/..."
                  className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs font-mono text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            )}

            <button
              type="submit"
              className="px-4 py-2 bg-primary text-on-primary text-xs font-bold rounded-xl shadow-md hover:opacity-90 transition-all flex items-center gap-1 cursor-pointer"
            >
              <Check className="h-4 w-4" /> Save Channel Preferences
            </button>
          </Card>
        </form>
      ) : (
        <Card className="p-5 border-outline-variant/60">
          {isLoading ? (
            <LoadingSkeleton height={200} />
          ) : notifications.length === 0 ? (
            <div className="p-12 text-center text-on-surface-variant">
              <Bell className="h-10 w-10 text-primary mx-auto mb-2 opacity-40" />
              <p className="text-xs font-bold text-on-surface">No notifications recorded.</p>
            </div>
          ) : (
            <div className="divide-y divide-outline-variant/30">
              {notifications.map((notif) => {
                const isCritical = notif.severity === "CRITICAL" || notif.severity === "ERROR";
                return (
                  <div
                    key={notif.id}
                    onClick={() => {
                      if (notif.link) {
                        navigate(notif.link);
                      }
                    }}
                    className={`py-3.5 px-3 flex items-start justify-between gap-4 rounded-xl transition-colors ${notif.link ? 'cursor-pointer hover:bg-surface-container-low' : ''} ${
                      !notif.is_read ? "bg-primary/5" : ""
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5">
                        {isCritical ? (
                          <ShieldAlert className="h-5 w-5 text-error" />
                        ) : notif.severity === "WARNING" ? (
                          <AlertTriangle className="h-5 w-5 text-amber-400" />
                        ) : (
                          <Info className="h-5 w-5 text-primary" />
                        )}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-xs text-on-surface">{notif.title}</span>
                          <span className="px-1.5 py-0.2 bg-surface-container-high text-[9px] font-mono font-bold rounded uppercase">
                            {notif.category}
                          </span>
                        </div>
                        <p className="text-xs text-on-surface-variant mt-0.5">{notif.message}</p>
                        <span className="text-[10px] font-mono text-on-surface-variant/70 block mt-1">
                          {new Date(notif.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>

                    {!notif.is_read && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          markReadMutation.mutate(notif.id);
                        }}
                        className="px-2.5 py-1 bg-surface-container hover:bg-surface-container-high text-on-surface text-[10px] font-bold rounded-lg border border-outline-variant/40 cursor-pointer"
                      >
                        Mark Read
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      )}
    </div>
  );
};
