/** @type {import('next').NextConfig} */
const nextConfig = {
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
  // Configure build-time environment variables
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  },
}

module.exports = nextConfig 