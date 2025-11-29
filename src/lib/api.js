const API_BASE_URL = 'https://hubs-pro.onrender.com'

class API {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  async get(endpoint, token = null) {
    const headers = token ? { 
      'Authorization': `Bearer ${token}`,
    } : {}
    
    return this.request(endpoint, { 
      method: 'GET', 
      headers 
    })
  }

  async post(endpoint, data, token = null) {
    const headers = token ? { 
      'Authorization': `Bearer ${token}`,
    } : {}
    
    return this.request(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    })
  }
}

export const api = new API()
