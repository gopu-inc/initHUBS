let allBadges = [];

async function loadBadges() {
    const badgesGrid = document.getElementById('badges-grid');
    if (!badgesGrid) return;
    
    badgesGrid.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Chargement des badges...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/badges`);
        
        if (response.ok) {
            const data = await response.json();
            allBadges = data.badges || [];
            
            displayBadges(allBadges);
            
            // Mettre à jour le compteur
            document.getElementById('badge-count').textContent = allBadges.length;
        } else {
            await handleAPIError(response);
            badgesGrid.innerHTML = `
                <div class="error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Erreur lors du chargement des badges</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erreur chargement badges:', error);
        badgesGrid.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Erreur de connexion au serveur</p>
            </div>
        `;
    }
}

function displayBadges(badges) {
    const badgesGrid = document.getElementById('badges-grid');
    if (!badgesGrid) return;
    
    if (badges.length === 0) {
        badgesGrid.innerHTML = `
            <div class="no-badges">
                <i class="fas fa-shield-alt"></i>
                <h3>Aucun badge trouvé</h3>
                <p>Aucun badge n'a encore été créé.</p>
                <button class="btn btn-primary" onclick="openBadgeCreator()">
                    <i class="fas fa-plus"></i> Créer un badge
                </button>
            </div>
        `;
        return;
    }
    
    const badgesHTML = badges.map(badge => `
        <div class="badge-item">
            <div class="badge-preview">
                <img src="${API_BASE_URL}/badge/svg/${badge.name}${badge.logo ? `?logo=${badge.logo}` : ''}" 
                     alt="${badge.label}: ${badge.value}" 
                     style="height: 20px;">
            </div>
            <h4>${escapeHtml(badge.label)}: ${escapeHtml(badge.value)}</h4>
            <p>Nom: <code>${escapeHtml(badge.name)}</code></p>
            <p>Couleur: <span class="color-dot" style="background-color: ${getColorHex(badge.color)}"></span> ${badge.color}</p>
            ${badge.logo ? `<p>Logo: ${escapeHtml(badge.logo)}</p>` : ''}
            
            <div class="badge-markdown">
                ![${escapeHtml(badge.label)}: ${escapeHtml(badge.value)}](${API_BASE_URL}/badge/svg/${badge.name})
            </div>
            
            <div class="badge-actions">
                <button class="btn btn-small" onclick="copyBadgeMarkdown('${badge.name}')">
                    <i class="fas fa-copy"></i> Copier
                </button>
                ${currentToken ? `
                    <button class="btn btn-small btn-danger" onclick="deleteBadge('${badge.name}')">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
    
    badgesGrid.innerHTML = badgesHTML;
}

function getColorHex(color) {
    const colors = {
        'blue': '#007ec6',
        'green': '#4c1',
        'red': '#e05d44',
        'orange': '#fe7d37',
        'yellow': '#dfb317',
        'purple': '#9f4ca5',
        'gray': '#9f9f9f'
    };
    return colors[color] || colors.blue;
}

function openBadgeCreator() {
    if (!currentToken) {
        showNotification('Vous devez être connecté pour créer un badge', 'error');
        openAuthModal();
        return;
    }
    
    openModal('badge-creator-modal');
    updateBadgePreview();
    
    // Gérer la soumission du formulaire
    const form = document.getElementById('badge-form');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await createBadge();
    });
    
    // Mettre à jour l'aperçu en temps réel
    document.getElementById('badge-label').addEventListener('input', updateBadgePreview);
    document.getElementById('badge-value').addEventListener('input', updateBadgePreview);
    document.getElementById('badge-color').addEventListener('change', updateBadgePreview);
    document.getElementById('badge-logo').addEventListener('input', updateBadgePreview);
}

function closeBadgeCreator() {
    closeModal('badge-creator-modal');
}

function updateBadgePreview() {
    const label = document.getElementById('badge-label').value || 'label';
    const value = document.getElementById('badge-value').value || 'value';
    const color = document.getElementById('badge-color').value;
    const logo = document.getElementById('badge-logo').value;
    
    const previewDiv = document.getElementById('badge-preview');
    if (!previewDiv) return;
    
    // Générer l'URL du badge
    let badgeUrl = `${API_BASE_URL}/badge/custom/${encodeURIComponent(label)}/${encodeURIComponent(value)}/${color}`;
    if (logo) {
        badgeUrl += `/${encodeURIComponent(logo)}`;
    }
    
    previewDiv.innerHTML = `
        <div class="badge-preview-container">
            <img src="${badgeUrl}" alt="${label}: ${value}" style="height: 20px;">
            <p class="preview-url">${badgeUrl}</p>
        </div>
    `;
}

async function createBadge() {
    const name = document.getElementById('badge-name').value;
    const label = document.getElementById('badge-label').value;
    const value = document.getElementById('badge-value').value;
    const color = document.getElementById('badge-color').value;
    const logo = document.getElementById('badge-logo').value;
    
    if (!name || !label || !value) {
        showNotification('Veuillez remplir tous les champs obligatoires', 'error');
        return;
    }
    
    const createBtn = document.getElementById('create-badge-btn');
    const originalText = createBtn.innerHTML;
    createBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Création...';
    createBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/badges`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${currentToken}`
            },
            body: JSON.stringify({
                name: name,
                label: label,
                value: value,
                color: color,
                logo: logo || undefined
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification('Badge créé avec succès !', 'success');
            closeBadgeCreator();
            loadBadges(); // Recharger la liste
        } else {
            await handleAPIError(response);
        }
    } catch (error) {
        showNotification('Erreur lors de la création du badge', 'error');
    } finally {
        createBtn.innerHTML = originalText;
        createBtn.disabled = false;
    }
}

async function deleteBadge(badgeName) {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer le badge "${badgeName}" ?`)) {
        return;
    }
    
    try {
        // Note: L'API ne fournit pas d'endpoint DELETE pour les badges
        // Cette fonction est donc pour le moment un placeholder
        showNotification('La suppression des badges n\'est pas encore implémentée via l\'API', 'info');
    } catch (error) {
        showNotification('Erreur lors de la suppression du badge', 'error');
    }
}

function copyBadgeMarkdown(badgeName) {
    const badge = allBadges.find(b => b.name === badgeName);
    if (!badge) return;
    
    const markdown = `![${badge.label}: ${badge.value}](${API_BASE_URL}/badge/svg/${badge.name})`;
    
    navigator.clipboard.writeText(markdown).then(() => {
        showNotification('Markdown copié dans le presse-papier !', 'success');
    }).catch(() => {
        // Fallback pour les anciens navigateurs
        const textarea = document.createElement('textarea');
        textarea.value = markdown;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showNotification('Markdown copié dans le presse-papier !', 'success');
    });
}

function showBadgeWorkshop() {
    showSection('badges');
}

function openBadgeWorkshop() {
    // Cette fonction ouvrirait un atelier de badges plus avancé
    // Pour l'instant, on ouvre simplement le créateur de badges
    openBadgeCreator();
}

// Exposer les fonctions globales
window.openBadgeCreator = openBadgeCreator;
window.closeBadgeCreator = closeBadgeCreator;
window.updateBadgePreview = updateBadgePreview;
window.showBadgeWorkshop = showBadgeWorkshop;
window.openBadgeWorkshop = openBadgeWorkshop;
