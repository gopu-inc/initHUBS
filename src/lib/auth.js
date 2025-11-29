'use client'
import { createContext, useContext, useState, useEffect } from 'react'
import { api } from './api'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const savedToken = localStorage.getItem('inithub_token')
    if (savedToken) {
      setToken(savedToken)
      // Ne pas charger l'utilisateur tout de suite pour éviter les erreurs
      setLoading(false)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async (userToken) => {
    try {
      // Utiliser l'endpoint dashboard pour récupérer les infos utilisateur
      const userData = await api.get('/api/dashboard', userToken)
      setUser({
        id: 1, // Temporaire
        username: 'user', // Temporaire
        email: 'user@example.com', // Temporaire
        ...userData
      })
    } catch (error) {
      console.error('Erreur récupération utilisateur:', error)
      // Ne pas logout immédiatement, peut-être juste un problème temporaire
    }
  }

  const login = async (email, password) => {
    try {
      console.log('🔄 Tentative de connexion...')
      
      const response = await api.post('/api/auth/login', { 
        email, 
        password 
      })
      
      console.log('✅ Réponse login:', response)
      
      if (response.access_token) {
        localStorage.setItem('inithub_token', response.access_token)
        setToken(response.access_token)
        
        // Créer un objet utilisateur temporaire
        const tempUser = {
          id: 1,
          username: email.split('@')[0],
          email: email,
          full_name: 'Utilisateur'
        }
        setUser(tempUser)
        
        return { success: true }
      } else {
        return { success: false, error: 'Token non reçu' }
      }
    } catch (error) {
      console.error('❌ Erreur login:', error)
      return { 
        success: false, 
        error: error.message || 'Erreur de connexion' 
      }
    }
  }

  const register = async (userData) => {
    try {
      console.log('🔄 Tentative d inscription...')
      
      const response = await api.post('/api/auth/register', userData)
      console.log('✅ Réponse register:', response)
      
      return { success: true, data: response }
    } catch (error) {
      console.error('❌ Erreur register:', error)
      return { 
        success: false, 
        error: error.message || 'Erreur d inscription' 
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('inithub_token')
    setUser(null)
    setToken(null)
  }

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      register,
      logout,
      fetchUser
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
