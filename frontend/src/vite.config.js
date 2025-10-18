import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  root: '.', // frontend folder root
  build: {
    outDir: 'dist', // default output folder
  },
});
