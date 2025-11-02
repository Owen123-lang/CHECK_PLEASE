import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-dark': '#0a0a0a', // Latar belakang utama (sangat gelap)
        'brand-container': '#1a1a1a', // Latar belakang panel/kontainer
        'brand-border': '#2a2a2a', // Border
        'brand-text': '#e0e0e0', // Teks sekunder
        'brand-yellow': {
          DEFAULT: '#FFD700', // Kuning primer (Saul Goodman)
          dark: '#b89c00',
        },
        'brand-red': {
          DEFAULT: '#D70000', // Merah primer
          dark: '#a00000',
        },
      },
    },
  },
  plugins: [],
};
export default config;
