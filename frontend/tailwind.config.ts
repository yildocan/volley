import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"] ,
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Work Sans", "sans-serif"]
      },
      colors: {
        ink: "#141414",
        clay: "#f0e3d1",
        tide: "#1a8b7a",
        coral: "#f15b41",
        steel: "#324356",
        mist: "#eef2f1"
      },
      boxShadow: {
        glow: "0 18px 45px rgba(15, 44, 66, 0.18)",
        lift: "0 12px 30px rgba(17, 24, 39, 0.18)"
      }
    }
  },
  plugins: []
} satisfies Config;
