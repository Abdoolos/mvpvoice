import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Sidebar } from '../components/layout/Sidebar'
import { Header } from '../components/layout/Header'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Callcenter Agent',
  description: 'AI-drevet analyse av telefonsamtaler for norsk telekom-salg',
  keywords: ['AI', 'callcenter', 'Norge', 'telecom', 'analyse', 'GDPR'],
  authors: [{ name: 'AI Team' }],
  creator: 'AI Team',
  publisher: 'AI Team',
  robots: 'index, follow',
  manifest: '/manifest.json',
  icons: {
    icon: [
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  },
  openGraph: {
    type: 'website',
    locale: 'nb_NO',
    title: 'AI Callcenter Agent',
    description: 'AI-drevet analyse av telefonsamtaler for norsk telekom-salg',
    siteName: 'AI Callcenter Agent',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Callcenter Agent',
    description: 'AI-drevet analyse av telefonsamtaler for norsk telekom-salg',
    creator: '@aiteam',
  },
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="no" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>
      <body className={`${inter.className} antialiased`}>
        <Providers>
          <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
            {/* Sidebar */}
            <div className="hidden md:flex md:w-64 md:flex-col">
              <Sidebar />
            </div>

            {/* Main content area */}
            <div className="flex flex-1 flex-col overflow-hidden">
              {/* Header */}
              <Header />

              {/* Main content */}
              <main className="flex-1 overflow-y-auto">
                <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                  {children}
                </div>
              </main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  )
}
