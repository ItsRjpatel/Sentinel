import React, { useState } from "react";
import { Bell, CheckCheck } from "lucide-react";
import { useNotificationsList, useMarkAllNotificationsRead } from "../api/notificationsApi";
import { Link } from "react-router-dom";

export const NotificationBell: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { data: notifications = [] } = useNotificationsList(false);
  const markAllRead = useMarkAllNotificationsRead();

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-xl transition-colors relative cursor-pointer"
        title="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 px-1.5 py-0.2 bg-primary text-on-primary font-mono text-[9px] font-bold rounded-full animate-pulse">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-surface-container-low border border-outline-variant rounded-2xl shadow-2xl z-50 overflow-hidden text-xs">
          <div className="p-3 bg-surface-container-high border-b border-outline-variant/60 flex items-center justify-between font-bold text-on-surface">
            <span>Notifications ({unreadCount} unread)</span>
            <button
              onClick={() => markAllRead.mutate()}
              className="text-[10px] text-primary hover:underline flex items-center gap-1 cursor-pointer"
            >
              <CheckCheck className="h-3 w-3" /> Mark all read
            </button>
          </div>

          <div className="max-h-72 overflow-y-auto divide-y divide-outline-variant/30">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-on-surface-variant text-xs">No notifications.</div>
            ) : (
              notifications.slice(0, 5).map((n) => (
                <div key={n.id} className={`p-3 space-y-1 ${!n.is_read ? "bg-primary/5" : ""}`}>
                  <span className="font-bold text-on-surface block">{n.title}</span>
                  <p className="text-[11px] text-on-surface-variant line-clamp-2">{n.message}</p>
                </div>
              ))
            )}
          </div>

          <Link
            to="/notifications"
            onClick={() => setIsOpen(false)}
            className="block p-2.5 bg-surface-container text-center font-bold text-primary hover:underline border-t border-outline-variant/40"
          >
            View All Notifications
          </Link>
        </div>
      )}
    </div>
  );
};
