# 🔧 Plan de Restauration - Claire et Marcus

## Phase 1: Résolution Immédiate (Urgente) 🚨

### Problème: Écran blanc lors de la création de compte
- **Status**: ❌ Le site https://clairemarcus.netlify.app retourne 404
- **Cause**: Variable d'environnement incorrecte sur Netlify

### Solution Immédiate:
1. **Configurer Netlify** (à faire par l'utilisateur):
   - Dashboard Netlify → Site settings → Environment variables
   - Ajouter: `REACT_APP_BACKEND_URL = https://claire-marcus-api.onrender.com`
   - Redéployer le site

2. **Vérification Backend**:
   - ✅ Backend Render.com fonctionne: https://claire-marcus-api.onrender.com
   - ✅ Endpoints d'auth disponibles (mode démo)
   - ✅ Toutes les routes principales actives

## Phase 2: Restauration Backend Complète 🔄

### 2.1 Configuration Base de Données
- **Problème**: Backend utilise MongoDB local (inaccessible depuis Render)
- **Solution**: Configurer MongoDB Atlas ou Railway Postgres
- **Impact**: Authentification réelle, sauvegarde des données

### 2.2 Restauration des Modules Principaux
```
Priority 1: Auth.py (authentification JWT)
Priority 2: Website_analyzer.py (analyse de site)
Priority 3: Analytics.py (analyses de performance) 
Priority 4: Social_media.py (intégrations réseaux)
Priority 5: Payments.py (paiements Stripe)
```

### 2.3 Variables d'Environnement Render
À configurer sur Render.com :
```
MONGO_URL=<URL_MongoDB_Atlas>
OPENAI_API_KEY=sk-proj-5yB5Gizh6fOpqVmx1UXQ...
STRIPE_API_KEY=<Votre_clé_Stripe>
JWT_SECRET_KEY=<Clé_sécurisée>
FACEBOOK_APP_ID=1098326618299035
FACEBOOK_APP_SECRET=c53e50103b69083e974fe25996d339ea
```

## Phase 3: Intégrations Tierces 🔌

### 3.1 Paiements Complets
- Stripe: ✅ Partiellement configuré
- Apple Pay: ❌ À implémenter
- Google Pay: ❌ À implémenter
- PayPal: ❌ À implémenter

### 3.2 Réseaux Sociaux
- Facebook/Instagram: ✅ Configuré
- LinkedIn: ⚠️ Clés à fournir
- Autres plateformes: ❌ À définir

### 3.3 IA/Génération
- OpenAI GPT: ✅ Clé disponible
- Analyse de sites: ✅ Code prêt
- Génération optimisée: ✅ Algorithmes prêts

## Phase 4: Tests et Optimisation 🧪

### 4.1 Tests End-to-End
- Workflow complet utilisateur
- Intégrations API
- Performance et stabilité

### 4.2 Surveillance
- Monitoring Render.com
- Logs d'erreur
- Métriques d'utilisation

## Timeline Proposé ⏱️

**Immédiat (0-1h)**:
- Fix Netlify + redéploiement
- Vérification fonctionnement de base

**Court terme (1-3 jours)**:
- Configuration MongoDB
- Restauration auth.py + modules essentiels
- Tests complets

**Moyen terme (1 semaine)**:
- Intégrations paiements complètes
- Toutes les fonctionnalités SaaS
- Interface admin

---

**Prochaine étape**: Une fois Netlify fixé, confirmer le bon fonctionnement du site, puis procéder à la restauration MongoDB et des modules backend.