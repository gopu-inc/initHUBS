// Configuration
const API_BASE_URL = 'https://hubs-ja2g.onrender.com/api';
let authToken = localStorage.getItem('inithub_token');

// Client API simple
class InitHUBClient {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }
    
    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(`API Error ${response.status}: ${error}`);
        }
        
        return response.json();
    }
    
    // Authentification
    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        authToken = data.access_token;
        localStorage.setItem('inithub_token', data.access_token);
        return data;
    }
    
    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
    
    async getCurrentUser() {
        try {
            return await this.request('/users/me');
        } catch {
            return null;
        }
    }
    
    async logout() {
        localStorage.removeItem('inithub_token');
        authToken = null;
    }
    
    // Hébergement
    async createSite(name, domain, type = 'static') {
        return this.request('/hosting/sites', {
            method: 'POST',
            body: JSON.stringify({ name, domain, type })
        });
    }
    
    async listSites() {
        return this.request('/hosting/sites');
    }
    
    // Projets
    async listProjects(page = 1) {
        return this.request(`/projects?page=${page}`);
    }
    
    async pushProject(projectName, files) {
        return this.request('/projects/push', {
            method: 'POST',
            body: JSON.stringify({
                project_name: projectName,
                files: files,
                force: false
            })
        });
    }
    
    async pullProject(projectName) {
        return this.request('/projects/pull', {
            method: 'POST',
            body: JSON.stringify({
                project_name: projectName,
                force: false
            })
        });
    }
    
    // Copilot
    async askCopilot(question) {
        return this.request('/copilot/ask', {
            method: 'POST',
            body: JSON.stringify({ question })
        });
    }
    
    // Système
    async health() {
        return this.request('/health');
    }
    
    async systemInfo() {
        return this.request('/system/info');
    }
    
    // Terminal (WebSocket)
    createTerminal() {
        if (!authToken) throw new Error('Non authentifié');
        
        const ws = new WebSocket(`wss://hubs-ja2g.onrender.com/ws/terminal?token=${authToken}`);
        
        return {
            send: (command) => ws.send(JSON.stringify({ type: 'command', command })),
            onMessage: (callback) => ws.onmessage = (event) => callback(JSON.parse(event.data)),
            onError: (callback) => ws.onerror = callback,
            close: () => ws.close()
        };
    }
}

// Export global
const api = new InitHUBClient();
window.initHUB = api;

// Auto-login check
if (authToken && window.location.pathname.includes('login')) {
    api.getCurrentUser().then(user => {
        if (user) window.location.href = 'app.html';
    });
}
