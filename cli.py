#!/usr/bin/env python3
"""
initHUB CLI - Client complet avec interface moderne
Version 5.0 - Support complet hébergement web, terminal, gestion de fichiers
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
{Colors.RED}    ⚠️  FORCE CONNECTÉ À LA PRODUCTION{Colors.END}
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
        print_info(f"Connexion à: {self.base_url}")
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
            raise Exception(f"Impossible de se connecter au serveur à {self.base_url}")
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
# 🚀 COMMANDES PRINCIPALES
# ============================================================================

def handle_auth_login(args):
    """Connexion au serveur initHUB"""
    email = args.email
    password = args.password
    
    print_info(f"Connexion à: {config.get_server_url()}")
    
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
    username = args.username
    email = args.email
    password = args.password
    full_name = args.full_name or ""
    
    print_info(f"Création de compte sur: {config.get_server_url()}")
    
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
    print(f"{Colors.RED}⚠️  FORCE CONNECTÉ À LA PRODUCTION{Colors.END}")
    
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

# ... (le reste des fonctions handle_* reste identique)

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
  inithub auth register --email votre@email.com --password secret

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
        
        # ... (autres commandes restent identiques)
        
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
