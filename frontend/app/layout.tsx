import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Luminark - System Assessment',
  description: 'The Antikythera Engine for Self-Understanding',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
