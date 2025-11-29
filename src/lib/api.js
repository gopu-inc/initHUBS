const API_BASE_URL = 'https://hubs-pro.onrender.com'

class API {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    console.log(`🔄 API Call: ${url}`) // Debug log

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      console.log(`📡 Response Status: ${response.status}`) // Debug log
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error(`❌ API Error: ${response.status} - ${errorText}`)
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
      }
      
      const data = await response.json()
      console.log('✅ API Success:', data) // Debug log
      return data
    } catch (error) {
      console.error('❌ API request failed:', error)
      throw error
    }
  }

  async get(endpoint, token = null) {
    const headers = token ? { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    } : {
      'Content-Type': 'application/json'
    }
    
    return this.request(endpoint, { 
      method: 'GET', 
      headers 
    })
  }

  async post(endpoint, data, token = null) {
    const headers = token ? { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    } : {
      'Content-Type': 'application/json'
    }
    
    return this.request(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    })
  }

  async put(endpoint, data, token = null) {
    const headers = token ? { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    } : {
      'Content-Type': 'application/json'
    }
    
    return this.request(endpoint, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    })
  }

  async delete(endpoint, token = null) {
    const headers = token ? { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    } : {
      'Content-Type': 'application/json'
    }
    
    return this.request(endpoint, { 
      method: 'DELETE', 
      headers 
    })
  }
}

export const api = new API()
