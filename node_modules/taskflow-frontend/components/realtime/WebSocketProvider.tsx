"use client";

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from "react";
import { WebSocketClient, TaskWSMessage } from "@/lib/websocket-client";
import type { WSConnectionState } from "@/lib/types";

interface WebSocketContextValue {
  connectionState: WSConnectionState;
  lastMessage: TaskWSMessage | null;
  onTaskEvent: (handler: (message: TaskWSMessage) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextValue>({
  connectionState: "disconnected",
  lastMessage: null,
  onTaskEvent: () => () => {},
});

export function useWebSocket() {
  return useContext(WebSocketContext);
}

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const clientRef = useRef<WebSocketClient | null>(null);
  const [connectionState, setConnectionState] = useState<WSConnectionState>("disconnected");
  const [lastMessage, setLastMessage] = useState<TaskWSMessage | null>(null);
  const handlersRef = useRef<Set<(message: TaskWSMessage) => void>>(new Set());

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    const userId = localStorage.getItem("user_id");

    if (!token || !userId) {
      return;
    }

    const client = new WebSocketClient();
    clientRef.current = client;

    // Listen for state changes
    client.onStateChange(setConnectionState);

    // Listen for messages
    client.onMessage((message) => {
      setLastMessage(message);
      handlersRef.current.forEach((handler) => {
        try {
          handler(message);
        } catch (e) {
          console.error("WebSocket handler error:", e);
        }
      });
    });

    client.connect(userId, token);

    return () => {
      client.disconnect();
      clientRef.current = null;
    };
  }, []);

  const onTaskEvent = useCallback((handler: (message: TaskWSMessage) => void) => {
    handlersRef.current.add(handler);
    return () => {
      handlersRef.current.delete(handler);
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ connectionState, lastMessage, onTaskEvent }}>
      {children}
    </WebSocketContext.Provider>
  );
}
