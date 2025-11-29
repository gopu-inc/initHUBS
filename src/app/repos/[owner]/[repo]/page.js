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
                        </h2>
                      </div>
                      <div className="prose prose-invert max-w-none">
                        <h1 className="text-2xl font-bold text-white">{repo.name}</h1>
                        <p className="text-gray-300">{repo.description}</p>
                        
                        <h2 className="text-xl font-semibold text-white mt-6">Installation</h2>
                        <pre className="bg-gray-800 p-4 rounded text-gray-300">
                          <code>git clone https://inithub.com/{repo.full_name}.git</code>
                        </pre>
                        
                        <h2 className="text-xl font-semibold text-white mt-6">Utilisation</h2>
                        <p className="text-gray-300">
                          Instructions d'utilisation du projet. Vous pouvez configurer l'environnement de développement et lancer l'application.
                        </p>
                      </div>
                    </div>

                    {/* Dernier commit */}
                    <div className="github-card">
                      <h3 className="text-lg font-semibold text-white mb-4">
                        Dernier commit
                      </h3>
                      <div className="flex items-center space-x-3 p-3 bg-gray-800 rounded">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-sm">U</span>
                        </div>
                        <div>
                          <p className="text-white text-sm">Initial commit - Setup project structure</p>
                          <p className="text-gray-400 text-xs">
                            {user.username} • {new Date(repo.created_at).toLocaleDateString('fr-FR')}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Sidebar */}
                  <div className="space-y-6">
                    {/* À propos */}
                    <div className="github-card">
                      <h3 className="text-lg font-semibold text-white mb-4">
                        À propos
                      </h3>
                      <p className="text-gray-400 text-sm mb-4">
                        {repo.description}
                      </p>
                      
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Créé le</span>
                          <span className="text-white">
                            {new Date(repo.created_at).toLocaleDateString('fr-FR')}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Dernière mise à jour</span>
                          <span className="text-white">
                            {new Date(repo.updated_at).toLocaleDateString('fr-FR')}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Branche par défaut</span>
                          <span className="text-white">{repo.default_branch}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Langage principal</span>
                          <span className="text-white">{repo.language}</span>
                        </div>
                      </div>
                    </div>

                    {/* Releases */}
                    <div className="github-card">
                      <h3 className="text-lg font-semibold text-white mb-4">
                        Releases
                      </h3>
                      <div className="text-center py-4">
                        <Download className="mx-auto text-gray-400 mb-2" size={24} />
                        <p className="text-gray-400 text-sm">
                          Aucune release publiée
                        </p>
                        <button className="btn-primary mt-2 text-sm">
                          Créer une release
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="p-8 text-center">
              <p className="text-gray-400">Repository non trouvé</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
