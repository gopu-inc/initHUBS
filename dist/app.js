document.addEventListener('DOMContentLoaded', async () => {
    // Vérifier l'authentification
    const user = await window.initHUB.getCurrentUser();
    if (!user) {
        window.location.href = 'login.html';
        return;
    }
    
    // Afficher l'utilisateur
    document.getElementById('userName').textContent = user.username;
    document.getElementById('userEmail').textContent = user.email;
    
    // Charger les données
    loadDashboard();
    
    // Navigation
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.getAttribute('data-page');
            showPage(page);
        });
    });
    
    // Bouton logout
    document.getElementById('logoutBtn').addEventListener('click', () => {
        window.initHUB.logout();
        window.location.href = 'index.html';
    });
});

async function loadDashboard() {
    try {
        const [dashboard, projects, sites, health] = await Promise.all([
            window.initHUB.getDashboard(),
            window.initHUB.listProjects(),
            window.initHUB.listSites(),
            window.initHUB.health()
        ]);
        
        // Mettre à jour les stats
        document.getElementById('projectsCount').textContent = dashboard.total_repos || 0;
        document.getElementById('sitesCount').textContent = sites.length || 0;
        
        // Afficher les projets récents
        const projectsList = document.getElementById('projectsList');
        projects.projects?.slice(0, 5).forEach(project => {
            projectsList.innerHTML += `
                <div class="card">
                    <h4>${project.name}</h4>
                    <p>${project.description || 'Aucune description'}</p>
                    <div class="project-meta">
                        <span><i class="fas fa-code-branch"></i> ${project.files_count || 0} fichiers</span>
                        <a href="#" onclick="openProject('${project.full_name}')">Ouvrir</a>
                    </div>
                </div>
            `;
        });
        
        // Statut du serveur
        document.getElementById('serverStatus').innerHTML = `
            <span class="status-online">🟢 En ligne</span>
            <small>Version: ${health.version}</small>
        `;
        
    } catch (error) {
        console.error('Erreur chargement:', error);
    }
}

function showPage(page) {
    // Cacher toutes les pages
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    
    // Afficher la page demandée
    document.getElementById(`${page}Page`).style.display = 'block';
    
    // Mettre à jour le menu actif
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-page') === page) {
            item.classList.add('active');
        }
    });
    
    // Charger les données spécifiques à la page
    switch(page) {
        case 'projects':
            loadProjects();
            break;
        case 'hosting':
            loadHosting();
            break;
        case 'terminal':
            initTerminal();
            break;
        case 'files':
            loadFiles();
            break;
    }
}

async function loadProjects() {
    const projects = await window.initHUB.listProjects();
    const container = document.getElementById('projectsContainer');
    
    container.innerHTML = `
        <button class="btn primary" onclick="createProject()">
            <i class="fas fa-plus"></i> Nouveau projet
        </button>
    `;
    
    projects.projects?.forEach(project => {
        container.innerHTML += `
            <div class="card project-card">
                <div class="project-header">
                    <h3>${project.name}</h3>
                    <span class="badge">${project.is_private ? '🔒 Privé' : '🌐 Public'}</span>
                </div>
                <p>${project.description || ''}</p>
                <div class="project-stats">
                    <span><i class="fas fa-file"></i> ${project.files_count || 0} fichiers</span>
                    <span><i class="fas fa-database"></i> ${(project.total_size / 1024).toFixed(1)} KB</span>
                </div>
                <div class="project-actions">
                    <button class="btn" onclick="pushProject('${project.name}')">
                        <i class="fas fa-upload"></i> Push
                    </button>
                    <button class="btn" onclick="pullProject('${project.name}')">
                        <i class="fas fa-download"></i> Pull
                    </button>
                    <a href="https://hubs-ja2g.onrender.com/projects/${project.full_name}" 
                       class="btn" target="_blank">
                        <i class="fas fa-external-link-alt"></i> Ouvrir
                    </a>
                </div>
            </div>
        `;
    });
}

async function loadHosting() {
    const sites = await window.initHUB.listSites();
    const container = document.getElementById('hostingContainer');
    
    container.innerHTML = `
        <button class="btn primary" onclick="createSite()">
            <i class="fas fa-plus"></i> Créer un site
        </button>
    `;
    
    sites.forEach(site => {
        container.innerHTML += `
            <div class="card">
                <h3>${site.name}</h3>
                <p>${site.domain}</p>
                <div class="site-status">
                    <span class="status-online">🟢 ${site.status}</span>
                    <a href="https://hubs-ja2g.onrender.com${site.url}" target="_blank">
                        <i class="fas fa-external-link-alt"></i> Visiter
                    </a>
                </div>
            </div>
        `;
    });
}

function initTerminal() {
    try {
        const terminal = window.initHUB.createTerminal();
        const output = document.getElementById('terminalOutput');
        
        terminal.onMessage(data => {
            if (data.type === 'output') {
                output.innerHTML += `<div>${data.content}</div>`;
                output.scrollTop = output.scrollHeight;
            }
        });
        
        document.getElementById('terminalForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const input = document.getElementById('terminalInput');
            const command = input.value.trim();
            
            if (command) {
                terminal.send(command);
                output.innerHTML += `<div class="prompt">$ ${command}</div>`;
                input.value = '';
            }
        });
        
    } catch (error) {
        document.getElementById('terminalOutput').innerHTML = `
            <div class="error">Erreur terminal: ${error.message}</div>
        `;
    }
}

// Fonctions utilitaires
function createProject() {
    const name = prompt('Nom du projet:');
    if (name) {
        window.initHUB.createRepository({ name, description: '', is_private: true })
            .then(() => {
                alert('Projet créé !');
                loadProjects();
            })
            .catch(err => alert('Erreur: ' + err.message));
    }
}

function createSite() {
    const name = prompt('Nom du site:');
    if (name) {
        window.initHUB.createSite(name)
            .then(() => {
                alert('Site créé !');
                loadHosting();
            })
            .catch(err => alert('Erreur: ' + err.message));
    }
}

function pushProject(name) {
    // Simuler le push
    alert(`Pushing ${name}...`);
}

function pullProject(name) {
    // Simuler le pull
    alert(`Pulling ${name}...`);
}

function askCopilot() {
    const question = document.getElementById('copilotQuestion').value;
    if (question) {
        window.initHUB.askCopilot(question)
            .then(response => {
                document.getElementById('copilotAnswer').innerHTML = `
                    <div class="copilot-response">
                        <strong>🤖 Copilot:</strong>
                        <p>${response.response}</p>
                    </div>
                `;
            });
    }
}
