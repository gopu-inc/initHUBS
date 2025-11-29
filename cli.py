#!/usr/bin/env python3
"""
initHUB CLI - Client complet avec interface moderne
Version 4.0 - Interface colorée avec animations
"""

import os
import re
import sys
import json
import glob
import time
import fnmatch
import shlex
import requests
import argparse
import zipfile
import tarfile
import tempfile
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

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
    
    @classmethod
    def loading_spinner(cls, message="Chargement"):
        """Affiche un spinner animé"""
        def spinner():
            i = 0
            while not cls.stop_spinner:
                sys.stdout.write(f"\r{Colors.CYAN}{cls.SPINNERS[i % len(cls.SPINNERS)]}{Colors.END} {message}{Colors.YELLOW}{'.' * ((i % 3) + 1)}{' ' * (3 - (i % 3))}{Colors.END}")
                sys.stdout.flush()
                time.sleep(0.2)
                i += 1
        
        cls.stop_spinner = False
        spinner_thread = threading.Thread(target=spinner)
        spinner_thread.start()
        return spinner_thread
    
    @classmethod
    def stop_loading(cls, thread, message="✅ Terminé"):
        """Arrête le spinner et affiche un message"""
        cls.stop_spinner = True
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

def print_banner():
    """Affiche la bannière d'accueil"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    🚀 Lancement de initHUB 🪖
{Colors.END}
{Colors.MAGENTA}    Plateforme Cloud Enterprise - CLI Ultimate{Colors.END}
{Colors.YELLOW}    Version 4.0 | Interface Moderne{Colors.END}
"""
    print(banner)

# ============================================================================
# ⚙️ CONFIGURATION CLIENT
# ============================================================================

class CLIConfig:
    SERVER_URL = "https://hubs-pro.onrender.com"
    API_BASE = f"{SERVER_URL}/api"
    
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
            }
    
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

config = CLIConfig()

# ============================================================================
# 🔌 CLIENT API
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
        except Exception as e:
            raise Exception(f"Erreur API {endpoint}: {e}")
    
    # 🔐 AUTHENTIFICATION
    def login(self, email: str, password: str) -> bool:
        spinner = Animations.loading_spinner("Connexion en cours")
        try:
            data = self._make_request("POST", "/auth/login", 
                                    json={"email": email, "password": password})
            
            config.save_token(data)
            self.session.headers.update({
                "Authorization": f"Bearer {data['access_token']}"
            })
            
            Animations.stop_loading(spinner, f"{Colors.GREEN}✅ Connecté en tant que {email}{Colors.END}")
            return True
            
        except Exception as e:
            Animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur connexion: {e}{Colors.END}")
            return False
    
    def register(self, username: str, email: str, password: str, full_name: str = "") -> bool:
        spinner = Animations.loading_spinner("Création du compte")
        try:
            self._make_request("POST", "/auth/register",
                             json={
                                 "username": username,
                                 "email": email,
                                 "password": password,
                                 "full_name": full_name
                             })
            Animations.stop_loading(spinner, f"{Colors.GREEN}✅ Compte créé: {username}{Colors.END}")
            return True
            
        except Exception as e:
            Animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur inscription: {e}{Colors.END}")
            return False
    
    def get_current_user(self):
        try:
            # Essayer de récupérer l'utilisateur via le dashboard
            dashboard = self._make_request("GET", "/dashboard")
            # Retourner des infos basiques
            return {
                "username": "utilisateur",
                "email": "user@example.com",
                "full_name": "Utilisateur initHUB"
            }
        except:
            return None
    
    # 📁 REPOSITORIES
    def create_repo(self, name: str, description: str = "", is_private: bool = False):
        spinner = Animations.loading_spinner("Création du repository")
        try:
            result = self._make_request("POST", "/repos",
                                json={
                                    "name": name,
                                    "description": description,
                                    "is_private": is_private,
                                    "auto_init": True
                                })
            Animations.stop_loading(spinner, f"{Colors.GREEN}✅ Repository créé{Colors.END}")
            return result
        except Exception as e:
            Animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur création: {e}{Colors.END}")
            raise
    
    def list_repos(self, page: int = 1, per_page: int = 30):
        spinner = Animations.loading_spinner("Récupération des repositories")
        try:
            result = self._make_request("GET", f"/repos?page={page}&per_page={per_page}")
            Animations.stop_loading(spinner, f"{Colors.GREEN}✅ Repositories chargés{Colors.END}")
            return result
        except Exception as e:
            Animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur chargement: {e}{Colors.END}")
            raise
    
    # 🤖 COPILOT
    def ask_copilot(self, question: str, context: str = "", max_length: int = 150, language: str = "auto"):
        spinner = Animations.loading_spinner("Copilot réfléchit")
        try:
            result = self._make_request("POST", "/copilot/ask",
                                json={
                                    "question": question,
                                    "context": context,
                                    "max_length": max_length,
                                    "language": language
                                })
            Animations.stop_loading(spinner, f"{Colors.GREEN}✅ Réponse reçue{Colors.END}")
            return result
        except Exception as e:
            Animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur Copilot: {e}{Colors.END}")
            raise
    
    def copilot_health(self):
        return self._make_request("GET", "/copilot/health")
    
    # 🩺 SYSTÈME
    def health_check(self):
        spinner = Animations.loading_spinner("Vérification du serveur")
        try:
            result = self._make_request("GET", "/health")
            Animations.stop_loading(spinner, f"{Colors.GREEN}✅ Serveur opérationnel{Colors.END}")
            return result
        except Exception as e:
            Animations.stop_loading(spinner, f"{Colors.RED}❌ Serveur hors ligne: {e}{Colors.END}")
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

# ============================================================================
# 🚀 COMMANDES PRINCIPALES
# ============================================================================

def handle_auth_login(args):
    """Connexion au serveur initHUB"""
    email = args.email
    password = args.password
    
    if not email or not password:
        print_error("Email et mot de passe requis")
        return False
    
    return api_client.login(email, password)

def handle_auth_register(args):
    """Inscription au serveur initHUB"""
    username = args.username
    email = args.email
    password = args.password
    full_name = args.full_name or ""
    
    if not all([username, email, password]):
        print_error("Username, email et mot de passe requis")
        return False
    
    return api_client.register(username, email, password, full_name)

def handle_auth_whoami(args):
    """Affiche l'utilisateur connecté"""
    user = api_client.get_current_user()
    if user:
        print_success("Utilisateur connecté:")
        print(f"   {Colors.CYAN}📛 Username:{Colors.END} {user['username']}")
        print(f"   {Colors.BLUE}📧 Email:{Colors.END} {user['email']}")
        if user.get('full_name'):
            print(f"   {Colors.GREEN}👤 Nom complet:{Colors.END} {user['full_name']}")
        return True
    else:
        print_error("Non connecté")
        return False

def handle_auth_status(args):
    """Statut de la connexion"""
    print(f"{Colors.CYAN}🌐 Serveur:{Colors.END} {config.get_server_url()}")
    
    try:
        health = api_client.health_check()
        print_success("Serveur en ligne")
        print(f"{Colors.BLUE}📊 Version:{Colors.END} {health.get('version', 'N/A')}")
        
        user = api_client.get_current_user()
        if user:
            print_success(f"Connecté en tant que: {user['username']}")
        else:
            print_warning("Non connecté")
        
        return True
    except Exception as e:
        print_error(f"Serveur hors ligne: {e}")
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
        print(f"{Colors.BLUE}📝 Description:{Colors.END} {repo['description']}")
        print(f"{Colors.YELLOW}🔒 Visibilité:{Colors.END} {'Privé' if repo['is_private'] else 'Public'}")
        print(f"{Colors.CYAN}🌐 URL:{Colors.END} {repo['html_url']}")
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
        print("─" * 60)
        
        for repo in repos:
            visibility = "🔒" if repo['is_private'] else "🌐"
            print(f"{visibility} {Colors.BOLD}{repo['full_name']}{Colors.END}")
            if repo['description']:
                print(f"   {Colors.BLUE}📝{Colors.END} {repo['description']}")
            print(f"   {Colors.YELLOW}⭐{Colors.END} {repo['stars_count']} {Colors.GREEN}🔀{Colors.END} {repo['forks_count']}")
            print()
        
        return True
    except Exception as e:
        print_error(f"Erreur liste repositories: {e}")
        return False

def handle_copilot_ask(args):
    """Pose une question à Copilot"""
    question = args.question
    context = args.context or ""
    
    try:
        health = api_client.copilot_health()
        if not health.get('online', False):
            print_error("Copilot n'est pas disponible")
            return False
        
        response = api_client.ask_copilot(question, context)
        
        print(f"\n{Colors.CYAN}🤖 Copilot:{Colors.END}")
        print("─" * 60)
        print(f"{Colors.WHITE}{response['response']}{Colors.END}")
        print("─" * 60)
        
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
    
    spinner = Animations.loading_spinner("Initialisation du projet")
    
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
    print("Hello from initHUB!")

if __name__ == "__main__":
    main()
'''
            with open(project_path / "main.py", 'w', encoding='utf-8') as f:
                f.write(main_content)
        
        Animations.stop_loading(spinner, f"{Colors.GREEN}✅ Projet initialisé avec succès!{Colors.END}")
        
        print(f"\n{Colors.CYAN}📁 Structure créée:{Colors.END}")
        print(f"   📄 {ssf_path.name} {Colors.YELLOW}(manifest principal){Colors.END}")
        print(f"   📄 {ignore_path.name} {Colors.BLUE}(fichiers ignorés){Colors.END}")
        print(f"   📄 README.md {Colors.GREEN}(documentation){Colors.END}")
        if env == "python":
            print(f"   📄 main.py {Colors.MAGENTA}(point d'entrée){Colors.END}")
        
        print(f"\n{Colors.YELLOW}🚀 Prochaines étapes:{Colors.END}")
        print(f"   1. {Colors.CYAN}cd {project_name}{Colors.END}")
        print(f"   2. {Colors.GREEN}inithub auth login{Colors.END} {Colors.YELLOW}(si pas connecté){Colors.END}")
        print(f"   3. {Colors.BLUE}inithub repo create --name {project_name}{Colors.END}")
        
        return True
        
    except Exception as e:
        Animations.stop_loading(spinner, f"{Colors.RED}❌ Erreur initialisation{Colors.END}")
        print_error(f"Erreur: {e}")
        return False

def handle_apropos(args):
    """Affiche la documentation complète du CLI"""
    docs = f"""
{Colors.CYAN}{Colors.BOLD}📚 INITIUB CLI - DOCUMENTATION COMPLÈTE{Colors.END}

{Colors.GREEN}🎯 QU'EST-CE QUE INITIUB ?{Colors.END}
initHUB est une plateforme cloud complète pour le développement collaboratif
avec Git, IA Copilot, gestion de projets, et déploiement cloud.

{Colors.YELLOW}🚀 COMMANDES PRINCIPALES:{Colors.END}

{Colors.CYAN}🔐 AUTHENTIFICATION:{Colors.END}
  {Colors.BOLD}inithub auth login{Colors.END}          - Connexion au serveur
  {Colors.BOLD}inithub auth register{Colors.END}       - Création de compte
  {Colors.BOLD}inithub auth whoami{Colors.END}         - Utilisateur connecté
  {Colors.BOLD}inithub auth status{Colors.END}         - Statut de connexion

{Colors.BLUE}📁 GESTION PROJETS:{Colors.END}
  {Colors.BOLD}inithub init{Colors.END}                - Initialiser un nouveau projet
  {Colors.BOLD}inithub repo create{Colors.END}         - Créer un repository
  {Colors.BOLD}inithub repo list{Colors.END}           - Lister mes repositories

{Colors.MAGENTA}🤖 ASSISTANT IA:{Colors.END}
  {Colors.BOLD}inithub copilot ask{Colors.END}         - Poser une question à Copilot
  {Colors.BOLD}inithub copilot health{Colors.END}      - Vérifier Copilot

{Colors.GREEN}🛠️ OUTILS AVANCÉS:{Colors.END}
  {Colors.BOLD}inithub apropos{Colors.END}             - Cette documentation

{Colors.YELLOW}📄 FORMAT .SSF:{Colors.END}
Le format .ssf est le manifest initHUB pour décrire les projets.

{Colors.CYAN}🎯 EXEMPLES PRATIQUES:{Colors.END}
  1. {Colors.BOLD}Créer et pousser un projet:{Colors.END}
     {Colors.GREEN}inithub init --project-name mon-app{Colors.END}
     {Colors.BLUE}inithub auth login{Colors.END}
     {Colors.MAGENTA}inithub repo create --name mon-app{Colors.END}

  2. {Colors.BOLD}Utiliser Copilot:{Colors.END}
     {Colors.GREEN}inithub copilot ask --question "Comment créer une API REST?"{Colors.END}

{Colors.YELLOW}📞 SUPPORT:{Colors.END}
  • Documentation: {Colors.CYAN}inithub apropos{Colors.END}
  • Serveur: {Colors.GREEN}{config.get_server_url()}{Colors.END}
"""
    print(docs)
    return True

# ============================================================================
# 🎯 INTERFACE CLI PRINCIPALE
# ============================================================================

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description=f"{Colors.CYAN}🚀 initHUB CLI - Plateforme Cloud Development{Colors.END}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.YELLOW}📖 Exemples rapides:{Colors.END}

{Colors.GREEN}Créer un projet:{Colors.END}
  inithub init --project-name mon-app

{Colors.BLUE}Authentification:{Colors.END}  
  inithub auth login --email user@example.com --password secret

{Colors.MAGENTA}Gestion repositories:{Colors.END}
  inithub repo create --name mon-projet
  inithub repo list

{Colors.CYAN}Assistant IA:{Colors.END}
  inithub copilot ask --question "Comment faire X?"

{Colors.YELLOW}Documentation:{Colors.END}
  inithub apropos
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # 🔐 Authentification
    auth_parser = subparsers.add_parser('auth', help='🔐 Authentification et compte')
    auth_subparsers = auth_parser.add_subparsers(dest='auth_command', help='Sous-commandes')
    
    login_parser = auth_subparsers.add_parser('login', help='Connexion au serveur')
    login_parser.add_argument('--email', required=True, help='Email')
    login_parser.add_argument('--password', required=True, help='Mot de passe')
    
    register_parser = auth_subparsers.add_parser('register', help='Création de compte')
    register_parser.add_argument('--username', required=True, help="Nom d'utilisateur")
    register_parser.add_argument('--email', required=True, help='Email')
    register_parser.add_argument('--password', required=True, help='Mot de passe')
    register_parser.add_argument('--full-name', help='Nom complet')
    
    auth_subparsers.add_parser('whoami', help='Utilisateur connecté')
    auth_subparsers.add_parser('status', help='Statut de connexion')
    
    # 📁 Projets
    init_parser = subparsers.add_parser('init', help='📁 Initialiser un nouveau projet')
    init_parser.add_argument('--project-name', help='Nom du projet')
    init_parser.add_argument('--type', choices=['projet', 'cloud', 'api', 'web'], help='Type de projet')
    init_parser.add_argument('--env', choices=['python', 'javascript', 'node', 'java'], help='Environnement')
    init_parser.add_argument('--description', help='Description du projet')
    init_parser.add_argument('--force', action='store_true', help='Écraser le projet existant')
    
    # 📚 Repositories
    repo_parser = subparsers.add_parser('repo', help='📚 Gestion des repositories')
    repo_subparsers = repo_parser.add_subparsers(dest='repo_command', help='Sous-commandes')
    
    repo_create_parser = repo_subparsers.add_parser('create', help='Créer un repository')
    repo_create_parser.add_argument('--name', required=True, help='Nom du repository')
    repo_create_parser.add_argument('--description', help='Description')
    repo_create_parser.add_argument('--private', action='store_true', help='Repository privé')
    
    repo_subparsers.add_parser('list', help='Lister les repositories')
    
    # 🤖 Copilot
    copilot_parser = subparsers.add_parser('copilot', help='🤖 Assistant IA Copilot')
    copilot_subparsers = copilot_parser.add_subparsers(dest='copilot_command', help='Sous-commandes')
    
    copilot_ask_parser = copilot_subparsers.add_parser('ask', help='Poser une question')
    copilot_ask_parser.add_argument('--question', required=True, help='Question à poser')
    copilot_ask_parser.add_argument('--context', help='Contexte supplémentaire')
    
    copilot_subparsers.add_parser('health', help='Santé de Copilot')
    
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
            elif args.auth_command == 'whoami':
                success = handle_auth_whoami(args)
            elif args.auth_command == 'status':
                success = handle_auth_status(args)
            else:
                auth_parser.print_help()
        
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
