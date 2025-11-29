const fs = require('fs')
const path = require('path')

// Créer la structure de dossiers
const directories = [
  'app',
  'app/dashboard',
  'app/repos',
  'app/repos/[owner]',
  'app/repos/[owner]/[repo]',
  'app/copilot',
  'app/releases',
  'app/wiki',
  'app/api/auth',
  'components',
  'lib',
  'public'
]

directories.forEach(dir => {
  const dirPath = path.join(__dirname, '..', dir)
  if (!fs.existsSync(dirPath)) {
