import React from 'react';
import '../styles/globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Video Generation App',
  description: 'Generate videos from lyrics and audio',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main className="main-container">
          <header className="site-header">
            <div className="container header-content">
              <h1 className="site-title">Video Generator</h1>
              <nav>
                <ul className="nav-list">
                  <li><a href="/" className="nav-link">Home</a></li>
                  <li><a href="/generate" className="nav-link">Generate</a></li>
                </ul>
              </nav>
            </div>
          </header>
          <div className="content-area container">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
} 