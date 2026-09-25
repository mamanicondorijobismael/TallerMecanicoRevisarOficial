tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "#001330",
        "primary-container": "#0D284E",
        "on-primary": "#ffffff",
        "on-primary-container": "#7990bc",
        "primary-fixed": "#d7e3ff",
        "primary-fixed-dim": "#b0c7f6",
        "on-primary-fixed": "#001b3e",
        "on-primary-fixed-variant": "#30476e",

        "secondary": "#446082",
        "secondary-blue": "#3E5A7B",
        "secondary-container": "#bad7fe",
        "on-secondary": "#ffffff",
        "on-secondary-container": "#415d7f",
        "secondary-fixed": "#d2e4ff",
        "secondary-fixed-dim": "#acc9ef",
        "on-secondary-fixed": "#001d36",
        "on-secondary-fixed-variant": "#2c4869",

        "tertiary": "#1c1200",
        "tertiary-container": "#352600",
        "tertiary-fixed": "#ffdf9d",
        "tertiary-fixed-dim": "#f9bd14",
        "gold": "#F2B705",
        "on-tertiary": "#ffffff",
        "on-tertiary-container": "#b58800",
        "on-tertiary-fixed": "#251a00",
        "on-tertiary-fixed-variant": "#5b4300",

        "surface": "#f9f9ff",
        "surface-dim": "#d3daef",
        "surface-bright": "#f9f9ff",
        "surface-variant": "#dce2f7",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f1f3ff",
        "surface-container": "#e9edff",
        "surface-container-high": "#e1e8fd",
        "surface-container-highest": "#dce2f7",
        "on-surface": "#141b2b",
        "on-surface-variant": "#44474e",

        "background": "#F1F3F5",
        "on-background": "#141b2b",

        "outline": "#74777f",
        "outline-variant": "#c4c6cf",
        "card-border": "#E5E7EB",

        "error": "#ba1a1a",
        "error-container": "#ffdad6",
        "on-error": "#ffffff",
        "on-error-container": "#93000a",

        "green": "#16A34A",
        "red": "#DC2626",
        "amber": "#D97706"
      },
      borderRadius: {
        "DEFAULT": "0.5rem",
        "sm": "0.25rem",
        "md": "0.5rem",
        "lg": "0.75rem",
        "xl": "1rem",
        "2xl": "1.25rem",
        "full": "9999px"
      },
      spacing: {
        "sidebar-width": "260px",
        "container-margin": "24px",
        "gutter": "16px"
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        display: ["Inter", "sans-serif"],
        body: ["Inter", "sans-serif"]
      },
      boxShadow: {
        "level-1": "0px 4px 6px rgba(0, 0, 0, 0.05)",
        "level-2": "0px 10px 15px rgba(0, 0, 0, 0.10)",
        "level-3": "0px 20px 25px -5px rgba(0, 0, 0, 0.15), 0px 10px 10px -5px rgba(0, 0, 0, 0.04)",
        "glow-gold": "0 0 20px rgba(242, 183, 5, 0.25)",
        "glow-blue": "0 0 20px rgba(13, 40, 78, 0.15)"
      }
    }
  }
};
