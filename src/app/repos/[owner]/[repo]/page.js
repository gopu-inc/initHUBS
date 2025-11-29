'use client'
import { useEffect, useState } from 'react'
import { useAuth } from '../../../../lib/auth'
import { useRouter, useParams } from 'next/navigation'
import Header from '../../../../components/Header'
import Sidebar from '../../../../components/Sidebar'
import { Code, GitBranch, Star, GitFork, Eye, Download } from 'lucide-react'

export default function RepoDetailPage() {
  const { user, token } = useAuth()
  const router = useRouter()
  const params = useParams()
  const [repo, setRepo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      router.push('/')
      return
    }

    // Données simulées pour le détail du repo
    setTimeout(() => {
      setRepo({
        id: 1,
        name: params.repo,
        full_name: `${params.owner}/${params.repo}`,
        description: 'Description détaillée du repository avec toutes les informations importantes sur le projet et ses fonctionnalités.',
        is_private: false,
        stars_count: 15,
        forks_count: 3,
        watchers_count: 8,
        default_branch: 'main',
        language: 'JavaScript',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      setLoading(false)
    }, 1000)
  }, [user, router, params])

  if (!user) return null

  return (
    <div className="min-h-screen bg-github-dark">
      <Header />
      <div className="flex">
        <Sidebar />
        
        <main className="flex-1">
          {loading ? (
            <div className="p-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            </div>
          ) : repo ? (
            <>
              {/* Header du repo */}
              <div className="border-b border-github-border bg-github-gray">
                <div className="max-w-7xl mx-auto px-8 py-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h1 className="text-2xl font-bold text-white">
                        {repo.name}
                      </h1>
                      <p className="text-gray-400 mt-1">
                        {repo.description}
                      </p>
                    </div>
                    
                    <div className="flex space-x-4">
                      <button className="btn-secondary flex items-center">
                        <Eye size={16} className="mr-2" />
                        Watch {repo.watchers_count}
                      </button>
                      <button className="btn-secondary flex items-center">
                        <Star size={16} className="mr-2" />
                        Star {repo.stars_count}
                      </button>
                      <button className="btn-secondary flex items-center">
                        <GitFork size={16} className="mr-2" />
                        Fork {repo.forks_count}
                      </button>
                    </div>
                  </div>
                  
                  {/* Navigation du repo */}
                  <nav className="mt-6 flex space-x-8">
                    {['Code', 'Issues', 'Pull Requests', 'Actions', 'Projects', 'Wiki', 'Security', 'Insights'].map((item) => (
                      <button
                        key={item}
                        className="pb-2 px-1 border-b-2 border-transparent hover:border-gray-300 text-gray-400 hover:text-white transition-colors"
                      >
                        {item}
                      </button>
                    ))}
                  </nav>
                </div>
              </div>

              {/* Contenu du repo */}
              <div className="max-w-7xl mx-auto p-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* Colonne principale */}
                  <div className="lg:col-span-2 space-y-6">
                    {/* Readme */}
                    <div className="github-card">
                      <div className="border-b border-github-border pb-4 mb-4">
                        <h2 className="text-xl font-semibold text-white">
                          README.md
