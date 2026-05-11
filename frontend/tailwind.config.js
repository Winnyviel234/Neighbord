/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        neighbor: {
          navy: '#062b5f',
          blue: '#1469b8',
          sky: '#38a7e8',
          green: '#2f9b2e',
          leaf: '#86c45f',
          mist: '#eef7fb'
        }
      },
      boxShadow: {
        soft: '0 18px 45px rgba(6, 43, 95, 0.10)'
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-in': 'bounceIn 0.5s ease-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' }
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' }
        }
      }
    }
  },
  plugins: [
    // Plugin para formas personalizadas
    function({ addUtilities }) {
      addUtilities({
        '.text-balance': {
          'text-wrap': 'balance'
        },
        '.scrollbar-hide': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
          '&::-webkit-scrollbar': {
            display: 'none'
          }
        }
      });
    }
  ],
  // Optimizaciones de producción
  future: {
    hoverOnlyWhenSupported: true
  },
  experimental: {
    optimizeUniversalDefaults: true
  }
};
