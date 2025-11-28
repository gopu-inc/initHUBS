import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '../lib/auth'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'initHUB Cloud Enterprise',
  description: 'Plateforme cloud complète avec Copilot, Dashboard, Releases et Analytics',
}

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
