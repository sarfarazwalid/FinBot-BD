import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Canvas & Surfaces
        bg: "#16120E",
        surface: "#221D18",
        card: "#2E2720",
        "card-hover": "#3A3228",

        // Accent — Copper
        accent: "#B87333",
        "accent-hover": "#D4944A",
        "accent-muted": "rgba(184, 115, 51, 0.12)",

        // Text
        text: "#F0EAE0",
        "text-secondary": "rgba(240, 234, 224, 0.72)",
        "text-muted": "rgba(240, 234, 224, 0.5)",

        // Borders
        border: "rgba(212, 148, 74, 0.12)",
        divider: "rgba(255, 255, 255, 0.05)",

        // Semantic
        danger: "#D64545",
        success: "#5FA36A",
        warning: "#D6A34A",
        info: "#5E8BB8",

        // Overlays
        overlay: "rgba(22, 18, 14, 0.8)",
        "overlay-light": "rgba(22, 18, 14, 0.5)",
      },
      fontFamily: {
        sans: ['"Satoshi"', '"Noto Sans Bengali"', "system-ui", "-apple-system", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "0.875rem" }],
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.8125rem", { lineHeight: "1.25rem" }],
        base: ["0.9375rem", { lineHeight: "1.5rem" }],
        lg: ["1.0625rem", { lineHeight: "1.625rem" }],
        xl: ["1.25rem", { lineHeight: "1.75rem" }],
        "2xl": ["1.5rem", { lineHeight: "2rem" }],
        "3xl": ["1.875rem", { lineHeight: "2.25rem" }],
        "4xl": ["2.25rem", { lineHeight: "2.75rem" }],
      },
      borderRadius: {
        sm: "8px",
        md: "12px",
        lg: "16px",
        xl: "20px",
        "2xl": "24px",
        full: "9999px",
      },
      boxShadow: {
        sm: "0 1px 2px rgba(0,0,0,0.2)",
        DEFAULT: "0 2px 8px rgba(0,0,0,0.22)",
        md: "0 4px 12px rgba(0,0,0,0.25)",
        lg: "0 8px 30px rgba(0,0,0,0.35)",
        xl: "0 12px 40px rgba(0,0,0,0.45)",
        "card": "0 4px 16px rgba(0,0,0,0.3)",
        "card-hover": "0 8px 30px rgba(0,0,0,0.4)",
        "button": "0 2px 8px rgba(184, 115, 51, 0.2)",
        "button-hover": "0 4px 14px rgba(212, 148, 74, 0.25)",
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
        30: "7.5rem",
      },
      animation: {
        "fade-in": "fadeIn 0.2s ease-out",
        "fade-up": "fadeUp 0.25s ease-out",
        "scale-in": "scaleIn 0.18s ease-out",
        "slide-up": "slideUp 0.2s ease-out",
        "spin-slow": "spin 2s linear infinite",
        "pulse-subtle": "pulseSubtle 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.97)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        slideUp: {
          "0%": { transform: "translateY(4px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        pulseSubtle: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;