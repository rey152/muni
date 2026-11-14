import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  vite: {
    // MapLibre is about 1 MB and only loads on /near-me/, so its size warning is expected.
    build: { chunkSizeWarningLimit: 1200 },
  },
});
