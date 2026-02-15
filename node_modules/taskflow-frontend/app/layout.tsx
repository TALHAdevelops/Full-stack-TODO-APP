import type { Metadata } from "next";
import "./globals.css";
import { WebSocketProvider } from "@/components/realtime/WebSocketProvider";

export const metadata: Metadata = {
  title: "TaskFlow | Phase 5",
  description: "Secure Full-Stack Task Management with Real-Time Sync",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className="antialiased bg-background text-foreground min-h-screen"
        suppressHydrationWarning
      >
        <WebSocketProvider>
          {children}
        </WebSocketProvider>
      </body>
    </html>
  );
}
