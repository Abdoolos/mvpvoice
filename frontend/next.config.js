/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_APP_NAME: 'AI Callcenter Agent',
    NEXT_PUBLIC_DESIGNER: 'Abdullah Alawiss',
  },
  // Ensure CSS processing works correctly
  experimental: {
    optimizeCss: true,
  },
  // Webpack configuration to handle PostCSS properly
  webpack: (config, { dev, isServer }) => {
    // Ensure autoprefixer and postcss are loaded correctly
    if (!dev && !isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
      }
    }
    return config
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
