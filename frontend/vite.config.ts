import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // server: {          // ← comment hết block này
  //   proxy: {
  //     "/api": "http://localhost:8000",
  //   },
  // },
});