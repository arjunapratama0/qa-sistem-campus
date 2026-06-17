/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        campus: {
          ink: "#172033",
          muted: "#667085",
          line: "#d9dee8",
          blue: "#1d4ed8",
          green: "#0f766e",
          gold: "#b7791f",
        },
      },
      boxShadow: {
        panel: "0 12px 30px rgba(23, 32, 51, 0.08)",
      },
    },
  },
  plugins: [],
};

