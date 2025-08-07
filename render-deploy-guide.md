# 🚀 GUIDE RENDER.COM - CLAIRE ET MARCUS BACKEND

## ÉTAPE 1 : PRÉPARATION

### ✅ Vérifiez que votre code est sur GitHub
- Votre repo doit contenir le dossier `backend/` avec tous les fichiers
- Fichiers nécessaires : `server.py`, `requirements.txt`, `render.yaml`

## ÉTAPE 2 : INSCRIPTION RENDER.COM

### 2.1 Créez un compte
1. Allez sur **https://render.com**
2. Cliquez **"Get Started for Free"**
3. **Connectez-vous avec GitHub** (recommandé)

### 2.2 Autorisations
- Autorisez Render à accéder à vos repos GitHub
- Sélectionnez "All repositories" ou votre repo spécifique

## ÉTAPE 3 : CRÉER LE SERVICE WEB

### 3.1 Nouveau service
1. Sur Render Dashboard : **"New +"**
2. Sélectionnez **"Web Service"**
3. **"Build and deploy from a Git repository"**
4. **Connectez votre repo GitHub**

### 3.2 Configuration du service
```
┌─────────────────────────────────────────────────┐
│ Repository: votre-username/claire-marcus        │
│ Name: claire-marcus-api                         │
│ Region: Oregon (US West)                        │
│ Branch: main                                    │
│ Root Directory: backend                         │
│ Environment: Python 3                          │
│ Build Command: pip install -r requirements.txt │
│ Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT │
│ Plan: Free                                      │
└─────────────────────────────────────────────────┘
```

**⚠️ IMPORTANT :**
- **Root Directory** = `backend` (pas vide !)
- **Build Command** = `pip install -r requirements.txt`
- **Start Command** = `uvicorn server:app --host 0.0.0.0 --port $PORT`

## ÉTAPE 4 : VARIABLES D'ENVIRONNEMENT

### 4.1 Ajout des variables
Dans Render Dashboard → **Environment** :

**Variables OBLIGATOIRES :**
```
MONGO_URL = mongodb+srv://username:password@cluster.mongodb.net/claire_marcus
OPENAI_API_KEY = sk-proj-votre-clé-openai
JWT_SECRET_KEY = votre-super-secret-key-2024
DB_NAME = claire_marcus
```

**Variables OPTIONNELLES (pour plus tard) :**
```
STRIPE_API_KEY = sk_test_votre-clé-stripe
LINKEDIN_CLIENT_ID = votre-id-linkedin
LINKEDIN_CLIENT_SECRET = votre-secret-linkedin
FACEBOOK_APP_ID = votre-id-facebook
FACEBOOK_APP_SECRET = votre-secret-facebook
```

### 4.2 MongoDB Atlas
Si vous n'avez pas encore MongoDB :
1. Créez un compte sur **https://cloud.mongodb.com**
2. Créez un cluster gratuit (M0)
3. Ajoutez un utilisateur de base de données
4. Whitelist : `0.0.0.0/0` (toutes les IPs)
5. Récupérez la connection string

## ÉTAPE 5 : PREMIER DÉPLOIEMENT

### 5.1 Lancement
1. Cliquez **"Create Web Service"**
2. Render va :
   - Cloner votre repo
   - Aller dans `/backend/`
   - Installer les dépendances
   - Démarrer l'API

### 5.2 Durée
- **Premier déploiement** : 3-5 minutes
- **Redéploiements** : 1-2 minutes

### 5.3 URL générée
Votre API sera accessible sur :
`https://claire-marcus-api.onrender.com`

## ÉTAPE 6 : TESTS & VÉRIFICATION

### 6.1 Tests de santé
Vérifiez ces URLs :
- `https://votre-app.onrender.com/api/health` ← Doit retourner "healthy"
- `https://votre-app.onrender.com/docs` ← Documentation API

### 6.2 Logs
- **Dashboard** → votre service → **Logs**
- Vérifiez qu'il n'y a pas d'erreurs

## ÉTAPE 7 : CONNECTER À NETLIFY

### 7.1 Mise à jour Netlify
Dans Netlify → **Environment variables** :
```
REACT_APP_BACKEND_URL = https://votre-app.onrender.com
```

### 7.2 Test complet
- Frontend Netlify : `https://claire-marcus.com`
- Backend Render : `https://votre-app.onrender.com`
- Les deux communiquent ✅

## ÉTAPE 8 : GESTION DE LA VEILLE

### 8.1 Plan gratuit - Limitation
- **Se met en veille** après 15 minutes d'inactivité
- **Réveil** : 30 secondes au premier accès
- **750h/mois** incluses (largement suffisant)

### 8.2 Solutions
**Option 1 - Accepter (Recommandé pour MVP) :**
- Normal pour un projet en développement
- Utilisateurs habitués aux startups

**Option 2 - Éviter la veille :**
- Plan payant Render : $7/mois
- Ou service de ping (UptimeRobot, etc.)

## 🎯 RÉSULTAT FINAL

**Votre stack complète :**
- ✅ **Frontend** : claire-marcus.com (Netlify)
- ✅ **Backend** : votre-app.onrender.com (Render)
- ✅ **Base de données** : MongoDB Atlas
- ✅ **Total coût** : 0€/mois !

## 🔄 DÉPLOIEMENT CONTINU

**À chaque push GitHub :**
1. **Render** redéploie automatiquement le backend
2. **Netlify** redéploie automatiquement le frontend
3. **Tout est synchronisé** ! 🎉

## 🆘 DÉPANNAGE COURANT

**Erreurs fréquentes :**
- `ModuleNotFoundError` → Vérifiez requirements.txt
- `Connection refused` → Vérifiez MONGO_URL  
- `Port binding failed` → Render gère automatiquement

**Port :**
- Render définit automatiquement `$PORT`
- Votre code doit utiliser `--port $PORT` (déjà fait)

**Logs utiles :**
```
# Voir les derniers logs :
Dashboard → Service → Logs → Live tail
```