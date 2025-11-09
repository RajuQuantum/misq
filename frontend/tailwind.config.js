/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        quantum: {
          background: '#0f172a',
          panel: '#1e293b',
          accent: '#38bdf8',
          green: '#16a34a',
          red: '#dc2626',
        },
      },
      animation: {
        blink: 'blink 0.6s ease-in-out',
        pulseAura: 'pulseAura 1.2s ease-in-out',
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.3 },
        },
        pulseAura: {
          '0%': { boxShadow: '0 0 0px rgba(56, 189, 248, 0.4)' },
          '50%': { boxShadow: '0 0 25px rgba(56, 189, 248, 0.6)' },
          '100%': { boxShadow: '0 0 0px rgba(56, 189, 248, 0.4)' },
        },
      },
    },
  },
  plugins: [],
};
