'use client'
import { useAuth } from '../lib/auth'
import { LogOut, User, Settings } from 'lucide-react'

export default function Header() {
  const { user, logout } = useAuth()

  return (
    <header className="bg-github-gray border-b border-github-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-white">
                🚀 initHUB Cloud
              </h1>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {user && (
              <>
                <span className="text-sm text-gray-300">
                  Bienvenue, {user.username}
                </span>
                <button className="p-2 text-gray-400 hover:text-white transition-colors">
                  <User size={20} />
                </button>
                <button className="p-2 text-gray-400 hover:text-white transition-colors">
                  <Settings size={20} />
                </button>
                <button
                  onClick={logout}
                  className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                >
                  <LogOut size={20} />
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
