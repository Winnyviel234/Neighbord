import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react()
  ],
  server: {
    port: 5173,
    host: true, // Permite conexiones desde cualquier IP
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Backend en puerto 8000
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path
      }
    }
  },
  build: {
    // Optimizaciones de build
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: false, // Deshabilitar en producción para mejor performance
    rollupOptions: {
      output: {
        // Separar chunks por funcionalidad
        manualChunks: {
          router: ['react-router-dom'],
          ui: ['lucide-react'],
          utils: ['axios']
        }
      }
    },
    // Compresión
    reportCompressedSize: false, // No reportar tamaños comprimidos en build
    chunkSizeWarningLimit: 1000 // Advertir si chunks > 1000kb
  },
  optimizeDeps: {
    // Pre-bundle dependencies
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      'lucide-react'
    ]
  },
  // Configuración de CSS
  css: {
    devSourcemap: true
  }
});
