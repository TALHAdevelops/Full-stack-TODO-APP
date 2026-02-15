'use client'

import { SignInForm } from '@/components/auth/SignInForm'
import { Hexagon, Layout, Shield, Zap } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen relative flex items-center justify-center px-4 py-20 overflow-hidden">
      {/* Background purely for aesthetic appeal */}
      <div className="absolute top-0 left-0 w-full h-full -z-10 overflow-hidden">
        <div className="absolute top-[10%] left-[5%] w-72 h-72 bg-[#00f2ff] rounded-full blur-[120px] opacity-10 animate-pulse"></div>
        <div className="absolute bottom-[10%] right-[5%] w-96 h-96 bg-[#9d00ff] rounded-full blur-[150px] opacity-10 animate-float"></div>
      </div>

      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        {/* Left Column: Branding */}
        <div className="space-y-8 fade-in slide-in-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold uppercase tracking-widest">
            <Zap className="w-3 h-3 text-[#00f2ff]" />
            v2.0 Deploying
          </div>

          <div className="space-y-4">
            <h1 className="text-6xl md:text-8xl font-black text-white leading-none tracking-tighter italic">
              TASK<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00f2ff] to-[#9d00ff]">FLOW</span>
            </h1>
            <p className="text-xl text-gray-400 font-light max-w-lg leading-relaxed">
                Experience the next evolution of task management. <span className="text-white font-medium">Fast. Secure. Futuristic.</span> Built for operatives who demand peak performance.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6 pt-8">
            <div className="space-y-2">
                <div className="flex items-center gap-2 text-white font-bold text-sm uppercase tracking-wider">
                    <Shield className="w-4 h-4 text-[#00f2ff]" />
                    Cyber Auth
                </div>
                <p className="text-gray-500 text-xs">Better-Auth secured sessions with JWT encryption.</p>
            </div>
            <div className="space-y-2">
                <div className="flex items-center gap-2 text-white font-bold text-sm uppercase tracking-wider">
                    <Layout className="w-4 h-4 text-[#9d00ff]" />
                    Grid Engine
                </div>
                <p className="text-gray-500 text-xs">Neon-lit interface with real-time response.</p>
            </div>
          </div>
        </div>

        {/* Right Column: Form */}
        <div className="relative fade-in slide-in-bottom delay-200">
            <div className="absolute inset-0 bg-gradient-to-br from-[#00f2ff]/20 to-[#9d00ff]/20 blur-3xl -z-10 rounded-full"></div>
            <SignInForm />

            {/* Decorative icons */}
            <Hexagon className="absolute -top-6 -right-6 w-12 h-12 text-[#9d00ff] opacity-20 animate-spin-slow" />
            <Hexagon className="absolute -bottom-10 -left-10 w-16 h-16 text-[#00f2ff] opacity-10 animate-float" />
        </div>
      </div>
    </div>
  )
}
