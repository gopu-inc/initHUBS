#!/usr/bin/env python3
"""
initHUB CLI - Client complet avec connexion au serveur en ligne
Version améliorée avec commande pull - Sans contenus Markdown
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
    SERVER_URL = "https://hubs-ja2g.onrender.com"
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
# 🔌 CLIENT API AMÉLIORÉ
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
    
    def login(self, email: str, password: str) -> bool:
        """Connexion au serveur"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            data = self._handle_response(response)
            
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
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "full_name": full_name
                }
            )
            data = self._handle_response(response)
            print(f"✅ Compte créé: {data['username']}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur inscription: {e}")
            return False
    
    def get_current_user(self):
        """Récupère les infos de l'utilisateur connecté"""
        try:
            response = self.session.get(f"{self.base_url}/auth/me")
            return self._handle_response(response)
        except Exception as e:
            print(f"❌ Erreur récupération utilisateur: {e}")
            return None
    
    def push_project(self, manifest_data: Dict[str, Any], project_path: str) -> bool:
        """Push un projet vers le serveur"""
        try:
            print(f"🚀 Création du projet {manifest_data['name']}...")
            
            # Créer le projet d'abord
            project_response = self.session.post(
                f"{self.base_url}/projects",
                json={
                    "name": manifest_data['name'],
                    "description": manifest_data.get('metadata', {}).get('description', 'Projet créé via CLI'),
                    "project_type": "ssf",
                    "primary_language": "python",
                    "is_public": True
                }
            )
            project_data = self._handle_response(project_response)
            
            print(f"✅ Projet créé: {project_data['name']} (ID: {project_data['id']})")
            
            # Uploader les fichiers
            return self._upload_files_corrected(manifest_data, project_data['id'], project_path)
            
        except Exception as e:
            print(f"❌ Erreur création projet: {e}")
            return False
    
    def _upload_files_corrected(self, manifest_data: Dict[str, Any], project_id: int, project_path: str) -> bool:
        """Upload les fichiers du projet"""
        file_patterns = manifest_data.get('files', [])
        all_files = expand_file_patterns(project_path, file_patterns)
        
        print(f"📤 Upload de {len(all_files)} fichiers...")
        
        success_count = 0
        for file_path in all_files:
            try:
                full_path = Path(project_path) / file_path
                
                if not full_path.exists():
                    print(f"  ⚠️  Fichier non trouvé: {file_path}")
                    continue
                
                # Préparer les données pour l'upload
                with open(full_path, 'rb') as f:
                    files = {
                        'file': (file_path, f, 'application/octet-stream')
                    }
                    
                    data = {
                        'project_id': str(project_id),
                        'description': f"Fichier {file_path} du projet {manifest_data['name']}"
                    }
                    
                    upload_response = self.session.post(
                        f"{self.base_url}/upload",
                        files=files,
                        data=data
                    )
                    
                    if upload_response.status_code == 200:
                        print(f"  ✅ {file_path}")
                        success_count += 1
                    else:
                        error_detail = upload_response.json().get('detail', 'Erreur inconnue')
                        print(f"  ❌ {file_path} - Erreur {upload_response.status_code}: {error_detail}")
                        
            except Exception as e:
                print(f"  ❌ {file_path} - {e}")
        
        print(f"📊 Upload terminé: {success_count}/{len(all_files)} fichiers uploadés avec succès")
        return success_count > 0
    
    def list_projects(self, user_only: bool = False):
        """Liste les projets de l'utilisateur"""
        try:
            response = self.session.get(f"{self.base_url}/projects")
            projects = self._handle_response(response)
            
            if user_only and self.get_current_user():
                current_user = self.get_current_user()
                projects = [p for p in projects if p.get('author_username') == current_user['username']]
            
            if not projects:
                print("📭 Aucun projet trouvé")
                return []
                
            return projects
            
        except Exception as e:
            print(f"❌ Erreur liste projets: {e}")
            return []
    
    def list_models(self, user_only: bool = False):
        """Liste les modèles IA"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            models = self._handle_response(response)
            
            if user_only and self.get_current_user():
                current_user = self.get_current_user()
                models = [m for m in models if m.get('author_username') == current_user['username']]
            
            if not models:
                print("🤖 Aucun modèle IA trouvé")
                return []
                
            return models
            
        except Exception as e:
            print(f"❌ Erreur liste modèles: {e}")
            return []

    def get_project_details(self, project_id: int):
        """Récupère les détails d'un projet spécifique"""
        try:
            projects = self.list_projects()
            for project in projects:
                if project['id'] == project_id:
                    return project
            return None
        except Exception as e:
            print(f"❌ Erreur détails projet: {e}")
            return None

    def get_model_details(self, model_id: int):
        """Récupère les détails d'un modèle spécifique"""
        try:
            models = self.list_models()
            for model in models:
                if model['id'] == model_id:
                    return model
            return None
        except Exception as e:
            print(f"❌ Erreur détails modèle: {e}")
            return None

    def download_project(self, project_id: int, output_path: str) -> bool:
        """Télécharge un projet complet avec ses fichiers"""
        try:
            # Récupérer les détails du projet
            project = self.get_project_details(project_id)
            if not project:
                print(f"❌ Projet {project_id} non trouvé")
                return False
            
            print(f"📥 Téléchargement du projet: {project['name']}")
            
            # Créer le répertoire de destination
            output_dir = Path(output_path) / project['name']
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder les métadonnées du projet
            metadata_file = output_dir / "project_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Métadonnées sauvegardées: {metadata_file}")
            
            # Créer un fichier .ssf basique pour le projet
            ssf_content = generate_ssf_from_project(project)
            ssf_file = output_dir / "init.ssf"
            with open(ssf_file, 'w', encoding='utf-8') as f:
                f.write(ssf_content)
            
            print(f"✅ Fichier .ssf généré: {ssf_file}")
            
            # Créer une structure de base
            create_basic_project_structure(output_dir, project)
            
            print(f"✅ Projet téléchargé dans: {output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur téléchargement projet: {e}")
            return False

    def download_model(self, model_id: int, output_path: str) -> bool:
        """Télécharge un modèle IA avec sa configuration"""
        try:
            # Récupérer les détails du modèle
            model = self.get_model_details(model_id)
            if not model:
                print(f"❌ Modèle {model_id} non trouvé")
                return False
            
            print(f"📥 Téléchargement du modèle: {model['name']}")
            
            # Créer le répertoire de destination
            output_dir = Path(output_path) / model['name']
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder les métadonnées du modèle
            metadata_file = output_dir / "model_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(model, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Métadonnées sauvegardées: {metadata_file}")
            
            # Créer des fichiers de configuration basiques selon le framework
            create_model_files(output_dir, model)
            
            print(f"✅ Modèle téléchargé dans: {output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur téléchargement modèle: {e}")
            return False

    def search_projects(self, query: str, search_in: List[str] = None):
        """Recherche des projets"""
        try:
            projects = self.list_projects()
            if not projects:
                return []
            
            if search_in is None:
                search_in = ['name', 'description', 'author_username']
            
            results = []
            for project in projects:
                for field in search_in:
                    if field in project and query.lower() in str(project[field]).lower():
                        results.append(project)
                        break
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur recherche projets: {e}")
            return []

    def search_models(self, query: str, search_in: List[str] = None):
        """Recherche des modèles"""
        try:
            models = self.list_models()
            if not models:
                return []
            
            if search_in is None:
                search_in = ['name', 'description', 'framework', 'task_type', 'author_username']
            
            results = []
            for model in models:
                for field in search_in:
                    if field in model and query.lower() in str(model[field]).lower():
                        results.append(model)
                        break
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur recherche modèles: {e}")
            return []

    def test_upload(self, project_id: int, test_file_path: str):
        """Test simple d'upload pour debugger"""
        try:
            full_path = Path(test_file_path)
            if not full_path.exists():
                print(f"❌ Fichier de test non trouvé: {test_file_path}")
                return False
            
            with open(full_path, 'rb') as f:
                files = {'file': (full_path.name, f, 'text/plain')}
                data = {'project_id': str(project_id)}
                
                response = self.session.post(
                    f"{self.base_url}/upload",
                    files=files,
                    data=data
                )
                
                print(f"📡 Statut: {response.status_code}")
                print(f"📡 Réponse: {response.text}")
                
                if response.status_code == 200:
                    print("✅ Upload test réussi!")
                    return True
                else:
                    print(f"❌ Upload test échoué: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erreur test upload: {e}")
            return False

# Client global
api_client = InitHUBClient()

# ============================================================================
# 📄 PARSER MANIFEST .SSF (LZL-ZOBA)
# ============================================================================

class SSFParser:
    def __init__(self):
        self.manifest_data = {}
    
    def parse_ssf(self, content: str) -> Dict[str, Any]:
        """Parse le contenu d'un fichier .ssf"""
        lines = content.split('\n')
        self.manifest_data = {
            'name': 'unknown',
            'version': '1.0.0',
            'files': [],
            'tags': [],
            'branch': 'main',
            'author': 'anonymous',
            'init_files': [],
            'model_config': {},
            'dependencies': {'python': '', 'packages': []},
            'scripts': {},
            'metadata': {}
        }
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('#'):
                i += 1
                continue
                
            try:
                if line.startswith('I si name:'):
                    self._parse_name(line)
                elif line.startswith('[{cersion:'):
                    self._parse_version(line)
                elif line.startswith('[file:'):
                    i = self._parse_files(lines, i)
                elif line.startswith('—tags('):
                    i = self._parse_tags(lines, i)
                elif line.startswith(':') and '#' in line:
                    self._parse_branch(line)
                elif line.startswith('<=/>'):
                    i = self._parse_author(lines, i)
                elif line.startswith('init.get('):
                    i = self._parse_init_get(lines, i)
                elif line.startswith('model.config('):
                    i = self._parse_model_config(lines, i)
                elif line.startswith('deps.require('):
                    i = self._parse_dependencies(lines, i)
                elif line.startswith('scripts.run('):
                    i = self._parse_scripts(lines, i)
                elif line.startswith('meta.set('):
                    i = self._parse_metadata(lines, i)
            except Exception as e:
                print(f"⚠️  Erreur parsing ligne {i}: {e}")
            
            i += 1
        
        return self.manifest_data
    
    def _parse_name(self, line: str):
        """Parse le nom du projet"""
        match = re.search(r'I si name:\s*([^\]\s]+)', line)
        if match:
            self.manifest_data['name'] = match.group(1).strip()
    
    def _parse_version(self, line: str):
        """Parse la version"""
        match = re.search(r'\[{cersion:\s*([^}]+)}', line)
        if match:
            self.manifest_data['version'] = match.group(1).strip()
    
    def _parse_files(self, lines: List[str], start_idx: int) -> int:
        """Parse la section fichiers"""
        i = start_idx + 1
        files = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line == ']} ==> push-hub':
                break
            
            if line.startswith('-'):
                file_pattern = line[1:].strip()
                if file_pattern:
                    files.append(file_pattern)
            
            i += 1
        
        self.manifest_data['files'] = files
        return i
    
    def _parse_tags(self, lines: List[str], start_idx: int) -> int:
        """Parse les tags"""
        i = start_idx
        tags = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('):'):
                break
            
            if line.startswith('>'):
                tag = line[1:].strip()
                if tag:
                    tags.append(tag)
            
            i += 1
        
        self.manifest_data['tags'] = tags
        return i
    
    def _parse_branch(self, line: str):
        """Parse la branche"""
        if '#' in line:
            parts = line.split('#')
            branch_part = parts[0].strip(': ')
            comment = parts[1].strip()
            
            if '@' in comment:
                fork_match = re.search(r'@([\w-]+)', comment)
                if fork_match:
                    self.manifest_data['fork'] = fork_match.group(1)
            
            self.manifest_data['branch'] = branch_part
    
    def _parse_author(self, lines: List[str], start_idx: int) -> int:
        """Parse l'auteur"""
        i = start_idx
        if i + 1 < len(lines):
            author_line = lines[i + 1].strip()
            match = re.search(r'{author\s*=\s*\(([^)]+)\)', author_line)
            if match:
                self.manifest_data['author'] = match.group(1).strip()
            return i + 1
        return i
    
    def _parse_init_get(self, lines: List[str], start_idx: int) -> int:
        """Parse init.get()"""
        i = start_idx
        init_files = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line == ')':
                break
            
            if line.startswith('-'):
                file_spec = line[1:].strip()
                if ':' in file_spec:
                    name, ext = file_spec.split(':', 1)
                    init_files.append(f"{name}.{ext}")
                else:
                    init_files.append(file_spec)
            
            i += 1
        
        self.manifest_data['init_files'] = init_files
        return i
    
    def _parse_model_config(self, lines: List[str], start_idx: int) -> int:
        """Parse model.config()"""
        i = start_idx
        model_config = {}
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line == ')':
                break
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',')]
                
                model_config[key] = value
            
            i += 1
        
        self.manifest_data['model_config'] = model_config
        return i
    
    def _parse_dependencies(self, lines: List[str], start_idx: int) -> int:
        """Parse deps.require()"""
        i = start_idx
        dependencies = {
            'python': '',
            'packages': []
        }
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line == ')':
                break
            
            if '>=' in line:
                parts = line.split('>=')
                if len(parts) == 2:
                    pkg = parts[0].strip()
                    version = '>=' + parts[1].strip()
                    
                    if pkg == 'python':
                        dependencies['python'] = version
                    else:
                        dependencies['packages'].append(f"{pkg}{version}")
            
            i += 1
        
        self.manifest_data['dependencies'] = dependencies
        return i
    
    def _parse_scripts(self, lines: List[str], start_idx: int) -> int:
        """Parse scripts.run()"""
        i = start_idx
        scripts = {}
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line == ')':
                break
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')
                scripts[key] = value
            
            i += 1
        
        self.manifest_data['scripts'] = scripts
        return i
    
    def _parse_metadata(self, lines: List[str], start_idx: int) -> int:
        """Parse meta.set()"""
        i = start_idx
        metadata = {}
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line == ')':
                break
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                metadata[key] = value
            
            i += 1
        
        self.manifest_data['metadata'] = metadata
        return i

# ============================================================================
# 🛠️ UTILITAIRES FICHIERS
# ============================================================================

def expand_file_patterns(base_path: str, patterns: List[str]) -> List[str]:
    """Étend les patterns de fichiers .ssf de manière robuste"""
    base = Path(base_path)
    all_files = set()
    
    for pattern in patterns:
        if pattern.startswith('!'):
            continue
        
        clean_pattern = pattern.strip()
        if not clean_pattern:
            continue
            
        try:
            # Essayer d'abord avec glob
            matches = glob.glob(str(base / clean_pattern), recursive=True)
            
            for match in matches:
                file_path = Path(match)
                if file_path.is_file():
                    try:
                        rel_path = file_path.relative_to(base)
                        all_files.add(str(rel_path))
                    except ValueError:
                        pass
            
            # Si pas de résultats avec glob, essayer de traiter comme un fichier simple
            if not matches:
                simple_path = base / clean_pattern
                if simple_path.exists() and simple_path.is_file():
                    all_files.add(clean_pattern)
                    
        except Exception as e:
            print(f"⚠️  Erreur pattern '{pattern}': {e}")
    
    exclude_patterns = [p[1:] for p in patterns if p.startswith('!')]
    final_files = []
    
    for file_path in all_files:
        if not any(fnmatch.fnmatch(file_path, excl) for excl in exclude_patterns):
            final_files.append(file_path)
    
    return sorted(final_files)

def find_ssf_file(project_path: str) -> Optional[Path]:
    """Trouve le fichier .ssf dans le projet"""
    path = Path(project_path)
    
    ssf_files = list(path.glob("*.ssf"))
    
    if not ssf_files:
        return None
    
    for ssf_file in ssf_files:
        if ssf_file.name == "init.ssf":
            return ssf_file
    
    return ssf_files[0]

def generate_ssf_from_project(project_data: Dict[str, Any]) -> str:
    """Génère un fichier .ssf basique à partir des métadonnées d'un projet"""
    name = project_data.get('name', 'unknown')
    description = project_data.get('description', 'Projet téléchargé depuis initHUB')
    author = project_data.get('author_username', 'anonymous')
    
    ssf_content = f"""Init.glob(
[
I si name: {name}]
 [{{cersion: 1.0.0}}]
 [file: 
         - *.py
         - *.md
         - requirements.txt
         - *.json
         - !__pycache__/**
 ]}} ==> push-hub
   —tags( # >
        downloaded >
        cli
):main-{name}

<=/>{{author =({author})}}

init.get(
   - README:md
)

# Configuration de base
meta.set(
   description = "{description}"
   visibility = public
   downloaded_from = "initHUB"
   original_id = {project_data.get('id', 'unknown')}
)
"""
    return ssf_content

def create_basic_project_structure(output_dir: Path, project_data: Dict[str, Any]):
    """Crée une structure de projet basique avec les métadonnées"""
    # Fichier Python principal
    main_py_content = '''"""
Module principal du projet
Projet téléchargé depuis initHUB
"""

def main():
    """Fonction principale"""
    print("Hello from initHUB project!")
    
if __name__ == "__main__":
    main()
'''
    
    with open(output_dir / "main.py", 'w', encoding='utf-8') as f:
        f.write(main_py_content)
    
    # Requirements
    with open(output_dir / "requirements.txt", 'w', encoding='utf-8') as f:
        f.write("# Requirements for the project\nrequests>=2.25.0\n")

def create_model_files(output_dir: Path, model_data: Dict[str, Any]):
    """Crée des fichiers de configuration pour un modèle IA"""
    framework = model_data.get('framework', 'unknown')
    
    # Fichier de configuration du modèle
    config_content = {
        "model_name": model_data.get('name'),
        "framework": framework,
        "task_type": model_data.get('task_type', 'unknown'),
        "version": model_data.get('version', '1.0.0'),
        "description": model_data.get('description', ''),
        "author": model_data.get('author_username', ''),
        "download_date": str(Path(output_dir).name),
        "original_id": model_data.get('id')
    }
    
    with open(output_dir / "model_config.json", 'w', encoding='utf-8') as f:
        json.dump(config_content, f, indent=2, ensure_ascii=False)
    
    # Fichier d'exemple d'utilisation selon le framework
    if framework.lower() == 'pytorch':
        example_file = output_dir / "example_usage.py"
        example_content = '''"""
Exemple d'utilisation pour un modèle PyTorch
"""

import torch
import torch.nn as nn
import json

# Charger la configuration
with open('model_config.json', 'r') as f:
    config = json.load(f)

print(f"Configuration du modèle: {config}")

# Structure de modèle exemple
class ExampleModel(nn.Module):
    def __init__(self):
        super(ExampleModel, self).__init__()
        self.layer = nn.Linear(10, 1)
    
    def forward(self, x):
        return self.layer(x)

print("Modèle prêt pour l'inférence!")
'''
    elif framework.lower() == 'tensorflow':
        example_file = output_dir / "example_usage.py"
        example_content = '''"""
Exemple d'utilisation pour un modèle TensorFlow
"""

import tensorflow as tf
import json

# Charger la configuration
with open('model_config.json', 'r') as f:
    config = json.load(f)

print(f"Configuration du modèle: {config}")

# Modèle exemple
model = tf.keras.Sequential([
    tf.keras.layers.Dense(10, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

print("Modèle prêt pour l'inférence!")
'''
    else:
        example_file = output_dir / "example_usage.py"
        example_content = '''"""
Exemple d'utilisation générique pour un modèle IA
"""

import json

# Charger la configuration
with open('model_config.json', 'r') as f:
    config = json.load(f)

print(f"Modèle: {config['model_name']}")
print(f"Framework: {config['framework']}")
print(f"Type de tâche: {config['task_type']}")
'''
    
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(example_content)

# ============================================================================
# 🚀 COMMANDES .SSF
# ============================================================================

def handle_ssf_init(args):
    """Crée un nouveau manifest .ssf"""
    project_path = args.path or "."
    project_name = args.name or Path(project_path).name
    
    print(f"🚀 Création du manifest .ssf pour {project_name}...")
    
    ssf_path = Path(project_path) / "init.ssf"
    if ssf_path.exists() and not args.force:
        print("❌ Un fichier init.ssf existe déjà. Utilisez --force pour écraser.")
        return False
    
    description = args.description or "Nouveau projet initHUB"
    author = args.author or "anonymous"
    namespace = args.namespace or "default"
    
    ssf_content = f"""Init.glob(
[
I si name: {project_name}]
 [{{cersion: 1.0.0}}]
 [file: 
         - *.py
         - *.md
         - requirements.txt
         - !__pycache__/**
 ]}} ==> push-hub
   —tags( # >
        {namespace} >
        cli
):main-{project_name}

<=/>{{author =({author})}}

init.get(
   - README:md
)

# Configuration de base
meta.set(
   description = "{description}"
   visibility = public
)
"""
    
    try:
        ssf_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ssf_path, 'w', encoding='utf-8') as f:
            f.write(ssf_content)
        
        print(f"✅ Manifest créé: {ssf_path}")
        print(f"📊 Nom: {project_name}")
        print(f"📊 Auteur: {author}")
        print(f"📊 Namespace: {namespace}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création: {e}")
        return False

def handle_ssf_push(args):
    """Push avec le manifest .ssf vers le serveur"""
    project_path = args.path or "."
    
    # Vérifier la connexion
    user = api_client.get_current_user()
    if not user:
        print("❌ Non connecté. Utilisez 'inithub login' d'abord.")
        return False
    
    print(f"👤 Connecté en tant que: {user['username']}")
    
    # Trouver le fichier .ssf
    ssf_path = find_ssf_file(project_path)
    if not ssf_path:
        print("❌ Aucun fichier .ssf trouvé dans le projet")
        return False
    
    print(f"📦 Chargement du manifest: {ssf_path.name}")
    
    # Parser le manifest
    parser = SSFParser()
    try:
        with open(ssf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        manifest = parser.parse_ssf(content)
        print(f"📦 Manifest chargé: {manifest['name']} v{manifest.get('version', '1.0.0')}")
        
        # Vérifier les fichiers
        file_patterns = manifest.get('files', [])
        all_files = expand_file_patterns(project_path, file_patterns)
        
        if not all_files:
            print("⚠️  Aucun fichier trouvé avec les patterns définis")
            print("📋 Patterns:", file_patterns)
            create_sample = input("📝 Créer des fichiers d'exemple? (y/n): ")
            if create_sample.lower() == 'y':
                create_sample_files(project_path, manifest['name'])
                all_files = expand_file_patterns(project_path, file_patterns)
        
        print(f"📁 Fichiers à uploader ({len(all_files)}):")
        for file_path in all_files:
            full_path = Path(project_path) / file_path
            if full_path.exists():
                print(f"  ✅ {file_path} ({full_path.stat().st_size} bytes)")
            else:
                print(f"  ❌ {file_path} (NON TROUVÉ)")
        
        # Demander confirmation
        confirm = input(f"🚀 Pousser le projet vers initHUB? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Opération annulée")
            return False
        
        # Push vers le serveur
        return api_client.push_project(manifest, project_path)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_sample_files(project_path: str, project_name: str):
    """Crée des fichiers d'exemple si aucun fichier n'est trouvé"""
    project_path = Path(project_path)
    
    # Fichier Python exemple
    py_content = '''"""
Module exemple pour initHUB
"""

def hello_world():
    """Fonction d'exemple"""
    print("Hello initHUB!")
    
if __name__ == "__main__":
    hello_world()
'''
    
    with open(project_path / "example.py", 'w', encoding='utf-8') as f:
        f.write(py_content)
    
    # Requirements
    with open(project_path / "requirements.txt", 'w', encoding='utf-8') as f:
        f.write("requests>=2.25.0\n")
    
    print("✅ Fichiers d'exemple créés: example.py, requirements.txt")

def handle_ssf_validate(args):
    """Valide un manifest .ssf"""
    project_path = args.path or "."
    
    ssf_path = find_ssf_file(project_path)
    if not ssf_path:
        print("❌ Aucun fichier .ssf trouvé")
        return False
    
    parser = SSFParser()
    try:
        with open(ssf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        manifest = parser.parse_ssf(content)
        
        required = ['name', 'files', 'branch']
        missing = [field for field in required if field not in manifest]
        
        if missing:
            print(f"❌ Champs manquants: {', '.join(missing)}")
            return False
        
        file_patterns = manifest.get('files', [])
        if not file_patterns:
            print("⚠️  Aucun pattern de fichiers défini")
        
        all_files = expand_file_patterns(project_path, file_patterns)
        if not all_files:
            print("⚠️  Aucun fichier trouvé avec les patterns définis")
        
        print("✅ Manifest .ssf valide!")
        print(f"📊 Nom: {manifest['name']}")
        print(f"📊 Version: {manifest.get('version', '1.0.0')}")
        print(f"📊 Fichiers: {len(all_files)} fichiers trouvés")
        print(f"📊 Tags: {len(manifest.get('tags', []))}")
        print(f"📊 Branche: {manifest['branch']}")
        
        if 'author' in manifest:
            print(f"📊 Auteur: {manifest['author']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

def handle_ssf_show(args):
    """Affiche le contenu parsé d'un manifest .ssf"""
    project_path = args.path or "."
    
    ssf_path = find_ssf_file(project_path)
    if not ssf_path:
        print("❌ Aucun fichier .ssf trouvé")
        return False
    
    parser = SSFParser()
    try:
        with open(ssf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        manifest = parser.parse_ssf(content)
        
        print(f"📄 Contenu parsé de {ssf_path.name}:")
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return True
        
    except Exception as e:
        print(f"❌ Erreur parsing: {e}")
        return False

def handle_ssf_list(args):
    """Liste tous les fichiers .ssf du projet"""
    project_path = args.path or "."
    path = Path(project_path)
    
    ssf_files = list(path.glob("**/*.ssf"))
    
    if not ssf_files:
        print("❌ Aucun fichier .ssf trouvé")
        return False
    
    print(f"📁 Fichiers .ssf trouvés dans {project_path}:")
    for ssf_file in ssf_files:
        print(f"  📄 {ssf_file.relative_to(path)}")
    
    return True

# ============================================================================
# 🔐 COMMANDES AUTHENTIFICATION
# ============================================================================

def handle_login(args):
    """Connexion au serveur initHUB"""
    email = args.email
    password = args.password
    
    if not email or not password:
        print("❌ Email et mot de passe requis")
        return False
    
    return api_client.login(email, password)

def handle_register(args):
    """Inscription au serveur initHUB"""
    username = args.username
    email = args.email
    password = args.password
    full_name = args.full_name or ""
    
    if not all([username, email, password]):
        print("❌ Username, email et mot de passe requis")
        return False
    
    return api_client.register(username, email, password, full_name)

def handle_whoami(args):
    """Affiche l'utilisateur connecté"""
    user = api_client.get_current_user()
    if user:
        print(f"👤 Utilisateur connecté:")
        print(f"   📛 Nom: {user['username']}")
        print(f"   📧 Email: {user['email']}")
        print(f"   👤 Nom complet: {user.get('full_name', 'Non défini')}")
        return True
    else:
        print("❌ Non connecté")
        return False

def handle_logout(args):
    """Déconnexion du serveur"""
    config.TOKEN_FILE.unlink(missing_ok=True)
    print("✅ Déconnecté avec succès")
    return True

# ============================================================================
# 📥 COMMANDES PULL
# ============================================================================

def handle_pull_project(args):
    """Télécharge un projet depuis initHUB"""
    project_id = args.project_id
    output_path = args.output or config.get_download_dir()
    
    if not project_id:
        print("❌ ID du projet requis")
        return False
    
    try:
        project_id = int(project_id)
    except ValueError:
        print("❌ L'ID du projet doit être un nombre")
        return False
    
    user = api_client.get_current_user()
    if not user:
        print("❌ Non connecté. Utilisez 'inithub login' d'abord.")
        return False
    
    return api_client.download_project(project_id, output_path)

def handle_pull_model(args):
    """Télécharge un modèle IA depuis initHUB"""
    model_id = args.model_id
    output_path = args.output or config.get_download_dir()
    
    if not model_id:
        print("❌ ID du modèle requis")
        return False
    
    try:
        model_id = int(model_id)
    except ValueError:
        print("❌ L'ID du modèle doit être un nombre")
        return False
    
    user = api_client.get_current_user()
    if not user:
        print("❌ Non connecté. Utilisez 'inithub login' d'abord.")
        return False
    
    return api_client.download_model(model_id, output_path)

def handle_pull_list(args):
    """Liste les projets et modèles disponibles pour téléchargement"""
    user = api_client.get_current_user()
    if not user:
        print("❌ Non connecté. Utilisez 'inithub login' d'abord.")
        return False
    
    print("🔄 Récupération des projets et modèles...")
    
    # Lister les projets
    projects = api_client.list_projects()
    if projects:
        print(f"\n📁 PROJETS DISPONIBLES ({len(projects)}):")
        print("─" * 80)
        for project in projects[:10]:
            print(f"  🆔 {project['id']} | 📦 {project['name']} | 👤 {project.get('author_username', 'Inconnu')}")
            if 'description' in project and project['description']:
                desc = project['description'][:60] + "..." if len(project['description']) > 60 else project['description']
                print(f"     📝 {desc}")
            print()
    
    # Lister les modèles
    models = api_client.list_models()
    if models:
        print(f"🧠 MODÈLES IA DISPONIBLES ({len(models)}):")
        print("─" * 80)
        for model in models[:10]:
            print(f"  🆔 {model['id']} | 🔧 {model['name']} | 🏷️ {model['framework']} | 👤 {model.get('author_username', 'Inconnu')}")
            if 'description' in model and model['description']:
                desc = model['description'][:60] + "..." if len(model['description']) > 60 else model['description']
                print(f"     📝 {desc}")
            print()
    
    if not projects and not models:
        print("📭 Aucun projet ou modèle disponible")
    
    print(f"\n💡 Utilisez 'inithub pull project <ID>' ou 'inithub pull model <ID>' pour télécharger")
    return True

def handle_search(args):
    """Recherche des projets et modèles"""
    query = args.query
    if not query:
        print("❌ Terme de recherche requis")
        return False
    
    user = api_client.get_current_user()
    if not user:
        print("❌ Non connecté. Utilisez 'inithub login' d'abord.")
        return False
    
    print(f"🔍 Recherche: '{query}'")
    
    # Rechercher dans les projets
    projects = api_client.search_projects(query)
    if projects:
        print(f"\n📁 PROJETS TROUVÉS ({len(projects)}):")
        print("─" * 80)
        for project in projects:
            print(f"  🆔 {project['id']} | 📦 {project['name']} | 👤 {project.get('author_username', 'Inconnu')}")
            if 'description' in project and project['description']:
                print(f"     📝 {project['description']}")
            print()
    
    # Rechercher dans les modèles
    models = api_client.search_models(query)
    if models:
        print(f"🧠 MODÈLES IA TROUVÉS ({len(models)}):")
        print("─" * 80)
        for model in models:
            print(f"  🆔 {model['id']} | 🔧 {model['name']} | 🏷️ {model['framework']} | 👤 {model.get('author_username', 'Inconnu')}")
            if 'description' in model and model['description']:
                print(f"     📝 {model['description']}")
            print()
    
    if not projects and not models:
        print("❌ Aucun résultat trouvé")
        return False
    
    return True

# ============================================================================
# 📦 COMMANDES PROJETS ET MODÈLES
# ============================================================================

def handle_projects_list(args):
    """Liste les projets de l'utilisateur"""
    user = api_client.get_current_user()
    if not user:
        print("❌ Non connecté. Utilisez 'inithub login' d'abord.")
        return False
    
    user_only = getattr(args, 'user_only', False)
    projects = api_client.list_projects(user_only=user_only)
    
    if not projects:
        print("📭 Aucun projet trouvé")
        return True
        
    print(f"📁 {len(projects)} projets trouvés:")
    for project in projects:
        print(f"  📦 {project['name']} (ID: {project['id']})")
        print(f"     📝 {project.get('description', 'Pas de description')}")
        print(f"     👤 {project.get('author_username', 'Inconnu')}")
        print(f"     ⭐ {project.get('star_count', 0)} stars")
        print(f"     🏷️  {project.get('project_type', 'N/A')} | {project.get('primary_language', 'N/A')}")
        print()
    
    return True

def handle_models_list(args):
    """Liste les modèles IA disponibles"""
    user_only = getattr(args, 'user_only', False)
    models = api_client.list_models(user_only=user_only)
    
    if not models:
        print("🤖 Aucun modèle IA trouvé")
        return True
        
    print(f"🧠 {len(models)} modèles IA trouvés:")
    for model in models:
        print(f"  🔧 {model['name']} (ID: {model['id']})")
        print(f"     🏷️  {model['framework']} - {model['task_type']}")
        print(f"     👤 {model.get('author_username', 'Inconnu')}")
        print(f"     ❤️  {model.get('like_count', 0)} likes | 📥 {model.get('download_count', 0)} downloads")
        print(f"     📝 {model.get('description', 'Pas de description')}")
        print()
    
    return True

def handle_status(args):
    """Statut de la connexion et informations"""
    print(f"🌐 Serveur: {config.get_server_url()}")
    
    user = api_client.get_current_user()
    if user:
        print(f"✅ Connecté en tant que: {user['username']}")
        print(f"📧 Email: {user['email']}")
        
        # Statistiques utilisateur
        projects = api_client.list_projects(user_only=True)
        models = api_client.list_models(user_only=True)
        
        print(f"📊 Statistiques:")
        print(f"   📁 Projets: {len(projects)}")
        print(f"   🧠 Modèles: {len(models)}")
    else:
        print("❌ Non connecté")
    
    # Test de connexion au serveur
    try:
        response = requests.get(config.get_server_url(), timeout=5)
        print(f"📡 Serveur status: {'🟢 En ligne' if response.status_code == 200 else '🔴 Hors ligne'}")
    except:
        print("📡 Serveur status: 🔴 Hors ligne")
    
    # Informations de configuration
    print(f"📂 Répertoire de téléchargement: {config.get_download_dir()}")
    
    return True

def handle_test_upload(args):
    """Test d'upload pour debugger"""
    user = api_client.get_current_user()
    if not user:
        print("❌ Non connecté")
        return False
    
    # Créer un projet de test
    try:
        project_response = api_client.session.post(
            f"{api_client.base_url}/projects",
            json={
                "name": "test-upload",
                "description": "Projet de test pour upload",
                "project_type": "test",
                "primary_language": "python",
                "is_public": False
            }
        )
        project_data = api_client._handle_response(project_response)
        print(f"✅ Projet test créé: {project_data['id']}")
        
        # Tester l'upload
        test_file = Path("test_upload.txt")
        with open(test_file, 'w') as f:
            f.write("Ceci est un fichier de test pour initHUB")
        
        success = api_client.test_upload(project_data['id'], "test_upload.txt")
        
        # Nettoyer
        test_file.unlink(missing_ok=True)
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

# ============================================================================
# 🎯 INTERFACE CLI PRINCIPALE
# ============================================================================

def main():
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║              🚀 initHUB CLI v3.0              ║
    ║     Version améliorée - Commandes PULL        ║
    ╚═══════════════════════════════════════════════╝
    """
    
    print(banner)
    
    parser = argparse.ArgumentParser(
        description="🚀 initHUB CLI - Client complet avec connexion serveur et téléchargement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  🔐 Authentification:
    inithub login --email user@example.com --password secret
    inithub register --username john --email john@example.com --password secret
    inithub whoami
    inithub logout

  📁 Gestion projets .ssf:
    inithub ssf-init --name mon-projet
    inithub ssf-validate --path ./mon-projet
    inithub ssf-push --path ./mon-projet
    inithub ssf-list --path ./mon-projet

  📥 Téléchargement (PULL):
    inithub pull list                          # Lister les projets/modèles disponibles
    inithub pull project 123                   # Télécharger le projet ID 123
    inithub pull model 456                     # Télécharger le modèle ID 456
    inithub pull project 123 --output ./my_dir # Spécifier le répertoire de sortie
    inithub search "machine learning"          # Rechercher projets et modèles

  📦 Projets et modèles:
    inithub projects list
    inithub projects list --user-only          # Seulement mes projets
    inithub models list
    inithub models list --user-only            # Seulement mes modèles
    inithub status

  🐛 Debug:
    inithub test-upload
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # 🔐 Authentification
    login_parser = subparsers.add_parser('login', help='Connexion au serveur')
    login_parser.add_argument('--email', required=True, help='Email')
    login_parser.add_argument('--password', required=True, help='Mot de passe')
    
    register_parser = subparsers.add_parser('register', help='Inscription au serveur')
    register_parser.add_argument('--username', required=True, help='Nom d\'utilisateur')
    register_parser.add_argument('--email', required=True, help='Email')
    register_parser.add_argument('--password', required=True, help='Mot de passe')
    register_parser.add_argument('--full-name', help='Nom complet')
    
    whoami_parser = subparsers.add_parser('whoami', help='Affiche l\'utilisateur connecté')
    logout_parser = subparsers.add_parser('logout', help='Déconnexion')
    
    # 📁 Commandes .ssf
    ssf_init_parser = subparsers.add_parser('ssf-init', help='Crée un manifest .ssf')
    ssf_init_parser.add_argument('--name', help='Nom du projet')
    ssf_init_parser.add_argument('--path', help='Chemin du projet')
    ssf_init_parser.add_argument('--namespace', help='Namespace')
    ssf_init_parser.add_argument('--author', help='Auteur')
    ssf_init_parser.add_argument('--description', help='Description')
    ssf_init_parser.add_argument('--force', action='store_true', help='Écraser le fichier existant')
    
    ssf_push_parser = subparsers.add_parser('ssf-push', help='Push vers le serveur')
    ssf_push_parser.add_argument('--path', help='Chemin du projet')
    
    ssf_validate_parser = subparsers.add_parser('ssf-validate', help='Valide un manifest .ssf')
    ssf_validate_parser.add_argument('--path', help='Chemin du projet')
    
    ssf_show_parser = subparsers.add_parser('ssf-show', help='Affiche le manifest parsé')
    ssf_show_parser.add_argument('--path', help='Chemin du projet')
    
    ssf_list_parser = subparsers.add_parser('ssf-list', help='Liste les fichiers .ssf')
    ssf_list_parser.add_argument('--path', help='Chemin du projet')
    
    # 📥 Commandes PULL
    pull_parser = subparsers.add_parser('pull', help='Téléchargement depuis initHUB')
    pull_subparsers = pull_parser.add_subparsers(dest='pull_subcommand')
    
    pull_project_parser = pull_subparsers.add_parser('project', help='Télécharger un projet')
    pull_project_parser.add_argument('project_id', help='ID du projet')
    pull_project_parser.add_argument('--output', help='Répertoire de sortie')
    
    pull_model_parser = pull_subparsers.add_parser('model', help='Télécharger un modèle IA')
    pull_model_parser.add_argument('model_id', help='ID du modèle')
    pull_model_parser.add_argument('--output', help='Répertoire de sortie')
    
    pull_subparsers.add_parser('list', help='Lister les projets et modèles disponibles')
    
    # 🔍 Recherche
    search_parser = subparsers.add_parser('search', help='Recherche projets et modèles')
    search_parser.add_argument('query', help='Terme de recherche')
    
    # 📦 Commandes serveur
    projects_parser = subparsers.add_parser('projects', help='Gestion des projets')
    projects_subparsers = projects_parser.add_subparsers(dest='subcommand')
    projects_list_parser = projects_subparsers.add_parser('list', help='Liste les projets')
    projects_list_parser.add_argument('--user-only', action='store_true', help='Seulement mes projets')
    
    models_parser = subparsers.add_parser('models', help='Gestion des modèles IA')
    models_subparsers = models_parser.add_subparsers(dest='subcommand')
    models_list_parser = models_subparsers.add_parser('list', help='Liste les modèles IA')
    models_list_parser.add_argument('--user-only', action='store_true', help='Seulement mes modèles')
    
    status_parser = subparsers.add_parser('status', help='Statut de la connexion')
    
    # 🐛 Debug
    test_upload_parser = subparsers.add_parser('test-upload', help='Test d\'upload')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        success = False
        
        # 🔐 Authentification
        if args.command == 'login':
            success = handle_login(args)
        elif args.command == 'register':
            success = handle_register(args)
        elif args.command == 'whoami':
            success = handle_whoami(args)
        elif args.command == 'logout':
            success = handle_logout(args)
        
        # 📁 Commandes .ssf
        elif args.command == 'ssf-init':
            success = handle_ssf_init(args)
        elif args.command == 'ssf-push':
            success = handle_ssf_push(args)
        elif args.command == 'ssf-validate':
            success = handle_ssf_validate(args)
        elif args.command == 'ssf-show':
            success = handle_ssf_show(args)
        elif args.command == 'ssf-list':
            success = handle_ssf_list(args)
        
        # 📥 Commandes PULL
        elif args.command == 'pull':
            if args.pull_subcommand == 'project':
                success = handle_pull_project(args)
            elif args.pull_subcommand == 'model':
                success = handle_pull_model(args)
            elif args.pull_subcommand == 'list':
                success = handle_pull_list(args)
            else:
                pull_parser.print_help()
        
        # 🔍 Recherche
        elif args.command == 'search':
            success = handle_search(args)
        
        # 📦 Commandes serveur
        elif args.command == 'projects':
            if args.subcommand == 'list':
                success = handle_projects_list(args)
            else:
                projects_parser.print_help()
        elif args.command == 'models':
            if args.subcommand == 'list':
                success = handle_models_list(args)
            else:
                models_parser.print_help()
        elif args.command == 'status':
            success = handle_status(args)
        
        # 🐛 Debug
        elif args.command == 'test-upload':
            success = handle_test_upload(args)
        
        else:
            print(f"❌ Commande inconnue: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n👋 Opération annulée!")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
