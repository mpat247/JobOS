module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        caribbean: {
          50: "#eafff6",
          100: "#cdfee7",
          200: "#a0fad4",
          300: "#63f2be",
          400: "#25e2a3",
          500: "#00cd90",
          600: "#00a474",
          700: "#008360",
          800: "#00674d",
          900: "#005541",
          950: "#003026",
        },
      },
    },
  },
  plugins: [],
};
