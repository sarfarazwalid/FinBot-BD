/**
 * FinBot BD — Official Design Token System
 * Gunmetal & Copper: Industrial Premium Banking
 *
 * Do NOT hardcode these values anywhere.
 * Import from this file or use CSS variables.
 */

export const colors = {
  // Canvas & Surfaces
  bg: "#16120E", // Canvas — primary background
  surface: "#221D18", // Gunmetal — panels, sidebar
  card: "#2E2720", // Dark Warm — elevated cards, inputs
  "card-hover": "#3A3228", // Card hover state

  // Accent — Copper
  accent: "#B87333", // Copper — primary accent
  "accent-hover": "#D4944A", // Bright Copper — hover state
  "accent-muted": "rgba(184, 115, 51, 0.12)", // Copper glow/ping

  // Text
  text: "#F0EAE0", // Warm White — primary text
  "text-secondary": "rgba(240, 234, 224, 0.72)", // Secondary text
  "text-muted": "rgba(240, 234, 224, 0.5)", // Muted/placeholder

  // Borders & Dividers
  border: "rgba(212, 148, 74, 0.12)", // Copper-tinted border
  divider: "rgba(255, 255, 255, 0.05)", // Subtle divider

  // Semantic
  danger: "#D64545",
  success: "#5FA36A",
  warning: "#D6A34A",
  info: "#5E8BB8",

  // Overlays
  overlay: "rgba(22, 18, 14, 0.8)",
  "overlay-light": "rgba(22, 18, 14, 0.5)",
} as const;

export const radius = {
  // Border radii
  sm: "8px",
  md: "12px",
  lg: "16px",
  xl: "20px",
  "2xl": "24px",
  full: "9999px",
} as const;

export const spacing = {
  // 8px grid system
  0: "0",
  1: "4px",
  2: "8px",
  3: "12px",
  4: "16px",
  5: "20px",
  6: "24px",
  7: "28px",
  8: "32px",
  10: "40px",
  12: "48px",
  14: "56px",
  16: "64px",
  20: "80px",
  24: "96px",
} as const;

export const shadows = {
  // Very soft, no glow
  sm: "0 1px 2px rgba(0,0,0,0.2)",
  md: "0 4px 12px rgba(0,0,0,0.25)",
  lg: "0 8px 30px rgba(0,0,0,0.35)",
  xl: "0 12px 40px rgba(0,0,0,0.45)",
  "card-hover": "0 8px 30px rgba(0,0,0,0.4)",
  "button-primary": "0 2px 8px rgba(184, 115, 51, 0.2)",
} as const;

export const typography = {
  fontFamily: {
    heading: '"Space Grotesk", sans-serif',
    body: '"Inter", system-ui, -apple-system, sans-serif',
    mono: '"JetBrains Mono", monospace',
  },
  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
} as const;