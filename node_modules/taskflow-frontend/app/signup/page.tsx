'use client'

import { SignUpForm } from '@/components/auth/SignUpForm'

export default function SignUpPage() {
  return (
            <div className="min-h-screen bg-background flex items-center justify-center px-4 py-12">
              <div className="max-w-md w-full">
                <div className="text-center mb-8">
                  <h1 className="text-5xl font-extrabold text-neon-purple tracking-tight">TaskFlow</h1>
                </div>        <SignUpForm />
      </div>
    </div>
  )
}
