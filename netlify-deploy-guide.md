# Guide de Déploiement Claire et Marcus sur Netlify

## 1. PRÉPARATION DU FRONTEND

### Build de production
```bash
cd /app/frontend
npm run build
# ou
yarn build
```

### Configuration du domaine dans .env
Créez un fichier `.env.production` dans /app/frontend/ :
```
REACT_APP_BACKEND_URL=https://api.claire-marcus.com
```

## 2. CONFIGURATION NETLIFY

### Structure des fichiers pour Netlify
Créez `netlify.toml` dans le dossier frontend :
```toml
[build]
  publish = "build"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

## 3. DÉPLOIEMENT SUR NETLIFY

### Option A : Drag & Drop (Simple)
1. Allez sur https://netlify.com
2. Connectez-vous ou créez un compte
3. Glissez-déposez le dossier `build` sur la zone de drop
4. Votre site sera accessible sur un sous-domaine netlify.app

### Option B : Git (Recommandé)
1. Pushé votre code sur GitHub/GitLab
2. Sur Netlify : "New site from Git"
3. Connectez votre repo
4. Configuration :
   - Branch: main
   - Build command: `npm run build`
   - Publish directory: `build`
   - Base directory: `frontend`

## 4. CONFIGURATION DOMAINE OVH → NETLIFY

### Dans Netlify Dashboard :
1. Allez dans "Domain settings"
2. Cliquez "Add custom domain"
3. Ajoutez : `claire-marcus.com` et `www.claire-marcus.com`
4. Netlify vous donnera des DNS records

### Dans OVH Manager :
1. Connectez-vous à votre espace client OVH
2. Allez dans "Noms de domaine" → `claire-marcus.com`
3. Onglet "Zone DNS"
4. Ajoutez les enregistrements DNS :

```
Type: CNAME
Nom: www
Cible: [votre-site].netlify.app

Type: A
Nom: @
Adresse IP: [IP fournie par Netlify]
```

### Alternative avec CNAME (Recommandé) :
```
Type: CNAME
Nom: @
Cible: [votre-site].netlify.app

Type: CNAME  
Nom: www
Cible: [votre-site].netlify.app
```

## 5. CERTIFICAT SSL (HTTPS)

Netlify active automatiquement Let's Encrypt SSL :
1. Dans Netlify Dashboard → "Domain settings"
2. Section "HTTPS" → "Verify DNS configuration"
3. Cliquez "Provision certificate"
4. Activez "Force HTTPS"

## 6. BACKEND - OPTIONS D'HÉBERGEMENT

⚠️ **IMPORTANT** : Netlify ne peut PAS héberger votre backend FastAPI. Vous avez plusieurs options :

### Option A : Heroku (Simple)
```bash
# Créez un Procfile dans /app/backend/
echo "web: uvicorn server:app --host=0.0.0.0 --port=\$PORT" > Procfile

# Déployez sur Heroku
heroku create claire-marcus-api
git subtree push --prefix=backend heroku main
```

### Option B : Railway (Recommandé)
1. Allez sur https://railway.app
2. "Deploy from GitHub"
3. Sélectionnez votre repo
4. Configurez le service FastAPI
5. Votre API sera sur : `https://[app-name].railway.app`

### Option C : DigitalOcean App Platform
1. Créez une app sur DigitalOcean
2. Connectez votre repo GitHub
3. Configurez le build : `pip install -r requirements.txt`
4. Start command : `uvicorn server:app --host=0.0.0.0 --port=8080`

## 7. VARIABLES D'ENVIRONNEMENT

### Frontend (Netlify)
Dans Netlify Dashboard → "Site settings" → "Environment variables" :
```
REACT_APP_BACKEND_URL=https://votre-api-url.com
NODE_ENV=production
```

### Backend (Heroku/Railway)
```
MONGO_URL=votre-url-mongodb-atlas
OPENAI_API_KEY=votre-clé-openai
STRIPE_API_KEY=votre-clé-stripe
LINKEDIN_CLIENT_ID=votre-id-linkedin
LINKEDIN_CLIENT_SECRET=votre-secret-linkedin
FACEBOOK_APP_ID=votre-id-facebook
FACEBOOK_APP_SECRET=votre-secret-facebook
```

## 8. BASE DE DONNÉES

### MongoDB Atlas (Recommandé)
1. Créez un cluster sur https://cloud.mongodb.com
2. Créez un utilisateur de base de données
3. Ajoutez votre IP à la whitelist (ou 0.0.0.0/0 pour production)
4. Récupérez la connection string
5. Remplacez MONGO_URL dans vos variables d'environnement

## 9. VÉRIFICATION FINALE

### Tests à effectuer :
- [ ] Frontend accessible sur claire-marcus.com
- [ ] HTTPS fonctionne (certificat SSL)
- [ ] API backend répond
- [ ] Authentification fonctionne
- [ ] Intégrations sociales actives
- [ ] Base de données connectée

## 10. MAINTENANCE

### Mises à jour automatiques :
- Frontend : Se déploie automatiquement à chaque push Git
- Backend : Dépend de la plateforme choisie
- Base de données : Sauvegardée automatiquement sur Atlas

### Monitoring :
- Netlify Analytics pour le frontend
- Logs du backend sur la plateforme choisie
- MongoDB Atlas monitoring