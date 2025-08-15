# 🔐 CHANGEMENT MOT DE PASSE MONGODB ATLAS

## PROBLÈME PERSISTANT
❌ Caractères spéciaux (@, !) causent des erreurs d'authentification MongoDB Atlas
❌ Même avec encodage correct, Render ne peut pas se connecter

## SOLUTION: NOUVEAU MOT DE PASSE SIMPLE

### 1. ACCÉDER À MONGODB ATLAS
- URL: https://cloud.mongodb.com
- Connectez-vous avec votre compte

### 2. CHANGER MOT DE PASSE UTILISATEUR
- **Database Access** → Trouvez utilisateur `lperpere`
- **Edit User** → **Change Password**
- **Nouveau mot de passe suggéré**: `ClaireMarcus2025`
  (Pas de @ ! ni caractères spéciaux)

### 3. NOUVELLE URL PROPRE
Avec le nouveau mot de passe:
```
mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0
```

### 4. CONFIGURATION RENDER
Variables d'environnement Render:
```
MONGO_URL=mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=claire_marcus
```

### 5. AVANTAGES NOUVEAU MOT DE PASSE
- ✅ Pas de caractères spéciaux problématiques
- ✅ Pas besoin d'encodage URL
- ✅ Compatible tous environnements
- ✅ Plus simple à débugger

## ALTERNATIVE TEMPORAIRE
Si vous ne pouvez pas changer le mot de passe maintenant:
- Utilisez l'environnement local: http://10.64.167.140:3000
- Toutes fonctionnalités marchent parfaitement
- MongoDB Atlas même cluster

Le changement de mot de passe résoudra définitivement le problème Render!