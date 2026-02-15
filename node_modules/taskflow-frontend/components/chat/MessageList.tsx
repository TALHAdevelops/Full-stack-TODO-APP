/**
 * MessageList component for displaying chat messages
 * @spec: T-329 (spec.md UI, plan.md Chat Components)
 */

"use client";

import { useEffect, useRef } from "react";
import { MessageCircle, Loader2 } from "lucide-react";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  tool_calls?: Array<{
    tool_name: string;
    result?: Record<string, unknown>;
  }>;
}

interface MessageListProps {
  messages: Message[];
  loading: boolean;
}

function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;

  return date.toLocaleDateString();
}

export function MessageList({ messages, loading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
        <MessageCircle className="w-16 h-16 mb-4 opacity-30 text-[#00f2ff]" />
        <p className="text-lg font-medium text-gray-300">
          Start a conversation
        </p>
        <p className="text-sm text-gray-500">
          Try saying "Add buy milk" or "Show my tasks"
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-4 p-4 overflow-y-auto flex-1 bg-gradient-to-b from-[#05010d] to-[#0a0015]">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.role === "user" ? "justify-end" : "justify-start"
          }`}
        >
          <div
            className={`max-w-xs lg:max-w-md xl:max-w-lg rounded-lg px-4 py-2 ${
              message.role === "user"
                ? "bg-gradient-to-r from-[#00f2ff]/20 to-[#9d00ff]/20 text-white border border-[#00f2ff]/30 rounded-br-none"
                : "bg-black/50 text-gray-100 border border-white/10 rounded-bl-none"
            }`}
          >
            <p className="text-sm whitespace-pre-wrap break-words">
              {message.content}
            </p>

            {message.tool_calls && message.tool_calls.length > 0 && (
              <div className="mt-2 pt-2 border-t border-opacity-30 border-current text-xs opacity-80">
                {message.tool_calls.map((call, idx) => (
                  <div key={idx} className="mb-1">
                    {call.result?.status === "success" ? "✓ " : "✗ "}
                    <span className="text-[#00f2ff]">{call.tool_name}</span>
                  </div>
                ))}
              </div>
            )}

            <p className="text-xs opacity-50 mt-1">
              {formatTimestamp(message.created_at)}
            </p>
          </div>
        </div>
      ))}

      {loading && (
        <div className="flex justify-start">
          <div className="bg-black/50 border border-[#00f2ff]/30 text-[#00f2ff] rounded-lg rounded-bl-none px-4 py-2 flex items-center space-x-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Assistant is thinking...</span>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
