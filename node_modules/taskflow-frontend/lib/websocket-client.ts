/**
 * WebSocket client with auto-reconnect (exponential backoff, max 5 attempts).
 * Handles connection lifecycle, heartbeat, and event dispatching.
 */

export type WSMessageHandler = (message: TaskWSMessage) => void;

export interface TaskWSMessage {
  type: string;
  data: Record<string, unknown>;
  timestamp: string;
  correlation_id: string;
  event_id: string;
}

export type WSConnectionState = "connecting" | "connected" | "disconnected" | "reconnecting";

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private pingInterval: ReturnType<typeof setInterval> | null = null;
  private handlers: Set<WSMessageHandler> = new Set();
  private stateHandlers: Set<(state: WSConnectionState) => void> = new Set();
  private userId: string = "";
  private token: string = "";
  private _state: WSConnectionState = "disconnected";

  get state(): WSConnectionState {
    return this._state;
  }

  private setState(state: WSConnectionState) {
    this._state = state;
    this.stateHandlers.forEach((handler) => handler(state));
  }

  onMessage(handler: WSMessageHandler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  onStateChange(handler: (state: WSConnectionState) => void) {
    this.stateHandlers.add(handler);
    return () => this.stateHandlers.delete(handler);
  }

  connect(userId: string, token: string) {
    this.userId = userId;
    this.token = token;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `ws://${window.location.hostname}:8000`;
    const url = `${wsUrl}/ws/user/${userId}/tasks?token=${token}`;

    this.setState("connecting");

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.setState("connected");
        this.startPing();
      };

      this.ws.onmessage = (event) => {
        const data = event.data;

        // Handle ping/pong
        if (data === "ping") {
          this.ws?.send("pong");
          return;
        }
        if (data === "pong") {
          return;
        }

        // Parse and dispatch event
        try {
          const message: TaskWSMessage = JSON.parse(data);
          this.handlers.forEach((handler) => {
            try {
              handler(message);
            } catch (e) {
              console.error("WebSocket handler error:", e);
            }
          });
        } catch {
          // Ignore non-JSON messages
        }
      };

      this.ws.onclose = (event) => {
        this.stopPing();
        if (event.code === 4001 || event.code === 4003) {
          // Auth error — don't reconnect
          this.setState("disconnected");
          return;
        }
        this.reconnect();
      };

      this.ws.onerror = () => {
        // onclose will fire after onerror
      };
    } catch {
      this.reconnect();
    }
  }

  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.setState("disconnected");
      return;
    }

    this.setState("reconnecting");
    this.reconnectAttempts++;

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    setTimeout(() => {
      if (this.userId && this.token) {
        this.connect(this.userId, this.token);
      }
    }, delay);
  }

  private startPing() {
    this.stopPing();
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send("ping");
      }
    }, 30000);
  }

  private stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  disconnect() {
    this.stopPing();
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnect
    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }
    this.setState("disconnected");
  }
}
