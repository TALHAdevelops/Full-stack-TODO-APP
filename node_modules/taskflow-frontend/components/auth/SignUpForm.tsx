"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { authClient } from "@/lib/auth-client";
import { Mail, ShieldCheck, UserPlus, Fingerprint } from "lucide-react";

export function SignUpForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!email.includes("@")) newErrors.email = "INVALID DATA FORMAT: EMAIL";
    if (password.length < 8)
      newErrors.password = "SECURITY RISK: PASSKEY TOO SHORT";
    if (password !== confirmPassword)
      newErrors.confirmPassword = "PARITY ERROR: MISMATCH";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setApiError("");

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name: "" }),
        }
      );

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to create account");
      }

      const data = await res.json();

      // Store the token in localStorage
      localStorage.setItem("auth_token", data.access_token);

      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 500);
    } catch (err: any) {
      setApiError(err.message || "SYSTEM ERROR. REGISTRATION FAILED.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 glass-card p-10 rounded-2xl border-white/5 relative overflow-hidden group"
    >
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#9d00ff] to-transparent opacity-50"></div>

      <div className="flex justify-center mb-6">
        <div className="p-3 rounded-full bg-[#9d00ff]/10 border border-[#9d00ff]/30 animate-pulse">
          <UserPlus className="w-8 h-8 text-[#9d00ff]" />
        </div>
      </div>

      <div className="text-center mb-8">
        <h2 className="text-3xl font-black text-white tracking-tighter uppercase italic">
          New operative
        </h2>
        <p className="text-gray-500 text-xs mt-1 font-mono uppercase tracking-widest">
          Establish Security Clearance
        </p>
      </div>

      {apiError && (
        <div className="p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-xs font-mono text-center">
          {apiError}
        </div>
      )}

      <div className="space-y-4">
        <Input
          label="Identity"
          type="email"
          value={email}
          onChange={setEmail}
          error={errors.email}
          placeholder="user@taskflow.net"
          required
          icon={<Mail className="w-4 h-4" />}
        />

        <Input
          label="Set Passkey"
          type="password"
          value={password}
          onChange={setPassword}
          error={errors.password}
          placeholder="••••••••"
          required
          icon={<Fingerprint className="w-4 h-4" />}
        />

        <Input
          label="Verify Passkey"
          type="password"
          value={confirmPassword}
          onChange={setConfirmPassword}
          error={errors.confirmPassword}
          placeholder="••••••••"
          required
          icon={<ShieldCheck className="w-4 h-4" />}
        />
      </div>

      <Button
        type="submit"
        variant="secondary"
        loading={loading}
        className="w-full mt-4 h-12"
      >
        Register Identity
      </Button>

      <p className="text-center text-xs text-gray-500 mt-6 font-mono">
        ALREADY REGISTERED?{" "}
        <a
          href="/"
          className="text-[#00f2ff] hover:text-[#9d00ff] transition-colors duration-300 underline underline-offset-4"
        >
          LOGIN HERE
        </a>
      </p>
    </form>
  );
}
