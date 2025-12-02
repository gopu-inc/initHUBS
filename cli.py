#!/usr/bin/env python3
"""
initHUB CLI - Client complet avec interface moderne
Version 5.0 - Support complet hébergement web, terminal, gestion de fichiers
FORCÉ À LA PRODUCTION : https://hubs-ja2g.onrender.com
"""

import os
import re
import sys
import json
import time
import shlex
import requests
import argparse
import webbrowser
import getpass
import zipfile
import tarfile
import tempfile
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# ============================================================================
# 🎨 SYSTÈME DE COULEURS ET ANIMATIONS
# ============================================================================

class Colors:
    """Codes de couleurs ANSI"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Animations:
    """Animations de chargement"""
    SPINNERS = ["🪖", "💫", "🚀", "🔧", "⚡", "🌟", "🎯", "🔥"]
    
    def __init__(self):
        self.stop_spinner = False
    
    def loading_spinner(self, message="Chargement"):
        """Affiche un spinner animé"""
        self.stop_spinner = False
        
        def spinner():
            i = 0
            while not self.stop_spinner:
                dots = '.' * ((i % 3) + 1)
                spaces = ' ' * (3 - (i % 3))
                sys.stdout.write(f"\r{Colors.CYAN}{self.SPINNERS[i % len(self.SPINNERS)]}{Colors.END} {message}{Colors.YELLOW}{dots}{spaces}{Colors.END}")
                sys.stdout.flush()
                time.sleep(0.2)
                i += 1
        
        spinner_thread = threading.Thread(target=spinner)
        spinner_thread.start()
        return spinner_thread
    
    def stop_loading(self, thread, message="✅ Terminé"):
        """Arrête le spinner et affiche un message"""
        self.stop_spinner = True
        thread.join()
        sys.stdout.write(f"\r{message}{' ' * 50}\n")
        sys.stdout.flush()

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """Affiche un message d'information"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    """Affiche un message d'avertissement"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_table(headers, rows):
    """Affiche un tableau formaté"""
    # Calculer les largeurs de colonnes
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Afficher l'en-tête
    header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in col_widths)
    
    print(f"{Colors.CYAN}{header_line}{Colors.END}")
    print(f"{Colors.CYAN}{separator}{Colors.END}")
    
    # Afficher les lignes
    for row in rows:
        row_line = " | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row))
        print(row_line)

def print_banner():
    """Affiche la bannière d'accueil"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    🚀 initHUB Cloud CLI 🪖
{Colors.END}
{Colors.MAGENTA}    Plateforme Cloud Enterprise Ultimate{Colors.END}
{Colors.YELLOW}    Version 5.0 | Hébergement Web + Terminal{Colors.END}
{Colors.BLUE}    URL serveur: https://hubs-ja2g.onrender.com{Colors.END}
{Colors.RED}    ⚠️  CONNECTÉ À LA PRODUCTION{Colors.END}
"""
    print(banner)

# ============================================================================
# ⚙️ CONFIGURATION CLIENT - URL DE PRODUCTION FORCÉE
# ============================================================================

class CLIConfig:
    # ✅ URL DE PRODUCTION FORCÉE - PAS DE LOCALHOST
    DEFAULT_SERVER = "https://hubs-ja2g.onrender.com"
    
    CONFIG_DIR = Path.home() / ".inithub"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    TOKEN_FILE = CONFIG_DIR / "token.json"
    CACHE_DIR = CONFIG_DIR / "cache"
    DOWNLOAD_DIR = Path.home() / "inithub_downloads"
    
    def __init__(self):
        self.config_dir = self.CONFIG_DIR
        self.config_dir.mkdir(exist_ok=True)
        self.cache_dir = self.CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
        self.download_dir = self.DOWNLOAD_DIR
        self.download_dir.mkdir(exist_ok=True)
        self._load_config()
    
    def _load_config(self):
        # FORCE l'URL de production, ignore toute ancienne configuration
        self.data = {
            "server_url": self.DEFAULT_SERVER,  # ✅ TOUJOURS la production
            "default_download_dir": str(self.DOWNLOAD_DIR),
            "auto_open_browser": True,
            "theme": "dark"
        }
        
        # Si un fichier config existe, on garde seulement les autres paramètres
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    existing_data = json.load(f)
                    # Garde les autres paramètres sauf server_url
                    for key, value in existing_data.items():
                        if key != "server_url":
                            self.data[key] = value
            except:
                pass  # Si erreur, on garde la config par défaut
        
        self.save_config()
    
    def save_config(self):
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def save_token(self, token_data):
        with open(self.TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    def load_token(self):
        if self.TOKEN_FILE.exists():
            try:
                with open(self.TOKEN_FILE, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def clear_token(self):
        if self.TOKEN_FILE.exists():
            self.TOKEN_FILE.unlink()
    
    def get_server_url(self):
        """Retourne TOUJOURS l'URL de production"""
        return self.DEFAULT_SERVER  # ✅ FORCE la production
    
    def set_server_url(self, url):
        """Ignoré - on force toujours la production"""
        print_warning("URL serveur verrouillée sur la production")
        print_info(f"Utilisation de: {self.DEFAULT_SERVER}")
        return False

config = CLIConfig()

# ============================================================================
# 🔌 CLIENT API COMPLET - CONNECTÉ À LA PRODUCTION
# ============================================================================

class InitHUBClient:
    def __init__(self):
        self.base_url = config.get_server_url() + "/api"
        print_info(f"🔗 Connexion à: {self.base_url}")
        self.token_data = config.load_token()
        self.session = requests.Session()
        self.animations = Animations()
        
        if self.token_data:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token_data.get('access_token')}"
            })
    
    def _handle_response(self, response):
        try:
            data = response.json()
        except:
            data = {"detail": response.text}
        
        if response.status_code >= 400:
            error_msg = data.get('detail', 'Erreur inconnue')
            raise Exception(f"API Error {response.status_code}: {error_msg}")
        
        return data
    
    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            raise Exception(f"❌ Impossible de se connecter au serveur à {self.base_url}")
        except Exception as e:
            raise Exception(f"Erreur API {endpoint}: {e}")
    
    # 🔐 AUTHENTIFICATION
    def login(self, email: str, password: str) -> bool:
        spinner = self.animations.loading_spinner("Connexion à initHUB Cloud")
        try:
            data = self._make_request("POST", "/auth/login", 
                                    json={"email": email, "password": password})
            
            config.save_token(data)
            self.session.headers.update({
                "Authorization": f"Bearer {data['access_token']}"
            })
            
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Connecté en tant que {email}{Colors.END}")
            return True
            
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur connexion: {e}{Colors.END}")
            return False
    
    def register(self, username: str, email: str, password: str, full_name: str = "") -> bool:
        spinner = self.animations.loading_spinner("Création de compte initHUB")
        try:
            self._make_request("POST", "/auth/register",
                             json={
                                 "username": username,
                                 "email": email,
                                 "password": password,
                                 "full_name": full_name
                             })
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Compte créé: {username}{Colors.END}")
            return True
            
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur inscription: {e}{Colors.END}")
            return False
    
    def logout(self):
        config.clear_token()
        self.session.headers.pop("Authorization", None)
        return True
    
    def get_current_user(self):
        try:
            user = self._make_request("GET", "/users/me")
            return user
        except:
            return None
    
    # 🏠 HÉBERGEMENT WEB
    def create_hosting_site(self, name: str, domain: str = None, site_type: str = "static"):
        spinner = self.animations.loading_spinner("Création du site web")
        try:
            result = self._make_request("POST", "/hosting/sites",
                                json={
                                    "name": name,
                                    "domain": domain,
                                    "type": site_type
                                })
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Site web créé{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur création site: {e}{Colors.END}")
            raise
    
    def list_hosting_sites(self):
        spinner = self.animations.loading_spinner("Récupération des sites")
        try:
            result = self._make_request("GET", "/hosting/sites")
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Sites chargés{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur chargement sites: {e}{Colors.END}")
            raise
    
    def get_hosting_status(self):
        spinner = self.animations.loading_spinner("Vérification hébergement")
        try:
            result = self._make_request("GET", "/hosting/status")
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Statut hébergement{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur statut: {e}{Colors.END}")
            raise
    
    # 📁 GESTION DE FICHIERS
    def list_files(self, path: str = ""):
        spinner = self.animations.loading_spinner("Liste des fichiers")
        try:
            params = {"path": path} if path else {}
            result = self._make_request("GET", "/files", params=params)
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Fichiers chargés{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur liste fichiers: {e}{Colors.END}")
            raise
    
    def upload_file(self, file_path: str, remote_path: str = ""):
        spinner = self.animations.loading_spinner("Upload du fichier")
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f)}
                data = {'path': remote_path} if remote_path else {}
                result = self._make_request("POST", "/files/upload", 
                                         files=files, data=data)
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Fichier uploadé{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur upload: {e}{Colors.END}")
            raise
    
    # 📊 DASHBOARD
    def get_dashboard(self):
        spinner = self.animations.loading_spinner("Chargement dashboard")
        try:
            result = self._make_request("GET", "/dashboard")
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Dashboard chargé{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur dashboard: {e}{Colors.END}")
            raise
    
    # 🖥️ SYSTÈME
    def health_check(self):
        spinner = self.animations.loading_spinner("Vérification du serveur")
        try:
            result = self._make_request("GET", "/health")
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Serveur opérationnel{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Serveur hors ligne: {e}{Colors.END}")
            raise
    
    def get_system_info(self):
        spinner = self.animations.loading_spinner("Informations système")
        try:
            result = self._make_request("GET", "/system/info")
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Informations système{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur système: {e}{Colors.END}")
            raise
    
    def get_nginx_status(self):
        spinner = self.animations.loading_spinner("Statut Nginx")
        try:
            result = self._make_request("GET", "/system/nginx/status")
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Statut Nginx{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur Nginx: {e}{Colors.END}")
            raise
    
    # 📚 REPOSITORIES
    def create_repo(self, name: str, description: str = "", is_private: bool = False):
        spinner = self.animations.loading_spinner("Création du repository")
        try:
            result = self._make_request("POST", "/repos",
                                json={
                                    "name": name,
                                    "description": description,
                                    "is_private": is_private,
                                    "auto_init": True
                                })
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Repository créé{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur création: {e}{Colors.END}")
            raise
    
    def list_repos(self, page: int = 1, per_page: int = 30):
        spinner = self.animations.loading_spinner("Récupération des repositories")
        try:
            result = self._make_request("GET", f"/repos?page={page}&per_page={per_page}")
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Repositories chargés{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur chargement: {e}{Colors.END}")
            raise
    
    # 🤖 COPILOT
    def ask_copilot(self, question: str, context: str = "", max_length: int = 150, language: str = "auto"):
        spinner = self.animations.loading_spinner("Copilot réfléchit")
        try:
            result = self._make_request("POST", "/copilot/ask",
                                json={
                                    "question": question,
                                    "context": context,
                                    "max_length": max_length,
                                    "language": language
                                })
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Réponse reçue{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur Copilot: {e}{Colors.END}")
            raise
    
    def copilot_health(self):
        spinner = self.animations.loading_spinner("Vérification Copilot")
        try:
            result = self._make_request("GET", "/copilot/health")
            self.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Copilot vérifié{Colors.END}")
            return result
        except Exception as e:
            self.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur vérification: {e}{Colors.END}")
            raise

api_client = InitHUBClient()

# ============================================================================
# 📄 SYSTÈME .SSF AVANCÉ
# ============================================================================

def create_ssf_manifest(project_name: str, project_type: str = "projet", 
                       env: str = "python", description: str = "") -> str:
    """Crée un manifest .ssf avancé"""
    
    ssf_content = f"""init.conf(
    [name: {project_name}]
    {{version: 1.0.0}}
    :{{{{description: {description or f"Projet {project_name}"}}}}}
    [{{type: {project_type}}}]
    [{{env: {env}}}]
    
    # Dépendances
    [{{dep=>env: requests, numpy}}]
    
    # Structure de fichiers
    files: [
        - *.py
        - *.md
        - requirements.txt
        - !__pycache__/**
        - !*.pyc
    ]
    
    # Configuration
    config: {{
        main: main.py
        language: {env}
    }}
)
"""
    return ssf_content

def create_initignore(project_path: str):
    """Crée un fichier .initignore par défaut"""
    ignore_content = """# Fichiers à ignorer pour initHUB
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store
Thumbs.db
*.log
.cache
.coverage
.pytest_cache/
build/
dist/
*.egg-info/
"""
    
    ignore_path = Path(project_path) / ".initignore"
    with open(ignore_path, 'w', encoding='utf-8') as f:
        f.write(ignore_content)
    
    return ignore_path

def create_web_project_template(project_path: str, project_type: str = "static"):
    """Crée un template de projet web"""
    project_path = Path(project_path)
    
    # Structure de base
    (project_path / "public_html").mkdir(exist_ok=True)
    (project_path / "public_html" / "css").mkdir(exist_ok=True)
    (project_path / "public_html" / "js").mkdir(exist_ok=True)
    (project_path / "public_html" / "images").mkdir(exist_ok=True)
    
    # index.html
    index_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mon Site initHUB</title>
    <link rel="stylesheet" href="css/style.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        
        .hero {
            max-width: 1200px;
            margin: 0 auto;
            padding: 4rem 2rem;
            text-align: center;
        }
        
        h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
        }
        
        .btn {
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 2rem;
            transition: transform 0.3s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🚀 Bienvenue sur initHUB Cloud!</h1>
        <p>Votre site web est hébergé sur initHUB Cloud Enterprise</p>
        <a href="https://inithub.com" class="btn">Documentation</a>
    </div>
    
    <script src="js/main.js"></script>
</body>
</html>"""
    
    (project_path / "public_html" / "index.html").write_text(index_content)
    
    # style.css
    css_content = """/* Style principal */
.hero {
    animation: fadeIn 1s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}"""
    
    (project_path / "public_html" / "css" / "style.css").write_text(css_content)
    
    # main.js
    js_content = """// Script principal
console.log('🚀 Site initHUB chargé!');

// Animation simple
document.addEventListener('DOMContentLoaded', function() {
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.opacity = '0';
        setTimeout(() => {
            hero.style.transition = 'opacity 0.5s ease';
            hero.style.opacity = '1';
        }, 100);
    }
});"""
    
    (project_path / "public_html" / "js" / "main.js").write_text(js_content)
    
    return True

# ============================================================================
# 🚀 COMMANDES PRINCIPALES - TOUTES LES FONCTIONS
# ============================================================================

def handle_auth_login(args):
    """Connexion au serveur initHUB"""
    print_info(f"🌐 Connexion à: {config.get_server_url()}")
    
    email = args.email
    password = args.password
    
    # Si pas d'email/password, demander interactivement
    if not email:
        email = input(f"{Colors.CYAN}📧 Email: {Colors.END}")
    if not password:
        password = getpass.getpass(f"{Colors.CYAN}🔒 Mot de passe: {Colors.END}")
    
    if not email or not password:
        print_error("Email et mot de passe requis")
        return False
    
    success = api_client.login(email, password)
    
    if success and args.open:
        webbrowser.open(f"{config.get_server_url()}/app")
    
    return success

def handle_auth_register(args):
    """Inscription au serveur initHUB"""
    print_info(f"🌐 Création de compte sur: {config.get_server_url()}")
    
    username = args.username
    email = args.email
    password = args.password
    full_name = args.full_name or ""
    
    # Si pas de paramètres, demander interactivement
    if not username:
        username = input(f"{Colors.CYAN}👤 Username: {Colors.END}")
    if not email:
        email = input(f"{Colors.CYAN}📧 Email: {Colors.END}")
    if not password:
        password = getpass.getpass(f"{Colors.CYAN}🔒 Mot de passe: {Colors.END}")
    
    if not all([username, email, password]):
        print_error("Username, email et mot de passe requis")
        return False
    
    return api_client.register(username, email, password, full_name)

def handle_auth_logout(args):
    """Déconnexion"""
    success = api_client.logout()
    if success:
        print_success("Déconnexion réussie")
    else:
        print_error("Erreur déconnexion")
    return success

def handle_auth_whoami(args):
    """Affiche l'utilisateur connecté"""
    user = api_client.get_current_user()
    if user:
        print_success("Utilisateur connecté:")
        print(f"   {Colors.CYAN}📛 Username:{Colors.END} {user['username']}")
        print(f"   {Colors.BLUE}📧 Email:{Colors.END} {user['email']}")
        if user.get('full_name'):
            print(f"   {Colors.GREEN}👤 Nom complet:{Colors.END} {user['full_name']}")
        print(f"   {Colors.YELLOW}🆔 ID:{Colors.END} {user['id']}")
        print(f"   {Colors.MAGENTA}📅 Créé le:{Colors.END} {user['created_at']}")
        return True
    else:
        print_error("Non connecté. Utilisez 'inithub auth login'")
        return False

def handle_auth_status(args):
    """Statut de la connexion"""
    print(f"{Colors.CYAN}🌐 Serveur:{Colors.END} {config.get_server_url()}")
    print(f"{Colors.RED}⚠️  CONNECTÉ À LA PRODUCTION{Colors.END}")
    
    try:
        health = api_client.health_check()
        print_success("Serveur initHUB Cloud en ligne")
        print(f"{Colors.BLUE}📊 Version:{Colors.END} {health.get('version', 'N/A')}")
        
        user = api_client.get_current_user()
        if user:
            print_success(f"Connecté en tant que: {user['username']}")
            
            # Afficher le statut des services
            services = health.get('services', {})
            print(f"\n{Colors.YELLOW}🛠️ Services:{Colors.END}")
            for service, status in services.items():
                status_icon = "🟢" if status in ['online', 'running'] else "🔴"
                print(f"   {status_icon} {service}: {status}")
        else:
            print_warning("Non connecté")
        
        return True
    except Exception as e:
        print_error(f"Serveur hors ligne: {e}")
        print_info("Vérifiez que le serveur est disponible à: https://hubs-ja2g.onrender.com")
        return False

def handle_hosting_create(args):
    """Crée un nouveau site d'hébergement"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    name = args.name
    if not name:
        print_error("Nom du site requis")
        return False
    
    domain = args.domain
    site_type = args.type or "static"
    
    try:
        site = api_client.create_hosting_site(name, domain, site_type)
        
        print_success(f"Site web créé: {site['name']}")
        print(f"{Colors.BLUE}🌐 URL:{Colors.END} {config.get_server_url()}{site['url']}")
        print(f"{Colors.YELLOW}🔧 Type:{Colors.END} {site['type']}")
        print(f"{Colors.GREEN}📅 Créé le:{Colors.END} {site['created_at']}")
        
        # Créer une structure de projet local
        if args.create_local:
            local_path = Path(name)
            if local_path.exists() and not args.force:
                print_warning(f"Le dossier '{name}' existe déjà. Utilisez --force pour écraser.")
            else:
                create_web_project_template(name)
                print_info(f"Structure de projet créée dans: ./{name}")
        
        if args.open:
            webbrowser.open(f"{config.get_server_url()}{site['url']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur création site: {e}")
        return False

def handle_hosting_list(args):
    """Liste les sites d'hébergement"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    try:
        sites = api_client.list_hosting_sites()
        
        if not sites:
            print_info("Aucun site d'hébergement")
            return True
        
        print(f"{Colors.CYAN}🌐 Sites d'hébergement ({len(sites)}):{Colors.END}")
        
        headers = ["Nom", "Domaine", "Type", "Statut", "URL"]
        rows = []
        
        for site in sites:
            rows.append([
                site['name'],
                site['domain'],
                site['type'],
                f"{Colors.GREEN}🟢{Colors.END}" if site['status'] == 'active' else f"{Colors.RED}🔴{Colors.END}",
                f"{config.get_server_url()}{site['url']}"
            ])
        
        print_table(headers, rows)
        
        if args.open and sites:
            webbrowser.open(f"{config.get_server_url()}{sites[0]['url']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur liste sites: {e}")
        return False

def handle_hosting_status(args):
    """Statut de l'hébergement"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    try:
        status = api_client.get_hosting_status()
        
        print_success(f"Statut hébergement pour {status['user']}")
        print(f"{Colors.BLUE}📊 Sites actifs:{Colors.END} {status['active_sites']}")
        print(f"{Colors.GREEN}💾 Espace utilisé:{Colors.END} {status['disk_usage']}")
        
        if status.get('monthly_traffic'):
            print(f"{Colors.YELLOW}📈 Trafic mensuel:{Colors.END} {status['monthly_traffic']}")
        
        if status.get('limits'):
            limits = status['limits']
            print(f"\n{Colors.CYAN}📋 Limites:{Colors.END}")
            print(f"   📦 Stockage max: {limits['max_storage']}")
            print(f"   🌐 Sites max: {limits['max_sites']}")
            if limits.get('max_databases'):
                print(f"   🗄️  Bases de données max: {limits['max_databases']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur statut hébergement: {e}")
        return False

def handle_files_list(args):
    """Liste les fichiers"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    try:
        files_data = api_client.list_files(args.path)
        files = files_data.get('files', [])
        current_path = files_data.get('path', '')
        
        if not files:
            print_info(f"Aucun fichier dans '{current_path or 'racine'}'")
            return True
        
        print(f"{Colors.CYAN}📁 Fichiers ({len(files)}) dans '{current_path or '/'}':{Colors.END}")
        
        headers = ["Nom", "Type", "Taille", "Modifié"]
        rows = []
        
        for file in files:
            file_type = "📁" if file['type'] == 'directory' else "📄"
            size = f"{file['size'] / 1024:.1f} KB" if file['size'] > 0 else "-"
            
            mod_time = datetime.fromtimestamp(file['modified']).strftime('%Y-%m-%d %H:%M')
            
            rows.append([
                f"{file_type} {file['name']}",
                file['type'],
                size,
                mod_time
            ])
        
        print_table(headers, rows)
        
        return True
    except Exception as e:
        print_error(f"Erreur liste fichiers: {e}")
        return False

def handle_files_upload(args):
    """Upload un fichier"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    file_path = args.file
    if not Path(file_path).exists():
        print_error(f"Fichier non trouvé: {file_path}")
        return False
    
    try:
        result = api_client.upload_file(file_path, args.path)
        
        print_success(f"Fichier uploadé: {result['filename']}")
        print(f"{Colors.BLUE}📁 Chemin:{Colors.END} {result['path']}")
        print(f"{Colors.GREEN}📦 Taille:{Colors.END} {result['size']} bytes")
        if result.get('url'):
            print(f"{Colors.YELLOW}🌐 URL:{Colors.END} {config.get_server_url()}{result['url']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur upload: {e}")
        return False

def handle_dashboard_show(args):
    """Affiche le dashboard"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    try:
        dashboard = api_client.get_dashboard()
        
        print_success("Dashboard initHUB Cloud")
        print(f"{Colors.BLUE}📊 Vue d'ensemble:{Colors.END}")
        print(f"   📚 Repositories: {dashboard['total_repos']}")
        print(f"   ⭐ Stars: {dashboard['total_stars']}")
        print(f"   🔀 Forks: {dashboard['total_forks']}")
        
        if dashboard.get('user_activity'):
            activity = dashboard['user_activity']
            print(f"\n{Colors.GREEN}📈 Votre activité:{Colors.END}")
            if activity.get('repos_created'):
                print(f"   📁 Repos créés: {activity['repos_created']}")
            if activity.get('repos_starred'):
                print(f"   ⭐ Repos starés: {activity['repos_starred']}")
        
        if args.open:
            webbrowser.open(f"{config.get_server_url()}/app")
        
        return True
    except Exception as e:
        print_error(f"Erreur dashboard: {e}")
        return False

def handle_system_health(args):
    """Vérifie la santé du système"""
    try:
        health = api_client.health_check()
        
        print_success("initHUB Cloud - Santé du système")
        print(f"{Colors.BLUE}📊 Version:{Colors.END} {health.get('version', 'N/A')}")
        print(f"{Colors.GREEN}📅 Date:{Colors.END} {health.get('timestamp', 'N/A')}")
        
        if health.get('services'):
            print(f"\n{Colors.YELLOW}🛠️ Services:{Colors.END}")
            for service, status in health['services'].items():
                status_icon = "🟢" if status in ['online', 'running'] else "🔴"
                print(f"   {status_icon} {service}: {status}")
        
        if health.get('resources'):
            print(f"\n{Colors.CYAN}📦 Ressources:{Colors.END}")
            for resource, value in health['resources'].items():
                print(f"   📊 {resource}: {value}")
        
        return True
    except Exception as e:
        print_error(f"Erreur vérification santé: {e}")
        return False

def handle_system_info(args):
    """Informations système détaillées"""
    try:
        info = api_client.get_system_info()
        
        print_success("Informations système détaillées")
        
        if info.get('system'):
            print(f"\n{Colors.BLUE}💻 Système:{Colors.END}")
            for key, value in info['system'].items():
                print(f"   📝 {key}: {value}")
        
        if info.get('resources'):
            print(f"\n{Colors.GREEN}📊 Ressources:{Colors.END}")
            for resource_type, details in info['resources'].items():
                print(f"   {resource_type.upper()}:")
                for key, value in details.items():
                    print(f"     📌 {key}: {value}")
        
        if info.get('inithub'):
            print(f"\n{Colors.YELLOW}🚀 initHUB:{Colors.END}")
            init_info = info['inithub']
            if init_info.get('storage_paths'):
                print("   📁 Chemins de stockage:")
                for name, path in init_info['storage_paths'].items():
                    print(f"     📂 {name}: {path}")
            
            if init_info.get('git_repos_count'):
                print(f"   📚 Repos Git: {init_info['git_repos_count']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur informations système: {e}")
        return False

def handle_system_nginx(args):
    """Statut de nginx"""
    try:
        nginx_status = api_client.get_nginx_status()
        
        if nginx_status['running']:
            print_success("Nginx est en cours d'exécution")
            print(f"{Colors.GREEN}🌐 Sites activés:{Colors.END} {nginx_status['sites_enabled']}")
            print(f"{Colors.BLUE}📁 Configuration:{Colors.END} {nginx_status['config_path']}")
        else:
            print_error("Nginx n'est pas en cours d'exécution")
            if nginx_status.get('error'):
                print(f"   {Colors.RED}Erreur:{Colors.END} {nginx_status['error']}")
        
        return nginx_status['running']
    except Exception as e:
        print_error(f"Erreur statut nginx: {e}")
        return False

def handle_repo_create(args):
    """Crée un nouveau repository"""
    name = args.name
    description = args.description or ""
    is_private = args.private
    
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    try:
        repo = api_client.create_repo(name, description, is_private)
        
        print_success(f"Repository créé: {repo['full_name']}")
        print(f"{Colors.BLUE}📝 Description:{Colors.END} {repo['description'] or 'Aucune description'}")
        print(f"{Colors.YELLOW}🔒 Visibilité:{Colors.END} {'🔒 Privé' if repo['is_private'] else '🌐 Public'}")
        print(f"{Colors.CYAN}🌐 URL:{Colors.END} {repo['html_url']}")
        print(f"{Colors.GREEN}📅 Créé le:{Colors.END} {repo['created_at']}")
        
        if args.open:
            webbrowser.open(repo['html_url'])
        
        return True
    except Exception as e:
        print_error(f"Erreur création repository: {e}")
        return False

def handle_repo_list(args):
    """Liste les repositories"""
    try:
        repos = api_client.list_repos()
        
        if not repos:
            print_info("Aucun repository trouvé")
            return True
        
        print(f"{Colors.CYAN}📁 Repositories ({len(repos)}):{Colors.END}")
        print("─" * 80)
        
        for repo in repos:
            visibility = "🔒" if repo['is_private'] else "🌐"
            print(f"{visibility} {Colors.BOLD}{repo['full_name']}{Colors.END}")
            
            if repo['description']:
                print(f"   {Colors.BLUE}📝{Colors.END} {repo['description']}")
            
            stats = []
            if repo.get('stars_count', 0) > 0:
                stats.append(f"{Colors.YELLOW}⭐ {repo['stars_count']}{Colors.END}")
            if repo.get('forks_count', 0) > 0:
                stats.append(f"{Colors.GREEN}🔀 {repo['forks_count']}{Colors.END}")
            if repo.get('watchers_count', 0) > 0:
                stats.append(f"{Colors.CYAN}👁️ {repo['watchers_count']}{Colors.END}")
            
            if stats:
                print(f"   {' '.join(stats)}")
            
            print(f"   {Colors.MAGENTA}📅 Mis à jour:{Colors.END} {repo.get('updated_at', 'N/A')}")
            print()
        
        return True
    except Exception as e:
        print_error(f"Erreur liste repositories: {e}")
        return False

def handle_copilot_ask(args):
    """Pose une question à Copilot"""
    question = args.question
    context = args.context or ""
    
    # Si pas de question, demander interactivement
    if not question:
        question = input(f"{Colors.CYAN}🤖 Question pour Copilot: {Colors.END}")
    
    if not question:
        print_error("Question requise")
        return False
    
    try:
        # Vérifier d'abord la santé de Copilot avec animation
        health_spinner = api_client.animations.loading_spinner("Vérification Copilot")
        try:
            health = api_client.copilot_health()
            api_client.animations.stop_loading(health_spinner, f"{Colors.GREEN}✅ Copilot disponible{Colors.END}")
        except:
            api_client.animations.stop_loading(health_spinner, f"{Colors.RED}❌ Copilot indisponible{Colors.END}")
            return False
        
        if not health.get('online', False):
            print_error("Copilot n'est pas disponible")
            return False
        
        response = api_client.ask_copilot(question, context)
        
        print(f"\n{Colors.CYAN}🤖 Copilot 🪖:{Colors.END}")
        print("─" * 80)
        print(f"{Colors.WHITE}{response['response']}{Colors.END}")
        print("─" * 80)
        
        if response.get('copilot_online'):
            print(f"{Colors.GREEN}🟢 Copilot en ligne{Colors.END}")
        
        if response.get('timestamp'):
            print(f"{Colors.BLUE}📅 Réponse générée à:{Colors.END} {response['timestamp']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur Copilot: {e}")
        return False

def handle_copilot_health(args):
    """Vérifie l'état de Copilot"""
    try:
        health = api_client.copilot_health()
        
        status = f"{Colors.GREEN}🟢 EN LIGNE{Colors.END}" if health['online'] else f"{Colors.RED}🔴 HORS LIGNE{Colors.END}"
        print(f"{Colors.CYAN}🤖 Copilot:{Colors.END} {status}")
        print(f"{Colors.BLUE}🌐 URL:{Colors.END} {health['base_url']}")
        
        if health.get('timestamp'):
            print(f"{Colors.YELLOW}📅 Dernière vérification:{Colors.END} {health['timestamp']}")
        
        return health['online']
    except Exception as e:
        print_error(f"Erreur vérification Copilot: {e}")
        return False

def handle_init_project(args):
    """Initialise un nouveau projet avec manifest .ssf"""
    project_name = args.project_name or "mon-projet"
    project_type = args.type or "projet"
    env = args.env or "python"
    description = args.description or f"Projet {project_name}"
    
    project_path = Path(project_name)
    
    if project_path.exists() and not args.force:
        print_error(f"Le dossier '{project_name}' existe déjà. Utilisez --force pour écraser.")
        return False
    
    spinner = api_client.animations.loading_spinner("Initialisation du projet")
    
    try:
        # Créer la structure
        project_path.mkdir(exist_ok=True)
        
        # Créer le manifest .ssf
        ssf_content = create_ssf_manifest(project_name, project_type, env, description)
        ssf_path = project_path / "init.ssf"
        with open(ssf_path, 'w', encoding='utf-8') as f:
            f.write(ssf_content)
        
        # Créer .initignore
        ignore_path = create_initignore(project_path)
        
        # Créer des fichiers de base
        readme_content = f"# {project_name}\n\n{description}\n"
        with open(project_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Créer un fichier Python principal si env est python
        if env == "python":
            main_content = f'''"""
{project_name}
{description}
"""

def main():
    """Fonction principale"""
    print("🚀 Hello from initHUB!")

if __name__ == "__main__":
    main()
'''
            with open(project_path / "main.py", 'w', encoding='utf-8') as f:
                f.write(main_content)
        
        # Créer requirements.txt
        requirements_content = f"""# Dépendances pour {project_name}
requests>=2.28.0
python-dotenv>=0.21.0
"""
        with open(project_path / "requirements.txt", 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        # Si c'est un projet web, créer la structure web
        if project_type in ["web", "static", "api"]:
            create_web_project_template(project_path, project_type)
        
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Projet initialisé avec succès!{Colors.END}")
        
        print(f"\n{Colors.CYAN}📁 Structure créée:{Colors.END}")
        print(f"   📄 {ssf_path.name} {Colors.YELLOW}(manifest principal){Colors.END}")
        print(f"   📄 {ignore_path.name} {Colors.BLUE}(fichiers ignorés){Colors.END}")
        print(f"   📄 README.md {Colors.GREEN}(documentation){Colors.END}")
        if env == "python":
            print(f"   📄 main.py {Colors.MAGENTA}(point d'entrée){Colors.END}")
            print(f"   📄 requirements.txt {Colors.CYAN}(dépendances){Colors.END}")
        
        if project_type in ["web", "static", "api"]:
            print(f"   📁 public_html/ {Colors.YELLOW}(contenu web){Colors.END}")
        
        print(f"\n{Colors.YELLOW}🚀 Prochaines étapes:{Colors.END}")
        print(f"   1. {Colors.CYAN}cd {project_name}{Colors.END}")
        print(f"   2. {Colors.GREEN}inithub auth login{Colors.END} {Colors.YELLOW}(si pas connecté){Colors.END}")
        
        if args.create_repo:
            print(f"   3. {Colors.BLUE}inithub repo create --name {project_name} --description '{description}'{Colors.END}")
        
        if args.create_hosting and project_type in ["web", "static"]:
            print(f"   4. {Colors.MAGENTA}inithub hosting create --name {project_name} --type {project_type}{Colors.END}")
        
        return True
        
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur initialisation{Colors.END}")
        print_error(f"Erreur: {e}")
        return False

def handle_config_set(args):
    """Configure les paramètres du CLI"""
    if args.server:
        print_warning("URL serveur verrouillée sur la production")
        print_info(f"Utilisation de: {config.get_server_url()}")
        print_info("Le serveur ne peut pas être modifié - connecté à la production")
    
    if args.open_browser is not None:
        config.data["auto_open_browser"] = args.open_browser
        config.save_config()
        status = "activé" if args.open_browser else "désactivé"
        print_success(f"Ouverture automatique du navigateur: {status}")
    
    if args.theme:
        config.data["theme"] = args.theme
        config.save_config()
        print_success(f"Thème configuré: {args.theme}")
    
    return True

def handle_config_show(args):
    """Affiche la configuration actuelle"""
    print_success("Configuration initHUB CLI")
    print(f"{Colors.BLUE}🌐 Serveur:{Colors.END} {config.get_server_url()} {Colors.RED}(PRODUCTION VERROUILLÉE){Colors.END}")
    print(f"{Colors.GREEN}📁 Dossier config:{Colors.END} {config.config_dir}")
    print(f"{Colors.YELLOW}📥 Dossier téléchargements:{Colors.END} {config.download_dir}")
    
    print(f"\n{Colors.CYAN}⚙️ Paramètres:{Colors.END}")
    for key, value in config.data.items():
        if key not in ['server_url']:
            print(f"   📝 {key}: {value}")
    
    # Vérifier si connecté
    token = config.load_token()
    if token:
        print(f"\n{Colors.GREEN}🔐 Connecté:{Colors.END} Oui")
        user = api_client.get_current_user()
        if user:
            print(f"   👤 Utilisateur: {user['username']}")
            print(f"   📧 Email: {user['email']}")
    else:
        print(f"\n{Colors.YELLOW}🔐 Connecté:{Colors.END} Non")
    
    # Vérifier la connexion au serveur
    print(f"\n{Colors.MAGENTA}🔗 Test de connexion:{Colors.END}")
    try:
        health = api_client.health_check()
        print(f"   {Colors.GREEN}🟢 Serveur accessible{Colors.END}")
        print(f"   📊 Version: {health.get('version', 'N/A')}")
    except Exception as e:
        print(f"   {Colors.RED}🔴 Serveur inaccessible: {e}{Colors.END}")
    
    return True

def handle_web_open(args):
    """Ouvre l'interface web dans le navigateur"""
    page = args.page or "app"
    
    if page == "app":
        url = f"{config.get_server_url()}/app"
    elif page == "docs":
        url = f"{config.get_server_url()}/api/docs"
    elif page == "dashboard":
        url = f"{config.get_server_url()}/"
    else:
        url = f"{config.get_server_url()}/{page}"
    
    try:
        print_info(f"🌐 Ouverture de {url}")
        webbrowser.open(url)
        return True
    except Exception as e:
        print_error(f"Erreur ouverture navigateur: {e}")
        return False

def handle_apropos(args):
    """Affiche la documentation complète du CLI"""
    docs = f"""
{Colors.CYAN}{Colors.BOLD}📚 INITIUB CLI - DOCUMENTATION COMPLÈTE{Colors.END}

{Colors.RED}⚠️  IMPORTANT: CLI CONNECTÉ À LA PRODUCTION{Colors.END}
{Colors.BLUE}🌐 URL: {config.get_server_url()}{Colors.END}

{Colors.GREEN}🎯 QU'EST-CE QUE INITIUB ?{Colors.END}
initHUB est une plateforme cloud complète pour le développement collaboratif
avec Git, IA Copilot, gestion de projets, hébergement web et déploiement cloud.

{Colors.YELLOW}🚀 COMMANDES PRINCIPALES:{Colors.END}

{Colors.CYAN}🔐 AUTHENTIFICATION:{Colors.END}
  {Colors.BOLD}inithub auth login{Colors.END}          - Connexion au serveur
  {Colors.BOLD}inithub auth register{Colors.END}       - Création de compte
  {Colors.BOLD}inithub auth logout{Colors.END}         - Déconnexion
  {Colors.BOLD}inithub auth whoami{Colors.END}         - Utilisateur connecté
  {Colors.BOLD}inithub auth status{Colors.END}         - Statut de connexion

{Colors.BLUE}🌐 HÉBERGEMENT WEB:{Colors.END}
  {Colors.BOLD}inithub hosting create{Colors.END}      - Créer un site web
  {Colors.BOLD}inithub hosting list{Colors.END}        - Lister mes sites
  {Colors.BOLD}inithub hosting status{Colors.END}      - Statut hébergement

{Colors.MAGENTA}📁 GESTION DE FICHIERS:{Colors.END}
  {Colors.BOLD}inithub files list{Colors.END}          - Lister les fichiers
  {Colors.BOLD}inithub files upload{Colors.END}        - Uploader un fichier

{Colors.GREEN}📊 DASHBOARD:{Colors.END}
  {Colors.BOLD}inithub dashboard{Colors.END}           - Afficher le dashboard

{Colors.YELLOW}🛠️ SYSTÈME:{Colors.END}
  {Colors.BOLD}inithub system health{Colors.END}       - Santé du système
  {Colors.BOLD}inithub system info{Colors.END}         - Informations système
  {Colors.BOLD}inithub system nginx{Colors.END}        - Statut nginx

{Colors.CYAN}📁 GESTION PROJETS:{Colors.END}
  {Colors.BOLD}inithub init{Colors.END}                - Initialiser un nouveau projet
  {Colors.BOLD}inithub repo create{Colors.END}         - Créer un repository
  {Colors.BOLD}inithub repo list{Colors.END}           - Lister mes repositories

{Colors.MAGENTA}🤖 ASSISTANT IA:{Colors.END}
  {Colors.BOLD}inithub copilot ask{Colors.END}         - Poser une question à Copilot
  {Colors.BOLD}inithub copilot health{Colors.END}      - Vérifier Copilot

{Colors.BLUE}⚙️ CONFIGURATION:{Colors.END}
  {Colors.BOLD}inithub config set{Colors.END}          - Configurer le CLI
  {Colors.BOLD}inithub config show{Colors.END}         - Afficher la configuration
  {Colors.BOLD}inithub web open{Colors.END}            - Ouvrir l'interface web

{Colors.GREEN}📚 DOCUMENTATION:{Colors.END}
  {Colors.BOLD}inithub apropos{Colors.END}             - Cette documentation

{Colors.YELLOW}📄 FORMAT .SSF:{Colors.END}
Le format .ssf est le manifest initHUB pour décrire les projets.

{Colors.CYAN}🎯 EXEMPLES PRATIQUES:{Colors.END}

  1. {Colors.BOLD}Créer et héberger un site web:{Colors.END}
     {Colors.GREEN}inithub init --project-name mon-site --type web{Colors.END}
     {Colors.BLUE}inithub auth login{Colors.END}
     {Colors.MAGENTA}inithub hosting create --name mon-site --type static{Colors.END}
     {Colors.YELLOW}inithub web open{Colors.END}

  2. {Colors.BOLD}Gérer un projet Git:{Colors.END}
     {Colors.GREEN}inithub init --project-name mon-app{Colors.END}
     {Colors.BLUE}inithub auth login{Colors.END}
     {Colors.MAGENTA}inithub repo create --name mon-app{Colors.END}

  3. {Colors.BOLD}Utiliser Copilot:{Colors.END}
     {Colors.GREEN}inithub copilot ask --question "Comment créer une API REST?"{Colors.END}

  4. {Colors.BOLD}Gestion de fichiers cloud:{Colors.END}
     {Colors.GREEN}inithub files list{Colors.END}
     {Colors.BLUE}inithub files upload monfichier.txt{Colors.END}

{Colors.YELLOW}📞 SUPPORT:{Colors.END}
  • Documentation: {Colors.CYAN}inithub apropos{Colors.END}
  • Serveur: {Colors.GREEN}{config.get_server_url()}{Colors.END}
  • Interface web: {Colors.MAGENTA}inithub web open{Colors.END}

{Colors.RED}🔒 SÉCURITÉ:{Colors.END}
  • URL serveur verrouillée sur la production
  • Impossible de changer de serveur
  • Connexion sécurisée HTTPS
"""
    print(docs)
    return True

# ============================================================================
# 🎯 INTERFACE CLI PRINCIPALE
# ============================================================================

def main():
    print_banner()
    
    # SUPPRIME TOUTE ANCIENNE CONFIG LOCALHOST
    config_path = Path.home() / ".inithub" / "config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                old_config = json.load(f)
                if old_config.get('server_url', '').startswith('http://localhost'):
                    print_warning("⚠️  Suppression de l'ancienne configuration localhost")
                    # Réinitialise la configuration
                    config = CLIConfig()
        except:
            pass
    
    parser = argparse.ArgumentParser(
        description=f"{Colors.CYAN}🚀 initHUB CLI - Plateforme Cloud Production{Colors.END}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.RED}⚠️  ATTENTION: CLI CONNECTÉ À LA PRODUCTION{Colors.END}
{Colors.BLUE}🌐 URL: https://hubs-ja2g.onrender.com{Colors.END}

{Colors.YELLOW}📖 Exemples rapides:{Colors.END}

{Colors.GREEN}Créer un compte:{Colors.END}
  inithub auth register --email votre@email.com --password secret --username votrepseudo

{Colors.GREEN}Se connecter:{Colors.END}
  inithub auth login --email votre@email.com --password secret

{Colors.GREEN}Vérifier la connexion:{Colors.END}
  inithub auth status

{Colors.GREEN}Créer un site web:{Colors.END}
  inithub init --project-name mon-site --type web
  inithub hosting create --name mon-site

{Colors.YELLOW}Documentation:{Colors.END}
  inithub apropos
  inithub web open --page docs
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # 🔐 Authentification
    auth_parser = subparsers.add_parser('auth', help='🔐 Authentification et compte')
    auth_subparsers = auth_parser.add_subparsers(dest='auth_command', help='Sous-commandes')
    
    login_parser = auth_subparsers.add_parser('login', help='Connexion au serveur')
    login_parser.add_argument('--email', help='Email')
    login_parser.add_argument('--password', help='Mot de passe')
    login_parser.add_argument('--open', action='store_true', help='Ouvrir le navigateur après connexion')
    
    register_parser = auth_subparsers.add_parser('register', help='Création de compte')
    register_parser.add_argument('--username', help="Nom d'utilisateur")
    register_parser.add_argument('--email', help='Email')
    register_parser.add_argument('--password', help='Mot de passe')
    register_parser.add_argument('--full-name', help='Nom complet')
    
    auth_subparsers.add_parser('logout', help='Déconnexion')
    auth_subparsers.add_parser('whoami', help='Utilisateur connecté')
    auth_subparsers.add_parser('status', help='Statut de connexion')
    
    # 🌐 Hébergement Web
    hosting_parser = subparsers.add_parser('hosting', help='🌐 Hébergement web')
    hosting_subparsers = hosting_parser.add_subparsers(dest='hosting_command', help='Sous-commandes')
    
    hosting_create_parser = hosting_subparsers.add_parser('create', help='Créer un site web')
    hosting_create_parser.add_argument('--name', required=True, help='Nom du site')
    hosting_create_parser.add_argument('--domain', help='Domaine personnalisé')
    hosting_create_parser.add_argument('--type', choices=['static', 'php', 'nodejs', 'python'], default='static', help='Type de site')
    hosting_create_parser.add_argument('--create-local', action='store_true', help='Créer une structure locale')
    hosting_create_parser.add_argument('--force', action='store_true', help='Écraser les fichiers existants')
    hosting_create_parser.add_argument('--open', action='store_true', help='Ouvrir dans le navigateur')
    
    hosting_subparsers.add_parser('list', help='Lister les sites')
    hosting_subparsers.add_parser('status', help='Statut hébergement')
    
    # 📁 Fichiers
    files_parser = subparsers.add_parser('files', help='📁 Gestion de fichiers cloud')
    files_subparsers = files_parser.add_subparsers(dest='files_command', help='Sous-commandes')
    
    files_list_parser = files_subparsers.add_parser('list', help='Lister les fichiers')
    files_list_parser.add_argument('--path', default='', help='Chemin spécifique')
    
    files_upload_parser = files_subparsers.add_parser('upload', help='Uploader un fichier')
    files_upload_parser.add_argument('file', help='Chemin du fichier local')
    files_upload_parser.add_argument('--path', default='', help='Chemin distant')
    
    # 📊 Dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='📊 Tableau de bord')
    dashboard_parser.add_argument('--open', action='store_true', help='Ouvrir dans le navigateur')
    
    # 🛠️ Système
    system_parser = subparsers.add_parser('system', help='🛠️ Système et monitoring')
    system_subparsers = system_parser.add_subparsers(dest='system_command', help='Sous-commandes')
    
    system_subparsers.add_parser('health', help='Santé du système')
    system_subparsers.add_parser('info', help='Informations système')
    system_subparsers.add_parser('nginx', help='Statut nginx')
    
    # 📁 Projets
    init_parser = subparsers.add_parser('init', help='📁 Initialiser un nouveau projet')
    init_parser.add_argument('--project-name', help='Nom du projet')
    init_parser.add_argument('--type', choices=['projet', 'web', 'api', 'cloud'], default='projet', help='Type de projet')
    init_parser.add_argument('--env', choices=['python', 'javascript', 'node', 'java'], default='python', help='Environnement')
    init_parser.add_argument('--description', help='Description du projet')
    init_parser.add_argument('--force', action='store_true', help='Écraser le projet existant')
    init_parser.add_argument('--create-repo', action='store_true', help='Créer un repository après initialisation')
    init_parser.add_argument('--create-hosting', action='store_true', help='Créer un hébergement web après initialisation')
    
    # 📚 Repositories
    repo_parser = subparsers.add_parser('repo', help='📚 Gestion des repositories Git')
    repo_subparsers = repo_parser.add_subparsers(dest='repo_command', help='Sous-commandes')
    
    repo_create_parser = repo_subparsers.add_parser('create', help='Créer un repository')
    repo_create_parser.add_argument('--name', required=True, help='Nom du repository')
    repo_create_parser.add_argument('--description', help='Description')
    repo_create_parser.add_argument('--private', action='store_true', help='Repository privé')
    repo_create_parser.add_argument('--open', action='store_true', help='Ouvrir dans le navigateur')
    
    repo_subparsers.add_parser('list', help='Lister les repositories')
    
    # 🤖 Copilot
    copilot_parser = subparsers.add_parser('copilot', help='🤖 Assistant IA Copilot')
    copilot_subparsers = copilot_parser.add_subparsers(dest='copilot_command', help='Sous-commandes')
    
    copilot_ask_parser = copilot_subparsers.add_parser('ask', help='Poser une question')
    copilot_ask_parser.add_argument('--question', help='Question à poser')
    copilot_ask_parser.add_argument('--context', help='Contexte supplémentaire')
    
    copilot_subparsers.add_parser('health', help='Santé de Copilot')
    
    # ⚙️ Configuration
    config_parser = subparsers.add_parser('config', help='⚙️ Configuration du CLI')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Sous-commandes')
    
    config_set_parser = config_subparsers.add_parser('set', help='Configurer les paramètres')
    config_set_parser.add_argument('--server', help='URL du serveur initHUB (IGNORÉ - production forcée)')
    config_set_parser.add_argument('--open-browser', type=lambda x: (str(x).lower() == 'true'), help='Ouverture automatique du navigateur (true/false)')
    config_set_parser.add_argument('--theme', choices=['dark', 'light', 'auto'], help='Thème du CLI')
    
    config_subparsers.add_parser('show', help='Afficher la configuration')
    
    # 🌐 Web
    web_parser = subparsers.add_parser('web', help='🌐 Interface web')
    web_subparsers = web_parser.add_subparsers(dest='web_command', help='Sous-commandes')
    
    web_open_parser = web_subparsers.add_parser('open', help='Ouvrir dans le navigateur')
    web_open_parser.add_argument('--page', choices=['app', 'docs', 'dashboard'], default='app', help='Page à ouvrir')
    
    # 📚 Documentation
    subparsers.add_parser('apropos', help='📚 Documentation complète')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        success = False
        
        if args.command == 'auth':
            if args.auth_command == 'login':
                success = handle_auth_login(args)
            elif args.auth_command == 'register':
                success = handle_auth_register(args)
            elif args.auth_command == 'logout':
                success = handle_auth_logout(args)
            elif args.auth_command == 'whoami':
                success = handle_auth_whoami(args)
            elif args.auth_command == 'status':
                success = handle_auth_status(args)
            else:
                auth_parser.print_help()
        
        elif args.command == 'hosting':
            if args.hosting_command == 'create':
                success = handle_hosting_create(args)
            elif args.hosting_command == 'list':
                success = handle_hosting_list(args)
            elif args.hosting_command == 'status':
                success = handle_hosting_status(args)
            else:
                hosting_parser.print_help()
        
        elif args.command == 'files':
            if args.files_command == 'list':
                success = handle_files_list(args)
            elif args.files_command == 'upload':
                success = handle_files_upload(args)
            else:
                files_parser.print_help()
        
        elif args.command == 'dashboard':
            success = handle_dashboard_show(args)
        
        elif args.command == 'system':
            if args.system_command == 'health':
                success = handle_system_health(args)
            elif args.system_command == 'info':
                success = handle_system_info(args)
            elif args.system_command == 'nginx':
                success = handle_system_nginx(args)
            else:
                system_parser.print_help()
        
        elif args.command == 'init':
            success = handle_init_project(args)
        
        elif args.command == 'repo':
            if args.repo_command == 'create':
                success = handle_repo_create(args)
            elif args.repo_command == 'list':
                success = handle_repo_list(args)
            else:
                repo_parser.print_help()
        
        elif args.command == 'copilot':
            if args.copilot_command == 'ask':
                success = handle_copilot_ask(args)
            elif args.copilot_command == 'health':
                success = handle_copilot_health(args)
            else:
                copilot_parser.print_help()
        
        elif args.command == 'config':
            if args.config_command == 'set':
                success = handle_config_set(args)
            elif args.config_command == 'show':
                success = handle_config_show(args)
            else:
                config_parser.print_help()
        
        elif args.command == 'web':
            if args.web_command == 'open':
                success = handle_web_open(args)
            else:
                web_parser.print_help()
        
        elif args.command == 'apropos':
            success = handle_apropos(args)
        
        else:
            print_error(f"Commande inconnue: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Opération annulée!{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
