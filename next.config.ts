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
        destination: "http://localhost:5328/api/:path*", // For HTTPS SSL is required
      },
    ]
  },
  
  // Configuración de imágenes para permitir dominios externos
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5328',
        pathname: '/static/**',
      },
    ],
  }
};

export default nextConfig;
