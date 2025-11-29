'use client'
import { useEffect, useState } from 'react'
import { useAuth } from '../../lib/auth'
import { useRouter } from 'next/navigation'
import Header from '../../components/Header'
import Sidebar from '../../components/Sidebar'
import { Download, Tag, Calendar, User } from 'lucide-react'

export default function ReleasesPage() {
  const { user, token } = useAuth()
  const router = useRouter()
  const [releases, setReleases] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      router.push('/')
      return
    }
    fetchReleases()
  }, [user, router])

  const fetchReleases = async () => {
    try {
      // Simuler le chargement des releases
      setTimeout(() => {
        setReleases([
          {
            id: 1,
            tag_name: 'v1.0.0',
            name: 'Version 1.0.0',
            body: 'Première release stable',
            author: { username: user.username },
            created_at: new Date().toISOString(),
            prerelease: false,
            draft: false,
            assets: []
          },
          {
            id: 2,
            tag_name: 'v0.9.0',
            name: 'Version Beta',
            body: 'Version bêta de test',
            author: { username: user.username },
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            prerelease: true,
            draft: false,
            assets: []
          }
        ])
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Erreur chargement releases:', error)
      setLoading(false)
    }
  }

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
                <h1 className="text-3xl font-bold text-white">Releases</h1>
                <p className="text-gray-400 mt-2">
                  Gérez les releases de vos projets
                </p>
              </div>
              
              <button className="btn-primary flex items-center">
                <Tag size={20} className="mr-2" />
                Nouvelle release
              </button>
            </div>

            {loading ? (
              <div className="github-card text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-gray-400 mt-4">Chargement des releases...</p>
              </div>
            ) : (
              <div className="space-y-6">
                {releases.map((release) => (
                  <div key={release.id} className="github-card">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center space-x-3 mb-2">
                          <Tag className="text-blue-400" size={20} />
                          <h2 className="text-xl font-bold text-white">
                            {release.name}
                          </h2>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            release.prerelease 
                              ? 'bg-yellow-500 text-white' 
                              : release.draft
                              ? 'bg-gray-500 text-white'
                              : 'bg-green-500 text-white'
                          }`}>
                            {release.prerelease ? 'Pre-release' : release.draft ? 'Draft' : 'Latest'}
                          </span>
                        </div>
                        <p className="text-gray-400 text-sm">
                          {release.tag_name} • Publié le {' '}
                          {new Date(release.created_at).toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                      
                      <button className="btn-secondary flex items-center text-sm">
                        <Download size={16} className="mr-2" />
                        Télécharger
                      </button>
                    </div>
                    
                    <div className="prose prose-invert max-w-none mb-4">
                      <p>{release.body}</p>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-400">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center">
                          <User size={16} className="mr-1" />
                          Par {release.author.username}
                        </div>
                        <div className="flex items-center">
                          <Calendar size={16} className="mr-1" />
                          {new Date(release.created_at).toLocaleDateString('fr-FR')}
                        </div>
                      </div>
                      
                      <div className="flex space-x-3">
                        <button className="text-blue-400 hover:text-blue-300">
                          Éditer
                        </button>
                        <button className="text-red-400 hover:text-red-300">
                          Supprimer
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {releases.length === 0 && (
                  <div className="github-card text-center py-12">
                    <Download className="mx-auto text-gray-400 mb-4" size={48} />
                    <h3 className="text-xl font-semibold text-white mb-2">
                      Aucune release
                    </h3>
                    <p className="text-gray-400 mb-6">
                      Créez votre première release pour distribuer votre projet
                    </p>
                    <button className="btn-primary">
                      <Tag size={20} className="mr-2" />
                      Créer une release
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
