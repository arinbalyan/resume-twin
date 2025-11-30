import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  const isProduction = mode === 'production'

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      port: 3000,
      host: true,
      // Proxy only works in development - in production, API calls go directly to backend
      proxy: isProduction ? undefined : {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path: string) => path.replace(/^\/api/, '/api'),
        },
      },
    },
    build: {
      outDir: 'dist',
      // Disable sourcemaps in production for smaller bundle
      sourcemap: !isProduction,
      // Use esbuild for minification (faster and included by default)
      minify: 'esbuild',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom'],
            ui: ['@headlessui/react', '@heroicons/react'],
            query: ['@tanstack/react-query'],
          },
        },
      },
      // Increase chunk size warning limit
      chunkSizeWarningLimit: 1000,
    },
    define: {
      global: 'globalThis',
    },
    // Preview server config (for testing production build locally)
    preview: {
      port: 3000,
      host: true,
    },
  }
})