import type { Metadata, Viewport } from "next";
import { headers } from "next/headers";
import "./globals.css";

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0A0B0D",
  colorScheme: "dark",
};

const structuredData = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "Polis Protocol",
  applicationCategory: "DeveloperApplication",
  operatingSystem: "Cross-platform",
  softwareVersion: "2.0",
  description:
    "A Git-native coordination protocol for coding agents that stores tasks, routing history, lessons, and decisions in one shared folder.",
  codeRepository: "https://github.com/ymxlx/polis-protocol",
  downloadUrl: "https://pypi.org/project/polis-protocol/",
  license: "https://github.com/ymxlx/polis-protocol/blob/main/LICENSE",
};

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host") ?? "localhost:3000";
  const protocol = requestHeaders.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");
  const origin = `${protocol}://${host}`;

  return {
    metadataBase: new URL(origin),
    title: "Polis Protocol — Git-native coordination for coding agents",
    description:
      "Coordinate Claude Code, Codex, Gemini, Cursor, and other coding agents through one shared Git-native workspace for tasks, routing history, lessons, and decisions.",
    applicationName: "Polis Protocol",
    alternates: { canonical: "/" },
    authors: [{ name: "Polis Protocol contributors", url: "https://github.com/ymxlx/polis-protocol" }],
    keywords: ["coding agents", "multi-agent", "Claude Code", "Codex", "Gemini", "Git", "MCP", "agent coordination"],
    icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
    openGraph: {
      type: "website",
      url: origin,
      siteName: "Polis Protocol",
      title: "Polis Protocol — Git-native coordination for coding agents",
      description: "One shared Git-native workspace for tasks, routing history, lessons, and decisions across coding-agent vendors.",
      images: [{ url: `${origin}/og.png`, width: 1536, height: 1024, alt: "Polis Protocol — Git-native coordination for coding agents" }],
    },
    twitter: {
      card: "summary_large_image",
      title: "Polis Protocol — Git-native coordination for coding agents",
      description: "One shared Git-native workspace for tasks, routing history, lessons, and decisions across coding-agent vendors.",
      images: [`${origin}/og.png`],
    },
  };
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData).replace(/</g, "\\u003c") }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
