export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    // Solo aplicar cssnano en producción para optimización
    ...(process.env.NODE_ENV === 'production' ? {
      cssnano: {
        preset: ['default', {
          discardComments: { removeAll: true },
          normalizeWhitespace: false // Mantener legibilidad en desarrollo
        }]
      }
    } : {})
  }
};

