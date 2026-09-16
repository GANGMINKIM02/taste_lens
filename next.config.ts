import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  images: {
    // Production images are pre-generated and served from Supabase Storage.
    // Runtime image generation is intentionally not part of Taste Lens.
    remotePatterns: [{ protocol: 'https', hostname: '**' }]
  }
};
export default nextConfig;
