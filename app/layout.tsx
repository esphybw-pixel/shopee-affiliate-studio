import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Shopee Affiliate Intelligence Studio",
  description: "วิเคราะห์สินค้า วางกลยุทธ์ และผลิตคอนเทนต์ Shopee Affiliate ด้วย AI",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th">
      <body className="antialiased">{children}</body>
    </html>
  );
}
