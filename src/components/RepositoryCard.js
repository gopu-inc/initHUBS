'use client'
import { useRouter } from 'next/navigation'
import { Star, GitFork, Lock, Globe } from 'lucide-react'

export default function RepositoryCard({ repo }) {
  const router = useRouter()

  const handleClick = () => {
    router.push(`/repos/${repo.full_name}`)
  }

  return (
    <div 
      className="github-card hover:border-gray-500 transition-colors cursor-pointer"
      onClick={handleClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <h3 className="text-xl font-semibold text-blue-400">
            {repo.name}
          </h3>
          {repo.is_private ? (
            <Lock size={16} className="text-gray-400" />
          ) : (
            <Globe size={16} className="text-gray-400" />
          )}
        </div>
        
        <button className="btn-secondary text-sm">
          <Star size={16} className="mr-1" />
          Star
        </button>
      </div>
      
      <p className="text-gray-400 mb-4 line-clamp-2">
        {repo.description || 'Aucune description'}
      </p>
      
      <div className="flex items-center space-x-4 text-sm text-gray-400">
        <div className="flex items-center">
          <span className={`w-3 h-3 rounded-full mr-1 ${
            repo.language === 'JavaScript' ? 'bg-yellow-400' :
            repo.language === 'Python' ? 'bg-blue-400' :
            repo.language === 'HTML' ? 'bg-red-400' :
            repo.language === 'CSS' ? 'bg-purple-400' :
            'bg-gray-400'
          }`}></span>
          {repo.language || 'Text'}
        </div>
        
        <div className="flex items-center">
          <Star size={16} className="mr-1" />
          {repo.stars_count}
        </div>
        
        <div className="flex items-center">
          <GitFork size={16} className="mr-1" />
          {repo.forks_count}
        </div>
        
        <span>
          Mis à jour le {new Date(repo.updated_at).toLocaleDateString('fr-FR')}
        </span>
      </div>
    </div>
  )
}
