/**
 * Chat page for Phase III AI Chatbot
 * @spec: T-328, T-332, T-333 (spec.md §Chat UI, plan.md §Frontend)
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  MessageList,
  Message as MessageType,
} from "@/components/chat/MessageList";
import { ChatInput } from "@/components/chat/ChatInput";
import { Header } from "@/components/layout/Header";
import {
  sendMessage,
  listConversations,
  getConversation,
  ChatAPIError,
} from "@/lib/api/chat-client";
import { ChevronLeft, Plus, Trash2, MessageSquare } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface User {
  id: string;
  email: string;
  name?: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  // State
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<
    string | null
  >(null);
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversationsLoading, setConversationsLoading] = useState(false);

  // Check authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("auth_token");
        if (!token) {
          router.push("/");
          setAuthLoading(false);
          return;
        }

        // Verify token is still valid by checking with backend
        const response = await fetch(`${API_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          localStorage.removeItem("auth_token");
          router.push("/");
        }
      } catch (err) {
        console.error("Auth check failed:", err);
        localStorage.removeItem("auth_token");
        router.push("/");
      } finally {
        setAuthLoading(false);
      }
    };
    checkAuth();
  }, [router]);

  // Load conversations when user is authenticated
  useEffect(() => {
    if (user && !authLoading) {
      loadConversations();
    }
  }, [user, authLoading]);

  // Load conversation messages when conversation changes
  useEffect(() => {
    if (currentConversationId && user) {
      loadConversationMessages(currentConversationId);
    }
  }, [currentConversationId, user]);

  const loadConversations = async () => {
    if (!user?.id) return;

    try {
      setConversationsLoading(true);

      // Get JWT token from localStorage
      const token = localStorage.getItem("auth_token");

      if (!token) {
        console.error("No token available");
        router.push("/");
        return;
      }

      console.log("Loading conversations for user:", user.id);
      const convs = await listConversations(user.id, token);
      console.log("Loaded conversations:", convs);
      setConversations(convs);

      // Auto-select first conversation if none selected
      if (convs.length > 0 && !currentConversationId) {
        setCurrentConversationId(convs[0].id);
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
      if (err instanceof ChatAPIError && err.status === 401) {
        router.push("/");
      }
    } finally {
      setConversationsLoading(false);
    }
  };

  const loadConversationMessages = async (conversationId: string) => {
    if (!user?.id) return;

    try {
      setLoading(true);
      setError(null);

      // Get JWT token from localStorage
      const token = localStorage.getItem("auth_token");

      if (!token) {
        console.error("No token available");
        return;
      }

      const conversation = await getConversation(
        user.id,
        conversationId,
        token
      );

      // Transform messages to match Message interface
      const transformedMessages: MessageType[] = conversation.messages.map(
        (msg) => {
          let toolCalls = undefined;
          if (msg.tool_calls) {
            // Handle both formats: {"calls": [...]} and direct array
            const callsArray = msg.tool_calls.calls || msg.tool_calls;
            if (Array.isArray(callsArray)) {
              toolCalls = callsArray.map((call: any) => ({
                tool_name: call.tool_name,
                result: call.result,
              }));
            }
          }
          return {
            id: msg.id,
            role: msg.role as "user" | "assistant",
            content: msg.content,
            created_at: msg.created_at,
            tool_calls: toolCalls,
          };
        }
      );

      setMessages(transformedMessages);
    } catch (err) {
      console.error("Failed to load conversation:", err);
      if (err instanceof ChatAPIError) {
        setError(err.detail);
        if (err.status === 401) {
          router.push("/");
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    if (!user?.id) {
      setError("User not authenticated");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem("auth_token");
      if (!token) {
        setError("No authentication token available");
        setLoading(false);
        return;
      }

      console.log("Sending message:", {
        userId: user.id,
        conversationId: currentConversationId,
        message: messageText,
      });

      // Add user message optimistically
      const userMessage: MessageType = {
        id: `temp-${Date.now()}`,
        role: "user",
        content: messageText,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Send message to API (conversation_id is optional, backend will create one if needed)
      const response = await sendMessage(
        user.id,
        {
          conversation_id: currentConversationId || undefined,
          message: messageText,
        },
        token
      );

      console.log("Chat response:", response);

      // If this was a new conversation, update the conversation ID
      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: MessageType = {
        id: response.id,
        role: "assistant",
        content: response.content,
        created_at: response.created_at,
        tool_calls: response.tool_calls,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Reload conversations to update timestamps/titles
      await loadConversations();
    } catch (err) {
      console.error("Failed to send message:", err);
      if (err instanceof ChatAPIError) {
        setError(err.detail);
        if (err.status === 401) {
          router.push("/");
        }
      } else {
        setError(err instanceof Error ? err.message : "Failed to send message");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
  };

  const handleDeleteConversation = async (conversationId: string) => {
    // TODO: Implement delete endpoint in backend
    console.log("Delete conversation:", conversationId);
  };

  const currentConversation = conversations.find(
    (c) => c.id === currentConversationId
  );

  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#05010d]">
        <div className="animate-pulse text-lg text-[#00f2ff]">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const handleSignOut = () => {
    router.push("/");
  };

  return (
    <div className="flex flex-col h-screen bg-[#05010d]">
      <Header userEmail={user?.email} onSignOut={handleSignOut} />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div
          className={`${
            sidebarOpen ? "w-64" : "w-0"
          } bg-black/50 backdrop-blur-md border-r border-white/10 flex flex-col transition-all duration-300 overflow-hidden`}
        >
          <div className="p-4 border-b border-white/10">
            <button
              onClick={handleNewChat}
              className="w-full bg-gradient-to-r from-[#00f2ff] to-[#9d00ff] hover:from-[#00f2ff]/80 hover:to-[#9d00ff]/80 text-black font-bold py-2 px-4 rounded-lg flex items-center justify-center space-x-2 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>New Chat</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {conversationsLoading ? (
              <div className="text-center text-sm text-gray-500">
                Loading...
              </div>
            ) : conversations.length === 0 ? (
              <div className="text-center text-sm text-gray-500">
                No conversations yet
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => setCurrentConversationId(conv.id)}
                  className={`p-3 rounded-lg cursor-pointer transition-all flex items-center justify-between group ${
                    currentConversationId === conv.id
                      ? "bg-[#00f2ff]/20 border border-[#00f2ff]/50 text-[#00f2ff]"
                      : "text-gray-400 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{conv.title}</p>
                    <p className="text-xs opacity-60">
                      {new Date(conv.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteConversation(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 hover:text-red-400 rounded transition-opacity"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>

          <div className="p-4 border-t border-white/10 text-sm text-gray-400">
            {user?.email}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-[#05010d]">
          {/* Header */}
          <div className="border-b border-white/10 bg-black/30 px-4 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors text-[#00f2ff]"
              >
                <ChevronLeft
                  className={`w-5 h-5 transition-transform ${
                    sidebarOpen ? "rotate-0" : "rotate-180"
                  }`}
                />
              </button>
              {currentConversation ? (
                <div>
                  <h1 className="text-lg font-semibold text-white">
                    {currentConversation.title}
                  </h1>
                  <p className="text-xs text-gray-400">
                    Created{" "}
                    {new Date(
                      currentConversation.created_at
                    ).toLocaleDateString()}
                  </p>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-gray-400">
                  <MessageSquare className="w-5 h-5" />
                  <span>New Chat</span>
                </div>
              )}
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <MessageList messages={messages} loading={loading} />

            {error && (
              <div className="px-4 py-3 bg-red-500/20 border-t border-red-500/30 text-sm text-red-400">
                {error}
              </div>
            )}
          </div>

          {/* Input Area */}
          <ChatInput onSubmit={handleSendMessage} loading={loading} />
        </div>
      </div>
    </div>
  );
}
