/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#F8FAFC',        // Slate-50 clean canvas
          card: '#FFFFFF',      // Pure crisp white card
          cardSubtle: '#F1F5F9',// Slate-100 subtle background
          border: '#E2E8F0',    // Slate-200 border
          borderHover: '#CBD5E1',
          textMain: '#0F172A',  // Slate-900 high contrast text
          textMuted: '#64748B', // Slate-500 secondary text
          accent: '#059669',    // Emerald-600 vibrant energy green
          accentLight: '#10B981',
          cyan: '#0284C7',      // Sky-600 power blue
          amber: '#D97706',     // Amber-600 solar
          purple: '#7C3AED',    // Violet-600 flexibility
          danger: '#DC2626'     // Red-600 grid risk
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      }
    },
  },
  plugins: [],
}
