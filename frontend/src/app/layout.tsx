import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinBot BD — Premium Banking Assistant",
  description:
    "Hybrid RAG-powered banking assistant for bKash, Nagad, and DBBL. Get intelligent answers in Bengali, English, and Banglish.",
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
    title: "FinBot BD — Premium Banking Assistant",
    description:
      "Hybrid RAG-powered banking assistant for bKash, Nagad, and DBBL.",
    type: "website",
    locale: "bn_BD",
    siteName: "FinBot BD",
  },
  twitter: {
    card: "summary_large_image",
    title: "FinBot BD — Premium Banking Assistant",
    description:
      "Hybrid RAG-powered banking assistant for bKash, Nagad, and DBBL.",
  },
  robots: {
    index: true,
    follow: true,
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
      <body className="antialiased bg-background text-foreground min-h-screen overflow-hidden">
        {children}
      </body>
    </html>
  );
}