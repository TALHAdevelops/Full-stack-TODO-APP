/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        neon: {
          blue: "var(--neon-blue)",
          purple: "var(--neon-purple)",
          pink: "var(--neon-pink)",
        }
      },
      boxShadow: {
        'neon-blue': '0 0 15px rgba(0, 242, 255, 0.4)',
        'neon-purple': '0 0 15px rgba(157, 0, 255, 0.4)',
      }
    },
  },
  plugins: [],
}
