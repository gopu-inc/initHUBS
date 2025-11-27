#!/usr/bin/env python3
"""
initHUB CLI - Client complet avec connexion au serveur en ligne
Support .ssf LZL-ZOBA + API initHUB
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
from pathlib import Path
from typing import Dict, List, Any, Optional

# ============================================================================
# ⚙️ CONFIGURATION CLIENT
# ============================================================================

class CLIConfig:
    # URL de votre serveur déployé
    SERVER_URL = "https://hubs-ja2g.onrender.com"
    API_BASE = f"{SERVER_URL}/api"
    
    # Chemins de configuration
    CONFIG_DIR = Path.home() / ".inithub"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    TOKEN_FILE = CONFIG_DIR / "token.json"
    
    def __init__(self):
        self.config_dir = self.CONFIG_DIR
        self.config_dir.mkdir(exist_ok=True)
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
            self.data = {"server_url": self.SERVER_URL}
    
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

# Configuration globale
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
                "Authorization": f"Bearer {self.token_data.get('access_token')}",
                "Content-Type": "application/json"
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
            return self._upload_files(manifest_data, project_data['id'], project_path)
            
        except Exception as e:
            print(f"❌ Erreur création projet: {e}")
            return False
    
    def _upload_files(self, manifest_data: Dict[str, Any], project_id: int, project_path: str) -> bool:
        """Upload les fichiers du projet"""
        file_patterns = manifest_data.get('files', [])
        all_files = expand_file_patterns(project_path, file_patterns)
        
        print(f"📤 Upload de {len(all_files)} fichiers...")
        
        success_count = 0
        for file_path in all_files:
            try:
                full_path = Path(project_path) / file_path
                
                with open(full_path, 'rb') as f:
                    files = {'file': (file_path, f, 'application/octet-stream')}
                    data = {'project_id': project_id, 'description': f"Fichier {file_path}"}
                    
                    response = self.session.post(
                        f"{self.base_url}/upload",
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        print(f"  ✅ {file_path}")
                        success_count += 1
                    else:
                        print(f"  ❌ {file_path} - Erreur: {response.status_code}")
                        
            except Exception as e:
                print(f"  ❌ {file_path} - {e}")
        
        print(f"📊 Upload terminé: {success_count}/{len(all_files)} fichiers")
        return success_count > 0
    
    def list_projects(self):
        """Liste les projets de l'utilisateur"""
        try:
            response = self.session.get(f"{self.base_url}/projects")
            projects = self._handle_response(response)
            
            if not projects:
                print("📭 Aucun projet trouvé")
                return True
                
            print(f"📁 {len(projects)} projets trouvés:")
            for project in projects:
                print(f"  📦 {project['name']} (ID: {project['id']})")
                print(f"     📝 {project.get('description', 'Pas de description')}")
                print(f"     👤 {project.get('author_username', 'Inconnu')}")
                print(f"     ⭐ {project.get('star_count', 0)} stars")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur liste projets: {e}")
            return False
    
    def list_models(self):
        """Liste les modèles IA"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            models = self._handle_response(response)
            
            if not models:
                print("🤖 Aucun modèle IA trouvé")
                return True
                
            print(f"🧠 {len(models)} modèles IA trouvés:")
            for model in models:
                print(f"  🔧 {model['name']} (ID: {model['id']})")
                print(f"     🏷️  {model['framework']} - {model['task_type']}")
                print(f"     👤 {model.get('author_username', 'Inconnu')}")
                print(f"     ❤️  {model.get('like_count', 0)} likes")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur liste modèles: {e}")
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
            matches = glob.glob(str(base / clean_pattern), recursive=True)
            
            for match in matches:
                file_path = Path(match)
                if file_path.is_file():
                    try:
                        rel_path = file_path.relative_to(base)
                        all_files.add(str(rel_path))
                    except ValueError:
                        pass
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

# ============================================================================
# 🚀 COMMANDES .SSF AVEC CONNEXION API
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
         - !__pycache__/**
 ]}} ==> push-hub
   —tags( # >
        {namespace} >
        cli
):main-{project_name}

<=/>{{author =({author})}}

init.get(
   - README:md
   - LICENSE:md
)

# Configuration de base
meta.set(
   description = "{description}"
   license = MIT
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
        
        # Push vers le serveur
        return api_client.push_project(manifest, project_path)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

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
# 📦 COMMANDES PROJETS ET MODÈLES
# ============================================================================

def handle_projects_list(args):
    """Liste les projets de l'utilisateur"""
    user = api_client.get_current_user()
    if not user:
        print("❌ Non connecté. Utilisez 'inithub login' d'abord.")
        return False
    
    return api_client.list_projects()

def handle_models_list(args):
    """Liste les modèles IA disponibles"""
    return api_client.list_models()

def handle_status(args):
    """Statut de la connexion et informations"""
    print(f"🌐 Serveur: {config.get_server_url()}")
    
    user = api_client.get_current_user()
    if user:
        print(f"✅ Connecté en tant que: {user['username']}")
        print(f"📧 Email: {user['email']}")
    else:
        print("❌ Non connecté")
    
    # Test de connexion au serveur
    try:
        response = requests.get(config.get_server_url(), timeout=5)
        print(f"📡 Serveur status: {'🟢 En ligne' if response.status_code == 200 else '🔴 Hors ligne'}")
    except:
        print("📡 Serveur status: 🔴 Hors ligne")
    
    return True

# ============================================================================
# 🎯 INTERFACE CLI PRINCIPALE
# ============================================================================

def main():
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║              🚀 initHUB CLI v2.0              ║
    ║        Connecté à: hubs-ja2g.onrender.com     ║
    ╚═══════════════════════════════════════════════╝
    """
    
    print(banner)
    
    parser = argparse.ArgumentParser(
        description="🚀 initHUB CLI - Client complet avec connexion serveur",
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

  📦 Projets et modèles:
    inithub projects list
    inithub models list
    inithub status

  🆓 Sans authentification:
    inithub ssf-show --path ./mon-projet
    inithub ssf-validate --path ./mon-projet
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
    
    # 📦 Commandes serveur
    projects_parser = subparsers.add_parser('projects', help='Gestion des projets')
    projects_subparsers = projects_parser.add_subparsers(dest='subcommand')
    projects_subparsers.add_parser('list', help='Liste les projets')
    
    models_parser = subparsers.add_parser('models', help='Gestion des modèles IA')
    models_subparsers = models_parser.add_subparsers(dest='subcommand')
    models_subparsers.add_parser('list', help='Liste les modèles IA')
    
    status_parser = subparsers.add_parser('status', help='Statut de la connexion')
    
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
