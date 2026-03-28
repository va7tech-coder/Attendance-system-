import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#101828",
        sunrise: "#f97316",
        sand: "#fff4dc",
        mint: "#d4f5dd",
        slateblue: "#335c81",
        shell: "#fffdf7"
      },
      boxShadow: {
        panel: "0 24px 70px rgba(16, 24, 40, 0.12)"
      },
      backgroundImage: {
        "hero-grid": "radial-gradient(circle at top, rgba(249,115,22,0.16), transparent 30%), linear-gradient(135deg, rgba(51,92,129,0.18), transparent 45%)"
      }
    }
  },
  plugins: []
};

export default config;
