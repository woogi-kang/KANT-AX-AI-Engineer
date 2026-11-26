import type { NextConfig } from "next";

// 정적 파일만 만들어 Cloudflare Pages에 올려요. 서버는 없어요.
const config: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  reactStrictMode: true,
};

export default config;
