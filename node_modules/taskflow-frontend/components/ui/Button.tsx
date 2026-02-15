import React from 'react'

interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  loading?: boolean
  disabled?: boolean
  className?: string
}

export function Button({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  loading = false,
  disabled = false,
  className = ''
}: ButtonProps) {
  const baseStyles = 'px-6 py-2.5 rounded-lg font-bold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center tracking-wider uppercase text-xs'

  const variantStyles = {
    primary: 'bg-transparent text-[#00f2ff] border border-[#00f2ff]/50 hover:bg-[#00f2ff]/10 hover:border-[#00f2ff] neon-glow-blue',
    secondary: 'bg-transparent text-[#9d00ff] border border-[#9d00ff]/50 hover:bg-[#9d00ff]/10 hover:border-[#9d00ff] neon-glow-purple',
    danger: 'bg-transparent text-[#ff00c8] border border-[#ff00c8]/50 hover:bg-[#ff00c8]/10 hover:border-[#ff00c8]',
    ghost: 'bg-transparent text-gray-400 hover:text-white hover:bg-white/5'
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <svg className="animate-spin h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </span>
      ) : children}
    </button>
  )
}
