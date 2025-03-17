import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        // Rewrite for Next.js API routes (under app/api)
        source: "/app/api/:path*",
        destination: "https://localhost:3000/api/:path*",
      },
      {
        // Rewrite for FastAPI backend routes (under backend/api)
        source: "/backend/api/:path*",
        destination: "https://localhost:5328/api/:path*",
      },
    ]
  }
  
};

export default nextConfig;
