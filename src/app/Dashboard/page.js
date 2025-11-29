'use client'
import { useEffect, useState } from 'react'
import { useAuth } from '../../lib/auth'
import { useRouter } from 'next/navigation'
import Header from '../../components/Header'
import Sidebar from '../../components/Sidebar'
import StatsCard from '../../components/StatsCard'
import { GitBranch, Star, GitFork, Users, Activity } from 'lucide-react'

export default function Dashboard() {
  const { user, token } = useAuth()
  const router = useRouter()
  const [stats, setStats] = useState(null)
  const [recentActivity, setRecentActivity] = useState([])

  useEffect(() => {
    if (!user) {
      router.push('/')
      return
    }

    setStats({
      total_repos: 12,
      total_stars: 45,
      total_forks: 8,
      total_contributors: 5
    })

    setRecentActivity([
      {
        type: 'repo',
        title: 'mon-projet',
        date: new Date().toISOString(),
        description: 'Repository créé'
      },
      {
        type: 'commit',
        title: 'Initial commit',
        date: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        description: 'Commit pushed'
      },
      {
        type: 'pr',
        title: 'Add new feature',
        date: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
        description: 'Pull request opened'
      }
    ])
  }, [user, router])

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-github-dark">
      <Header />
      <div className="flex">
        <Sidebar />
        
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold text-white mb-8">
              Dashboard
            </h1>

            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatsCard
                  title="Repositories"
                  value={stats.total_repos}
                  icon={<GitBranch size={24} />}
                  color="blue"
                />
                <StatsCard
                  title="Stars"
                  value={stats.total_stars}
                  icon={<Star size={24} />}
                  color="yellow"
                />
                <StatsCard
                  title="Forks"
                  value={stats.total_forks}
                  icon={<GitFork size={24} />}
                  color="green"
                />
                <StatsCard
                  title="Contributeurs"
                  value={stats.total_contributors}
                  icon={<Users size={24} />}
                  color="purple"
                />
              </div>
            )}

            <div className="github-card">
              <h2 className="text-xl font-bold text-white mb-4">
                Activité récente
              </h2>
              <div className="space-y-3">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-gray-800 rounded-lg">
                    <Activity size={16} className="text-gray-400" />
                    <div>
                      <p className="text-white text-sm">{activity.description}</p>
                      <p className="text-gray-400 text-xs">
                        {new Date(activity.date).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
