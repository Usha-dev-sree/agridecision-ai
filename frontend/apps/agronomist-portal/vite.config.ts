import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api/auth': { target: 'http://localhost:8000', changeOrigin: true, rewrite: (p) => p.replace(/^\/api\/auth/, '') },
      '/api/farm': { target: 'http://localhost:8001', changeOrigin: true, rewrite: (p) => p.replace(/^\/api\/farm/, '') },
      '/api/advisory': { target: 'http://localhost:8002', changeOrigin: true, rewrite: (p) => p.replace(/^\/api\/advisory/, '') },
      '/api/market': { target: 'http://localhost:8003', changeOrigin: true, rewrite: (p) => p.replace(/^\/api\/market/, '') },
      '/api/weather': { target: 'http://localhost:8004', changeOrigin: true, rewrite: (p) => p.replace(/^\/api\/weather/, '') },
      '/api/ai': { target: 'http://localhost:8080', changeOrigin: true, rewrite: (p) => p.replace(/^\/api\/ai/, '') },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          mui: ['@mui/material', '@mui/icons-material'],
          charts: ['chart.js', 'react-chartjs-2', 'recharts'],
          maps: ['leaflet', 'react-leaflet'],
          redux: ['@reduxjs/toolkit', 'react-redux'],
          query: ['@tanstack/react-query'],
        },
      },
    },
  },
})
