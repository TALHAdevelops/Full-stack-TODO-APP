"use client";

import { Button } from "@/components/ui/Button";
import { Activity, LogOut, Shield, MessageSquare, Layers } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";

interface HeaderProps {
  userEmail?: string;
  onSignOut: () => void;
}

export function Header({ userEmail, onSignOut }: HeaderProps) {
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch by only rendering pathname-dependent content on client
  useEffect(() => {
    setMounted(true);
  }, []);

  const isActive = (path: string) => mounted && pathname === path;

  return (
    <header className="bg-black/50 backdrop-blur-md border-b border-white/5 sticky top-0 z-50">
      {/* Animated scanline */}
      <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#00f2ff] to-transparent opacity-20"></div>

      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="absolute inset-0 bg-[#00f2ff]/20 blur-lg rounded-lg"></div>
            <div className="relative bg-black border border-[#00f2ff]/50 p-2 rounded-lg">
              <Shield className="w-5 h-5 text-[#00f2ff]" />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-black text-white tracking-tighter italic leading-none uppercase">
              TASKFLOW
            </span>
            <span className="text-[8px] text-[#00f2ff] uppercase font-bold tracking-[0.4em] leading-none mt-1">
              Command Tower
            </span>
          </div>
        </div>

        <div className="flex items-center gap-6">
          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-4">
            <Link href="/dashboard">
              <Button
                variant="ghost"
                className={`gap-2 h-9 px-4 text-[10px] transition-all ${
                  isActive("/dashboard")
                    ? "border-[#00f2ff]/50 text-[#00f2ff]"
                    : "border-white/5 hover:border-[#00f2ff]/30 text-gray-400 hover:text-[#00f2ff]"
                }`}
              >
                <Layers className="w-3 h-3" />
                Dashboard
              </Button>
            </Link>
            <Link href="/chat">
              <Button
                variant="ghost"
                className={`gap-2 h-9 px-4 text-[10px] transition-all ${
                  isActive("/chat")
                    ? "border-[#00f2ff]/50 text-[#00f2ff]"
                    : "border-white/5 hover:border-[#9d00ff]/30 text-gray-400 hover:text-[#9d00ff]"
                }`}
              >
                <MessageSquare className="w-3 h-3" />
                AI Chat
              </Button>
            </Link>
          </nav>

          {userEmail && (
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10">
              <Activity className="w-3 h-3 text-[#9d00ff]" />
              <span className="text-[10px] text-gray-400 font-mono uppercase tracking-widest">
                {userEmail}
              </span>
            </div>
          )}
          <Button
            variant="ghost"
            onClick={() => {
              localStorage.removeItem("auth_token");
              onSignOut();
            }}
            className="gap-2 h-9 px-4 text-[10px] border-white/5 hover:border-red-500/30 hover:text-red-400 transition-all"
          >
            <LogOut className="w-3 h-3" />
            Secure Sign Out
          </Button>
        </div>
      </div>
    </header>
  );
}
