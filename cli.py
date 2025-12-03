#!/usr/bin/env python3
"""
initHUB CLI - Client complet avec interface moderne
Version 6.0 - Support complet avec toutes les routes serveur
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
import base64

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
{Colors.YELLOW}    Version 6.0 | Toutes les routes serveur{Colors.END}
{Colors.BLUE}    URL serveur: https://hubs-ja2g.onrender.com{Colors.END}
{Colors.RED}    ⚠️  CONNECTÉ À LA PRODUCTION{Colors.END}
"""
    print(banner)

# ============================================================================
# ⚙️ CONFIGURATION CLIENT
# ============================================================================

class CLIConfig:
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
        self.data = {
            "server_url": self.DEFAULT_SERVER,
            "default_download_dir": str(self.DOWNLOAD_DIR),
            "auto_open_browser": True,
            "theme": "dark"
        }
        
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    existing_data = json.load(f)
                    for key, value in existing_data.items():
                        if key != "server_url":
                            self.data[key] = value
            except:
                pass
        
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
        return self.DEFAULT_SERVER
    
    def set_server_url(self, url):
        print_warning("URL serveur verrouillée sur la production")
        print_info(f"Utilisation de: {self.DEFAULT_SERVER}")
        return False

config = CLIConfig()

# ============================================================================
# 🔌 CLIENT API COMPLET - TOUTES LES ROUTES
# ============================================================================

class InitHUBClient:
    def __init__(self):
        self.base_url = config.get_server_url() + "/api"
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
        try:
            result = self._make_request("POST", "/hosting/sites",
                                json={
                                    "name": name,
                                    "domain": domain,
                                    "type": site_type
                                })
            return result
        except Exception as e:
            raise
    
    def list_hosting_sites(self):
        try:
            result = self._make_request("GET", "/hosting/sites")
            return result
        except Exception as e:
            raise
    
    def get_hosting_status(self):
        try:
            result = self._make_request("GET", "/hosting/status")
            return result
        except Exception as e:
            raise
    
    # 📁 GESTION DE FICHIERS
    def list_files(self, path: str = ""):
        try:
            params = {"path": path} if path else {}
            result = self._make_request("GET", "/files", params=params)
            return result
        except Exception as e:
            raise
    
    def upload_file(self, file_path: str, remote_path: str = ""):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f)}
                data = {'path': remote_path} if remote_path else {}
                result = self._make_request("POST", "/files/upload", 
                                         files=files, data=data)
            return result
        except Exception as e:
            raise
    
    # 📊 DASHBOARD
    def get_dashboard(self):
        try:
            result = self._make_request("GET", "/dashboard")
            return result
        except Exception as e:
            raise
    
    # 🖥️ SYSTÈME
    def health_check(self):
        try:
            result = self._make_request("GET", "/health")
            return result
        except Exception as e:
            raise
    
    def get_system_info(self):
        try:
            result = self._make_request("GET", "/system/info")
            return result
        except Exception as e:
            raise
    
    def get_nginx_status(self):
        try:
            result = self._make_request("GET", "/system/nginx/status")
            return result
        except Exception as e:
            raise
    
    # 📚 REPOSITORIES
    def create_repo(self, name: str, description: str = "", is_private: bool = False):
        try:
            result = self._make_request("POST", "/repos",
                                json={
                                    "name": name,
                                    "description": description,
                                    "is_private": is_private,
                                    "auto_init": True
                                })
            return result
        except Exception as e:
            raise
    
    def list_repos(self, page: int = 1, per_page: int = 30):
        try:
            result = self._make_request("GET", f"/repos?page={page}&per_page={per_page}")
            return result
        except Exception as e:
            raise
    
    # 🤖 COPILOT
    def ask_copilot(self, question: str, context: str = "", max_length: int = 150, language: str = "auto"):
        try:
            result = self._make_request("POST", "/copilot/ask",
                                json={
                                    "question": question,
                                    "context": context,
                                    "max_length": max_length,
                                    "language": language
                                })
            return result
        except Exception as e:
            raise
    
    def copilot_health(self):
        try:
            result = self._make_request("GET", "/copilot/health")
            return result
        except Exception as e:
            raise
    
    # 🚀 PROJETS AVEC PUSH/PULL
    def create_project(self, project_name: str):
        """Crée un projet dans la base de données"""
        try:
            result = self._make_request("POST", "/repos",
                                json={
                                    "name": project_name,
                                    "description": f"Projet {project_name}",
                                    "is_private": True,
                                    "auto_init": True
                                })
            return result
        except Exception as e:
            raise
    
    def push_project(self, project_name: str, files: List[Dict[str, Any]], force: bool = False):
        """Pousse un projet vers initHUB"""
        try:
            result = self._make_request("POST", "/projects/push",
                                json={
                                    "project_name": project_name,
                                    "files": files,
                                    "force": force
                                })
            return result
        except Exception as e:
            raise
    
    def pull_project(self, project_name: str, target_path: str = None, force: bool = False):
        """Télécharge un projet depuis initHUB"""
        try:
            result = self._make_request("POST", "/projects/pull",
                                json={
                                    "project_name": project_name,
                                    "target_path": target_path,
                                    "force": force
                                })
            return result
        except Exception as e:
            raise
    
    def list_projects(self, page: int = 1, per_page: int = 20):
        """Liste tous les projets"""
        try:
            result = self._make_request("GET", f"/projects?page={page}&per_page={per_page}")
            return result
        except Exception as e:
            raise
    
    def get_project_details(self, username: str, project_name: str):
        """Récupère les détails d'un projet spécifique"""
        try:
            result = self._make_request("GET", f"/projects/{username}/{project_name}")
            return result
        except Exception as e:
            raise
    
    def get_project_file(self, username: str, project_name: str, file_path: str):
        """Récupère un fichier spécifique d'un projet"""
        try:
            result = self._make_request("GET", f"/projects/{username}/{project_name}/files/{file_path}")
            return result
        except Exception as e:
            raise
    
    def upload_project_file(self, username: str, project_name: str, file_path: str, remote_path: str = ""):
        """Upload un fichier dans un projet"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f)}
                data = {'path': remote_path} if remote_path else {}
                result = self._make_request("POST", f"/projects/{username}/{project_name}/upload", 
                                         files=files, data=data)
            return result
        except Exception as e:
            raise
    
    def delete_project(self, username: str, project_name: str):
        """Supprime un projet"""
        try:
            result = self._make_request("DELETE", f"/projects/{username}/{project_name}")
            return result
        except Exception as e:
            raise
    
    def sync_project(self, project_name: str, action: str = "status"):
        """Synchronise un projet (push/pull/status)"""
        try:
            result = self._make_request("POST", f"/projects/sync?action={action}&project_name={project_name}")
            return result
        except Exception as e:
            raise

api_client = InitHUBClient()

# ============================================================================
# 🚀 COMMANDES PRINCIPALES
# ============================================================================

def handle_auth_login(args):
    """Connexion au serveur initHUB"""
    print_info(f"🌐 Connexion à: {config.get_server_url()}")
    
    email = args.email
    password = args.password
    
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
    
    spinner = api_client.animations.loading_spinner("Création du site web")
    try:
        site = api_client.create_hosting_site(name, domain, site_type)
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Site web créé{Colors.END}")
        
        print_success(f"Site web créé: {site['name']}")
        print(f"{Colors.BLUE}🌐 URL:{Colors.END} {config.get_server_url()}{site['url']}")
        print(f"{Colors.YELLOW}🔧 Type:{Colors.END} {site['type']}")
        print(f"{Colors.GREEN}📅 Créé le:{Colors.END} {site['created_at']}")
        
        if args.open:
            webbrowser.open(f"{config.get_server_url()}{site['url']}")
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur création site{Colors.END}")
        print_error(f"Erreur création site: {e}")
        return False

def handle_hosting_list(args):
    """Liste les sites d'hébergement"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    spinner = api_client.animations.loading_spinner("Récupération des sites")
    try:
        sites = api_client.list_hosting_sites()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Sites chargés{Colors.END}")
        
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
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur liste sites{Colors.END}")
        print_error(f"Erreur liste sites: {e}")
        return False

def handle_hosting_status(args):
    """Statut de l'hébergement"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    spinner = api_client.animations.loading_spinner("Vérification hébergement")
    try:
        status = api_client.get_hosting_status()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Statut hébergement{Colors.END}")
        
        print_success(f"Statut hébergement pour {status['user']}")
        print(f"{Colors.BLUE}📊 Sites actifs:{Colors.END} {status['active_sites']}")
        print(f"{Colors.GREEN}💾 Espace utilisé:{Colors.END} {status['disk_usage']}")
        
        if status.get('limits'):
            limits = status['limits']
            print(f"\n{Colors.CYAN}📋 Limites:{Colors.END}")
            print(f"   📦 Stockage max: {limits['max_storage']}")
            print(f"   🌐 Sites max: {limits['max_sites']}")
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur statut hébergement{Colors.END}")
        print_error(f"Erreur statut hébergement: {e}")
        return False

def handle_files_list(args):
    """Liste les fichiers"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    spinner = api_client.animations.loading_spinner("Liste des fichiers")
    try:
        files_data = api_client.list_files(args.path)
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Fichiers chargés{Colors.END}")
        
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
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur liste fichiers{Colors.END}")
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
    
    spinner = api_client.animations.loading_spinner("Upload du fichier")
    try:
        result = api_client.upload_file(file_path, args.path)
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Fichier uploadé{Colors.END}")
        
        print_success(f"Fichier uploadé: {result['filename']}")
        print(f"{Colors.BLUE}📁 Chemin:{Colors.END} {result['path']}")
        print(f"{Colors.GREEN}📦 Taille:{Colors.END} {result['size']} bytes")
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur upload{Colors.END}")
        print_error(f"Erreur upload: {e}")
        return False

def handle_dashboard_show(args):
    """Affiche le dashboard"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    spinner = api_client.animations.loading_spinner("Chargement dashboard")
    try:
        dashboard = api_client.get_dashboard()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Dashboard chargé{Colors.END}")
        
        print_success("Dashboard initHUB Cloud")
        print(f"{Colors.BLUE}📊 Vue d'ensemble:{Colors.END}")
        print(f"   📚 Repositories: {dashboard['total_repos']}")
        print(f"   ⭐ Stars: {dashboard['total_stars']}")
        print(f"   🔀 Forks: {dashboard['total_forks']}")
        
        if args.open:
            webbrowser.open(f"{config.get_server_url()}/app")
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur dashboard{Colors.END}")
        print_error(f"Erreur dashboard: {e}")
        return False

def handle_system_health(args):
    """Vérifie la santé du système"""
    spinner = api_client.animations.loading_spinner("Vérification du serveur")
    try:
        health = api_client.health_check()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Serveur opérationnel{Colors.END}")
        
        print_success("initHUB Cloud - Santé du système")
        print(f"{Colors.BLUE}📊 Version:{Colors.END} {health.get('version', 'N/A')}")
        
        if health.get('services'):
            print(f"\n{Colors.YELLOW}🛠️ Services:{Colors.END}")
            for service, status in health['services'].items():
                status_icon = "🟢" if status in ['online', 'running'] else "🔴"
                print(f"   {status_icon} {service}: {status}")
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Serveur hors ligne{Colors.END}")
        print_error(f"Erreur vérification santé: {e}")
        return False

def handle_system_info(args):
    """Informations système détaillées"""
    spinner = api_client.animations.loading_spinner("Informations système")
    try:
        info = api_client.get_system_info()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Informations système{Colors.END}")
        
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
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur informations système{Colors.END}")
        print_error(f"Erreur informations système: {e}")
        return False

def handle_system_nginx(args):
    """Statut de nginx"""
    spinner = api_client.animations.loading_spinner("Statut Nginx")
    try:
        nginx_status = api_client.get_nginx_status()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Statut Nginx{Colors.END}")
        
        if nginx_status['running']:
            print_success("Nginx est en cours d'exécution")
            print(f"{Colors.GREEN}🌐 Sites activés:{Colors.END} {nginx_status['sites_enabled']}")
        else:
            print_error("Nginx n'est pas en cours d'exécution")
        
        return nginx_status['running']
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur Nginx{Colors.END}")
        print_error(f"Erreur statut nginx: {e}")
        return False

def handle_repo_create(args):
    """Crée un nouveau repository"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    name = args.name
    description = args.description or ""
    is_private = args.private
    
    spinner = api_client.animations.loading_spinner("Création du repository")
    try:
        repo = api_client.create_repo(name, description, is_private)
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Repository créé{Colors.END}")
        
        print_success(f"Repository créé: {repo['full_name']}")
        print(f"{Colors.BLUE}📝 Description:{Colors.END} {repo['description'] or 'Aucune description'}")
        print(f"{Colors.YELLOW}🔒 Visibilité:{Colors.END} {'🔒 Privé' if repo['is_private'] else '🌐 Public'}")
        print(f"{Colors.CYAN}🌐 URL:{Colors.END} {repo['html_url']}")
        
        if args.open:
            webbrowser.open(repo['html_url'])
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur création repository{Colors.END}")
        print_error(f"Erreur création repository: {e}")
        return False

def handle_repo_list(args):
    """Liste les repositories"""
    spinner = api_client.animations.loading_spinner("Récupération des repositories")
    try:
        repos = api_client.list_repos()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Repositories chargés{Colors.END}")
        
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
            
            if stats:
                print(f"   {' '.join(stats)}")
            
            print()
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur liste repositories{Colors.END}")
        print_error(f"Erreur liste repositories: {e}")
        return False

def handle_copilot_ask(args):
    """Pose une question à Copilot"""
    question = args.question
    context = args.context or ""
    
    if not question:
        question = input(f"{Colors.CYAN}🤖 Question pour Copilot: {Colors.END}")
    
    if not question:
        print_error("Question requise")
        return False
    
    spinner = api_client.animations.loading_spinner("Copilot réfléchit")
    try:
        response = api_client.ask_copilot(question, context)
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Réponse reçue{Colors.END}")
        
        print(f"\n{Colors.CYAN}🤖 Copilot 🪖:{Colors.END}")
        print("─" * 80)
        print(f"{Colors.WHITE}{response['response']}{Colors.END}")
        print("─" * 80)
        
        return True
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur Copilot{Colors.END}")
        print_error(f"Erreur Copilot: {e}")
        return False

def handle_copilot_health(args):
    """Vérifie l'état de Copilot"""
    spinner = api_client.animations.loading_spinner("Vérification Copilot")
    try:
        health = api_client.copilot_health()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Copilot vérifié{Colors.END}")
        
        status = f"{Colors.GREEN}🟢 EN LIGNE{Colors.END}" if health['online'] else f"{Colors.RED}🔴 HORS LIGNE{Colors.END}"
        print(f"{Colors.CYAN}🤖 Copilot:{Colors.END} {status}")
        print(f"{Colors.BLUE}🌐 URL:{Colors.END} {health['base_url']}")
        
        return health['online']
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur vérification Copilot{Colors.END}")
        print_error(f"Erreur vérification Copilot: {e}")
        return False

def handle_project_init(args):
    """Initialise un nouveau projet local"""
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
        
        # Créer README
        readme_content = f"# {project_name}\n\n{description}\n"
        with open(project_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Créer .inithubignore
        ignore_content = """# Fichiers à ignorer pour initHUB
__pycache__/
*.pyc
.env
.venv/
node_modules/
dist/
build/
"""
        with open(project_path / ".inithubignore", 'w', encoding='utf-8') as f:
            f.write(ignore_content)
        
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
        
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Projet initialisé localement{Colors.END}")
        
        print(f"\n{Colors.CYAN}📁 Structure créée:{Colors.END}")
        print(f"   📄 README.md {Colors.GREEN}(documentation){Colors.END}")
        print(f"   📄 .inithubignore {Colors.BLUE}(fichiers ignorés){Colors.END}")
        if env == "python":
            print(f"   📄 main.py {Colors.MAGENTA}(point d'entrée){Colors.END}")
        
        print(f"\n{Colors.YELLOW}🚀 Prochaines étapes:{Colors.END}")
        print(f"   1. {Colors.CYAN}cd {project_name}{Colors.END}")
        print(f"   2. {Colors.GREEN}inithub auth login{Colors.END} {Colors.YELLOW}(si pas connecté){Colors.END}")
        
        if args.create_repo:
            print(f"   3. {Colors.BLUE}inithub repo create --name {project_name}{Colors.END}")
        
        if args.create_hosting and project_type in ["web", "static"]:
            print(f"   4. {Colors.MAGENTA}inithub hosting create --name {project_name} --type {project_type}{Colors.END}")
        
        return True
        
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur initialisation{Colors.END}")
        print_error(f"Erreur: {e}")
        return False

def handle_project_push(args):
    """Pousse un projet local vers initHUB"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    project_name = args.project_name
    force = args.force
    
    if not project_name:
        project_name = input(f"{Colors.CYAN}📁 Nom du projet: {Colors.END}")
    
    if not project_name:
        print_error("Nom du projet requis")
        return False
    
    # Vérifier si le projet existe localement
    project_path = Path(project_name)
    if not project_path.exists():
        print_error(f"Projet local '{project_name}' non trouvé")
        return False
    
    spinner = api_client.animations.loading_spinner("Préparation du push")
    
    try:
        # Lire les fichiers
        files = []
        total_size = 0
        
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                # Ignorer certains fichiers
                if any(ignore in str(file_path) for ignore in ['.git', '__pycache__', '.venv']):
                    continue
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                relative_path = str(file_path.relative_to(project_path))
                
                files.append({
                    "name": file_path.name,
                    "path": relative_path,
                    "content": base64.b64encode(content).decode('utf-8'),
                    "size": len(content)
                })
                total_size += len(content)
        
        if not files:
            print_error("Aucun fichier à pousser")
            return False
        
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ {len(files)} fichiers prêts{Colors.END}")
        
        # Pousser vers le serveur
        push_spinner = api_client.animations.loading_spinner("Envoi vers initHUB Cloud")
        result = api_client.push_project(project_name, files, force)
        api_client.animations.stop_loading(push_spinner, f"{Colors.GREEN}✅ Projet poussé avec succès{Colors.END}")
        
        print_success(f"Projet '{project_name}' poussé vers initHUB")
        print(f"{Colors.BLUE}📦 Fichiers:{Colors.END} {len(files)}")
        print(f"{Colors.GREEN}💾 Taille totale:{Colors.END} {total_size / 1024:.2f} KB")
        print(f"{Colors.CYAN}🌐 URL du projet:{Colors.END} {config.get_server_url()}/projects/{user['username']}/{project_name}")
        
        return True
        
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur push{Colors.END}")
        print_error(f"Erreur push: {e}")
        return False

def handle_project_pull(args):
    """Télécharge un projet depuis initHUB"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    project_name = args.project_name
    target_path = args.path or project_name
    force = args.force
    
    if not project_name:
        project_name = input(f"{Colors.CYAN}📁 Nom du projet à télécharger: {Colors.END}")
    
    if not project_name:
        print_error("Nom du projet requis")
        return False
    
    # Vérifier si le dossier existe déjà
    target_dir = Path(target_path)
    if target_dir.exists() and not force:
        print_error(f"Le dossier '{target_path}' existe déjà. Utilisez --force pour écraser.")
        return False
    
    spinner = api_client.animations.loading_spinner("Téléchargement du projet")
    
    try:
        # Télécharger le projet
        result = api_client.pull_project(project_name, target_path, force)
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Projet téléchargé{Colors.END}")
        
        if not result.get('success', False):
            print_error("Erreur lors du téléchargement")
            return False
        
        files = result.get('files', [])
        
        print_success(f"Projet '{project_name}' téléchargé")
        print(f"{Colors.BLUE}📦 Fichiers:{Colors.END} {len(files)}")
        print(f"{Colors.GREEN}💾 Taille totale:{Colors.END} {result.get('total_size', 0) / 1024:.2f} KB")
        print(f"{Colors.CYAN}📁 Dossier:{Colors.END} {target_path}")
        
        # Écrire les fichiers
        for file_info in files:
            file_path = target_dir / file_info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = base64.b64decode(file_info['content'])
            with open(file_path, 'wb') as f:
                f.write(content)
        
        print_success(f"✅ {len(files)} fichiers écrits dans '{target_path}'")
        
        return True
        
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur pull{Colors.END}")
        print_error(f"Erreur pull: {e}")
        return False

def handle_project_list(args):
    """Liste les projets sur initHUB"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    spinner = api_client.animations.loading_spinner("Récupération des projets")
    
    try:
        result = api_client.list_projects()
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Projets chargés{Colors.END}")
        
        projects = result.get('projects', [])
        
        if not projects:
            print_info("Aucun projet trouvé")
            return True
        
        print(f"{Colors.CYAN}📁 Projets ({len(projects)}):{Colors.END}")
        
        headers = ["Nom", "Type", "Fichiers", "Taille", "Visibilité", "Dernière modif"]
        rows = []
        
        for project in projects:
            visibility = "🔒" if project.get('is_private', True) else "🌐"
            size_mb = (project.get('total_size', 0) / (1024 * 1024))
            
            rows.append([
                project['full_name'],
                project.get('type', 'projet'),
                project.get('files_count', 0),
                f"{size_mb:.1f} MB" if size_mb > 0 else "-",
                visibility,
                project.get('updated_at', 'N/A')[:10]
            ])
        
        print_table(headers, rows)
        
        return True
        
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur liste projets{Colors.END}")
        print_error(f"Erreur liste projets: {e}")
        return False

def handle_project_show(args):
    """Affiche les détails d'un projet"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    project_name = args.project_name
    
    if not project_name:
        project_name = input(f"{Colors.CYAN}📁 Nom du projet: {Colors.END}")
    
    if not project_name:
        print_error("Nom du projet requis")
        return False
    
    spinner = api_client.animations.loading_spinner("Récupération des détails")
    
    try:
        project = api_client.get_project_details(user['username'], project_name)
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Détails chargés{Colors.END}")
        
        print_success(f"📁 Projet: {project['full_name']}")
        print(f"{Colors.BLUE}📝 Description:{Colors.END} {project.get('description', 'Aucune description')}")
        print(f"{Colors.YELLOW}👤 Propriétaire:{Colors.END} {project['owner']['username']}")
        print(f"{Colors.GREEN}🔒 Visibilité:{Colors.END} {'🔒 Privé' if project['is_private'] else '🌐 Public'}")
        print(f"{Colors.CYAN}📊 Statistiques:{Colors.END}")
        print(f"   📦 Fichiers: {project.get('files_count', 0)}")
        print(f"   💾 Taille: {project.get('total_size', 0) / 1024:.2f} KB")
        print(f"   ⭐ Stars: {project.get('stars_count', 0)}")
        print(f"   🔀 Forks: {project.get('forks_count', 0)}")
        
        if project.get('files') and len(project['files']) > 0:
            print(f"\n{Colors.MAGENTA}📄 Fichiers ({len(project['files'])}):{Colors.END}")
            for file in project['files'][:10]:  # Limiter à 10 fichiers
                size_kb = file['size'] / 1024
                print(f"   📄 {file['path']} ({size_kb:.1f} KB)")
            
            if len(project['files']) > 10:
                print(f"   ... et {len(project['files']) - 10} autres fichiers")
        
        print(f"\n{Colors.YELLOW}🔗 URLs:{Colors.END}")
        urls = project.get('urls', {})
        for key, url in urls.items():
            print(f"   {key}: {config.get_server_url()}{url}")
        
        return True
        
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur détails projet{Colors.END}")
        print_error(f"Erreur détails projet: {e}")
        return False

def handle_project_sync(args):
    """Synchronise un projet (push/pull/status)"""
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub auth login' d'abord.")
        return False
    
    project_name = args.project_name
    action = args.action or "status"
    
    if not project_name:
        project_name = input(f"{Colors.CYAN}📁 Nom du projet: {Colors.END}")
    
    if not project_name:
        print_error("Nom du projet requis")
        return False
    
    spinner = api_client.animations.loading_spinner(f"Synchronisation ({action})")
    
    try:
        result = api_client.sync_project(project_name, action)
        api_client.animations.stop_loading(spinner, f"{Colors.GREEN}✅ Synchronisation terminée{Colors.END}")
        
        if action == "status":
            print_success(f"📊 Statut de synchronisation pour '{project_name}'")
            
            sync_status = result.get('sync_status', {})
            
            local_only = sync_status.get('local_only', [])
            remote_only = sync_status.get('remote_only', [])
            both = sync_status.get('both', [])
            
            print(f"{Colors.BLUE}📁 Fichiers locaux uniquement:{Colors.END} {len(local_only)}")
            if local_only and args.verbose:
                for file in local_only[:5]:
                    print(f"   📄 {file.get('path', 'N/A')}")
            
            print(f"{Colors.GREEN}☁️ Fichiers distants uniquement:{Colors.END} {len(remote_only)}")
            if remote_only and args.verbose:
                for file in remote_only[:5]:
                    print(f"   📄 {file.get('path', 'N/A')}")
            
            print(f"{Colors.YELLOW}🔄 Fichiers synchronisés:{Colors.END} {len(both)}")
            
            if len(local_only) > 0:
                print(f"\n{Colors.CYAN}💡 Conseils:{Colors.END}")
                print("   Pour pousser les fichiers locaux: inithub project push")
                print("   Pour télécharger les fichiers distants: inithub project pull")
        
        elif action == "push":
            print_success(f"✅ Push réussi pour '{project_name}'")
            print(f"{Colors.BLUE}📦 Fichiers envoyés:{Colors.END} {result.get('files_count', 0)}")
        
        elif action == "pull":
            print_success(f"✅ Pull réussi pour '{project_name}'")
            print(f"{Colors.GREEN}📥 Fichiers téléchargés:{Colors.END} {result.get('remote_files_count', 0)}")
        
        return True
        
    except Exception as e:
        api_client.animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur synchronisation{Colors.END}")
        print_error(f"Erreur synchronisation: {e}")
        return False

def handle_config_set(args):
    """Configure les paramètres du CLI"""
    if args.server:
        print_warning("URL serveur verrouillée sur la production")
        print_info(f"Utilisation de: {config.get_server_url()}")
    
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
    else:
        print(f"\n{Colors.YELLOW}🔐 Connecté:{Colors.END} Non")
    
    # Vérifier la connexion au serveur
    print(f"\n{Colors.MAGENTA}🔗 Test de connexion:{Colors.END}")
    try:
        health = api_client.health_check()
        print(f"   {Colors.GREEN}🟢 Serveur accessible{Colors.END}")
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
initHUB est une plateforme cloud complète avec Git, IA Copilot, hébergement web,
gestion de projets et synchronisation cloud.

{Colors.YELLOW}🚀 COMMANDES PRINCIPALES:{Colors.END}

{Colors.CYAN}🔐 AUTHENTIFICATION:{Colors.END}
  {Colors.BOLD}inithub auth login{Colors.END}          - Connexion
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

{Colors.GREEN}🚀 GESTION DE PROJETS:{Colors.END}
  {Colors.BOLD}inithub project init{Colors.END}        - Initialiser un projet local
  {Colors.BOLD}inithub project push{Colors.END}        - Pousser un projet vers cloud
  {Colors.BOLD}inithub project pull{Colors.END}        - Télécharger un projet depuis cloud
  {Colors.BOLD}inithub project list{Colors.END}        - Lister mes projets
  {Colors.BOLD}inithub project show{Colors.END}        - Détails d'un projet
  {Colors.BOLD}inithub project sync{Colors.END}        - Synchroniser un projet

{Colors.YELLOW}📁 REPOSITORIES GIT:{Colors.END}
  {Colors.BOLD}inithub repo create{Colors.END}         - Créer un repository
  {Colors.BOLD}inithub repo list{Colors.END}           - Lister mes repositories

{Colors.CYAN}🤖 ASSISTANT IA:{Colors.END}
  {Colors.BOLD}inithub copilot ask{Colors.END}         - Poser une question à Copilot
  {Colors.BOLD}inithub copilot health{Colors.END}      - Vérifier Copilot

{Colors.MAGENTA}🛠️ SYSTÈME:{Colors.END}
  {Colors.BOLD}inithub system health{Colors.END}       - Santé du système
  {Colors.BOLD}inithub system info{Colors.END}         - Informations système
  {Colors.BOLD}inithub system nginx{Colors.END}        - Statut nginx

{Colors.BLUE}⚙️ CONFIGURATION:{Colors.END}
  {Colors.BOLD}inithub config set{Colors.END}          - Configurer le CLI
  {Colors.BOLD}inithub config show{Colors.END}         - Afficher la configuration
  {Colors.BOLD}inithub web open{Colors.END}            - Ouvrir l'interface web

{Colors.GREEN}📚 DOCUMENTATION:{Colors.END}
  {Colors.BOLD}inithub apropos{Colors.END}             - Cette documentation

{Colors.YELLOW}📞 SUPPORT:{Colors.END}
  • Documentation: {Colors.CYAN}inithub apropos{Colors.END}
  • Serveur: {Colors.GREEN}{config.get_server_url()}{Colors.END}
  • Interface web: {Colors.MAGENTA}inithub web open{Colors.END}
"""
    print(docs)
    return True

# ============================================================================
# 🎯 INTERFACE CLI PRINCIPALE
# ============================================================================

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description=f"{Colors.CYAN}🚀 initHUB CLI - Plateforme Cloud Production{Colors.END}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.RED}⚠️  ATTENTION: CLI CONNECTÉ À LA PRODUCTION{Colors.END}
{Colors.BLUE}🌐 URL: https://hubs-ja2g.onrender.com{Colors.END}

{Colors.YELLOW}📖 Exemples rapides:{Colors.END}

{Colors.GREEN}Créer et pousser un projet:{Colors.END}
  inithub project init --project-name mon-app
  inithub auth login
  inithub project push --project-name mon-app

{Colors.GREEN}Héberger un site web:{Colors.END}
  inithub hosting create --name mon-site --type static

{Colors.GREEN}Gérer des fichiers:{Colors.END}
  inithub files list
  inithub files upload monfichier.txt

{Colors.YELLOW}Documentation:{Colors.END}
  inithub apropos
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
    
    # 🚀 Projets
    project_parser = subparsers.add_parser('project', help='🚀 Gestion de projets')
    project_subparsers = project_parser.add_subparsers(dest='project_command', help='Sous-commandes')
    
    project_init_parser = project_subparsers.add_parser('init', help='Initialiser un projet local')
    project_init_parser.add_argument('--project-name', help='Nom du projet')
    project_init_parser.add_argument('--type', choices=['projet', 'web', 'api', 'cloud'], default='projet', help='Type de projet')
    project_init_parser.add_argument('--env', choices=['python', 'javascript', 'node', 'java'], default='python', help='Environnement')
    project_init_parser.add_argument('--description', help='Description du projet')
    project_init_parser.add_argument('--force', action='store_true', help='Écraser le projet existant')
    project_init_parser.add_argument('--create-repo', action='store_true', help='Créer un repository après initialisation')
    project_init_parser.add_argument('--create-hosting', action='store_true', help='Créer un hébergement web après initialisation')
    
    project_push_parser = project_subparsers.add_parser('push', help='Pousser un projet vers cloud')
    project_push_parser.add_argument('--project-name', help='Nom du projet')
    project_push_parser.add_argument('--force', action='store_true', help='Forcer le push')
    
    project_pull_parser = project_subparsers.add_parser('pull', help='Télécharger un projet depuis cloud')
    project_pull_parser.add_argument('--project-name', help='Nom du projet')
    project_pull_parser.add_argument('--path', help='Chemin de destination')
    project_pull_parser.add_argument('--force', action='store_true', help='Écraser les fichiers existants')
    
    project_subparsers.add_parser('list', help='Lister les projets')
    
    project_show_parser = project_subparsers.add_parser('show', help='Détails d\'un projet')
    project_show_parser.add_argument('--project-name', help='Nom du projet')
    
    project_sync_parser = project_subparsers.add_parser('sync', help='Synchroniser un projet')
    project_sync_parser.add_argument('--project-name', help='Nom du projet')
    project_sync_parser.add_argument('--action', choices=['push', 'pull', 'status'], default='status', help='Action de synchronisation')
    project_sync_parser.add_argument('--verbose', action='store_true', help='Afficher les détails')
    
    # 📁 Repositories
    repo_parser = subparsers.add_parser('repo', help='📁 Gestion des repositories Git')
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
    
    # 🛠️ Système
    system_parser = subparsers.add_parser('system', help='🛠️ Système et monitoring')
    system_subparsers = system_parser.add_subparsers(dest='system_command', help='Sous-commandes')
    
    system_subparsers.add_parser('health', help='Santé du système')
    system_subparsers.add_parser('info', help='Informations système')
    system_subparsers.add_parser('nginx', help='Statut nginx')
    
    # 📊 Dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='📊 Tableau de bord')
    dashboard_parser.add_argument('--open', action='store_true', help='Ouvrir dans le navigateur')
    
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
        
        elif args.command == 'project':
            if args.project_command == 'init':
                success = handle_project_init(args)
            elif args.project_command == 'push':
                success = handle_project_push(args)
            elif args.project_command == 'pull':
                success = handle_project_pull(args)
            elif args.project_command == 'list':
                success = handle_project_list(args)
            elif args.project_command == 'show':
                success = handle_project_show(args)
            elif args.project_command == 'sync':
                success = handle_project_sync(args)
            else:
                project_parser.print_help()
        
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
        
        elif args.command == 'system':
            if args.system_command == 'health':
                success = handle_system_health(args)
            elif args.system_command == 'info':
                success = handle_system_info(args)
            elif args.system_command == 'nginx':
                success = handle_system_nginx(args)
            else:
                system_parser.print_help()
        
        elif args.command == 'dashboard':
            success = handle_dashboard_show(args)
        
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
