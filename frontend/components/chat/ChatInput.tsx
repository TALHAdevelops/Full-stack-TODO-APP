/**
 * ChatInput component for user message entry
 * @spec: T-330 (spec.md UI, plan.md Chat Components)
 */

"use client";

import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSubmit: (message: string) => void;
  loading: boolean;
}

const MAX_MESSAGE_LENGTH = 5000;

export function ChatInput({ onSubmit, loading }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Focus input on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        120
      )}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim() || loading) {
      return;
    }

    onSubmit(message);
    setMessage("");

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (Shift+Enter for newline)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading) {
        handleSubmit(e as any);
      }
    }
  };

  const remainingChars = MAX_MESSAGE_LENGTH - message.length;
  const isOverLimit = remainingChars < 0;

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-white/10 bg-black/50 backdrop-blur-md p-4"
    >
      <div className="space-y-2">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) =>
            setMessage(e.target.value.slice(0, MAX_MESSAGE_LENGTH))
          }
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Shift+Enter for newline)"
          disabled={loading}
          className="w-full px-4 py-3 border border-white/20 bg-white/5 text-white placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00f2ff] focus:border-[#00f2ff] disabled:bg-white/5 disabled:text-gray-500 resize-none"
          rows={1}
        />

        <div className="flex items-center justify-between">
          <div
            className={`text-xs ${
              isOverLimit ? "text-red-400" : "text-gray-500"
            }`}
          >
            {message.length}/{MAX_MESSAGE_LENGTH}
          </div>

          <button
            type="submit"
            disabled={loading || !message.trim() || isOverLimit}
            className="bg-gradient-to-r from-[#00f2ff] to-[#9d00ff] hover:from-[#00f2ff]/80 hover:to-[#9d00ff]/80 disabled:from-gray-600 disabled:to-gray-600 text-black font-bold py-2 px-4 rounded-lg flex items-center space-x-2 transition-all"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
        </div>
      </div>
    </form>
  );
}
