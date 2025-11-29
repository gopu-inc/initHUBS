'use client'
import { useState } from 'react'
import { useAuth } from '../lib/auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { GitBranch, Bot, BarChart3, Download, BookOpen } from 'lucide-react'

export default function Home() {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    full_name: ''
  })
  const [message, setMessage] = useState('')
  const { user, login, register, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (user) {
      router.push('/dashboard')
    }
  }, [user, router])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage('')
    
    let result
    if (isLogin) {
      result = await login(formData.email, formData.password)
    } else {
      result = await register(formData)
    }
    
    if (result.success) {
      setMessage('✅ Connexion réussie! Redirection...')
    } else {
      setMessage(`❌ ${result.error}`)
    }
  }

  const features = [
    {
      icon: <GitBranch className="w-8 h-8" />,
      title: 'Git Repository Hosting',
      description: 'Hébergement de repositories Git avec support LFS'
    },
    {
      icon: <Bot className="w-8 h-8" />,
      title: 'Copilot IA intégré',
      description: 'Assistant IA pour le développement'
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: 'Dashboard Analytics',
      description: 'Analyses détaillées et métriques'
    },
    {
      icon: <Download className="w-8 h-8" />,
      title: 'Releases & Assets',
      description: 'Gestion des releases et assets'
    },
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: 'Wiki Documentation',
      description: 'Documentation intégrée avec wiki'
    }
  ]

  if (user) {
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="pt-8 pb-16 text-center">
          <h1 className="text-5xl font-bold text-white mb-4">
            🚀 initHUB Cloud Enterprise
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Plateforme cloud complète avec Copilot, Dashboard, Releases et Analytics
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {/* Formulaire */}
          <div className="github-card">
            <h2 className="text-2xl font-bold text-white mb-6">
              {isLogin ? 'Connexion' : 'Inscription'}
            </h2>
            
            {message && (
              <div className={`p-3 rounded-lg mb-4 ${
                message.includes('✅') ? 'bg-green-500' : 'bg-red-500'
              } text-white`}>
                {message}
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Nom d'utilisateur
                    </label>
                    <input
                      type="text"
                      required
                      className="w-full px-3 py-2 bg-gray-800 border border-github-border rounded-md text-white"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Nom complet
                    </label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 bg-gray-800 border border-github-border rounded-md text-white"
                      value={formData.full_name}
                      onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                    />
                  </div>
                </>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  required
                  className="w-full px-3 py-2 bg-gray-800 border border-github-border rounded-md text-white"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Mot de passe
                </label>
                <input
                  type="password"
                  required
                  className="w-full px-3 py-2 bg-gray-800 border border-github-border rounded-md text-white"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                />
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary py-3"
              >
                {loading ? 'Chargement...' : (isLogin ? 'Se connecter' : 'Créer un compte')}
              </button>
            </form>
            
            <div className="mt-4 text-center">
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="text-blue-400 hover:text-blue-300"
              >
                {isLogin ? 'Créer un compte' : 'Déjà un compte ? Se connecter'}
              </button>
            </div>
          </div>

          {/* Features */}
          <div>
            <h3 className="text-2xl font-bold text-white mb-6">Fonctionnalités</h3>
            <div className="grid gap-4">
              {features.map((feature, index) => (
                <div key={index} className="github-card flex items-start space-x-4">
                  <div className="text-blue-400 flex-shrink-0">
                    {feature.icon}
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-1">
                      {feature.title}
                    </h4>
                    <p className="text-gray-400">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
