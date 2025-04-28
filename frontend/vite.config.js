import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // Добавляем, если используем alias

export default defineConfig({
	plugins: [react()],
	server: {
		host: '0.0.0.0',
		port: 3000,
		proxy: {
			'/api': {
				target: 'http://backend:8000',
				changeOrigin: true,
				rewrite: path => path.replace(/^\/api/, ''),
			},
		},
	},
	optimizeDeps: {
		include: ['react-router-dom'], // Предварительно бандлит react-router-dom
	},
	resolve: {
		alias: {
			// Если другие импорты не разрешаются, можно добавить:
			'react-router-dom': path.resolve(__dirname, 'node_modules/react-router-dom'),
		},
	},
})
