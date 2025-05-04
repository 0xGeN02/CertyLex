import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { Toaster } from "sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CertyLex",
  description: "Next-Gen AI Agent for Legal Research",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-50 flex flex-col min-h-screen`}
      >
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <div className="flex-shrink-0 flex items-center">
                  <span className="text-xl font-bold text-indigo-600">CertyLex</span>
                  <span className="ml-2 text-xs bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full">AI Legal Assistant</span>
                </div>
                <nav className="hidden md:ml-8 md:flex md:space-x-8">
                  <Link href="/" className="border-indigo-500 text-gray-900 hover:border-indigo-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Chat General
                  </Link>
                  <Link href="/pdf-analysis" className="border-transparent text-gray-500 hover:border-indigo-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Análisis de Documentos
                  </Link>
                  <Link href="/imagen-enhancer" className="border-transparent text-gray-500 hover:border-indigo-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    Mejora de Imágenes
                  </Link>
                </nav>
              </div>
              <div className="hidden md:flex md:items-center">
                <span className="inline-flex rounded-md shadow-sm">
                  <Link href="/pdf-analysis" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                    Analizar PDF
                  </Link>
                </span>
              </div>
            </div>
          </div>
        </header>
        <main className="flex-grow">
          {children}
        </main>
        <footer className="bg-white border-t border-gray-200 py-3">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p className="text-center text-sm text-gray-500">© {new Date().getFullYear()} CertyLex. All rights reserved.</p>
          </div>
        </footer>
        <Toaster position="top-center" richColors />
      </body>
    </html>
  );
}