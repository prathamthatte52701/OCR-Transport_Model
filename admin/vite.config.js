import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 4000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:2000',
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 4000,
    strictPort: true,
    host: '127.0.0.1',
  },
})
