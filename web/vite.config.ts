import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const target = `http://127.0.0.1:${process.env.PORT ?? 8765}`;
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": target, "/media": target, "/course-files": target, "/workspace": target,
      "/ws": { target: target.replace("http", "ws"), ws: true },
    },
  },
  build: { outDir: "dist", emptyOutDir: true },
});
