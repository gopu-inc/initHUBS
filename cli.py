#!/usr/bin/env python3
"""
initHUB CLI - Support complet du format .ssf LZL-ZOBA
Version corrigée et améliorée
"""

import os
import re
import sys
import json
import glob
import fnmatch
import shlex
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# ============================================================================
# 📄 PARSER MANIFEST .SSF (LZL-ZOBA) AMÉLIORÉ
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
# 🛠️ UTILITAIRES FICHIERS AMÉLIORÉS
# ============================================================================

def expand_file_patterns(base_path: str, patterns: List[str]) -> List[str]:
    """Étend les patterns de fichiers .ssf de manière robuste"""
    base = Path(base_path)
    all_files = set()
    
    for pattern in patterns:
        if pattern.startswith('!'):
            continue
        
        # Nettoyer le pattern
        clean_pattern = pattern.strip()
        if not clean_pattern:
            continue
            
        try:
            # Utiliser glob avec gestion d'erreurs
            matches = glob.glob(str(base / clean_pattern), recursive=True)
            
            for match in matches:
                file_path = Path(match)
                if file_path.is_file():
                    try:
                        rel_path = file_path.relative_to(base)
                        all_files.add(str(rel_path))
                    except ValueError:
                        # Fichier en dehors du base_path
                        pass
        except Exception as e:
            print(f"⚠️  Erreur pattern '{pattern}': {e}")
    
    # Appliquer les exclusions
    exclude_patterns = [p[1:] for p in patterns if p.startswith('!')]
    final_files = []
    
    for file_path in all_files:
        if not any(fnmatch.fnmatch(file_path, excl) for excl in exclude_patterns):
            final_files.append(file_path)
    
    return sorted(final_files)

def find_ssf_file(project_path: str) -> Optional[Path]:
    """Trouve le fichier .ssf dans le projet"""
    path = Path(project_path)
    
    # Chercher init.ssf ou *.ssf
    ssf_files = list(path.glob("*.ssf"))
    
    if not ssf_files:
        return None
    
    # Préférer init.ssf
    for ssf_file in ssf_files:
        if ssf_file.name == "init.ssf":
            return ssf_file
    
    return ssf_files[0]

# ============================================================================
# 🚀 CLI AVEC COMMANDES .SSF AMÉLIORÉES
# ============================================================================

def handle_ssf_init(args):
    """Crée un nouveau manifest .ssf"""
    project_path = args.path or "."
    project_name = args.name or Path(project_path).name
    
    print(f"🚀 Création du manifest .ssf pour {project_name}...")
    
    # Vérifier si un manifest existe déjà
    ssf_path = Path(project_path) / "init.ssf"
    if ssf_path.exists() and not args.force:
        print("❌ Un fichier init.ssf existe déjà. Utilisez --force pour écraser.")
        return False
    
    # Générer le contenu .ssf sécurisé
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
        # Écrire le fichier
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
    """Push avec le manifest .ssf"""
    project_path = args.path or "."
    
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
        
        # Afficher les infos
        print(f"👤 Auteur: {manifest.get('author', 'anonymous')}")
        print(f"📁 Fichiers: {len(manifest.get('files', []))} patterns")
        print(f"🏷️  Tags: {', '.join(manifest.get('tags', []))}")
        print(f"🌿 Branche: {manifest.get('branch', 'main')}")
        
        if 'fork' in manifest:
            print(f"🍴 Fork de: {manifest['fork']}")
        
        # Traiter les fichiers
        file_patterns = manifest.get('files', [])
        all_files = expand_file_patterns(project_path, file_patterns)
        
        print(f"\n📤 {len(all_files)} fichiers à pousser:")
        for file_path in all_files[:10]:  # Afficher les 10 premiers
            print(f"  📄 {file_path}")
        
        if len(all_files) > 10:
            print(f"  ... et {len(all_files) - 10} autres fichiers")
        
        # Vérifier les dépendances
        deps = manifest.get('dependencies', {})
        if deps.get('python') or deps.get('packages'):
            print(f"\n📦 Dépendances:")
            if deps.get('python'):
                print(f"  🐍 Python {deps['python']}")
            for pkg in deps.get('packages', []):
                print(f"  📦 {pkg}")
        
        print("\n✅ Push simulé avec succès!")
        return True
        
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
        
        # Validation de base
        required = ['name', 'files', 'branch']
        missing = [field for field in required if field not in manifest]
        
        if missing:
            print(f"❌ Champs manquants: {', '.join(missing)}")
            return False
        
        # Validation des fichiers
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
# 🔥 NOUVELLES COMMANDES AVANCÉES
# ============================================================================

def handle_ssf_generate(args):
    """Génère un template de projet basé sur un type"""
    project_path = args.path or "."
    project_type = args.type or "basic"
    
    templates = {
        "basic": {
            "name": "mon-projet",
            "description": "Projet basique initHUB",
            "files": ["*.py", "*.md", "!__pycache__/**"],
            "tags": ["basic", "cli"]
        },
        "ml": {
            "name": "modele-ia",
            "description": "Projet de machine learning",
            "files": ["*.py", "*.md", "*.ipynb", "models/**", "data/**", "!__pycache__/**"],
            "tags": ["ml", "ai", "python"],
            "dependencies": ["torch>=1.9", "scikit-learn>=1.0"]
        },
        "web": {
            "name": "application-web",
            "description": "Projet d'application web",
            "files": ["*.py", "*.html", "*.css", "*.js", "static/**", "templates/**", "!__pycache__/**"],
            "tags": ["web", "api", "fastapi"]
        }
    }
    
    template = templates.get(project_type, templates["basic"])
    
    print(f"🚀 Génération template {project_type}...")
    
    # Créer les arguments pour ssf-init
    class Args:
        pass
    
    args_obj = Args()
    args_obj.path = project_path
    args_obj.name = template["name"]
    args_obj.description = template["description"]
    args_obj.namespace = project_type
    args_obj.author = args.author or "anonymous"
    args_obj.force = True
    
    return handle_ssf_init(args_obj)

def handle_ssf_stats(args):
    """Affiche les statistiques du projet .ssf"""
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
        file_patterns = manifest.get('files', [])
        all_files = expand_file_patterns(project_path, file_patterns)
        
        # Calculer les statistiques
        total_size = 0
        extensions = {}
        
        for file_path in all_files:
            full_path = Path(project_path) / file_path
            if full_path.exists():
                total_size += full_path.stat().st_size
                ext = full_path.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1
        
        print(f"📊 Statistiques du projet: {manifest['name']}")
        print(f"📁 Fichiers: {len(all_files)}")
        print(f"💾 Taille totale: {total_size / 1024:.1f} KB")
        print(f"🏷️  Tags: {', '.join(manifest.get('tags', []))}")
        print(f"📦 Dépendances: {len(manifest.get('dependencies', {}).get('packages', []))}")
        
        if extensions:
            print(f"📄 Extensions: {', '.join([f'{ext}({count})' for ext, count in extensions.items()])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")
        return False

# ============================================================================
# 🎯 INTERFACE CLI PRINCIPALE COMPLÈTE
# ============================================================================

def main():
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║              🚀 initHUB CLI                   ║
    ║        Support .ssf LZL-ZOBA v2.0            ║
    ╚═══════════════════════════════════════════════╝
    """
    
    print(banner)
    
    parser = argparse.ArgumentParser(
        description="🚀 initHUB CLI - Gestionnaire de projets .ssf LZL-ZOBA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  inithub ssf-init --name mon-projet
  inithub ssf-validate --path ./mon-projet
  inithub ssf-push --path ./mon-projet
  inithub ssf-generate --type ml --name mon-modele-ia
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # ssf-init
    ssf_init_parser = subparsers.add_parser('ssf-init', help='Crée un manifest .ssf')
    ssf_init_parser.add_argument('--name', help='Nom du projet')
    ssf_init_parser.add_argument('--path', help='Chemin du projet')
    ssf_init_parser.add_argument('--namespace', help='Namespace (dragon, cli, etc.)')
    ssf_init_parser.add_argument('--author', help='Auteur')
    ssf_init_parser.add_argument('--description', help='Description')
    ssf_init_parser.add_argument('--force', action='store_true', help='Écraser le fichier existant')
    
    # ssf-push
    ssf_push_parser = subparsers.add_parser('ssf-push', help='Push avec manifest .ssf')
    ssf_push_parser.add_argument('--path', help='Chemin du projet')
    
    # ssf-validate
    ssf_validate_parser = subparsers.add_parser('ssf-validate', help='Valide un manifest .ssf')
    ssf_validate_parser.add_argument('--path', help='Chemin du projet')
    
    # ssf-show
    ssf_show_parser = subparsers.add_parser('ssf-show', help='Affiche le manifest parsé')
    ssf_show_parser.add_argument('--path', help='Chemin du projet')
    
    # ssf-list
    ssf_list_parser = subparsers.add_parser('ssf-list', help='Liste les fichiers .ssf')
    ssf_list_parser.add_argument('--path', help='Chemin du projet')
    
    # ssf-generate
    ssf_generate_parser = subparsers.add_parser('ssf-generate', help='Génère un template de projet')
    ssf_generate_parser.add_argument('--type', choices=['basic', 'ml', 'web'], help='Type de template')
    ssf_generate_parser.add_argument('--path', help='Chemin du projet')
    ssf_generate_parser.add_argument('--author', help='Auteur')
    
    # ssf-stats
    ssf_stats_parser = subparsers.add_parser('ssf-stats', help='Affiche les statistiques du projet')
    ssf_stats_parser.add_argument('--path', help='Chemin du projet')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'ssf-init':
            success = handle_ssf_init(args)
        elif args.command == 'ssf-push':
            success = handle_ssf_push(args)
        elif args.command == 'ssf-validate':
            success = handle_ssf_validate(args)
        elif args.command == 'ssf-show':
            success = handle_ssf_show(args)
        elif args.command == 'ssf-list':
            success = handle_ssf_list(args)
        elif args.command == 'ssf-generate':
            success = handle_ssf_generate(args)
        elif args.command == 'ssf-stats':
            success = handle_ssf_stats(args)
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
