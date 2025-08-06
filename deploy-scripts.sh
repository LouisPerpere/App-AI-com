#!/bin/bash

# Scripts de déploiement Claire et Marcus

echo "🚀 Déploiement Claire et Marcus"

# 1. Build du frontend
echo "📦 Build du frontend..."
cd frontend
npm install
npm run build

# 2. Vérification du build
if [ -d "build" ]; then
    echo "✅ Build réussi!"
    echo "📁 Taille du build:"
    du -sh build/
    
    echo "📋 Fichiers dans build/:"
    ls -la build/
else
    echo "❌ Échec du build!"
    exit 1
fi

# 3. Instructions de déploiement
echo ""
echo "🌐 INSTRUCTIONS DE DÉPLOIEMENT NETLIFY:"
echo "1. Glissez-déposez le dossier 'build' sur netlify.com"
echo "2. Ou connectez votre repo GitHub à Netlify"
echo "3. Configurez votre domaine claire-marcus.com"
echo ""

# 4. Informations importantes
echo "⚠️  N'OUBLIEZ PAS:"
echo "• Configurer REACT_APP_BACKEND_URL dans Netlify"
echo "• Héberger votre backend FastAPI séparément"
echo "• Configurer MongoDB Atlas"
echo "• Ajouter les DNS sur OVH"

cd ..