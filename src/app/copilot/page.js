'use client'
import { useEffect, useState } from 'react'
import { useAuth } from '../../lib/auth'
import { useRouter } from 'next/navigation'
import Header from '../../components/Header'
import Sidebar from '../../components/Sidebar'
import CopilotChat from '../../components/CopilotChat'
import { Bot, Code, MessageSquare } from 'lucide-react'

export default function CopilotPage() {
  const { user, token } = useAuth()
  const router = useRouter()
  const [copilotHealth, setCopilotHealth] = useState(null)

  useEffect(() => {
    if (!user) {
      router.push('/')
      return
    }

    checkCopilotHealth()
  }, [user, router])

  const checkCopilotHealth = async () => {
    try {
      const response = await fetch('https://hubs-pro.onrender.com/api/copilot/health')
      const data = await response.json()
      setCopilotHealth(data)
    } catch (error) {
      console.error('Erreur vérification santé Copilot:', error)
      setCopilotHealth({ online: false })
    }
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-github-dark">
      <Header />
      <div className="flex">
        <Sidebar />
        
        <main className="flex-1 p-8">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  Copilot IA
                </h1>
                <p className="text-gray-400">
                  Assistant IA pour vous aider dans votre développement
                </p>
              </div>
              
              {copilotHealth && (
                <div className={`px-4 py-2 rounded-full ${
                  copilotHealth.online 
                    ? 'bg-green-500 text-white' 
                    : 'bg-red-500 text-white'
                }`}>
                  {copilotHealth.online ? 'En ligne' : 'Hors ligne'}
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <CopilotChat token={token} />
              </div>

              <div className="space-y-6">
                <div className="github-card">
                  <h3 className="text-lg font-semibold text-white mb-4">
                    Actions rapides
                  </h3>
                  <div className="space-y-3">
                    <button className="w-full btn-secondary text-left p-3">
                      <Code size={16} className="inline mr-2" />
                      Analyser du code
                    </button>
                    <button className="w-full btn-secondary text-left p-3">
                      <MessageSquare size={16} className="inline mr-2" />
                      Suggérer un commit
                    </button>
                  </div>
                </div>

                <div className="github-card">
                  <h3 className="text-lg font-semibold text-white mb-4">
                    Statut Copilot
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Statut:</span>
                      <span className={copilotHealth?.online ? 'text-green-400' : 'text-red-400'}>
                        {copilotHealth?.online ? 'En ligne' : 'Hors ligne'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Version:</span>
                      <span className="text-white">12.0.0</span>
                    </div>
                  </div>
                </div>

                <div className="github-card">
                  <h3 className="text-lg font-semibold text-white mb-4">
                    Tips Copilot
                  </h3>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>• Soyez précis dans vos questions</li>
                    <li>• Fournissez du contexte quand nécessaire</li>
                    <li>• Utilisez "fr" pour des réponses en français</li>
                    <li>• Testez l'analyse de code pour du debugging</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
