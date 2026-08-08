import React from "react";
import { Bell } from "lucide-react";
// import { useNotificationsList, useMarkAllNotificationsRead } from "../api/notificationsApi";

export const NotificationBell: React.FC = () => {
  return (
    <div className="relative">
      <button
        disabled
        className="p-2 text-on-surface-variant opacity-50 cursor-not-allowed rounded-xl relative"
        title="Notifications (Coming Soon)"
      >
        <Bell className="h-5 w-5" />
      </button>
    </div>
  );
};

