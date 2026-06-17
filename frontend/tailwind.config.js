/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        campus: {
          ink: "#101828",
          muted: "#667085",
          line: "#d9dee8",
          blue: "#005baa",
          navy: "#063970",
          cyan: "#00a6d6",
          green: "#0f766e",
          gold: "#f6c445",
          saffron: "#f59e0b",
          surface: "#f7fafc",
        },
      },
      boxShadow: {
        panel: "0 12px 30px rgba(23, 32, 51, 0.08)",
        premium: "0 24px 70px rgba(6, 57, 112, 0.22)",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};
