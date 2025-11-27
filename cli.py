#!/usr/bin/env python3
"""
initHUB CLI - Version sans dépendances externes
Utilise uniquement les modules Python standard
"""

import os
import sys
import json
import time
import uuid
import base64
import hashlib
import sqlite3
import getpass
import argparse
import platform
from pathlib import Path
from datetime import datetime
from urllib import request, parse, error
from http.client import HTTPResponse
from typing import Optional, List, Dict, Any

# Configuration
class Config:
    def __init__(self):
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".inithub"
        self.config_file = self.config_dir / "config.json"
        self.token_file = self.config_dir / "token"
        self.server_url = "https://hubs-ja2g.onrender.com"
        
        self._ensure_config_dir()
        self._load_config()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                self.server_url = config_data.get('server_url', self.server_url)
    
    def save_config(self, config_data: Dict[str, Any]):
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        self._load_config()
    
    def get_token(self) -> str:
        if self.token_file.exists():
            return self.token_file.read_text().strip()
        return None
    
    def save_token(self, token: str):
        self.token_file.write_text(token)
    
    def delete_token(self):
        if self.token_file.exists():
            self.token_file.unlink()

config = Config()

# Gestion d'authentification
class AuthManager:
    def __init__(self):
        self.base_url = config.server_url
        self.token = config.get_token()
    
    def is_authenticated(self) -> bool:
        return self.token is not None
    
    def login(self, email: str = None, password: str = None) -> bool:
        if not email:
            email = input("📧 Email: ")
        if not password:
            password = getpass.getpass("🔒 Mot de passe: ")
        
        try:
            data = json.dumps({"email": email, "password": password}).encode()
            req = request.Request(
                f"{self.base_url}/api/auth/login",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                token = result["access_token"]
                config.save_token(token)
                self.token = token
                print("✅ Connexion réussie!")
                return True
                
        except error.HTTPError as e:
            error_data = json.loads(e.read().decode())
            print(f"❌ Erreur de connexion: {error_data.get('detail', 'Unknown error')}")
            return False
        except Exception as e:
            print(f"❌ Erreur réseau: {e}")
            return False
    
    def register(self, username: str, email: str, password: str) -> bool:
        try:
            data = json.dumps({
                "username": username,
                "email": email,
                "password": password
            }).encode()
            
            req = request.Request(
                f"{self.base_url}/api/auth/register",
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with request.urlopen(req) as response:
                print("✅ Inscription réussie! Vous pouvez maintenant vous connecter.")
                return True
                
        except error.HTTPError as e:
            error_data = json.loads(e.read().decode())
            print(f"❌ Erreur d'inscription: {error_data.get('detail', 'Unknown error')}")
            return False
        except Exception as e:
            print(f"❌ Erreur réseau: {e}")
            return False
    
    def logout(self):
        config.delete_token()
        self.token = None
        print("✅ Déconnexion réussie!")
    
    def get_headers(self) -> Dict[str, str]:
        if not self.token:
            raise Exception("Non authentifié. Veuillez vous connecter avec 'inithub login'")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

auth_manager = AuthManager()

# Client API
class APIClient:
    def __init__(self):
        self.base_url = auth_manager.base_url
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Any:
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            headers = auth_manager.get_headers()
            
            if data:
                data_bytes = json.dumps(data).encode()
                req = request.Request(url, data=data_bytes, headers=headers, method=method)
            else:
                req = request.Request(url, headers=headers, method=method)
            
            with request.urlopen(req) as response:
                return json.loads(response.read().decode())
                
        except error.HTTPError as e:
            if e.code == 401:
                print("❌ Non authentifié. Veuillez vous connecter avec 'inithub login'")
                raise Exception("Authentication required")
            elif e.code == 404:
                print("❌ Ressource non trouvée")
                raise Exception("Resource not found")
            else:
                error_data = json.loads(e.read().decode())
                print(f"❌ Erreur {e.code}: {error_data.get('detail', 'Unknown error')}")
                raise Exception(f"API Error: {error_data.get('detail', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Erreur réseau: {e}")
            raise
    
    def get(self, endpoint: str, params: Dict = None) -> Any:
        if params:
            query_string = parse.urlencode(params)
            endpoint = f"{endpoint}?{query_string}"
        return self._make_request('GET', endpoint)
    
    def post(self, endpoint: str, data: Dict = None) -> Any:
        return self._make_request('POST', endpoint, data)
    
    def upload_file(self, file_path: str, model_id: Optional[int] = None, description: str = "") -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise Exception(f"Fichier non trouvé: {file_path}")
        
        print(f"📤 Upload de: {os.path.basename(file_path)}...")
        
        try:
            # Pour l'upload de fichiers, on utiliserait un formulaire multipart
            # Mais pour simplifier sans dépendances, on envoie le contenu en base64
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            file_b64 = base64.b64encode(file_content).decode()
            data = {
                "filename": os.path.basename(file_path),
                "content": file_b64,
                "description": description
            }
            
            if model_id:
                data["model_id"] = model_id
            
            return self.post("/upload", data)
            
        except Exception as e:
            print(f"❌ Erreur upload: {e}")
            raise

api_client = APIClient()

# Gestion des modèles
class ModelsManager:
    def list_models(self, framework: str = None, task_type: str = None, limit: int = 20):
        try:
            params = {"limit": limit}
            if framework:
                params['framework'] = framework
            if task_type:
                params['task_type'] = task_type
            
            models = api_client.get("/models", params)
            
            if not models:
                print("ℹ️ Aucun modèle trouvé")
                return
            
            print("🧠 Modèles initHUB:")
            print("-" * 80)
            for model in models:
                print(f"  {model['id']}: {model['name']}")
                print(f"     Framework: {model['framework']}, Type: {model['task_type']}")
                print(f"     Téléchargements: {model.get('download_count', 0)}")
                print()
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def create_model(self, name: str, framework: str, task_type: str, description: str = "", version: str = "1.0.0"):
        try:
            data = {
                "name": name,
                "framework": framework,
                "task_type": task_type,
                "description": description,
                "version": version
            }
            
            model = api_client.post("/models", data)
            print(f"✅ Modèle créé avec succès! ID: {model['id']}")
            return model
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def upload_model(self, file_path: str, model_id: int, description: str = ""):
        try:
            result = api_client.upload_file(file_path, model_id, description)
            print("✅ Fichier uploadé avec succès!")
            print(f"📁 Checksum: {result.get('checksum_sha256', 'N/A')}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def model_info(self, model_id: int):
        try:
            model = api_client.get(f"/models/{model_id}")
            
            print(f"🧠 Modèle #{model_id}")
            print("=" * 40)
            print(f"Nom: {model['name']}")
            print(f"Framework: {model['framework']}")
            print(f"Type: {model['task_type']}")
            print(f"Version: {model.get('version', '1.0.0')}")
            print(f"Description: {model.get('description', 'N/A')}")
            print(f"Téléchargements: {model.get('download_count', 0)}")
            print(f"Likes: {model.get('like_count', 0)}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")

models_manager = ModelsManager()

# Gestion des projets
class ProjectsManager:
    def list_projects(self, project_type: str = None, limit: int = 20):
        try:
            params = {"limit": limit}
            if project_type:
                params['project_type'] = project_type
            
            projects = api_client.get("/projects", params)
            
            if not projects:
                print("ℹ️ Aucun projet trouvé")
                return
            
            print("📁 Projets initHUB:")
            print("-" * 80)
            for project in projects:
                print(f"  {project['id']}: {project['name']}")
                print(f"     Type: {project['project_type']}, Langage: {project['primary_language']}")
                print(f"     Étoiles: {project.get('star_count', 0)}")
                print()
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def create_project(self, name: str, project_type: str, primary_language: str, description: str = ""):
        try:
            data = {
                "name": name,
                "project_type": project_type,
                "primary_language": primary_language,
                "description": description
            }
            
            project = api_client.post("/projects", data)
            print(f"✅ Projet créé avec succès! ID: {project['id']}")
            return project
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def project_info(self, project_id: int):
        try:
            project = api_client.get(f"/projects/{project_id}")
            
            print(f"📁 Projet #{project_id}")
            print("=" * 40)
            print(f"Nom: {project['name']}")
            print(f"Type: {project['project_type']}")
            print(f"Langage: {project['primary_language']}")
            print(f"Description: {project.get('description', 'N/A')}")
            print(f"Étoiles: {project.get('star_count', 0)}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")

projects_manager = ProjectsManager()

# Gestion IA
class AIManager:
    def generate_code(self, prompt: str, language: str = "python", max_length: int = 200):
        try:
            data = {
                "prompt": prompt,
                "language": language,
                "max_length": max_length
            }
            
            result = api_client.post("/ai/generate-code", data)
            
            if result.get('generated_code'):
                code = result['generated_code']
                print("🤖 Code généré:")
                print("```python")
                print(code)
                print("```")
                
                if result.get('bugs_detected'):
                    print("\n🐛 Bugs détectés:")
                    for bug in result['bugs_detected']:
                        print(f"  • {bug['message']} (sévérité: {bug['severity']})")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def explain_code(self, code_or_file: str):
        try:
            if os.path.exists(code_or_file):
                with open(code_or_file, 'r') as f:
                    code = f.read()
                print(f"📖 Lecture du fichier: {code_or_file}")
            else:
                code = code_or_file
            
            data = {"code": code}
            result = api_client.post("/ai/explain-code", data)
            
            if result.get('explanation'):
                print("🤖 Explication du code:")
                print(result['explanation'])
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur: {e}")

ai_manager = AIManager()

# Interface CLI principale
def main():
    parser = argparse.ArgumentParser(description="🚀 CLI initHUB - Plateforme collaborative IA")
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Authentification
    auth_parser = subparsers.add_parser('login', help='Se connecter')
    auth_parser.add_argument('--email', help='Email')
    auth_parser.add_argument('--password', help='Mot de passe')
    
    register_parser = subparsers.add_parser('register', help='Créer un compte')
    register_parser.add_argument('username', help='Nom d utilisateur')
    register_parser.add_argument('email', help='Email')
    register_parser.add_argument('password', help='Mot de passe')
    
    subparsers.add_parser('logout', help='Se déconnecter')
    subparsers.add_parser('status', help='Statut de connexion')
    
    # Modèles
    models_parser = subparsers.add_parser('models', help='Gestion des modèles')
    models_subparsers = models_parser.add_subparsers(dest='models_command')
    
    models_subparsers.add_parser('list', help='Lister les modèles')
    
    create_model_parser = models_subparsers.add_parser('create', help='Créer un modèle')
    create_model_parser.add_argument('name', help='Nom du modèle')
    create_model_parser.add_argument('framework', help='Framework')
    create_model_parser.add_argument('task_type', help='Type de tâche')
    create_model_parser.add_argument('--description', help='Description', default='')
    create_model_parser.add_argument('--version', help='Version', default='1.0.0')
    
    upload_parser = models_subparsers.add_parser('upload', help='Uploader un modèle')
    upload_parser.add_argument('file_path', help='Chemin du fichier')
    upload_parser.add_argument('model_id', type=int, help='ID du modèle')
    upload_parser.add_argument('--description', help='Description', default='')
    
    info_model_parser = models_subparsers.add_parser('info', help='Info modèle')
    info_model_parser.add_argument('model_id', type=int, help='ID du modèle')
    
    # Projets
    projects_parser = subparsers.add_parser('projects', help='Gestion des projets')
    projects_subparsers = projects_parser.add_subparsers(dest='projects_command')
    
    projects_subparsers.add_parser('list', help='Lister les projets')
    
    create_project_parser = projects_subparsers.add_parser('create', help='Créer un projet')
    create_project_parser.add_argument('name', help='Nom du projet')
    create_project_parser.add_argument('project_type', help='Type de projet')
    create_project_parser.add_argument('language', help='Langage principal')
    create_project_parser.add_argument('--description', help='Description', default='')
    
    info_project_parser = projects_subparsers.add_parser('info', help='Info projet')
    info_project_parser.add_argument('project_id', type=int, help='ID du projet')
    
    # IA
    ai_parser = subparsers.add_parser('ai', help='Assistant IA')
    ai_subparsers = ai_parser.add_subparsers(dest='ai_command')
    
    generate_parser = ai_subparsers.add_parser('generate', help='Générer du code')
    generate_parser.add_argument('prompt', help='Description du code')
    generate_parser.add_argument('--language', help='Langage', default='python')
    generate_parser.add_argument('--max-length', type=int, help='Longueur max', default=200)
    
    explain_parser = ai_subparsers.add_parser('explain', help='Expliquer du code')
    explain_parser.add_argument('code_or_file', help='Code ou chemin de fichier')
    
    # Système
    config_parser = subparsers.add_parser('config', help='Configuration')
    config_parser.add_argument('key', help='Clé de configuration')
    config_parser.add_argument('value', help='Valeur')
    
    subparsers.add_parser('version', help='Version')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Authentification
        if args.command == 'login':
            auth_manager.login(args.email, args.password)
        elif args.command == 'register':
            auth_manager.register(args.username, args.email, args.password)
        elif args.command == 'logout':
            auth_manager.logout()
        elif args.command == 'status':
            if auth_manager.is_authenticated():
                print("✅ Connecté à initHUB")
                print(f"🌐 Serveur: {config.server_url}")
            else:
                print("❌ Non connecté")
                print("💡 Utilisez 'inithub login' pour vous connecter")
        
        # Modèles
        elif args.command == 'models':
            if args.models_command == 'list':
                models_manager.list_models()
            elif args.models_command == 'create':
                models_manager.create_model(args.name, args.framework, args.task_type, args.description, args.version)
            elif args.models_command == 'upload':
                models_manager.upload_model(args.file_path, args.model_id, args.description)
            elif args.models_command == 'info':
                models_manager.model_info(args.model_id)
        
        # Projets
        elif args.command == 'projects':
            if args.projects_command == 'list':
                projects_manager.list_projects()
            elif args.projects_command == 'create':
                projects_manager.create_project(args.name, args.project_type, args.language, args.description)
            elif args.projects_command == 'info':
                projects_manager.project_info(args.project_id)
        
        # IA
        elif args.command == 'ai':
            if args.ai_command == 'generate':
                ai_manager.generate_code(args.prompt, args.language, args.max_length)
            elif args.ai_command == 'explain':
                ai_manager.explain_code(args.code_or_file)
        
        # Système
        elif args.command == 'config':
            config_data = {}
            if args.key == "server_url":
                config_data['server_url'] = args.value
            config.save_config(config_data)
            print(f"✅ Configuration mise à jour: {args.key} = {args.value}")
        
        elif args.command == 'version':
            print("initHUB CLI v1.0.0")
            print("🚀 Plateforme collaborative IA et code")
            print("📧 Support: contact@inithub.com")
            print("🌐 Site: https://inithub.com")
    
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
    except Exception as e:
        print(f"💥 Erreur: {e}")

if __name__ == "__main__":
    main()
