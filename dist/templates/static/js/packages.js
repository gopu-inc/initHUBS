let allPackages = [];

async function loadPackages() {
    const packagesGrid = document.getElementById('packages-grid');
    const loadingElement = document.getElementById('packages-loading');
    
    if (!packagesGrid || !loadingElement) return;
    
    // Afficher le chargement
    packagesGrid.innerHTML = '';
    loadingElement.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/packages`);
        
        if (response.ok) {
            const data = await response.json();
            allPackages = data.packages || [];
            
            // Masquer le chargement
            loadingElement.style.display = 'none';
            
            // Afficher les packages
            displayPackages(allPackages);
            
            // Mettre à jour le compteur
            document.getElementById('package-count').textContent = allPackages.length;
            
            // Configurer la recherche
            setupPackageSearch();
            
            // Configurer le filtre
            setupPackageFilter();
        } else {
            await handleAPIError(response);
            loadingElement.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <p>Erreur lors du chargement des packages</p>
            `;
        }
    } catch (error) {
        console.error('Erreur chargement packages:', error);
        loadingElement.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <p>Erreur de connexion au serveur</p>
        `;
    }
}

function displayPackages(packages) {
    const packagesGrid = document.getElementById('packages-grid');
    if (!packagesGrid) return;
    
    if (packages.length === 0) {
        packagesGrid.innerHTML = `
            <div class="no-packages">
                <i class="fas fa-box-open"></i>
                <h3>Aucun package trouvé</h3>
                <p>Aucun package n'est disponible pour le moment.</p>
            </div>
        `;
        return;
    }
    
    const packagesHTML = packages.map(pkg => `
        <div class="package-card" onclick="openPackageDetails('${pkg.name}')">
            <div class="package-header">
                <div>
                    <h4>${escapeHtml(pkg.name)}</h4>
                    <p class="package-author">Par ${escapeHtml(pkg.author || 'Inconnu')}</p>
                </div>
                <span class="package-version">v${escapeHtml(pkg.version)}</span>
            </div>
            
            <p class="package-description">${escapeHtml(pkg.description || 'Aucune description')}</p>
            
            <div class="package-footer">
                <div class="package-info">
                    <span><i class="fas fa-download"></i> ${pkg.downloads_count || 0}</span>
                    <span><i class="fas fa-balance-scale"></i> ${escapeHtml(pkg.license || 'MIT')}</span>
                </div>
                <div class="package-size">
                    ${formatFileSize(pkg.size || 0)}
                </div>
            </div>
        </div>
    `).join('');
    
    packagesGrid.innerHTML = packagesHTML;
}

function setupPackageSearch() {
    const searchInput = document.getElementById('package-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            displayPackages(allPackages);
            return;
        }
        
        const filteredPackages = allPackages.filter(pkg => {
            return pkg.name.toLowerCase().includes(searchTerm) ||
                   (pkg.description && pkg.description.toLowerCase().includes(searchTerm)) ||
                   (pkg.author && pkg.author.toLowerCase().includes(searchTerm));
        });
        
        displayPackages(filteredPackages);
    });
}

function setupPackageFilter() {
    const filterSelect = document.getElementById('package-filter');
    const refreshButton = document.getElementById('refresh-packages');
    
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const filterValue = this.value;
            let filteredPackages = [...allPackages];
            
            switch (filterValue) {
                case 'recent':
                    filteredPackages.sort((a, b) => 
                        new Date(b.updated_at) - new Date(a.updated_at)
                    );
                    break;
                    
                case 'popular':
                    filteredPackages.sort((a, b) => 
                        (b.downloads_count || 0) - (a.downloads_count || 0)
                    );
                    break;
                    
                default:
                    filteredPackages.sort((a, b) => a.name.localeCompare(b.name));
            }
            
            displayPackages(filteredPackages);
        });
    }
    
    if (refreshButton) {
        refreshButton.addEventListener('click', loadPackages);
    }
}

async function openPackageDetails(packageName) {
    const package = allPackages.find(p => p.name === packageName);
    if (!package) return;
    
    const modal = document.getElementById('package-modal');
    const modalTitle = document.getElementById('package-modal-title');
    const modalBody = document.getElementById('package-modal-body');
    
    if (!modal || !modalTitle || !modalBody) return;
    
    // Afficher le chargement
    modalBody.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Chargement des détails...</p>
        </div>
    `;
    
    openModal('package-modal');
    modalTitle.textContent = package.name;
    
    try {
        // Récupérer les fichiers du package
        const filesResponse = await fetch(`${API_BASE_URL}/api/files/${packageName}`);
        const filesData = await filesResponse.ok ? await filesResponse.json() : { files: [] };
        
        // Récupérer le README
        let readmeContent = '';
        try {
            const readmeResponse = await fetch(`${API_BASE_URL}/api/readme/${packageName}`);
            if (readmeResponse.ok) {
                readmeContent = await readmeResponse.text();
            }
        } catch (error) {
            console.error('Erreur chargement README:', error);
        }
        
        // Construire le HTML des détails
        modalBody.innerHTML = `
            <div class="package-details">
                <div class="package-header-details">
                    <div>
                        <h3>${escapeHtml(package.name)}</h3>
                        <p class="package-version">Version: ${escapeHtml(package.version)}</p>
                        <p class="package-author">Auteur: ${escapeHtml(package.author || 'Inconnu')}</p>
                        <p class="package-license">Licence: ${escapeHtml(package.license || 'MIT')}</p>
                    </div>
                    <div class="package-stats">
                        <div class="stat">
                            <i class="fas fa-download"></i>
                            <span>${package.downloads_count || 0} téléchargements</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-weight"></i>
                            <span>${formatFileSize(package.size || 0)}</span>
                        </div>
                        <div class="stat">
                            <i class="fas fa-calendar-alt"></i>
                            <span>${formatDate(package.updated_at)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="package-description-details">
                    <h4>Description</h4>
                    <p>${escapeHtml(package.description || 'Aucune description')}</p>
                </div>
                
                <div class="package-actions">
                    <button class="btn btn-primary" onclick="downloadPackage('${packageName}', '${package.version}')">
                        <i class="fas fa-download"></i> Télécharger
                    </button>
                    ${currentToken ? `
                        <button class="btn btn-secondary" onclick="showUploadModal()">
                            <i class="fas fa-upload"></i> Mettre à jour
                        </button>
                    ` : ''}
                </div>
                
                ${filesData.files && filesData.files.length > 0 ? `
                    <div class="package-files">
                        <h4>Fichiers</h4>
                        <div class="files-list">
                            ${filesData.files.map(file => `
                                <div class="file-item">
                                    <i class="fas ${file.type === 'dir' ? 'fa-folder' : 'fa-file'}"></i>
                                    <span>${escapeHtml(file.name)}</span>
                                    ${file.size ? `<span class="file-size">${formatFileSize(file.size)}</span>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${readmeContent ? `
                    <div class="package-readme">
                        <h4>README</h4>
                        <div class="readme-content">${readmeContent}</div>
                    </div>
                ` : ''}
            </div>
        `;
    } catch (error) {
        console.error('Erreur chargement détails:', error);
        modalBody.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Erreur lors du chargement des détails du package.</p>
            </div>
        `;
    }
}

function closePackageModal() {
    closeModal('package-modal');
}

async function downloadPackage(packageName, version) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/packages/download/${packageName}/${version}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${packageName}-${version}.zv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('Téléchargement démarré', 'success');
        } else {
            await handleAPIError(response);
        }
    } catch (error) {
        showNotification('Erreur lors du téléchargement', 'error');
    }
}

function showUploadModal() {
    if (!currentToken) {
        showNotification('Vous devez être connecté pour uploader un package', 'error');
        openAuthModal();
        return;
    }
    
    // Créer le modal d'upload
    const modalHTML = `
        <div class="modal" id="upload-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Uploader un Package</h3>
                    <button class="close-modal" onclick="closeUploadModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="upload-form" enctype="multipart/form-data">
                        <div class="form-group">
                            <label for="upload-name">Nom du package</label>
                            <input type="text" id="upload-name" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="upload-version">Version</label>
                            <input type="text" id="upload-version" placeholder="1.0.0" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="upload-description">Description</label>
                            <textarea id="upload-description" rows="3"></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="upload-license">Licence</label>
                            <select id="upload-license">
                                <option value="MIT">MIT</option>
                                <option value="Apache-2.0">Apache 2.0</option>
                                <option value="GPL-3.0">GPL v3</option>
                                <option value="BSD-3-Clause">BSD 3-Clause</option>
                                <option value="Proprietary">Propriétaire</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="upload-file">Fichier package (.zv)</label>
                            <input type="file" id="upload-file" accept=".zv" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="upload-readme">README (optionnel)</label>
                            <input type="file" id="upload-readme" accept=".md,.txt">
                        </div>
                        
                        <div class="form-group">
                            <label for="upload-license-file">Fichier de licence (optionnel)</label>
                            <input type="file" id="upload-license-file">
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="closeUploadModal()">
                                Annuler
                            </button>
                            <button type="submit" class="btn btn-primary" id="upload-btn">
                                <i class="fas fa-upload"></i> Uploader
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Ajouter le modal au DOM
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer);
    
    // Ouvrir le modal
    const modal = document.getElementById('upload-modal');
    const overlay = document.getElementById('modal-overlay');
    
    modal.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Gérer la soumission du formulaire
    const form = document.getElementById('upload-form');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const uploadBtn = document.getElementById('upload-btn');
        const originalText = uploadBtn.innerHTML;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Upload en cours...';
        uploadBtn.disabled = true;
        
        try {
            await uploadPackage();
        } finally {
            uploadBtn.innerHTML = originalText;
            uploadBtn.disabled = false;
        }
    });
}

function closeUploadModal() {
    const modal = document.getElementById('upload-modal');
    const overlay = document.getElementById('modal-overlay');
    
    if (modal && modal.parentNode) {
        modal.parentNode.remove();
    }
    
    overlay.classList.remove('active');
    document.body.style.overflow = '';
}

async function uploadPackage() {
    const name = document.getElementById('upload-name').value;
    const version = document.getElementById('upload-version').value;
    const description = document.getElementById('upload-description').value;
    const license = document.getElementById('upload-license').value;
    const fileInput = document.getElementById('upload-file');
    const readmeInput = document.getElementById('upload-readme');
    const licenseInput = document.getElementById('upload-license-file');
    
    if (!name || !version || !fileInput.files[0]) {
        showNotification('Veuillez remplir tous les champs obligatoires', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('version', version);
    formData.append('description', description);
    formData.append('license', license);
    formData.append('file', fileInput.files[0]);
    
    if (readmeInput.files[0]) {
        formData.append('readme', readmeInput.files[0]);
    }
    
    if (licenseInput.files[0]) {
        formData.append('license', licenseInput.files[0]);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/packages/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${currentToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification('Package uploadé avec succès !', 'success');
            closeUploadModal();
            loadPackages(); // Recharger la liste
        } else {
            await handleAPIError(response);
        }
    } catch (error) {
        showNotification('Erreur lors de l\'upload', 'error');
    }
}

// Utilitaires
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return 'Date inconnue';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Exposer les fonctions globales
window.openPackageDetails = openPackageDetails;
window.closePackageModal = closePackageModal;
window.downloadPackage = downloadPackage;
window.showUploadModal = showUploadModal;
window.closeUploadModal = closeUploadModal;
