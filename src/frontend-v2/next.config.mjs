/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ["res.cloudinary.com"],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
      },
      {
        protocol: 'https',
        hostname: '**', 
      },
      {
        protocol: 'http',
        hostname: '**', 
      },
    ],
  },
};

export default nextConfig;
