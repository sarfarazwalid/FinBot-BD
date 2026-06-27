import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinBot BD — Banking Intelligence",
  description:
    "Enterprise-grade hybrid RAG banking assistant for bKash, Nagad, and DBBL.",
  keywords: [
    "bKash",
    "Nagad",
    "DBBL",
    "Bangladesh banking",
    "fintech",
    "RAG",
    "AI assistant",
  ],
  openGraph: {
    title: "FinBot BD — Banking Intelligence",
    description:
      "Enterprise-grade hybrid RAG banking assistant for bKash, Nagad, and DBBL.",
    type: "website",
    locale: "bn_BD",
    siteName: "FinBot BD",
  },
  twitter: {
    card: "summary_large_image",
    title: "FinBot BD — Banking Intelligence",
    description:
      "Enterprise-grade hybrid RAG banking assistant for bKash, Nagad, and DBBL.",
  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="bn" className="dark" suppressHydrationWarning>
      <head>
        {/* Preload Satoshi and Noto Sans Bengali */}
        <link rel="preconnect" href="https://api.fontshare.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://fonts.googleapis.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="preload"
          as="style"
          href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,600,700&display=swap"
        />
        <link
          rel="preload"
          as="style"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;700&display=swap"
        />
      </head>
      <body className="antialiased bg-bg text-text min-h-screen overflow-hidden">
        {children}
      </body>
    </html>
  );
}