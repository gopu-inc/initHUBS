'use client'
import { useEffect, useState } from 'react'
import { useAuth } from '../../lib/auth'
import { useRouter } from 'next/navigation'
import Header from '../../components/Header'
import Sidebar from '../../components/Sidebar'
import RepositoryCard from '../../components/RepositoryCard'
import { Plus, Search, Filter } from 'lucide-react'

export default function ReposPage() {
  const { user, token } = useAuth()
  const router = useRouter()
  const [repos, setRepos] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (!user) {
      router.push('/')
      return
    }
    fetchRepositories()
  }, [user, router])

  const fetchRepositories = async () => {
    try {
      // Simuler le chargement des repositories
      // Dans une vraie implémentation, vous appelleriez votre API
      setTimeout(() => {
        setRepos([
          {
            id: 1,
            name: 'mon-projet',
            full_name: `${user.username}/mon-projet`,
            description: 'Mon premier projet sur initHUB',
            is_private: false,
            stars_count: 5,
            forks_count: 2,
            updated_at: new Date().toISOString()
          },
          {
            id: 2,
            name: 'api-backend',
            full_name: `${user.username}/api-backend`,
            description: 'Backend API en Node.js',
            is_private: true,
            stars_count: 3,
            forks_count: 1,
            updated_at: new Date().toISOString()
          }
        ])
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Erreur chargement repositories:', error)
      setLoading(false)
    }
  }

  const filteredRepos = repos.filter(repo =>
    repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    repo.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (!user) return null

  return (
    <div className="min-h-screen bg-github-dark">
      <Header />
      <div className="flex">
        <Sidebar />
        
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-3xl font-bold text-white">Repositories</h1>
                <p className="text-gray-400 mt-2">
                  Gérez vos dépôts de code
                </p>
              </div>
              
              <button className="btn-primary flex items-center">
                <Plus size={20} className="mr-2" />
                Nouveau repository
              </button>
            </div>

            {/* Barre de recherche et filtres */}
            <div className="github-card mb-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    placeholder="Rechercher un repository..."
                    className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-github-border rounded-md text-white"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                
                <select className="px-4 py-2 bg-gray-800 border border-github-border rounded-md text-white">
                  <option value="all">Tous les types</option>
                  <option value="public">Public</option>
                  <option value="private">Privé</option>
                </select>
                
                <select className="px-4 py-2 bg-gray-800 border border-github-border rounded-md text-white">
                  <option value="updated">Dernière mise à jour</option>
                  <option value="name">Nom</option>
                  <option value="stars">Étoiles</option>
                </select>
              </div>
            </div>

            {/* Liste des repositories */}
            {loading ? (
              <div className="github-card text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-gray-400 mt-4">Chargement des repositories...</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {filteredRepos.map((repo) => (
                  <RepositoryCard key={repo.id} repo={repo} />
                ))}
                
                {filteredRepos.length === 0 && (
                  <div className="github-card text-center py-12">
                    <p className="text-gray-400 text-lg">
                      {searchTerm ? 'Aucun repository trouvé' : 'Aucun repository'}
                    </p>
                    {!searchTerm && (
                      <button className="btn-primary mt-4">
                        <Plus size={20} className="mr-2" />
                        Créer votre premier repository
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
