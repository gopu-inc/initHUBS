// Gestion de l'authentification
function updateAuthUI() {
    const authSection = document.getElementById('auth-section');
    const mobileAuthSection = document.getElementById('mobile-auth-section');
    
    if (!authSection || !mobileAuthSection) return;
    
    if (currentUser) {
        // Utilisateur connecté
        authSection.innerHTML = `
            <div class="user-info">
                <div class="user-avatar">
                    ${currentUser.username.charAt(0).toUpperCase()}
                </div>
                <span>${currentUser.username}</span>
                <button class="auth-btn" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i>
                </button>
            </div>
        `;
        
        mobileAuthSection.innerHTML = `
            <div class="mobile-user-info">
                <div class="user-avatar">
                    ${currentUser.username.charAt(0).toUpperCase()}
                </div>
                <span>${currentUser.username}</span>
                <button class="auth-btn" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i> Déconnexion
                </button>
            </div>
        `;
    } else {
        // Utilisateur non connecté
        authSection.innerHTML = `
            <button class="auth-btn btn-login" onclick="openAuthModal()">
                <i class="fas fa-sign-in-alt"></i> Connexion
            </button>
        `;
        
        mobileAuthSection.innerHTML = `
            <button class="auth-btn btn-login" onclick="openAuthModal()">
                <i class="fas fa-sign-in-alt"></i> Connexion
            </button>
        `;
    }
}

function openAuthModal() {
    openModal('auth-modal');
}

function closeAuthModal() {
    closeModal('auth-modal');
}

function showAuthTab(tabName) {
    // Masquer tous les formulaires
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });
    
    // Désactiver tous les onglets
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Activer l'onglet sélectionné
    const selectedTab = document.querySelector(`.auth-tab[onclick*="${tabName}"]`);
    const selectedForm = document.getElementById(`${tabName}-form`);
    
    if (selectedTab && selectedForm) {
        selectedTab.classList.add('active');
        selectedForm.classList.add('active');
    }
}

async function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    if (!username || !password) {
        showNotification('Veuillez remplir tous les champs', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Stocker le token et les infos utilisateur
            currentToken = data.token.access_token;
            currentUser = data.user;
            
            localStorage.setItem('zenv_token', currentToken);
            localStorage.setItem('zenv_user', JSON.stringify(currentUser));
            
            showNotification('Connexion réussie !', 'success');
            updateAuthUI();
            closeAuthModal();
            
            // Recharger les données
            loadPackages();
            loadBadges();
        } else {
            await handleAPIError(response);
        }
    } catch (error) {
        showNotification('Erreur de connexion au serveur', 'error');
    }
}

async function register(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    if (!username || !email || !password) {
        showNotification('Veuillez remplir tous les champs', 'error');
        return;
    }
    
    if (password.length < 8) {
        showNotification('Le mot de passe doit faire au moins 8 caractères', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Stocker le token et les infos utilisateur
            currentToken = data.token.access_token;
            currentUser = data.user;
            
            localStorage.setItem('zenv_token', currentToken);
            localStorage.setItem('zenv_user', JSON.stringify(currentUser));
            
            showNotification('Inscription réussie ! Vous êtes maintenant connecté.', 'success');
            updateAuthUI();
            closeAuthModal();
            
            // Recharger les données
            loadPackages();
            loadBadges();
        } else {
            await handleAPIError(response);
        }
    } catch (error) {
        showNotification('Erreur lors de l\'inscription', 'error');
    }
}

async function loginWithToken() {
    const token = document.getElementById('token-input').value;
    
    if (!token) {
        showNotification('Veuillez entrer un token', 'error');
        return;
    }
    
    // Utiliser le token prédéfini pour l'admin
    if (token.startsWith('zenv_')) {
        try {
            // Vérifier le token
            const response = await fetch(`${API_BASE_URL}/api/tokens/verify?token=${encodeURIComponent(token)}`);
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.valid) {
                    currentToken = token;
                    currentUser = data.user;
                    
                    localStorage.setItem('zenv_token', currentToken);
                    localStorage.setItem('zenv_user', JSON.stringify(currentUser));
                    
                    showNotification('Connexion avec token réussie !', 'success');
                    updateAuthUI();
                    closeAuthModal();
                    
                    // Recharger les données
                    loadPackages();
                    loadBadges();
                } else {
                    showNotification('Token invalide', 'error');
                }
            } else {
                showNotification('Erreur de vérification du token', 'error');
            }
        } catch (error) {
            showNotification('Erreur de connexion au serveur', 'error');
        }
    } else {
        showNotification('Format de token invalide. Doit commencer par "zenv_"', 'error');
    }
}

function logout() {
    currentToken = null;
    currentUser = null;
    
    localStorage.removeItem('zenv_token');
    localStorage.removeItem('zenv_user');
    
    showNotification('Déconnexion réussie', 'info');
    updateAuthUI();
    
    // Recharger les packages (pour montrer la vue publique)
    loadPackages();
    loadBadges();
}

// Exposer les fonctions globales
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.showAuthTab = showAuthTab;
window.login = login;
window.register = register;
window.loginWithToken = loginWithToken;
window.logout = logout;
