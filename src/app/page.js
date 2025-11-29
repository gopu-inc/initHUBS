'use client'
import { useState, useEffect } from 'react'
import { useAuth } from '../lib/auth'
import ConnectionTest from '../components/ConnectionTest'

export default function Home() {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    full_name: ''
  })
  const [message, setMessage] = useState('')
  const { login, register, loading } = useAuth()

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
      setMessage('✅ Succès!')
    } else {
      setMessage(`❌ Erreur: ${result.error}`)
    }
  }

  return (
    <div className="min-h-screen bg-github-dark p-8">
      <div className="max-w-md mx-auto">
        <h1 className="text-3xl font-bold text-white text-center mb-8">
          initHUB Debug
        </h1>
        
        <ConnectionTest />
        
        {message && (
          <div className={`p-4 rounded-lg mt-4 ${
            message.includes('✅') ? 'bg-green-500' : 'bg-red-500'
          } text-white`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-8 space-y-4 bg-github-gray p-6 rounded-lg">
          <h2 className="text-xl font-bold text-white mb-4">
            {isLogin ? 'Connexion Test' : 'Inscription Test'}
          </h2>
          
          {!isLogin && (
            <>
              <div>
                <label className="block text-sm text-gray-300 mb-2">Username</label>
                <input
                  type="text"
                  required
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-2">Full Name</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                />
              </div>
            </>
          )}
          
          <div>
            <label className="block text-sm text-gray-300 mb-2">Email</label>
            <input
              type="email"
              required
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-300 mb-2">Password</label>
            <input
              type="password"
              required
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded disabled:opacity-50"
          >
            {loading ? 'Chargement...' : (isLogin ? 'Se connecter' : 'S inscrire')}
          </button>
          
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            className="w-full text-blue-400 hover:text-blue-300 text-sm"
          >
            {isLogin ? 'Créer un compte' : 'Déjà un compte ?'}
          </button>
        </form>
      </div>
    </div>
  )
}
