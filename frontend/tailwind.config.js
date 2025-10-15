/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          100: '#1E1F3A',
          200: '#16182D', 
          300: '#10112A',
          400: '#0B0C1C',
        }
      },
    },
  },
  plugins: [],
}