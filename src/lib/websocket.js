'use client'

class WebSocketService {
  constructor() {
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
  }

  connect(url, onMessage, onOpen, onClose, onError) {
    try {
      this.socket = new WebSocket(url)
      
      this.socket.onopen = (event) => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        if (onOpen) onOpen(event)
      }
      
      this.socket.onmessage = (event) => {
        if (onMessage) onMessage(JSON.parse(event.data))
      }
      
      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected')
        if (onClose) onClose(event)
        this.attemptReconnect(url, onMessage, onOpen, onClose, onError)
      }
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error)
        if (onError) onError(error)
      }
      
    } catch (error) {
      console.error('WebSocket connection failed:', error)
    }
  }

  attemptReconnect(url, onMessage, onOpen, onClose, onError) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect(url, onMessage, onOpen, onClose, onError)
      }, this.reconnectInterval)
    }
  }

  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }
}

export const websocketService = new WebSocketService()
