'use client'
import { useEffect } from 'react'
import { useAuth } from '../../lib/auth'
import { useRouter } from 'next/navigation'

export default function Dashboard() {
  const { user } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!user) {
      router.push('/')
      return
    }
  }, [user, router])

  if (!user) {
    return (
      <div className="min-h-screen bg-github-dark flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Redirection...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-github-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="github-card">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-blue-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 6a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6Z"/>
                  <path d="M2 12h20"/>
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-300">Repositories</p>
                <p className="text-2xl font-bold text-white">12</p>
              </div>
            </div>
          </div>
          
          <div className="github-card">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-yellow-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-300">Stars</p>
                <p className="text-2xl font-bold text-white">45</p>
              </div>
            </div>
          </div>
          
          <div className="github-card">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-green-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m15 18-6-6 6-6"/>
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-300">Forks</p>
                <p className="text-2xl font-bold text-white">8</p>
              </div>
            </div>
          </div>
          
          <div className="github-card">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-purple-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-300">Contributeurs</p>
                <p className="text-2xl font-bold text-white">5</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
