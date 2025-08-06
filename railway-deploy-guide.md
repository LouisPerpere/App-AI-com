# 🚂 GUIDE RAILWAY - CLAIRE ET MARCUS BACKEND

## ÉTAPE 1 : PRÉPARATION LOCALE

### 1.1 Vérifiez vos fichiers
Assurez-vous que le dossier `/app/backend/` contient :
- ✅ `server.py` (application principale)
- ✅ `requirements.txt` (dépendances)
- ✅ `Procfile` (commande de démarrage)
- ✅ `railway.json` (configuration Railway)
- ✅ Tous vos modules (.py)

### 1.2 Test local
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```
Vérifiez que http://localhost:8000 fonctionne

## ÉTAPE 2 : INSCRIPTION RAILWAY

### 2.1 Créez un compte
1. Allez sur https://railway.app
2. Cliquez "Sign up"
3. Connectez-vous avec GitHub (recommandé)

### 2.2 Vérifications
- ✅ Compte vérifié
- ✅ Connecté à GitHub

## ÉTAPE 3 : PUSH VERS GITHUB

### 3.1 Créez un repo GitHub
```bash
# Dans le dossier /app/
git init
git add .
git commit -m "Initial commit Claire et Marcus"
```

### 3.2 Push sur GitHub
1. Créez un repo sur github.com : "claire-marcus-backend"
2. Ajoutez le remote :
```bash
git remote add origin https://github.com/VOTRE-USERNAME/claire-marcus-backend.git
git branch -M main
git push -u origin main
```

## ÉTAPE 4 : DÉPLOIEMENT SUR RAILWAY

### 4.1 Nouveau projet
1. Sur Railway Dashboard : cliquez **"New Project"**
2. Sélectionnez **"Deploy from GitHub repo"**
3. Choisissez votre repo `claire-marcus-backend`
4. Cliquez **"Deploy Now"**

### 4.2 Configuration automatique
Railway détecte automatiquement :
- Python
- FastAPI
- requirements.txt
- Port dynamique

## ÉTAPE 5 : VARIABLES D'ENVIRONNEMENT

### 5.1 Dans Railway Dashboard
1. Allez dans votre projet
2. Onglet **"Variables"**
3. Ajoutez ces variables :

```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/claire_marcus
OPENAI_API_KEY=sk-proj-votre-clé-openai
STRIPE_API_KEY=sk_test_votre-clé-stripe
LINKEDIN_CLIENT_ID=votre-id-linkedin
LINKEDIN_CLIENT_SECRET=votre-secret-linkedin
FACEBOOK_APP_ID=votre-id-facebook
FACEBOOK_APP_SECRET=votre-secret-facebook
JWT_SECRET_KEY=votre-clé-jwt-ultra-secrète
DB_NAME=claire_marcus
```

### 5.2 Variables importantes
- `PORT` : Automatique (Railway gère)
- `DATABASE_URL` : Utilisez MongoDB Atlas
- Toutes les clés API de vos intégrations

## ÉTAPE 6 : MONGODB ATLAS

### 6.1 Créez un cluster MongoDB
1. Allez sur https://cloud.mongodb.com
2. Créez un compte gratuit
3. Créez un cluster (M0 gratuit)
4. Configurez :
   - Username/Password
   - IP Access List : `0.0.0.0/0` (toutes IPs)

### 6.2 Connection String
Format : `mongodb+srv://username:password@cluster.mongodb.net/claire_marcus`

## ÉTAPE 7 : CONFIGURATION DOMAINE

### 7.1 URL Railway
Votre backend sera accessible sur :
`https://votre-app-name.up.railway.app`

### 7.2 Domaine personnalisé (Optionnel)
1. Dans Railway : onglet **"Settings"**
2. Section **"Domains"**
3. **"Custom Domain"** : `api.claire-marcus.com`

### 7.3 Configuration OVH pour API
Si vous voulez `api.claire-marcus.com` :
```
Type: CNAME
Nom: api
Cible: votre-app.up.railway.app
```

## ÉTAPE 8 : TESTS & VÉRIFICATION

### 8.1 Tests de base
Vérifiez ces URLs :
- `https://votre-app.railway.app/` (Hello World)
- `https://votre-app.railway.app/api/health` (Santé API)
- `https://votre-app.railway.app/api/auth/register` (Endpoints)

### 8.2 Tests d'intégration
- ✅ MongoDB connecté
- ✅ API OpenAI fonctionne
- ✅ Authentification OK

## ÉTAPE 9 : LOGS & MONITORING

### 9.1 Voir les logs
1. Railway Dashboard → votre projet
2. Onglet **"Deployments"**
3. Cliquez sur le deployment actuel
4. Voir les **logs en temps réel**

### 9.2 Debugging courant
```bash
# Erreurs communes dans les logs :
- "Module not found" → Vérifiez requirements.txt
- "Port already in use" → Railway gère automatiquement
- "Database connection failed" → Vérifiez MONGO_URL
```

## ÉTAPE 10 : MISE À JOUR

### 10.1 Déploiement continu
Chaque push sur GitHub redéploie automatiquement :
```bash
git add .
git commit -m "Mise à jour"
git push
```

### 10.2 Rollback
Dans Railway Dashboard :
1. Onglet **"Deployments"**
2. Sélectionnez un deployment précédent
3. **"Redeploy"**

## 🎯 RÉSULTAT FINAL

Votre backend sera accessible sur :
**https://votre-app-name.up.railway.app**

Cette URL sera votre `REACT_APP_BACKEND_URL` pour Netlify !

## 🚨 CHECKLIST AVANT DE CONTINUER

- [ ] Backend déployé sur Railway
- [ ] MongoDB Atlas configuré
- [ ] Variables d'environnement ajoutées
- [ ] API testée et fonctionnelle
- [ ] URL Railway notée pour Netlify

**Une fois fait, vous pourrez configurer `REACT_APP_BACKEND_URL` dans Netlify !**