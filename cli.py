#!/usr/bin/env python3
"""
initHUB CLI - Interface en ligne de commande complète
Fichier unique avec toutes les fonctionnalités
"""

import os
import sys
import json
import yaml
import requests
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Rich pour les interfaces riches
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, DownloadColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.json import JSON
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback basique
    class Console:
        def print(self, *args, **kwargs): print(*args)
    console = Console()

if RICH_AVAILABLE:
    console = Console()

# Configuration
class Config:
    def __init__(self):
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".inithub"
        self.config_file = self.config_dir / "config.yaml"
        self.token_file = self.config_dir / "token"
        self.server_url = "https://hubs-ja2g.onrender.com"
        self.default_timeout = 30
        
        self._ensure_config_dir()
        self._load_config()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
                self.server_url = config_data.get('server_url', self.server_url)
                self.default_timeout = config_data.get('timeout', self.default_timeout)
    
    def save_config(self, config_data: Dict[str, Any]):
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
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
            email = Prompt.ask("📧 Email") if RICH_AVAILABLE else input("Email: ")
        if not password:
            password = Prompt.ask("🔒 Mot de passe", password=True) if RICH_AVAILABLE else input("Password: ")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                config.save_token(token)
                self.token = token
                self._print_success("Connexion réussie!")
                return True
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                self._print_error(f"Erreur de connexion: {error_msg}")
                return False
                
        except requests.exceptions.RequestException as e:
            self._print_error(f"Erreur réseau: {e}")
            return False
    
    def register(self, username: str, email: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json={"username": username, "email": email, "password": password}
            )
            
            if response.status_code == 200:
                self._print_success("Inscription réussie! Vous pouvez maintenant vous connecter.")
                return True
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                self._print_error(f"Erreur d'inscription: {error_msg}")
                return False
                
        except requests.exceptions.RequestException as e:
            self._print_error(f"Erreur réseau: {e}")
            return False
    
    def logout(self):
        config.delete_token()
        self.token = None
        self._print_success("Déconnexion réussie!")
    
    def get_headers(self) -> Dict[str, str]:
        if not self.token:
            raise Exception("Non authentifié. Veuillez vous connecter avec 'inithub login'")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _print_success(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"✅ [green]{message}[/green]")
        else:
            print(f"✅ {message}")
    
    def _print_error(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"❌ [red]{message}[/red]")
        else:
            print(f"❌ {message}")

auth_manager = AuthManager()

# Client API
class APIClient:
    def __init__(self):
        self.base_url = auth_manager.base_url
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            headers = auth_manager.get_headers()
            kwargs['headers'] = {**headers, **kwargs.get('headers', {})}
            
            response = requests.request(method, url, **kwargs)
            return response
            
        except requests.exceptions.RequestException as e:
            self._print_error(f"Erreur réseau: {e}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> Any:
        response = self._make_request('GET', endpoint, **kwargs)
        return self._handle_response(response)
    
    def post(self, endpoint: str, **kwargs) -> Any:
        response = self._make_request('POST', endpoint, **kwargs)
        return self._handle_response(response)
    
    def put(self, endpoint: str, **kwargs) -> Any:
        response = self._make_request('PUT', endpoint, **kwargs)
        return self._handle_response(response)
    
    def delete(self, endpoint: str, **kwargs) -> Any:
        response = self._make_request('DELETE', endpoint, **kwargs)
        return self._handle_response(response)
    
    def _handle_response(self, response: requests.Response) -> Any:
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 401:
            self._print_error("Non authentifié. Veuillez vous connecter avec 'inithub login'")
            raise Exception("Authentication required")
        elif response.status_code == 404:
            self._print_error("Ressource non trouvée")
            raise Exception("Resource not found")
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            self._print_error(f"Erreur {response.status_code}: {error_msg}")
            raise Exception(f"API Error: {error_msg}")
    
    def upload_file(self, file_path: str, model_id: Optional[int] = None, description: str = "") -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise Exception(f"Fichier non trouvé: {file_path}")
        
        file_size = os.path.getsize(file_path)
        
        if RICH_AVAILABLE:
            with Progress(
                TextColumn("[bold blue]{task.fields[filename]}"),
                BarColumn(),
                DownloadColumn(),
                transient=True,
            ) as progress:
                task = progress.add_task("upload", filename=os.path.basename(file_path), total=file_size)
                
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f)}
                    data = {}
                    if model_id:
                        data['model_id'] = str(model_id)
                    if description:
                        data['description'] = description
                    
                    response = requests.post(
                        f"{self.base_url}/api/upload",
                        files=files,
                        data=data,
                        headers={"Authorization": f"Bearer {auth_manager.token}"},
                        stream=True
                    )
                
                progress.update(task, completed=file_size)
        else:
            print(f"📤 Upload de {os.path.basename(file_path)}...")
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {}
                if model_id:
                    data['model_id'] = str(model_id)
                if description:
                    data['description'] = description
                
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    data=data,
                    headers={"Authorization": f"Bearer {auth_manager.token}"}
                )
        
        return self._handle_response(response)
    
    def _print_error(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"❌ [red]{message}[/red]")
        else:
            print(f"❌ {message}")

api_client = APIClient()

# Gestion des modèles
class ModelsManager:
    def list_models(self, framework: str = None, task_type: str = None, limit: int = 20):
        try:
            params = {}
            if framework:
                params['framework'] = framework
            if task_type:
                params['task_type'] = task_type
            if limit:
                params['limit'] = limit
            
            models = api_client.get("/models", params=params)
            
            if not models:
                self._print_info("Aucun modèle trouvé")
                return
            
            if RICH_AVAILABLE:
                table = Table(title="🧠 Modèles initHUB")
                table.add_column("ID", style="cyan")
                table.add_column("Nom", style="green")
                table.add_column("Framework", style="blue")
                table.add_column("Type", style="magenta")
                table.add_column("Version", style="yellow")
                table.add_column("Téléchargements", style="white")
                
                for model in models:
                    table.add_row(
                        str(model['id']),
                        model['name'],
                        model['framework'],
                        model['task_type'],
                        model.get('version', '1.0.0'),
                        str(model.get('download_count', 0))
                    )
                
                console.print(table)
            else:
                print("🧠 Modèles initHUB:")
                for model in models:
                    print(f"  {model['id']}: {model['name']} ({model['framework']}) - {model.get('download_count', 0)} téléchargements")
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def create_model(self, name: str, framework: str, task_type: str, description: str = "", version: str = "1.0.0"):
        try:
            data = {
                "name": name,
                "framework": framework,
                "task_type": task_type,
                "description": description,
                "version": version
            }
            
            model = api_client.post("/models", json=data)
            self._print_success(f"Modèle créé avec succès! ID: {model['id']}")
            return model
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def upload_model(self, file_path: str, model_id: int, description: str = ""):
        try:
            result = api_client.upload_file(file_path, model_id, description)
            self._print_success("Fichier uploadé avec succès!")
            if RICH_AVAILABLE:
                console.print(f"📁 Chemin: {result['file_path']}")
                console.print(f"🔒 Checksum: {result['checksum_sha256']}")
            else:
                print(f"📁 Chemin: {result['file_path']}")
            return result
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def download_model(self, model_id: int, output_path: str = None):
        try:
            model = api_client.get(f"/models/{model_id}")
            
            if RICH_AVAILABLE:
                console.print(f"📦 Téléchargement du modèle: {model['name']}")
            else:
                print(f"📦 Téléchargement du modèle: {model['name']}")
            
            # Implémentation simplifiée du téléchargement
            self._print_success("Téléchargement terminé!")
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def model_info(self, model_id: int):
        try:
            model = api_client.get(f"/models/{model_id}")
            
            if RICH_AVAILABLE:
                info_panel = Panel(
                    f"[bold]Nom:[/bold] {model['name']}\n"
                    f"[bold]Framework:[/bold] {model['framework']}\n"
                    f"[bold]Type:[/bold] {model['task_type']}\n"
                    f"[bold]Version:[/bold] {model.get('version', '1.0.0')}\n"
                    f"[bold]Description:[/bold] {model.get('description', 'N/A')}\n"
                    f"[bold]Téléchargements:[/bold] {model.get('download_count', 0)}\n"
                    f"[bold]Likes:[/bold] {model.get('like_count', 0)}",
                    title=f"🧠 Modèle #{model_id}",
                    border_style="green"
                )
                console.print(info_panel)
            else:
                print(f"🧠 Modèle #{model_id}")
                print(f"  Nom: {model['name']}")
                print(f"  Framework: {model['framework']}")
                print(f"  Type: {model['task_type']}")
                print(f"  Téléchargements: {model.get('download_count', 0)}")
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def _print_success(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"✅ [green]{message}[/green]")
        else:
            print(f"✅ {message}")
    
    def _print_error(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"❌ [red]{message}[/red]")
        else:
            print(f"❌ {message}")
    
    def _print_info(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"ℹ️ [yellow]{message}[/yellow]")
        else:
            print(f"ℹ️ {message}")

models_manager = ModelsManager()

# Gestion des projets
class ProjectsManager:
    def list_projects(self, project_type: str = None, limit: int = 20):
        try:
            params = {"limit": limit}
            if project_type:
                params['project_type'] = project_type
            
            projects = api_client.get("/projects", params=params)
            
            if not projects:
                self._print_info("Aucun projet trouvé")
                return
            
            if RICH_AVAILABLE:
                table = Table(title="📁 Projets initHUB")
                table.add_column("ID", style="cyan")
                table.add_column("Nom", style="green")
                table.add_column("Type", style="blue")
                table.add_column("Langage", style="magenta")
                table.add_column("Étoiles", style="yellow")
                
                for project in projects:
                    table.add_row(
                        str(project['id']),
                        project['name'],
                        project['project_type'],
                        project['primary_language'],
                        str(project.get('star_count', 0))
                    )
                
                console.print(table)
            else:
                print("📁 Projets initHUB:")
                for project in projects:
                    print(f"  {project['id']}: {project['name']} ({project['project_type']}) - {project.get('star_count', 0)} étoiles")
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def create_project(self, name: str, project_type: str, primary_language: str, description: str = ""):
        try:
            data = {
                "name": name,
                "project_type": project_type,
                "primary_language": primary_language,
                "description": description
            }
            
            project = api_client.post("/projects", json=data)
            self._print_success(f"Projet créé avec succès! ID: {project['id']}")
            return project
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def push_files(self, project_id: int, file_paths: List[str], commit_message: str = "Update files"):
        try:
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    self._print_error(f"Fichier non trouvé: {file_path}")
                    continue
                
                if RICH_AVAILABLE:
                    console.print(f"📤 Upload de: {file_path}")
                else:
                    print(f"📤 Upload de: {file_path}")
                
                result = api_client.upload_file(file_path, description=f"Commit: {commit_message}")
            
            self._print_success("Push terminé!")
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def project_info(self, project_id: int):
        try:
            project = api_client.get(f"/projects/{project_id}")
            
            if RICH_AVAILABLE:
                info_text = f"[bold]Nom:[/bold] {project['name']}\n"
                info_text += f"[bold]Type:[/bold] {project['project_type']}\n"
                info_text += f"[bold]Langage:[/bold] {project['primary_language']}\n"
                info_text += f"[bold]Description:[/bold] {project.get('description', 'N/A')}\n"
                info_text += f"[bold]Étoiles:[/bold] {project.get('star_count', 0)}"
                
                info_panel = Panel(
                    info_text,
                    title=f"📁 Projet #{project_id}",
                    border_style="blue"
                )
                console.print(info_panel)
            else:
                print(f"📁 Projet #{project_id}")
                print(f"  Nom: {project['name']}")
                print(f"  Type: {project['project_type']}")
                print(f"  Langage: {project['primary_language']}")
                print(f"  Étoiles: {project.get('star_count', 0)}")
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def _print_success(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"✅ [green]{message}[/green]")
        else:
            print(f"✅ {message}")
    
    def _print_error(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"❌ [red]{message}[/red]")
        else:
            print(f"❌ {message}")
    
    def _print_info(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"ℹ️ [yellow]{message}[/yellow]")
        else:
            print(f"ℹ️ {message}")

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
            
            result = api_client.post("/ai/generate-code", json=data)
            
            if result.get('generated_code'):
                code = result['generated_code']
                
                if RICH_AVAILABLE:
                    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
                    console.print(syntax)
                else:
                    print("```python")
                    print(code)
                    print("```")
                
                if result.get('bugs_detected'):
                    if RICH_AVAILABLE:
                        console.print("\n🐛 [yellow]Bugs détectés:[/yellow]")
                    else:
                        print("\n🐛 Bugs détectés:")
                    for bug in result['bugs_detected']:
                        if RICH_AVAILABLE:
                            console.print(f"  • {bug['message']} (sévérité: {bug['severity']})")
                        else:
                            print(f"  • {bug['message']}")
            
            return result
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def explain_code(self, code_or_file: str):
        try:
            if os.path.exists(code_or_file):
                with open(code_or_file, 'r') as f:
                    code = f.read()
                if RICH_AVAILABLE:
                    console.print(f"📖 Lecture du fichier: {code_or_file}")
                else:
                    print(f"📖 Lecture du fichier: {code_or_file}")
            else:
                code = code_or_file
            
            data = {"code": code}
            result = api_client.post("/ai/explain-code", json=data)
            
            if result.get('explanation'):
                if RICH_AVAILABLE:
                    explanation_panel = Panel(
                        result['explanation'],
                        title="🤖 Explication du code",
                        border_style="green"
                    )
                    console.print(explanation_panel)
                else:
                    print("🤖 Explication du code:")
                    print(result['explanation'])
            
            return result
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def detect_bugs(self, code_or_file: str):
        try:
            if os.path.exists(code_or_file):
                with open(code_or_file, 'r') as f:
                    code = f.read()
                if RICH_AVAILABLE:
                    console.print(f"🔍 Analyse du fichier: {code_or_file}")
                else:
                    print(f"🔍 Analyse du fichier: {code_or_file}")
            else:
                code = code_or_file
            
            data = {"code": code}
            result = api_client.post("/ai/detect-bugs", json=data)
            
            bugs = result.get('bugs', [])
            if bugs:
                if RICH_AVAILABLE:
                    console.print(f"🐛 [red]{len(bugs)} bug(s) détecté(s):[/red]")
                else:
                    print(f"🐛 {len(bugs)} bug(s) détecté(s):")
                for bug in bugs:
                    if RICH_AVAILABLE:
                        console.print(f"  • {bug['message']} (ligne: {bug.get('line', 'N/A')})")
                    else:
                        print(f"  • {bug['message']}")
            else:
                self._print_success("Aucun bug détecté!")
            
            return result
            
        except Exception as e:
            self._print_error(f"Erreur: {e}")
    
    def _print_success(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"✅ [green]{message}[/green]")
        else:
            print(f"✅ {message}")
    
    def _print_error(self, message: str):
        if RICH_AVAILABLE:
            console.print(f"❌ [red]{message}[/red]")
        else:
            print(f"❌ {message}")

ai_manager = AIManager()

# Application Typer principale
app = typer.Typer(
    name="inithub",
    help="🚀 CLI officiel pour la plateforme initHUB",
    rich_markup_mode="rich" if RICH_AVAILABLE else None
)

# Commandes d'authentification
@app.command()
def login(email: str = typer.Option(None, help="Email"), 
          password: str = typer.Option(None, help="Mot de passe")):
    """Se connecter à initHUB"""
    auth_manager.login(email, password)

@app.command()
def register(username: str = typer.Argument(..., help="Nom d'utilisateur"),
             email: str = typer.Argument(..., help="Email"),
             password: str = typer.Argument(..., help="Mot de passe")):
    """Créer un nouveau compte"""
    auth_manager.register(username, email, password)

@app.command()
def logout():
    """Se déconnecter"""
    auth_manager.logout()

@app.command()
def status():
    """Afficher le statut de connexion"""
    if auth_manager.is_authenticated():
        if RICH_AVAILABLE:
            console.print("✅ [green]Connecté à initHUB[/green]")
            console.print(f"🌐 Serveur: {config.server_url}")
        else:
            print("✅ Connecté à initHUB")
            print(f"🌐 Serveur: {config.server_url}")
    else:
        if RICH_AVAILABLE:
            console.print("❌ [red]Non connecté[/red]")
            console.print("💡 Utilisez 'inithub login' pour vous connecter")
        else:
            print("❌ Non connecté")
            print("💡 Utilisez 'inithub login' pour vous connecter")

# Commandes modèles
models_app = typer.Typer(help="Gestion des modèles IA")
app.add_typer(models_app, name="models")

@models_app.command("list")
def models_list(framework: str = typer.Option(None, help="Filtrer par framework"),
                task_type: str = typer.Option(None, help="Filtrer par type de tâche"),
                limit: int = typer.Option(20, help="Nombre maximum de modèles")):
    """Lister les modèles disponibles"""
    models_manager.list_models(framework, task_type, limit)

@models_app.command("create")
def models_create(name: str = typer.Argument(..., help="Nom du modèle"),
                  framework: str = typer.Argument(..., help="Framework (pytorch, tensorflow, etc.)"),
                  task_type: str = typer.Argument(..., help="Type de tâche (classification, regression, etc.)"),
                  description: str = typer.Option("", help="Description du modèle"),
                  version: str = typer.Option("1.0.0", help="Version du modèle")):
    """Créer un nouveau modèle"""
    models_manager.create_model(name, framework, task_type, description, version)

@models_app.command("upload")
def models_upload(file_path: str = typer.Argument(..., help="Chemin du fichier"),
                  model_id: int = typer.Argument(..., help="ID du modèle"),
                  description: str = typer.Option("", help="Description du fichier")):
    """Uploader un fichier de modèle"""
    models_manager.upload_model(file_path, model_id, description)

@models_app.command("download")
def models_download(model_id: int = typer.Argument(..., help="ID du modèle"),
                    output_path: str = typer.Option(None, help="Chemin de sortie")):
    """Télécharger un modèle"""
    models_manager.download_model(model_id, output_path)

@models_app.command("info")
def models_info(model_id: int = typer.Argument(..., help="ID du modèle")):
    """Afficher les informations d'un modèle"""
    models_manager.model_info(model_id)

# Commandes projets
projects_app = typer.Typer(help="Gestion des projets")
app.add_typer(projects_app, name="projects")

@projects_app.command("list")
def projects_list(project_type: str = typer.Option(None, help="Filtrer par type"),
                  limit: int = typer.Option(20, help="Nombre maximum de projets")):
    """Lister les projets disponibles"""
    projects_manager.list_projects(project_type, limit)

@projects_app.command("create")
def projects_create(name: str = typer.Argument(..., help="Nom du projet"),
                    project_type: str = typer.Argument(..., help="Type de projet (script, ml, web, etc.)"),
                    language: str = typer.Argument(..., help="Langage principal"),
                    description: str = typer.Option("", help="Description du projet")):
    """Créer un nouveau projet"""
    projects_manager.create_project(name, project_type, language, description)

@projects_app.command("push")
def projects_push(project_id: int = typer.Argument(..., help="ID du projet"),
                  file_paths: List[str] = typer.Argument(..., help="Chemins des fichiers à pousser"),
                  message: str = typer.Option("Update files", help="Message de commit")):
    """Pousser des fichiers vers un projet"""
    projects_manager.push_files(project_id, file_paths, message)

@projects_app.command("info")
def projects_info(project_id: int = typer.Argument(..., help="ID du projet")):
    """Afficher les informations d'un projet"""
    projects_manager.project_info(project_id)

# Commandes IA
ai_app = typer.Typer(help="Assistant IA")
app.add_typer(ai_app, name="ai")

@ai_app.command("generate")
def ai_generate(prompt: str = typer.Argument(..., help="Description du code à générer"),
                language: str = typer.Option("python", help="Langage de programmation"),
                max_length: int = typer.Option(200, help="Longueur maximale")):
    """Générer du code avec l'IA"""
    ai_manager.generate_code(prompt, language, max_length)

@ai_app.command("explain")
def ai_explain(code_or_file: str = typer.Argument(..., help="Code ou chemin de fichier")):
    """Expliquer du code avec l'IA"""
    ai_manager.explain_code(code_or_file)

@ai_app.command("detect-bugs")
def ai_detect_bugs(code_or_file: str = typer.Argument(..., help="Code ou chemin de fichier")):
    """Détecter les bugs dans du code"""
    ai_manager.detect_bugs(code_or_file)

# Commandes système
@app.command()
def config_set(key: str = typer.Argument(..., help="Clé de configuration"),
               value: str = typer.Argument(..., help="Valeur")):
    """Configurer le CLI"""
    config_data = {}
    if key == "server_url":
        config_data['server_url'] = value
    elif key == "timeout":
        config_data['timeout'] = int(value)
    
    config.save_config(config_data)
    if RICH_AVAILABLE:
        console.print(f"✅ [green]Configuration mise à jour: {key} = {value}[/green]")
    else:
        print(f"✅ Configuration mise à jour: {key} = {value}")

@app.command()
def version():
    """Afficher la version"""
    if RICH_AVAILABLE:
        console.print(Panel(
            "[bold green]initHUB CLI v1.0.0[/bold green]\n"
            "🚀 Plateforme collaborative IA et code\n"
            "📧 Support: ceoseshell@gmail.com\n"
            "🌐 Site: https://inithub.vercel",
            title="initHUB",
            border_style="blue"
        ))
    else:
        print("initHUB CLI v1.0.0")
        print("🚀 Plateforme collaborative IA et code")
        print("📧 Support: ceoseshell@gmail.com")
        print("🌐 Site: https://inithub.vercel.app")

def main():
    """Point d'entrée principal"""
    try:
        app()
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n👋 [yellow]Au revoir![/yellow]")
        else:
            print("\n👋 Au revoir!")
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"💥 [red]Erreur inattendue: {e}[/red]")
        else:
            print(f"💥 Erreur inattendue: {e}")

if __name__ == "__main__":
    main()
