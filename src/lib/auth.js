'use client'
import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const savedToken = localStorage.getItem('inithub_token')
    const savedUser = localStorage.getItem('inithub_user')
    
    if (savedToken && savedUser) {
      setToken(savedToken)
      setUser(JSON.parse(savedUser))
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      const response = await fetch('https://hubs-pro.onrender.com/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erreur de connexion')
      }

      const data = await response.json()
      
      const tempUser = {
        id: 1,
        username: email.split('@')[0],
        email: email,
        full_name: 'Utilisateur initHUB'
      }
      
      localStorage.setItem('inithub_token', data.access_token)
      localStorage.setItem('inithub_user', JSON.stringify(tempUser))
      setToken(data.access_token)
      setUser(tempUser)
      
      return { success: true }
    } catch (error) {
      console.error('Erreur login:', error)
      return { 
        success: false, 
        error: error.message 
      }
    }
  }

  const register = async (userData) => {
    try {
      const response = await fetch('https://hubs-pro.onrender.com/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erreur d inscription')
      }

      const data = await response.json()
      
      return { success: true, data }
    } catch (error) {
      console.error('Erreur register:', error)
      return { 
        success: false, 
        error: error.message 
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('inithub_token')
    localStorage.removeItem('inithub_user')
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
      logout
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
