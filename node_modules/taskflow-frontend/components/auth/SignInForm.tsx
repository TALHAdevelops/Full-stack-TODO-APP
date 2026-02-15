"use client";

import { useState } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Mail, Lock, Zap } from "lucide-react";

export function SignInForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    setApiError("");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      if (!res.ok) {
        throw new Error("Invalid email or password");
      }

      const data = await res.json();

      // Store the token in localStorage
      localStorage.setItem('auth_token', data.access_token);

      // Redirect to dashboard
      window.location.href = "/dashboard";
    } catch (err: any) {
      setApiError(err.message || "INVALID CREDENTIALS. ACCESS DENIED.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 glass-card p-10 rounded-2xl border-white/5 relative overflow-hidden group"
    >
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#00f2ff] to-transparent opacity-50"></div>

      <div className="flex justify-center mb-6">
        <div className="p-3 rounded-full bg-[#00f2ff]/10 border border-[#00f2ff]/30 animate-pulse">
          <Zap className="w-8 h-8 text-[#00f2ff]" />
        </div>
      </div>

      <div className="text-center mb-8">
        <h2 className="text-3xl font-black text-white tracking-tighter uppercase italic">
          Terminal Access
        </h2>
        <p className="text-gray-500 text-xs mt-1 font-mono uppercase tracking-widest">
          Authorized Personnel Only
        </p>
      </div>

      {apiError && (
        <div className="p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-xs font-mono text-center animate-shake">
          {apiError}
        </div>
      )}

      <div className="space-y-4">
        <Input
          label="Email Address"
          type="email"
          value={email}
          onChange={setEmail}
          placeholder="user@taskflow.net"
          required
          icon={<Mail className="w-4 h-4" />}
        />

        <Input
          label="Passkey"
          type="password"
          value={password}
          onChange={setPassword}
          placeholder="********"
          required
          icon={<Lock className="w-4 h-4" />}
        />
      </div>

      <Button type="submit" loading={loading} className="w-full mt-4 h-12">
        Initialize Session
      </Button>

      <p className="text-center text-xs text-gray-500 mt-6 font-mono">
        NEW USER?{" "}
        <a
          href="/signup"
          className="text-[#9d00ff] hover:text-[#00f2ff] transition-colors duration-300 underline underline-offset-4"
        >
          REGISTER HERE
        </a>
      </p>
    </form>
  );
}
