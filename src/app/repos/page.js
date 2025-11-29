'use client'
import { useEffect, useState } from 'react'
import { useAuth } from '../../lib/auth'
import { useRouter } from 'next/navigation'
import Header from '../../components/Header'
import Sidebar from '../../components/Sidebar'
import RepositoryCard from '../../components/RepositoryCard'
import { Plus, Search } from 'lucide-react'

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

    // Données simulées pour les repositories
    setTimeout(() => {
      setRepos([
        {
          id: 1,
          name: 'mon-projet',
          full_name: `${user.username}/mon-projet`,
          description: 'Mon premier projet sur initHUB avec une description plus longue pour tester',
          is_private: false,
          stars_count: 5,
          forks_count: 2,
          language: 'JavaScript',
          updated_at: new Date().toISOString()
        },
        {
          id: 2,
          name: 'api-backend',
          full_name: `${user.username}/api-backend`,
          description: 'Backend API en Node.js avec Express et MongoDB',
          is_private: true,
          stars_count: 3,
          forks_count: 1,
          language: 'Python',
          updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 3,
          name: 'frontend-app',
          full_name: `${user.username}/frontend-app`,
          description: 'Application React avec Tailwind CSS',
          is_private: false,
          stars_count: 8,
          forks_count: 4,
          language: 'TypeScript',
          updated_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
        }
      ])
      setLoading(false)
    }, 1000)
  }, [user, router])

  const filteredRepos = repos.filter(repo =>
    repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (repo.description && repo.description.toLowerCase().includes(searchTerm.toLowerCase()))
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

            {/* Barre de recherche */}
            <div className="github-card mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Rechercher un repository..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-github-border rounded-md text-white"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
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
                  <div
