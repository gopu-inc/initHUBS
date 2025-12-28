# Zenv Hub Frontend

Interface web pour le Zenv Package Hub, déployée sur Vercel.

## 🚀 Déploiement Rapide

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-repo/zenv-hub-frontend)

## 🔗 Connexion à l'API

Ce frontend se connecte automatiquement à l'API Zenv Hub:
- **URL API**: `https://zenv-hub.onrender.com`
- **Version API**: 2.1.0
- **Dépôt GitHub**: `gopu-inc/gsql-badge` (privé)

## ✨ Fonctionnalités

- 📦 **Liste des packages** - Affiche tous les packages disponibles
- 🎨 **Atelier badges** - Créez des badges personnalisés avec logos
- 📊 **Statistiques** - Metriques en temps réel
- 📱 **Responsive** - Compatible mobile et desktop
- 🌓 **Dark mode** - Support du thème sombre
- 🔗 **Intégration CLI** - Liens directs vers les commandes Zenv CLI

## 🛠️ Structure

```

zenv-hub-frontend/
├── index.html          # Page principale
├── vercel.json        # Configuration Vercel
├── package.json       # Dépendances
└── README.md         # Documentation

```

## 📡 API Proxy

Vercel redirige automatiquement:
- `/api/*` → `https://zenv-hub.onrender.com/api/*`
- `/badge/*` → `https://zenv-hub.onrender.com/badge/*`

## 🎯 Utilisation

### Avec le CLI Zenv
```bash
# Se connecter
zenv hub login zenv_votre_token

# Publier un package
zenv hub publish mon-package-1.0.0.zv

# Installer un package
zenv pkg install mon-package
```

Via l'interface web

1. Visitez https://zenv-hub.vercel.app
2. Parcourez les packages disponibles
3. Créez des badges avec l'atelier
4. Téléchargez les packages directement

🔧 Configuration

Variables d'environnement (optionnel):

```
NEXT_PUBLIC_API_URL=https://zenv-hub.onrender.com
NEXT_PUBLIC_API_VERSION=2.1.0
```

📄 Licence

MIT License - Voir LICENSE pour plus de détails.

🤝 Contribution

1. Fork le projet
2. Créez une branche (git checkout -b feature/amazing)
3. Commit (git commit -m 'Add amazing feature')
4. Push (git push origin feature/amazing)
5. Ouvrez une Pull Request

🔗 Liens Utiles

· Zenv CLI GitHub
· API Documentation
· PyPI Package

```

