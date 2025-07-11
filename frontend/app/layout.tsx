import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@/hooks/auth-context';
export const metadata: Metadata = {
  title: 'Futuras Cientistas',
  description: 'CETENE - Futuras Cientistas'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;700&display=swap" rel="stylesheet" />
      </head>
      

      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
