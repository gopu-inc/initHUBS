// Configuration
const API_BASE_URL = 'https://zenv-hub.onrender.com';
let currentUser = null;
let currentToken = null;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si un token est stocké
    const savedToken = localStorage.getItem('zenv_token');
    const savedUser = localStorage.getItem('zenv_user');
    
    if (savedToken && savedUser) {
        currentToken = savedToken;
        currentUser = JSON.parse(savedUser);
        updateAuthUI();
    }
    
    // Vérifier le statut du serveur
    checkServerStatus();
    
    // Charger les stats initiales
    loadStats();
    
    // Gestionnaire d'onglets
    setupTabNavigation();
    
    // Gestionnaire de menu mobile
    setupMobileMenu();
    
    // Charger les packages
    loadPackages();
    
    // Charger les badges
    loadBadges();
    
    // Charger la version API
    loadAPIVersion();
});

// Navigation
function setupTabNavigation() {
    // Navigation principale
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('href').substring(1);
            showSection(section);
            
            // Mettre à jour les liens actifs
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Fermer le menu mobile si ouvert
            document.getElementById('mobile-menu').classList.remove('active');
        });
    });
    
    // Navigation documentation
    const docsLinks = document.querySelectorAll('.docs-nav-link');
    docsLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('href').substring(1);
            showDocsSection(section);
            
            docsLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function showSection(sectionId) {
    // Masquer toutes les sections
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Afficher la section demandée
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
        
        // Mettre à jour l'URL
        history.pushState(null, '', `#${sectionId}`);
        
        // Charger les données si nécessaire
        if (sectionId === 'packages') {
            loadPackages();
        } else if (sectionId === 'badges') {
            loadBadges();
        }
    }
}

function showDocsSection(sectionId) {
    // Masquer toutes les sections de docs
    document.querySelectorAll('.docs-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Afficher la section demandée
    const section = document.getElementById(sectionId);
    if (section) {
        section.style.display = 'block';
    }
}

// Menu mobile
function setupMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const closeMenuBtn = document.getElementById('close-menu');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    if (closeMenuBtn) {
        closeMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Fermer en cliquant à l'extérieur
    mobileMenu.addEventListener('click', (e) => {
        if (e.target === mobileMenu) {
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
    
    // Liens du menu mobile
    const mobileLinks = document.querySelectorAll('.mobile-link');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('href').substring(1);
            showSection(section);
            
            // Mettre à jour les liens actifs
            mobileLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Fermer le menu
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
}

// Statut du serveur
async function checkServerStatus() {
    const statusElement = document.getElementById('server-status');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('span');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        
        if (response.ok) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Serveur connecté';
        } else {
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Serveur hors ligne';
        }
    } catch (error) {
        statusDot.className = 'status-dot offline';
        statusText.textContent = 'Erreur de connexion';
    }
}

// Charger les statistiques
async function loadStats() {
    try {
        // Récupérer les packages
        const packagesResponse = await fetch(`${API_BASE_URL}/api/packages`);
        if (packagesResponse.ok) {
            const packagesData = await packagesResponse.json();
            document.getElementById('package-count').textContent = packagesData.count || 0;
            
            // Calculer les téléchargements totaux
            let totalDownloads = 0;
            if (packagesData.packages) {
                packagesData.packages.forEach(pkg => {
                    totalDownloads += pkg.downloads_count || 0;
                });
            }
            document.getElementById('download-count').textContent = totalDownloads;
        }
        
        // Récupérer les badges
        const badgesResponse = await fetch(`${API_BASE_URL}/api/badges`);
        if (badgesResponse.ok) {
            const badgesData = await badgesResponse.json();
            document.getElementById('badge-count').textContent = badgesData.count || 0;
        }
    } catch (error) {
        console.error('Erreur chargement stats:', error);
    }
}

// Charger la version API
async function loadAPIVersion() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/version`);
        if (response.ok) {
            const data = await response.json();
            document.getElementById('api-version').textContent = data.api_version || '2.1.0';
        }
    } catch (error) {
        console.error('Erreur chargement version:', error);
    }
}

// Modals
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    const overlay = document.getElementById('modal-overlay');
    
    if (modal && overlay) {
        modal.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    const overlay = document.getElementById('modal-overlay');
    
    if (modal && overlay) {
        modal.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Utilitaires
function showNotification(message, type = 'info') {
    // Créer une notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 
                        type === 'error' ? 'exclamation-circle' : 
                        type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Ajouter au body
    document.body.appendChild(notification);
    
    // Animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Supprimer après 5 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Gestion des erreurs API
async function handleAPIError(response) {
    try {
        const errorData = await response.json();
        showNotification(errorData.error || 'Erreur API', 'error');
        return errorData;
    } catch (error) {
        showNotification(`Erreur ${response.status}: ${response.statusText}`, 'error');
        return null;
    }
}

// Style pour les notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: var(--radius);
        background: white;
        box-shadow: var(--shadow);
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 2000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        border-left: 4px solid var(--success-color);
    }
    
    .notification-success i {
        color: var(--success-color);
    }
    
    .notification-error {
        border-left: 4px solid var(--danger-color);
    }
    
    .notification-error i {
        color: var(--danger-color);
    }
    
    .notification-warning {
        border-left: 4px solid var(--warning-color);
    }
    
    .notification-warning i {
        color: var(--warning-color);
    }
    
    .notification-info {
        border-left: 4px solid var(--info-color);
    }
    
    .notification-info i {
        color: var(--info-color);
    }
`;
document.head.appendChild(notificationStyles);

// Exposer les fonctions globales
window.showSection = showSection;
window.showDocsSection = showDocsSection;
window.openModal = openModal;
window.closeModal = closeModal;
window.checkServerStatus = checkServerStatus;
