import React from 'react'

interface InputProps {
  label: string
  value: string
  onChange: (value: string) => void
  type?: 'text' | 'email' | 'password' | 'textarea'
  placeholder?: string
  error?: string
  required?: boolean
  maxLength?: number
  showCounter?: boolean
  icon?: React.ReactNode
}

export function Input({
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
  error,
  required = false,
  maxLength,
  showCounter = false,
  icon
}: InputProps) {
  const inputStyles = `w-full px-4 py-3 bg-black/40 border rounded-lg focus:ring-1 focus:ring-[#00f2ff]/50 focus:border-[#00f2ff] outline-none transition-all duration-300 placeholder-gray-600 text-white ${
    error ? 'border-red-500/50' : 'border-white/10'
  } ${icon ? 'pl-11' : ''}`

  return (
    <div className="w-full">
      <label className="block text-xs font-bold text-[#00f2ff] mb-2 uppercase tracking-widest">
        {label} {required && <span className="text-red-500">*</span>}
      </label>

      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
            {icon}
          </div>
        )}
        {type === 'textarea' ? (
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            maxLength={maxLength}
            rows={3}
            className={`${inputStyles} resize-none`}
          />
        ) : (
          <input
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            maxLength={maxLength}
            className={inputStyles}
          />
        )}
      </div>

      <div className="flex justify-between mt-1">
        <div>
          {error && <p className="text-xs text-red-400 font-medium">{error}</p>}
        </div>
        {showCounter && maxLength && (
          <p className={`text-xs ${value.length > maxLength ? 'text-red-500' : 'text-gray-500'}`}>
            {value.length}/{maxLength}
          </p>
        )}
      </div>
    </div>
  )
}
