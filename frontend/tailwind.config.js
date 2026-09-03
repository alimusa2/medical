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
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          900: '#0c4a6e',
        },
        pass: {
          bg: '#f0fdf4',
          border: '#bbf7d0',
          text: '#15803d',
          badge: '#16a34a'
        },
        fail: {
          bg: '#fef2f2',
          border: '#fecaca',
          text: '#b91c1c',
          badge: '#dc2626'
        },
        review: {
          bg: '#fffbeb',
          border: '#fef3c7',
          text: '#b45309',
          badge: '#d97706'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
