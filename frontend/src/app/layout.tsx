import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FinBot BD — Bangladesh Banking Assistant",
  description: "Bilingual hybrid RAG banking assistant for bKash, Nagad, and DBBL",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="bn" className="dark">
      <body className={inter.className}>{children}</body>
    </html>
  );
}