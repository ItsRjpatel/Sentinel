/**
 * Reusable WebSocket service interface (Stub for Phase 1)
 */

export interface WebSocketEventPayload {
  event_type: string;
  timestamp: string;
  request_id: string;
  user?: string;
  endpoint_id?: string;
  payload: any;
}

export class WebSocketService {
  private url: string;
  // private ws: WebSocket | null = null;

  constructor() {
    const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
    // Convert http(s):// to ws(s)://
    this.url = apiBase.replace(/^http/, "ws").replace(/\/api\/v1$/, "/ws/commands");
  }

  connect(token: string) {
    console.log(`[WebSocket] Stub: Connecting to ${this.url}?token=${token}`);
    // this.ws = new WebSocket(`${this.url}?token=${token}`);
    // ...
  }

  disconnect() {
    console.log("[WebSocket] Stub: Disconnecting");
    // this.ws?.close();
    // this.ws = null;
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  onMessage(_callback: (event: WebSocketEventPayload) => void) {
    console.log("[WebSocket] Stub: Registered onMessage callback");
  }
}

export const wsService = new WebSocketService();
