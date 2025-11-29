'use client'
import { useState, useEffect } from 'react'
import ConnectionTest from '../../components/ConnectionTest'

export default function DebugPage() {
  const [endpoints, setEndpoints] = useState({})

  const testEndpoint = async (name, url) => {
    try {
      const response = await fetch(`https://hubs-pro.onrender.com${url}`)
      const data = await response.json()
      return { status: 'success', data }
    } catch (error) {
      return { status: 'error', error: error.message }
    }
  }

  useEffect(() => {
    const testAllEndpoints = async () => {
      const endpointsToTest = [
        { name: 'Health', url: '/api/health' },
        { name: 'Docs', url: '/api/docs' },
        { name: 'Auth Login', url: '/api/auth/login' },
        { name: 'Auth Register', url: '/api/auth/register' }
      ]

      const results = {}
      for (const endpoint of endpointsToTest) {
        results[endpoint.name] = await testEndpoint(endpoint.name, endpoint.url)
      }
      setEndpoints(results)
    }

    testAllEndpoints()
  }, [])

  return (
    <div className="min-h-screen bg-github-dark p-8">
      <h1 className="text-3xl font-bold text-white mb-6">Debug Connection</h1>
      
      <ConnectionTest />
      
      <div className="mt-8 grid gap-4">
        {Object.entries(endpoints).map(([name, result]) => (
          <div key={name} className={`p-4 rounded-lg ${
            result.status === 'success' ? 'bg-green-500' : 'bg-red-500'
          } text-white`}>
            <h3 className="font-bold">{name}</h3>
            <pre className="text-sm mt-2">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  )
}
