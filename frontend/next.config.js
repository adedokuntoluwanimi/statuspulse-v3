/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  async rewrites() {
    const target = process.env.NEXT_PUBLIC_API_URL ?? "http://backend:8000";
    return [{ source: "/api/:path*", destination: `${target}/:path*` }];
  },
};

module.exports = nextConfig;

