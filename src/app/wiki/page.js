'use client'
import { useEffect, useState } from 'react'
import { useAuth } from '../../lib/auth'
import { useRouter } from 'next/navigation'
import Header from '../../components/Header'
import Sidebar from '../../components/Sidebar'
import { BookOpen, Plus, Edit, Search } from 'lucide-react'

export default function WikiPage() {
  const { user, token } = useAuth()
  const router = useRouter()
  const [pages, setPages] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (!user) {
      router.push('/')
      return
    }
    fetchWikiPages()
  }, [user, router])

  const fetchWikiPages = async () => {
    try {
      // Simuler le chargement des pages wiki
      setTimeout(() => {
        setPages([
          {
            id: 1,
            title: 'Accueil',
            content: 'Bienvenue dans la documentation du projet...',
            author: { username: user.username },
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 2,
            title: 'Installation',
            content: 'Guide d installation du projet...',
            author: { username: user.username },
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 3,
            title: 'API Reference',
            content: 'Documentation de l API...',
            author: { username: user.username },
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        ])
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Erreur chargement wiki:', error)
      setLoading(false)
    }
  }

  const filteredPages = pages.filter(page =>
    page.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    page.content.toLowerCase().includes(searchTerm.toLowerCase())
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
                <h1 className="text-3xl font-bold text-white">Wiki</h1>
                <p className="text-gray-400 mt-2">
                  Documentation de vos projets
                </p>
              </div>
              
              <button className="btn-primary flex items-center">
                <Plus size={20} className="mr-2" />
                Nouvelle page
              </button>
            </div>

            {/* Barre de recherche */}
            <div className="github-card mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Rechercher dans le wiki..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-github-border rounded-md text-white"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {loading ? (
              <div className="github-card text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-gray-400 mt-4">Chargement du wiki...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredPages.map((page) => (
                  <div key={page.id} className="github-card hover:border-gray-500 transition-colors cursor-pointer">
                    <div className="flex items-start justify-between mb-4">
                      <BookOpen className="text-blue-400 flex-shrink-0 mt-1" size={20} />
                      <button className="text-gray-400 hover:text-white">
                        <Edit size={16} />
                      </button>
                    </div>
                    
                    <h3 className="text-lg font-semibold text-white mb-2">
                      {page.title}
                    </h3>
                    
                    <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                      {page.content.substring(0, 100)}...
                    </p>
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Par {page.author.username}</span>
                      <span>
                        {new Date(page.updated_at).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                  </div>
                ))}
                
                {filteredPages.length === 0 && (
                  <div className="col-span-full github-card text-center py-12">
                    <BookOpen className="mx-auto text-gray-400 mb-4" size={48} />
                    <h3 className="text-xl font-semibold text-white mb-2">
                      {searchTerm ? 'Aucune page trouvée' : 'Aucune page wiki'}
                    </h3>
                    <p className="text-gray-400 mb-6">
                      {searchTerm 
                        ? 'Essayez avec d autres termes de recherche'
                        : 'Créez votre première page de documentation'
                      }
                    </p>
                    <button className="btn-primary">
                      <Plus size={20} className="mr-2" />
                      Créer une page
                    </button>
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
