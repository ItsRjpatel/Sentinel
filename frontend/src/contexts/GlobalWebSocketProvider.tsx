import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

interface WebSocketContextType {
  isConnected: boolean;
  lastEvent: any;
}

const GlobalWebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  lastEvent: null,
});

export const useGlobalWebSocket = () => useContext(GlobalWebSocketContext);

export const GlobalWebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<any>(null);
  const queryClient = useQueryClient();
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Check both sentinel_token (from AuthContext) and fallback access_token
    const token = localStorage.getItem("sentinel_token") || localStorage.getItem("access_token");

    // If no token exists: do not connect, do not retry continuously, fail gracefully without console spam
    if (!token) {
      setIsConnected(false);
      return;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.hostname === "localhost" ? "127.0.0.1:8000" : window.location.host;
    const wsUrl = `${protocol}//${host}/ws/commands?token=${encodeURIComponent(token)}`;

    let socket: WebSocket;
    let reconnectTimeout: any;

    const connect = () => {
      try {
        socket = new WebSocket(wsUrl);
        socketRef.current = socket;

        socket.onopen = () => {
          setIsConnected(true);
        };

        socket.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            setLastEvent(parsed);
            if (parsed.event_type && parsed.event_type.startsWith("notification_")) {
              queryClient.invalidateQueries({ queryKey: ["notifications"] });
            } else if (parsed.event_type && parsed.event_type.startsWith("alert_")) {
              queryClient.invalidateQueries({ queryKey: ["alerts"] });
            } else {
              queryClient.invalidateQueries({ queryKey: ["commands"] });
            }
          } catch {
            // ignore non-json messages (e.g. pong)
          }
        };

        socket.onclose = () => {
          setIsConnected(false);
          // Only retry if token still exists
          if (localStorage.getItem("sentinel_token") || localStorage.getItem("access_token")) {
            reconnectTimeout = setTimeout(connect, 5000);
          }
        };

        socket.onerror = () => {
          if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
            socket.close();
          }
        };
      } catch {
        setIsConnected(false);
      }
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [queryClient]);

  return (
    <GlobalWebSocketContext.Provider value={{ isConnected, lastEvent }}>
      {children}
    </GlobalWebSocketContext.Provider>
  );
};
