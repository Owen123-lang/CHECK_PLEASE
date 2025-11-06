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
        'brand-dark': '#1A1E21', // Latar belakang utama - match landing page
        'brand-container': '#232B2F', // Latar belakang panel/kontainer - slightly lighter
        'brand-border': '#2a2a2a', // Border
        'brand-text': '#e0e0e0', // Teks sekunder
        'brand-yellow': {
          DEFAULT: '#FFFF00', // Kuning primer - match landing page
          dark: '#FFD700',
        },
        'brand-red': {
          DEFAULT: '#FF0000', // Merah primer - match landing page
          dark: '#D70000',
        },
      },
    },
  },
  plugins: [],
};
export default config;
