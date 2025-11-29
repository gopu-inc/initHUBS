'use client'
import { useState, useEffect } from 'react'
import { api } from '../lib/api'

export default function ConnectionTest() {
  const [status, setStatus] = useState('testing')
  const [message, setMessage] = useState('')

  useEffect(() => {
    testConnection()
  }, [])

  const testConnection = async () => {
    try {
      setStatus('testing')
      setMessage('Test de connexion au backend...')
      
      const response = await fetch('https://hubs-pro.onrender.com/api/health')
      const data = await response.json()
      
      setStatus('success')
      setMessage(`✅ Backend connecté: ${data.status}`)
    } catch (error) {
      setStatus('error')
      setMessage(`❌ Erreur: ${error.message}`)
    }
  }

  return (
    <div className={`p-4 rounded-lg ${
      status === 'success' ? 'bg-green-500' :
      status === 'error' ? 'bg-red-500' :
      'bg-yellow-500'
    } text-white`}>
      <p>{message}</p>
    </div>
  )
}
