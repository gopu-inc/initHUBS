#!/usr/bin/env python3
"""
Setup script for initHUB CLI
Package sans dépendances externes - uniquement modules Python standard
"""

import os
import sys
from setuptools import setup, find_packages
from pathlib import Path

# Read the version from the CLI file
def get_version():
    """Extract version from the CLI script"""
    cli_file = Path("inithub_cli.py")
    if cli_file.exists():
        with open(cli_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

def read_long_description():
    """Read long description from README.md"""
    readme_path = Path("README.md")
    if readme_path.exists():
        try:
            return readme_path.read_text(encoding='utf-8')
        except:
            return "initHUB CLI - Interface en ligne de commande pour la plateforme initHUB"
    return "initHUB CLI - Interface en ligne de commande pour la plateforme initHUB"

# Configuration
setup(
    name="inithub-cli",
    version=get_version(),
    
    # Authors
    author="gopu-inc Team",
    author_email="ceoseshell@gmail.com",
    
    # Description
    description="CLI officiel pour la plateforme initHUB - Partage de modèles IA et collaboration",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    
    # URLs
    url="https://github.com/gopu-inc/initHUBS",
    project_urls={
        "Homepage": "https://inithub.vercel.app",
        "Documentation": "https://docs.inithub.vercel.app",
        "Source Code": "https://github.com/gopu-inc/initHUBS",
        "Bug Tracker": "https://github.com/gopu-inc/initHUBS/issues",
    },
    
    # Classifiers
    classifiers=[
        # Development status
        "Development Status :: 4 - Beta",
        
        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        
        # Topics
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Version Control",
        "Topic :: Utilities",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming languages
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # Operating systems
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        
        # Environment
        "Environment :: Console",
        "Natural Language :: English",
        "Natural Language :: French",
    ],
    
    # Keywords
    keywords=[
        "ai", "machine-learning", "cli", "collaboration", 
        "models", "huggingface", "inithub", "mlops",
        "python", "api", "developer-tools"
    ],
    
    # Packages
    packages=find_packages(include=['inithub', 'inithub.*']),
    
    # Python requirements
    python_requires=">=3.8",
    
    # No external dependencies - using only Python standard library
    install_requires=[],  # Vide car utilisation modules standard
    
    # Entry points
    entry_points={
        "console_scripts": [
            "inithub=cli:main",
        ],
    },
    
    # Package data
    package_data={
        "inithub": [
            "*.py",
            "*.md",
            "*.txt",
        ],
    },
    
    # Data files
    data_files=[
        ('share/doc/inithub', ['README.md', 'LICENSE']),
        ('share/man/man1', ['man/inithub.1']),
    ],
    
    # Options
    options={
        'bdist_wheel': {
            'universal': True
        }
    },
    
    # Zip safe
    zip_safe=True,
    
    # License
    license="MIT",
    
    # Platforms
    platforms=["any"],
    
    # Additional metadata
    provides=["inithub"],
    
    # Test suite
    test_suite="tests",
    
    # Tests require
    tests_require=[],  # Vide car tests utilisent modules standard
)
