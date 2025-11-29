#!/usr/bin/env python3
"""
initHUB CLI - Client complet avec toutes les routes du serveur
Version Ultimate avec connexion totale
"""

import os
import re
import sys
import json
import glob
import fnmatch
import shlex
import requests
import argparse
import zipfile
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

# ============================================================================
# ⚙️ CONFIGURATION CLIENT AMÉLIORÉE
# ============================================================================

class CLIConfig:
    # URL de votre serveur déployé
    SERVER_URL = "https://hubs-pro.onrender.com"
    API_BASE = f"{SERVER_URL}/api"
    
    # Chemins de configuration
    CONFIG_DIR = Path.home() / ".inithub"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    TOKEN_FILE = CONFIG_DIR / "token.json"
    CACHE_DIR = CONFIG_DIR / "cache"
    
    def __init__(self):
        self.config_dir = self.CONFIG_DIR
        self.config_dir.mkdir(exist_ok=True)
        self.cache_dir = self.CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration existante"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    self.data = json.load(f)
            except:
                self.data = {}
        else:
            self.data = {
                "server_url": self.SERVER_URL,
                "default_download_dir": str(Path.home() / "inithub_downloads"),
                "auto_extract": True,
                "preserve_structure": True
            }
    
    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def save_token(self, token_data):
        """Sauvegarde le token d'authentification"""
        with open(self.TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    def load_token(self):
        """Charge le token d'authentification"""
        if self.TOKEN_FILE.exists():
            try:
                with open(self.TOKEN_FILE, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def get_server_url(self):
        """Retourne l'URL du serveur"""
        return self.data.get("server_url", self.SERVER_URL)
    
    def get_download_dir(self):
        """Retourne le répertoire de téléchargement par défaut"""
        download_dir = Path(self.data.get("default_download_dir", 
                                        str(Path.home() / "inithub_downloads")))
        download_dir.mkdir(exist_ok=True)
        return download_dir

# Configuration globale
config = CLIConfig()

# ============================================================================
# 🔌 CLIENT API COMPLET AVEC TOUTES LES ROUTES
# ============================================================================

class InitHUBClient:
    def __init__(self):
        self.base_url = config.get_server_url() + "/api"
        self.token_data = config.load_token()
        self.session = requests.Session()
        
        if self.token_data:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token_data.get('access_token')}"
            })
    
    def _handle_response(self, response):
        """Gère la réponse de l'API"""
        try:
            data = response.json()
        except:
            data = {"detail": response.text}
        
        if response.status_code >= 400:
            error_msg = data.get('detail', 'Erreur inconnue')
            raise Exception(f"API Error {response.status_code}: {error_msg}")
        
        return data
    
    def _make_request(self, method, endpoint, **kwargs):
        """Fait une requête à l'API avec gestion d'erreur"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return self._handle_response(response)
        except Exception as e:
            raise Exception(f"Erreur API {endpoint}: {e}")
    
    # 🔐 AUTHENTIFICATION
    def login(self, email: str, password: str) -> bool:
        """Connexion au serveur"""
        try:
            data = self._make_request("POST", "/auth/login", 
                                    json={"email": email, "password": password})
            
            # Sauvegarder le token
            config.save_token(data)
            self.session.headers.update({
                "Authorization": f"Bearer {data['access_token']}"
            })
            
            print(f"✅ Connecté en tant que {email}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    def register(self, username: str, email: str, password: str, full_name: str = "") -> bool:
        """Inscription au serveur"""
        try:
            self._make_request("POST", "/auth/register",
                             json={
                                 "username": username,
                                 "email": email,
                                 "password": password,
                                 "full_name": full_name
                             })
            print(f"✅ Compte créé: {username}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur inscription: {e}")
            return False
    
    def refresh_token(self) -> bool:
        """Rafraîchit le token"""
        try:
            if not self.token_data or 'refresh_token' not in self.token_data:
                return False
            
            self.session.headers.update({
                "Authorization": f"Bearer {self.token_data['refresh_token']}"
            })
            
            data = self._make_request("POST", "/auth/refresh")
            
            # Sauvegarder le nouveau token
            config.save_token(data)
            self.session.headers.update({
                "Authorization": f"Bearer {data['access_token']}"
            })
            
            return True
        except:
            return False
    
    def get_current_user(self):
        """Récupère les infos de l'utilisateur connecté"""
        try:
            return self._make_request("GET", "/users/me")
        except:
            return None
    
    # 📁 REPOSITORIES
    def create_repo(self, name: str, description: str = "", is_private: bool = False):
        """Crée un nouveau repository"""
        return self._make_request("POST", "/repos",
                                json={
                                    "name": name,
                                    "description": description,
                                    "is_private": is_private,
                                    "auto_init": True
                                })
    
    def list_repos(self, page: int = 1, per_page: int = 30):
        """Liste les repositories"""
        return self._make_request("GET", f"/repos?page={page}&per_page={per_page}")
    
    def get_repo(self, owner: str, repo: str):
        """Récupère un repository spécifique"""
        return self._make_request("GET", f"/repos/{owner}/{repo}")
    
    def delete_repo(self, owner: str, repo: str):
        """Supprime un repository"""
        return self._make_request("DELETE", f"/repos/{owner}/{repo}")
    
    # ⭐ STARS & FORKS
    def star_repo(self, owner: str, repo: str):
        """Star un repository"""
        return self._make_request("POST", f"/repos/{owner}/{repo}/star")
    
    def unstar_repo(self, owner: str, repo: str):
        """Unstar un repository"""
        return self._make_request("DELETE", f"/repos/{owner}/{repo}/star")
    
    def fork_repo(self, owner: str, repo: str):
        """Fork un repository"""
        return self._make_request("POST", f"/repos/{owner}/{repo}/forks")
    
    # 🔑 TOKENS PERSONNELS
    def create_token(self, name: str, scopes: List[str] = None):
        """Crée un token personnel"""
        if scopes is None:
            scopes = ["read"]
        return self._make_request("POST", "/tokens",
                                json={"name": name, "scopes": scopes})
    
    def list_tokens(self):
        """Liste les tokens personnels"""
        return self._make_request("GET", "/tokens")
    
    def delete_token(self, token_id: int):
        """Supprime un token personnel"""
        return self._make_request("DELETE", f"/tokens/{token_id}")
    
    # 📊 DASHBOARD & ANALYTICS
    def get_dashboard(self):
        """Récupère le dashboard utilisateur"""
        return self._make_request("GET", "/dashboard")
    
    def get_repo_analytics(self, owner: str, repo: str):
        """Récupère les analytics d'un repository"""
        return self._make_request("GET", f"/analytics/repos/{owner}/{repo}")
    
    # 🤖 COPILOT
    def ask_copilot(self, question: str, context: str = "", max_length: int = 150, language: str = "auto"):
        """Pose une question à Copilot"""
        return self._make_request("POST", "/copilot/ask",
                                json={
                                    "question": question,
                                    "context": context,
                                    "max_length": max_length,
                                    "language": language
                                })
    
    def analyze_code(self, code: str, language: str, analysis_type: str = "complexity"):
        """Analyse du code avec Copilot"""
        return self._make_request("POST", "/copilot/analyze-code",
                                json={
                                    "code": code,
                                    "language": language,
                                    "analysis_type": analysis_type
                                })
    
    def suggest_commit(self, diff: str, files_changed: List[str]):
        """Suggère des messages de commit"""
        return self._make_request("POST", "/copilot/suggest-commit",
                                json={
                                    "diff": diff,
                                    "files_changed": files_changed
                                })
    
    def copilot_health(self):
        """Vérifie l'état de Copilot"""
        return self._make_request("GET", "/copilot/health")
    
    # 🏷️ RELEASES
    def create_release(self, owner: str, repo: str, release_data: Dict):
        """Crée une release"""
        return self._make_request("POST", f"/repos/{owner}/{repo}/releases",
                                json=release_data)
    
    def list_releases(self, owner: str, repo: str, page: int = 1, per_page: int = 30):
        """Liste les releases d'un repository"""
        return self._make_request("GET", f"/repos/{owner}/{repo}/releases?page={page}&per_page={per_page}")
    
    def upload_release_asset(self, owner: str, repo: str, tag_name: str, file_path: str):
        """Upload un asset de release"""
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            return self._make_request("POST", f"/repos/{owner}/{repo}/releases/{tag_name}/assets",
                                    files=files)
    
    # 📖 WIKI
    def create_wiki_page(self, owner: str, repo: str, title: str, content: str):
        """Crée une page wiki"""
        return self._make_request("POST", f"/repos/{owner}/{repo}/wiki",
                                json={"title": title, "content": content})
    
    def list_wiki_pages(self, owner: str, repo: str):
        """Liste les pages wiki"""
        return self._make_request("GET", f"/repos/{owner}/{repo}/wiki")
    
    # 🩺 SYSTÈME
    def health_check(self):
        """Vérifie la santé du serveur"""
        return self._make_request("GET", "/health")
    
    def system_info(self):
        """Récupère les infos système"""
        return self._make_request("GET", "/system/info")
    
    # 👥 UTILISATEURS
    def get_user(self, username: str):
        """Récupère les infos d'un utilisateur"""
        return self._make_request("GET", f"/users/{username}")
    
    def update_user(self, user_data: Dict):
        """Met à jour le profil utilisateur"""
        return self._make_request("PATCH", "/users/me", json=user_data)
    
    # 📁 PROJETS (pour compatibilité ancien code)
    def list_projects(self):
        """Liste les projets (alias pour repositories)"""
        return self.list_repos()
    
    def create_project(self, name: str, description: str = ""):
        """Crée un projet (alias pour repository)"""
        return self.create_repo(name, description)

# Client global
api_client = InitHUBClient()

# ============================================================================
# 🛠️ UTILITAIRES
# ============================================================================

def print_success(message):
    """Affiche un message de succès"""
    print(f"✅ {message}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"❌ {message}")

def print_info(message):
    """Affiche un message d'information"""
    print(f"ℹ️  {message}")

def print_warning(message):
    """Affiche un message d'avertissement"""
    print(f"⚠️  {message}")

def format_size(size_bytes):
    """Formate une taille en octets en format lisible"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def confirm_action(message: str) -> bool:
    """Demande confirmation à l'utilisateur"""
    response = input(f"❓ {message} (y/N): ")
    return response.lower() in ['y', 'yes', 'oui']

# ============================================================================
# 🚀 COMMANDES PRINCIPALES
# ============================================================================

def handle_login(args):
    """Connexion au serveur initHUB"""
    email = args.email
    password = args.password
    
    if not email or not password:
        print_error("Email et mot de passe requis")
        return False
    
    return api_client.login(email, password)

def handle_register(args):
    """Inscription au serveur initHUB"""
    username = args.username
    email = args.email
    password = args.password
    full_name = args.full_name or ""
    
    if not all([username, email, password]):
        print_error("Username, email et mot de passe requis")
        return False
    
    return api_client.register(username, email, password, full_name)

def handle_whoami(args):
    """Affiche l'utilisateur connecté"""
    user = api_client.get_current_user()
    if user:
        print_success("Utilisateur connecté:")
        print(f"   📛 Username: {user['username']}")
        print(f"   📧 Email: {user['email']}")
        print(f"   👤 Nom complet: {user.get('full_name', 'Non défini')}")
        print(f"   🏢 Company: {user.get('company', 'Non défini')}")
        print(f"   📍 Location: {user.get('location', 'Non défini')}")
        print(f"   📝 Bio: {user.get('bio', 'Non défini')}")
        return True
    else:
        print_error("Non connecté")
        return False

def handle_logout(args):
    """Déconnexion du serveur"""
    config.TOKEN_FILE.unlink(missing_ok=True)
    print_success("Déconnecté avec succès")
    return True

def handle_status(args):
    """Statut de la connexion et informations"""
    print(f"🌐 Serveur: {config.get_server_url()}")
    
    # Vérifier la santé du serveur
    try:
        health = api_client.health_check()
        print_success("Serveur en ligne")
        print(f"📊 Version: {health.get('version', 'N/A')}")
        print(f"🗄️  Database: {health.get('database', 'N/A')}")
        
        services = health.get('services', {})
        print("🔧 Services:")
        for service, status in services.items():
            status_icon = "🟢" if status == "online" or status == "running" else "🔴"
            print(f"   {status_icon} {service}: {status}")
            
    except Exception as e:
        print_error(f"Serveur hors ligne: {e}")
        return False
    
    # Informations utilisateur
    user = api_client.get_current_user()
    if user:
        print_success(f"Connecté en tant que: {user['username']}")
        
        # Récupérer le dashboard pour les stats
        try:
            dashboard = api_client.get_dashboard()
            stats = dashboard
            print("📊 Statistiques personnelles:")
            print(f"   📁 Repositories: {stats.get('total_repos', 0)}")
            print(f"   ⭐ Stars: {stats.get('total_stars', 0)}")
            print(f"   🔀 Forks: {stats.get('total_forks', 0)}")
        except:
            print_warning("Impossible de récupérer les statistiques")
    else:
        print_warning("Non connecté")
    
    return True

# ============================================================================
# 📁 COMMANDES REPOSITORIES
# ============================================================================

def handle_repo_create(args):
    """Crée un nouveau repository"""
    name = args.name
    description = args.description or ""
    is_private = args.private
    
    user = api_client.get_current_user()
    if not user:
        print_error("Non connecté. Utilisez 'inithub login' d'abord.")
        return False
    
    try:
        repo = api_client.create_repo(name, description, is_private)
        print_success(f"Repository créé: {repo['full_name']}")
        print(f"📝 Description: {repo['description']}")
        print(f"🔒 Visibilité: {'Privé' if repo['is_private'] else 'Public'}")
        print(f"🌐 URL: {repo['html_url']}")
        print(f"🔗 Clone: {repo['clone_url']}")
        return True
    except Exception as e:
        print_error(f"Erreur création repository: {e}")
        return False

def handle_repo_list(args):
    """Liste les repositories"""
    page = args.page or 1
    per_page = args.per_page or 30
    
    try:
        repos = api_client.list_repos(page, per_page)
        
        if not repos:
            print_info("Aucun repository trouvé")
            return True
        
        print(f"📁 Repositories ({len(repos)}):")
        print("─" * 80)
        
        for repo in repos:
            visibility = "🔒" if repo['is_private'] else "🌐"
            print(f"{visibility} {repo['full_name']}")
            print(f"   📝 {repo['description'] or 'Pas de description'}")
            print(f"   ⭐ {repo['stars_count']} stars | 🔀 {repo['forks_count']} forks | 👀 {repo['watchers_count']} watchers")
            print(f"   🏷️  {repo['default_branch']} | 📅 {repo['updated_at'][:10]}")
            print()
        
        return True
    except Exception as e:
        print_error(f"Erreur liste repositories: {e}")
        return False

def handle_repo_view(args):
    """Affiche les détails d'un repository"""
    owner = args.owner
    repo_name = args.repo
    
    try:
        repo = api_client.get_repo(owner, repo_name)
        
        print_success(f"Repository: {repo['full_name']}")
        print(f"📝 Description: {repo['description']}")
        print(f"🔒 Visibilité: {'Privé' if repo['is_private'] else 'Public'}")
        print(f"👤 Propriétaire: {repo['owner']['username']}")
        print(f"📊 Statistiques:")
        print(f"   ⭐ Stars: {repo['stars_count']}")
        print(f"   🔀 Forks: {repo['forks_count']}")
        print(f"   👀 Watchers: {repo['watchers_count']}")
        print(f"   🐛 Issues: {repo['open_issues_count']}")
        print(f"   🔀 PRs: {repo['open_pr_count']}")
        print(f"🌐 URLs:")
        print(f"   📄 HTML: {repo['html_url']}")
        print(f"   🔗 Clone: {repo['clone_url']}")
        print(f"   🔑 SSH: {repo['ssh_url']}")
        print(f"📅 Dates:")
        print(f"   Créé: {repo['created_at']}")
        print(f"   Modifié: {repo['updated_at']}")
        print(f"   Dernier push: {repo['pushed_at']}")
        
        # Récupérer les analytics si disponibles
        try:
            analytics = api_client.get_repo_analytics(owner, repo_name)
            print(f"📈 Analytics:")
            print(f"   👥 Contributeurs: {analytics.get('stats', {}).get('stargazers', 0)}")
            print(f"   📊 Vues: {analytics.get('traffic', {}).get('views', 0)}")
            print(f"   📥 Clones: {analytics.get('traffic', {}).get('clones', 0)}")
        except:
            print_warning("Analytics non disponibles")
        
        return True
    except Exception as e:
        print_error(f"Erreur vue repository: {e}")
        return False

def handle_repo_delete(args):
    """Supprime un repository"""
    owner = args.owner
    repo_name = args.repo
    
    if not confirm_action(f"Supprimer le repository {owner}/{repo_name} ? Cette action est irréversible."):
        print_info("Suppression annulée")
        return False
    
    try:
        api_client.delete_repo(owner, repo_name)
        print_success(f"Repository {owner}/{repo_name} supprimé")
        return True
    except Exception as e:
        print_error(f"Erreur suppression repository: {e}")
        return False

# ============================================================================
# ⭐ COMMANDES STARS & FORKS
# ============================================================================

def handle_repo_star(args):
    """Star un repository"""
    owner = args.owner
    repo_name = args.repo
    
    try:
        api_client.star_repo(owner, repo_name)
        print_success(f"Repository {owner}/{repo_name} staré")
        return True
    except Exception as e:
        print_error(f"Erreur star repository: {e}")
        return False

def handle_repo_unstar(args):
    """Unstar un repository"""
    owner = args.owner
    repo_name = args.repo
    
    try:
        api_client.unstar_repo(owner, repo_name)
        print_success(f"Repository {owner}/{repo_name} unstaré")
        return True
    except Exception as e:
        print_error(f"Erreur unstar repository: {e}")
        return False

def handle_repo_fork(args):
    """Fork un repository"""
    owner = args.owner
    repo_name = args.repo
    
    try:
        fork = api_client.fork_repo(owner, repo_name)
        print_success(f"Repository forké: {fork['full_name']}")
        print(f"🌐 URL: {fork['html_url']}")
        return True
    except Exception as e:
        print_error(f"Erreur fork repository: {e}")
        return False

# ============================================================================
# 🔑 COMMANDES TOKENS
# ============================================================================

def handle_token_create(args):
    """Crée un token personnel"""
    name = args.name
    scopes = args.scopes or ["read"]
    
    try:
        token = api_client.create_token(name, scopes)
        print_success(f"Token créé: {token['name']}")
        print(f"🔑 Token: {token['token']}")
        print(f"⚠️  IMPORTANT: Sauvegardez ce token, il ne sera plus affiché!")
        print(f"📋 Scopes: {', '.join(token['scopes'])}")
        print(f"📅 Créé: {token['created_at']}")
        return True
    except Exception as e:
        print_error(f"Erreur création token: {e}")
        return False

def handle_token_list(args):
    """Liste les tokens personnels"""
    try:
        tokens = api_client.list_tokens()
        
        if not tokens:
            print_info("Aucun token personnel trouvé")
            return True
        
        print(f"🔑 Tokens personnels ({len(tokens)}):")
        print("─" * 80)
        
        for token in tokens:
            print(f"📛 {token['name']} (ID: {token['id']})")
            print(f"   📋 Scopes: {', '.join(token['scopes'])}")
            print(f"   📅 Créé: {token['created_at']}")
            if token['last_used']:
                print(f"   🔄 Dernière utilisation: {token['last_used']}")
            print()
        
        return True
    except Exception as e:
        print_error(f"Erreur liste tokens: {e}")
        return False

def handle_token_delete(args):
    """Supprime un token personnel"""
    token_id = args.token_id
    
    if not confirm_action(f"Supprimer le token {token_id} ?"):
        print_info("Suppression annulée")
        return False
    
    try:
        api_client.delete_token(token_id)
        print_success(f"Token {token_id} supprimé")
        return True
    except Exception as e:
        print_error(f"Erreur suppression token: {e}")
        return False

# ============================================================================
# 🤖 COMMANDES COPILOT
# ============================================================================

def handle_copilot_ask(args):
    """Pose une question à Copilot"""
    question = args.question
    context = args.context or ""
    max_length = args.max_length or 150
    language = args.language or "auto"
    
    try:
        # Vérifier d'abord la santé de Copilot
        health = api_client.copilot_health()
        if not health.get('online', False):
            print_error("Copilot n'est pas disponible")
            return False
        
        response = api_client.ask_copilot(question, context, max_length, language)
        
        print_success("Réponse de Copilot:")
        print("─" * 80)
        print(response['response'])
        print("─" * 80)
        print(f"📅 {response['timestamp']} | 🌐 {'En ligne' if response['copilot_online'] else 'Hors ligne'}")
        
        return True
    except Exception as e:
        print_error(f"Erreur Copilot: {e}")
        return False

def handle_copilot_analyze(args):
    """Analyse du code avec Copilot"""
    code = args.code
    language = args.language
    analysis_type = args.analysis_type or "complexity"
    
    if not code:
        # Lire le code depuis un fichier
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    code = f.read()
            except Exception as e:
                print_error(f"Erreur lecture fichier: {e}")
                return False
        else:
            print_error("Code ou fichier requis")
            return False
    
    try:
        analysis = api_client.analyze_code(code, language, analysis_type)
        
        print_success(f"Analyse {analysis_type} du code {language}:")
        print("─" * 80)
        print(analysis['result'])
        print("─" * 80)
        
        return True
    except Exception as e:
        print_error(f"Erreur analyse code: {e}")
        return False

def handle_copilot_suggest(args):
    """Suggère des messages de commit"""
    diff = args.diff
    files = args.files or []
    
    if not diff:
        print_error("Diff requis")
        return False
    
    try:
        suggestions = api_client.suggest_commit(diff, files)
        
        print_success("Suggestions de messages de commit:")
        print("─" * 80)
        for i, suggestion in enumerate(suggestions['suggestions'], 1):
            print(f"{i}. {suggestion}")
        print("─" * 80)
        
        return True
    except Exception as e:
        print_error(f"Erreur suggestions commit: {e}")
        return False

def handle_copilot_health(args):
    """Vérifie l'état de Copilot"""
    try:
        health = api_client.copilot_health()
        
        status = "🟢 EN LIGNE" if health['online'] else "🔴 HORS LIGNE"
        print(f"🤖 Copilot: {status}")
        print(f"🌐 URL: {health['base_url']}")
        print(f"📅 Dernière vérification: {health['timestamp']}")
        
        return health['online']
    except Exception as e:
        print_error(f"Erreur vérification Copilot: {e}")
        return False

# ============================================================================
# 🏷️ COMMANDES RELEASES
# ============================================================================

def handle_release_create(args):
    """Crée une release"""
    owner = args.owner
    repo = args.repo
    tag_name = args.tag_name
    name = args.name or tag_name
    body = args.body or ""
    target = args.target or "main"
    draft = args.draft
    prerelease = args.prerelease
    
    release_data = {
        "tag_name": tag_name,
        "target_commitish": target,
        "name": name,
        "body": body,
        "draft": draft,
        "prerelease": prerelease
    }
    
    try:
        release = api_client.create_release(owner, repo, release_data)
        print_success(f"Release créée: {release['tag_name']}")
        print(f"📛 Nom: {release['name']}")
        print(f"📝 Description: {release['body']}")
        print(f"🏷️  Tag: {release['tag_name']}")
        print(f"🎯 Target: {release['target_commitish']}")
        print(f"📦 Assets: {len(release['assets'])}")
        print(f"👤 Auteur: {release['author']['username']}")
        print(f"📅 Créée: {release['created_at']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur création release: {e}")
        return False

def handle_release_list(args):
    """Liste les releases d'un repository"""
    owner = args.owner
    repo = args.repo
    page = args.page or 1
    per_page = args.per_page or 30
    
    try:
        releases = api_client.list_releases(owner, repo, page, per_page)
        
        if not releases:
            print_info("Aucune release trouvée")
            return True
        
        print(f"📦 Releases de {owner}/{repo} ({len(releases)}):")
        print("─" * 80)
        
        for release in releases:
            draft = "📝" if release['draft'] else "📦"
            prerelease = "🚧" if release['prerelease'] else "✅"
            print(f"{draft}{prerelease} {release['tag_name']} - {release['name']}")
            print(f"   📝 {release['body'][:100]}{'...' if len(release['body']) > 100 else ''}")
            print(f"   👤 {release['author']['username']} | 📅 {release['created_at'][:10]}")
            print(f"   📊 Assets: {len(release['assets'])}")
            print()
        
        return True
    except Exception as e:
        print_error(f"Erreur liste releases: {e}")
        return False

def handle_release_upload(args):
    """Upload un asset de release"""
    owner = args.owner
    repo = args.repo
    tag_name = args.tag_name
    file_path = args.file
    
    if not os.path.exists(file_path):
        print_error(f"Fichier non trouvé: {file_path}")
        return False
    
    try:
        asset = api_client.upload_release_asset(owner, repo, tag_name, file_path)
        print_success(f"Asset uploadé: {asset['name']}")
        print(f"📏 Taille: {format_size(asset['size'])}")
        print(f"📄 Type: {asset['content_type']}")
        print(f"🔗 URL: {asset['download_url']}")
        print(f"📅 Uploadé: {asset['uploaded_at']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur upload asset: {e}")
        return False

# ============================================================================
# 📖 COMMANDES WIKI
# ============================================================================

def handle_wiki_create(args):
    """Crée une page wiki"""
    owner = args.owner
    repo = args.repo
    title = args.title
    content = args.content or ""
    
    if not content and args.file:
        try:
            with open(args.file, 'r') as f:
                content = f.read()
        except Exception as e:
            print_error(f"Erreur lecture fichier: {e}")
            return False
    
    try:
        page = api_client.create_wiki_page(owner, repo, title, content)
        print_success(f"Page wiki créée: {page['title']}")
        print(f"📝 Contenu: {len(page['content'])} caractères")
        print(f"👤 Auteur: {page['author']['username']}")
        print(f"📅 Créée: {page['created_at']}")
        
        return True
    except Exception as e:
        print_error(f"Erreur création page wiki: {e}")
        return False

def handle_wiki_list(args):
    """Liste les pages wiki"""
    owner = args.owner
    repo = args.repo
    
    try:
        pages = api_client.list_wiki_pages(owner, repo)
        
        if not pages:
            print_info("Aucune page wiki trouvée")
            return True
        
        print(f"📖 Pages wiki de {owner}/{repo} ({len(pages)}):")
        print("─" * 80)
        
        for page in pages:
            print(f"📄 {page['title']}")
            print(f"   📝 {page['content'][:100]}{'...' if len(page['content']) > 100 else ''}")
            print(f"   👤 {page['author']['username']} | 📅 {page['updated_at'][:10]}")
            print()
        
        return True
    except Exception as e:
        print_error(f"Erreur liste pages wiki: {e}")
        return False

# ============================================================================
# 🎯 INTERFACE CLI PRINCIPALE
# ============================================================================

def main():
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║              🚀 initHUB CLI ULTIMATE          ║
    ║     Version complète - Toutes les routes      ║
    ╚═══════════════════════════════════════════════╝
    """
    
    print(banner)
    
    parser = argparse.ArgumentParser(
        description="🚀 initHUB CLI - Client complet avec toutes les routes du serveur",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  🔐 Authentification:
    inithub login --email user@example.com --password secret
    inithub register --username john --email john@example.com --password secret
    inithub whoami
    inithub logout
    inithub status

  📁 Repositories:
    inithub repo create --name mon-projet --description "Mon super projet"
    inithub repo list
    inithub repo view --owner user --repo mon-projet
    inithub repo delete --owner user --repo mon-projet

  ⭐ Social:
    inithub repo star --owner user --repo mon-projet
    inithub repo unstar --owner user --repo mon-projet  
    inithub repo fork --owner user --repo mon-projet

  🔑 Tokens:
    inithub token create --name "Mon token"
    inithub token list
    inithub token delete --token-id 123

  🤖 Copilot:
    inithub copilot ask --question "Comment faire X?"
    inithub copilot analyze --file mon_script.py --language python
    inithub copilot suggest --diff "git diff" --files file1.py file2.py
    inithub copilot health

  🏷️ Releases:
    inithub release create --owner user --repo mon-projet --tag-name v1.0.0
    inithub release list --owner user --repo mon-projet
    inithub release upload --owner user --repo mon-projet --tag-name v1.0.0 --file build.zip

  📖 Wiki:
    inithub wiki create --owner user --repo mon-projet --title "Documentation"
    inithub wiki list --owner user --repo mon-projet

  🩺 Système:
    inithub system health
    inithub system info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # 🔐 Authentification
    auth_parser = subparsers.add_parser('auth', help='Authentification')
    auth_subparsers = auth_parser.add_subparsers(dest='auth_command')
    
    login_parser = auth_subparsers.add_parser('login', help='Connexion')
    login_parser.add_argument('--email', required=True, help='Email')
    login_parser.add_argument('--password', required=True, help='Mot de passe')
    
    register_parser = auth_subparsers.add_parser('register', help='Inscription')
    register_parser.add_argument('--username', required=True, help='Nom d\'utilisateur')
    register_parser.add_argument('--email', required=True, help='Email')
    register_parser.add_argument('--password', required=True, help='Mot de passe')
    register_parser.add_argument('--full-name', help='Nom complet')
    
    auth_subparsers.add_parser('whoami', help='Utilisateur connecté')
    auth_subparsers.add_parser('logout', help='Déconnexion')
    auth_subparsers.add_parser('status', help='Statut connexion')
    
    # 📁 Repositories
    repo_parser = subparsers.add_parser('repo', help='Gestion des repositories')
    repo_subparsers = repo_parser.add_subparsers(dest='repo_command')
    
    repo_create_parser = repo_subparsers.add_parser('create', help='Créer un repository')
    repo_create_parser.add_argument('--name', required=True, help='Nom du repository')
    repo_create_parser.add_argument('--description', help='Description')
    repo_create_parser.add_argument('--private', action='store_true', help='Repository privé')
    
    repo_subparsers.add_parser('list', help='Lister les repositories')
    
    repo_view_parser = repo_subparsers.add_parser('view', help='Voir un repository')
    repo_view_parser.add_argument('--owner', required=True, help='Propriétaire')
    repo_view_parser.add_argument('--repo', required=True, help='Nom du repository')
    
    repo_delete_parser = repo_subparsers.add_parser('delete', help='Supprimer un repository')
    repo_delete_parser.add_argument('--owner', required=True, help='Propriétaire')
    repo_delete_parser.add_argument('--repo', required=True, help='Nom du repository')
    
    # ⭐ Social
    social_parser = subparsers.add_parser('social', help='Actions sociales')
    social_subparsers = social_parser.add_subparsers(dest='social_command')
    
    star_parser = social_subparsers.add_parser('star', help='Star un repository')
    star_parser.add_argument('--owner', required=True, help='Propriétaire')
    star_parser.add_argument('--repo', required=True, help='Nom du repository')
    
    unstar_parser = social_subparsers.add_parser('unstar', help='Unstar un repository')
    unstar_parser.add_argument('--owner', required=True, help='Propriétaire')
    unstar_parser.add_argument('--repo', required=True, help='Nom du repository')
    
    fork_parser = social_subparsers.add_parser('fork', help='Fork un repository')
    fork_parser.add_argument('--owner', required=True, help='Propriétaire')
    fork_parser.add_argument('--repo', required=True, help='Nom du repository')
    
    # 🔑 Tokens
    token_parser = subparsers.add_parser('token', help='Tokens personnels')
    token_subparsers = token_parser.add_subparsers(dest='token_command')
    
    token_create_parser = token_subparsers.add_parser('create', help='Créer un token')
    token_create_parser.add_argument('--name', required=True, help='Nom du token')
    token_create_parser.add_argument('--scopes', nargs='+', help='Scopes du token')
    
    token_subparsers.add_parser('list', help='Lister les tokens')
    
    token_delete_parser = token_subparsers.add_parser('delete', help='Supprimer un token')
    token_delete_parser.add_argument('--token-id', required=True, type=int, help='ID du token')
    
    # 🤖 Copilot
    copilot_parser = subparsers.add_parser('copilot', help='Assistant IA Copilot')
    copilot_subparsers = copilot_parser.add_subparsers(dest='copilot_command')
    
    copilot_ask_parser = copilot_subparsers.add_parser('ask', help='Poser une question')
    copilot_ask_parser.add_argument('--question', required=True, help='Question à poser')
    copilot_ask_parser.add_argument('--context', help='Contexte')
    copilot_ask_parser.add_argument('--max-length', type=int, help='Longueur max réponse')
    copilot_ask_parser.add_argument('--language', help='Langue de réponse')
    
    copilot_analyze_parser = copilot_subparsers.add_parser('analyze', help='Analyser du code')
    copilot_analyze_parser.add_argument('--code', help='Code à analyser')
    copilot_analyze_parser.add_argument('--file', help='Fichier à analyser')
    copilot_analyze_parser.add_argument('--language', required=True, help='Langage du code')
    copilot_analyze_parser.add_argument('--analysis-type', help='Type d\'analyse')
    
    copilot_suggest_parser = copilot_subparsers.add_parser('suggest', help='Suggérer commits')
    copilot_suggest_parser.add_argument('--diff', required=True, help='Diff git')
    copilot_suggest_parser.add_argument('--files', nargs='+', help='Fichiers modifiés')
    
    copilot_subparsers.add_parser('health', help='Santé de Copilot')
    
    # 🏷️ Releases
    release_parser = subparsers.add_parser('release', help='Gestion des releases')
    release_subparsers = release_parser.add_subparsers(dest='release_command')
    
    release_create_parser = release_subparsers.add_parser('create', help='Créer une release')
    release_create_parser.add_argument('--owner', required=True, help='Propriétaire')
    release_create_parser.add_argument('--repo', required=True, help='Repository')
    release_create_parser.add_argument('--tag-name', required=True, help='Nom du tag')
    release_create_parser.add_argument('--name', help='Nom de la release')
    release_create_parser.add_argument('--body', help='Description')
    release_create_parser.add_argument('--target', help='Branche cible')
    release_create_parser.add_argument('--draft', action='store_true', help='Release brouillon')
    release_create_parser.add_argument('--prerelease', action='store_true', help='Pre-release')
    
    release_list_parser = release_subparsers.add_parser('list', help='Lister les releases')
    release_list_parser.add_argument('--owner', required=True, help='Propriétaire')
    release_list_parser.add_argument('--repo', required=True, help='Repository')
    release_list_parser.add_argument('--page', type=int, help='Page')
    release_list_parser.add_argument('--per-page', type=int, help='Éléments par page')
    
    release_upload_parser = release_subparsers.add_parser('upload', help='Uploader un asset')
    release_upload_parser.add_argument('--owner', required=True, help='Propriétaire')
    release_upload_parser.add_argument('--repo', required=True, help='Repository')
    release_upload_parser.add_argument('--tag-name', required=True, help='Tag de la release')
    release_upload_parser.add_argument('--file', required=True, help='Fichier à uploader')
    
    # 📖 Wiki
    wiki_parser = subparsers.add_parser('wiki', help='Documentation wiki')
    wiki_subparsers = wiki_parser.add_subparsers(dest='wiki_command')
    
    wiki_create_parser = wiki_subparsers.add_parser('create', help='Créer une page')
    wiki_create_parser.add_argument('--owner', required=True, help='Propriétaire')
    wiki_create_parser.add_argument('--repo', required=True, help='Repository')
    wiki_create_parser.add_argument('--title', required=True, help='Titre de la page')
    wiki_create_parser.add_argument('--content', help='Contenu')
    wiki_create_parser.add_argument('--file', help='Fichier de contenu')
    
    wiki_list_parser = wiki_subparsers.add_parser('list', help='Lister les pages')
    wiki_list_parser.add_argument('--owner', required=True, help='Propriétaire')
    wiki_list_parser.add_argument('--repo', required=True, help='Repository')
    
    # 🩺 Système
    system_parser = subparsers.add_parser('system', help='Système et santé')
    system_subparsers = system_parser.add_subparsers(dest='system_command')
    
    system_subparsers.add_parser('health', help='Santé du serveur')
    system_subparsers.add_parser('info', help='Informations système')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        success = False
        
        # 🔐 Authentification
        if args.command == 'auth':
            if args.auth_command == 'login':
                success = handle_login(args)
            elif args.auth_command == 'register':
                success = handle_register(args)
            elif args.auth_command == 'whoami':
                success = handle_whoami(args)
            elif args.auth_command == 'logout':
                success = handle_logout(args)
            elif args.auth_command == 'status':
                success = handle_status(args)
            else:
                auth_parser.print_help()
        
        # 📁 Repositories
        elif args.command == 'repo':
            if args.repo_command == 'create':
                success = handle_repo_create(args)
            elif args.repo_command == 'list':
                success = handle_repo_list(args)
            elif args.repo_command == 'view':
                success = handle_repo_view(args)
            elif args.repo_command == 'delete':
                success = handle_repo_delete(args)
            else:
                repo_parser.print_help()
        
        # ⭐ Social
        elif args.command == 'social':
            if args.social_command == 'star':
                success = handle_repo_star(args)
            elif args.social_command == 'unstar':
                success = handle_repo_unstar(args)
            elif args.social_command == 'fork':
                success = handle_repo_fork(args)
            else:
                social_parser.print_help()
        
        # 🔑 Tokens
        elif args.command == 'token':
            if args.token_command == 'create':
                success = handle_token_create(args)
            elif args.token_command == 'list':
                success = handle_token_list(args)
            elif args.token_command == 'delete':
                success = handle_token_delete(args)
            else:
                token_parser.print_help()
        
        # 🤖 Copilot
        elif args.command == 'copilot':
            if args.copilot_command == 'ask':
                success = handle_copilot_ask(args)
            elif args.copilot_command == 'analyze':
                success = handle_copilot_analyze(args)
            elif args.copilot_command == 'suggest':
                success = handle_copilot_suggest(args)
            elif args.copilot_command == 'health':
                success = handle_copilot_health(args)
            else:
                copilot_parser.print_help()
        
        # 🏷️ Releases
        elif args.command == 'release':
            if args.release_command == 'create':
                success = handle_release_create(args)
            elif args.release_command == 'list':
                success = handle_release_list(args)
            elif args.release_command == 'upload':
                success = handle_release_upload(args)
            else:
                release_parser.print_help()
        
        # 📖 Wiki
        elif args.command == 'wiki':
            if args.wiki_command == 'create':
                success = handle_wiki_create(args)
            elif args.wiki_command == 'list':
                success = handle_wiki_list(args)
            else:
                wiki_parser.print_help()
        
        # 🩺 Système
        elif args.command == 'system':
            if args.system_command == 'health':
                success = handle_status(args)  # Réutilise status pour health
            elif args.system_command == 'info':
                try:
                    info = api_client.system_info()
                    print(json.dumps(info, indent=2))
                    success = True
                except Exception as e:
                    print_error(f"Erreur info système: {e}")
                    success = False
            else:
                system_parser.print_help()
        
        else:
            print_error(f"Commande inconnue: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n👋 Opération annulée!")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
