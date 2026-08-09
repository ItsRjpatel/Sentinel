import React, { useEffect, useState, useRef } from "react";
import { Bell, Check, BellRing, Info, AlertTriangle, AlertCircle, ShieldAlert } from "lucide-react";
import { 
  useNotificationsList, 
  useMarkNotificationRead,
  useMarkAllNotificationsRead,
} from "../../features/notifications/api/notificationsApi";
import type { NotificationItem } from "../../features/notifications/api/notificationsApi";
import { useNavigate } from "react-router-dom";

export function NotificationBell() {
  const { data: notifications = [] } = useNotificationsList(true); // true = unread_only
  const markReadMutation = useMarkNotificationRead();
  const markAllReadMutation = useMarkAllNotificationsRead();
  const navigate = useNavigate();

  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const handleMarkAsRead = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    markReadMutation.mutate(id);
  };

  const handleMarkAllRead = () => {
    markAllReadMutation.mutate();
  };

  const getIcon = (severity: string, category: string) => {
    if (category === "SECURITY") return <ShieldAlert className="w-5 h-5 text-error" />;
    if (severity === "CRITICAL") return <ShieldAlert className="w-5 h-5 text-error" />;
    if (severity === "ERROR" || severity === "HIGH") return <AlertCircle className="w-5 h-5 text-error" />;
    if (severity === "WARNING" || severity === "MEDIUM") return <AlertTriangle className="w-5 h-5 text-warning" />;
    return <Info className="w-5 h-5 text-primary" />;
  };

  return (
    <div className="relative inline-block" ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-on-surface-variant hover:bg-surface-container-highest rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50"
      >
        <Bell className="w-5 h-5" />
        {notifications.length > 0 && (
          <span className="absolute top-1 right-1.5 flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-error"></span>
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-surface border border-outline-variant rounded-xl shadow-xl z-50 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
          <div className="flex items-center justify-between px-4 py-3 border-b border-outline-variant bg-surface-container-lowest">
            <h3 className="font-semibold text-on-surface">Notifications</h3>
            {notifications.length > 0 && (
              <button
                onClick={handleMarkAllRead}
                disabled={markAllReadMutation.isPending}
                className="text-xs font-medium text-primary hover:text-primary/80 transition-colors flex items-center gap-1 disabled:opacity-50"
              >
                <Check className="w-3.5 h-3.5" />
                Mark all read
              </button>
            )}
          </div>
          
          <div className="max-h-[350px] overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-on-surface-variant flex flex-col items-center justify-center">
                <BellRing className="w-8 h-8 mb-2 opacity-50 text-on-surface-variant" />
                <p className="text-sm">You're all caught up!</p>
              </div>
            ) : (
              <ul className="divide-y divide-outline-variant/50">
                {notifications.slice(0, 10).map((notif: NotificationItem) => (
                  <li
                    key={notif.id}
                    onClick={() => {
                      if (notif.link) {
                        setIsOpen(false);
                        navigate(notif.link);
                      }
                    }}
                    className={`flex items-start gap-3 p-4 hover:bg-surface-container-low transition-colors group ${notif.link ? 'cursor-pointer' : 'cursor-default'}`}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      {getIcon(notif.severity, notif.category)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-on-surface truncate">{notif.title}</p>
                      <p className="text-xs text-on-surface-variant mt-0.5 line-clamp-2 leading-relaxed">
                        {notif.message}
                      </p>
                      <p className="text-[10px] text-on-surface-variant/70 mt-1.5 uppercase tracking-wider">
                        {new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleMarkAsRead(notif.id, e)}
                      disabled={markReadMutation.isPending}
                      className="opacity-0 group-hover:opacity-100 p-1.5 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-highest rounded-md transition-all shrink-0"
                      title="Mark as read"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="p-2 border-t border-outline-variant bg-surface-container-lowest">
            <button
              onClick={() => {
                setIsOpen(false);
                navigate("/notifications");
              }}
              className="block w-full py-2 text-center text-sm font-medium text-primary hover:bg-primary/10 rounded-lg transition-colors"
            >
              View all notifications
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
