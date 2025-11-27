#!/usr/bin/env python3
"""
initHUB CLI - Support complet du format .ssf LZL-ZOBA
"""

import os
import re
import shlex
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# ============================================================================
# 📄 PARSER MANIFEST .SSF (LZL-ZOBA)
# ============================================================================

class SSFParser:
    def __init__(self):
        self.manifest_data = {}
    
    def parse_ssf(self, content: str) -> Dict[str, Any]:
        """Parse le contenu d'un fichier .ssf"""
        lines = content.split('\n')
        self.manifest_data = {}
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
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
                # C'est un fork
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
                
                # Parse les tableaux
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
                
                # Supprimer les guillemets
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                metadata[key] = value
            
            i += 1
        
        self.manifest_data['metadata'] = metadata
        return i

# ============================================================================
# 🚀 CLI AVEC COMMANDES .SSF
# ============================================================================

def handle_ssf_init(args):
    """Crée un nouveau manifest .ssf"""
    project_path = args.path or "."
    project_name = args.name or Path(project_path).name
    
    print(f"🚀 Création du manifest .ssf pour {project_name}...")
    
    # Vérifier si un manifest existe déjà
    ssf_path = Path(project_path) / "init.ssf"
    if ssf_path.exists():
        print("❌ Un fichier init.ssf existe déjà")
        return False
    
    # Générer le contenu .ssf
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
        {args.namespace or "default"} >
        cli
):main-{project_name}

<=/>{{author =({args.author or "anonymous")}}

init.get(
   - README:md
   - LICENSE:md
)

# Configuration de base
meta.set(
   description = "{args.description or "Nouveau projet initHUB"}"
   license = MIT
   visibility = public
)
"""
    
    # Écrire le fichier
    with open(ssf_path, 'w') as f:
        f.write(ssf_content)
    
    print(f"✅ Manifest créé: {ssf_path}")
    return True

def handle_ssf_push(args):
    """Push avec le manifest .ssf"""
    project_path = args.path or "."
    ssf_path = Path(project_path) / "init.ssf"
    
    if not ssf_path.exists():
        print("❌ Fichier init.ssf non trouvé")
        return False
    
    # Parser le manifest
    parser = SSFParser()
    with open(ssf_path, 'r') as f:
        content = f.read()
    
    try:
        manifest = parser.parse_ssf(content)
        print(f"📦 Manifest chargé: {manifest['name']} v{manifest.get('version', '1.0.0')}")
        
        # Afficher les infos
        print(f"📁 Fichiers: {len(manifest.get('files', []))} patterns")
        print(f"🏷️  Tags: {', '.join(manifest.get('tags', []))}")
        print(f"🌿 Branche: {manifest.get('branch', 'main')}")
        
        if 'fork' in manifest:
            print(f"🍴 Fork de: {manifest['fork']}")
        
        # Traiter les fichiers
        file_patterns = manifest.get('files', [])
        all_files = self._expand_file_patterns(project_path, file_patterns)
        
        print(f"📤 {len(all_files)} fichiers à pousser...")
        
        # Simuler le push
        for file_path in all_files:
            print(f"  📄 {file_path}")
        
        print("✅ Push simulé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur parsing .ssf: {e}")
        return False

def _expand_file_patterns(self, base_path: str, patterns: List[str]) -> List[str]:
    """Étend les patterns de fichiers .ssf"""
    import glob
    import fnmatch
    
    base = Path(base_path)
    all_files = set()
    
    for pattern in patterns:
        if pattern.startswith('!'):
            # Exclusion - à gérer plus tard
            continue
        
        # Remplacer ** par * pour glob simple
        glob_pattern = pattern.replace('**', '*')
        
        # Trouver les fichiers correspondants
        matches = glob.glob(str(base / glob_pattern), recursive=True)
        
        for match in matches:
            file_path = Path(match)
            if file_path.is_file():
                # Chemin relatif
                rel_path = file_path.relative_to(base)
                all_files.add(str(rel_path))
    
    # Appliquer les exclusions
    exclude_patterns = [p[1:] for p in patterns if p.startswith('!')]
    final_files = []
    
    for file_path in all_files:
        if not any(fnmatch.fnmatch(file_path, excl) for excl in exclude_patterns):
            final_files.append(file_path)
    
    return sorted(final_files)

def handle_ssf_validate(args):
    """Valide un manifest .ssf"""
    project_path = args.path or "."
    ssf_path = Path(project_path) / "init.ssf"
    
    if not ssf_path.exists():
        print("❌ Fichier init.ssf non trouvé")
        return False
    
    parser = SSFParser()
    with open(ssf_path, 'r') as f:
        content = f.read()
    
    try:
        manifest = parser.parse_ssf(content)
        
        # Validation de base
        required = ['name', 'version', 'files', 'branch']
        missing = [field for field in required if field not in manifest]
        
        if missing:
            print(f"❌ Champs manquants: {', '.join(missing)}")
            return False
        
        print("✅ Manifest .ssf valide!")
        print(f"📊 Nom: {manifest['name']}")
        print(f"📊 Version: {manifest['version']}")
        print(f"📊 Fichiers: {len(manifest['files'])} patterns")
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
    ssf_path = Path(project_path) / "init.ssf"
    
    if not ssf_path.exists():
        print("❌ Fichier init.ssf non trouvé")
        return False
    
    parser = SSFParser()
    with open(ssf_path, 'r') as f:
        content = f.read()
    
    try:
        manifest = parser.parse_ssf(content)
        
        import json
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return True
        
    except Exception as e:
        print(f"❌ Erreur parsing: {e}")
        return False

# ============================================================================
# 🎯 INTERFACE CLI PRINCIPALE AMÉLIORÉE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="🚀 initHUB CLI - Support .ssf LZL-ZOBA")
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commandes .ssf
    ssf_init_parser = subparsers.add_parser('ssf-init', help='Crée un manifest .ssf')
    ssf_init_parser.add_argument('--name', help='Nom du projet')
    ssf_init_parser.add_argument('--path', help='Chemin du projet')
    ssf_init_parser.add_argument('--namespace', help='Namespace (dragon, cli, etc.)')
    ssf_init_parser.add_argument('--author', help='Auteur')
    ssf_init_parser.add_argument('--description', help='Description')
    
    ssf_push_parser = subparsers.add_parser('ssf-push', help='Push avec manifest .ssf')
    ssf_push_parser.add_argument('--path', help='Chemin du projet')
    
    ssf_validate_parser = subparsers.add_parser('ssf-validate', help='Valide un manifest .ssf')
    ssf_validate_parser.add_argument('--path', help='Chemin du projet')
    
    ssf_show_parser = subparsers.add_parser('ssf-show', help='Affiche le manifest parsé')
    ssf_show_parser.add_argument('--path', help='Chemin du projet')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'ssf-init':
            handle_ssf_init(args)
        elif args.command == 'ssf-push':
            handle_ssf_push(args)
        elif args.command == 'ssf-validate':
            handle_ssf_validate(args)
        elif args.command == 'ssf-show':
            handle_ssf_show(args)
        else:
            print(f"❌ Commande inconnue: {args.command}")
            
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")
    except Exception as e:
        print(f"💥 Erreur: {e}")

if __name__ == "__main__":
    main()
