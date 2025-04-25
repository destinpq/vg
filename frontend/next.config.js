/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // Optimizes for container deployments
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: [
      'localhost', 
      'video-generator-api.ondigitalocean.app',
      // Add any other domains you need to load images from
    ],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    // Enable modern features if needed
    serverActions: true,
  },
  // Configure build-time environment variables
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  },
}

module.exports = nextConfig 