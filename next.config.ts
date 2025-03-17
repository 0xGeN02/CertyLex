import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: "/api/flask/:path*",
        destination: "https://localhost:5000/:path*",
      },
    ]
  }
  
};

export default nextConfig;
