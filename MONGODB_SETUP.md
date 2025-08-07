# 🗄️ Configuration MongoDB pour Claire et Marcus

## Options de Base de Données

### Option 1: MongoDB Atlas (Recommandée pour Production)

**Avantages:** Gratuit jusqu'à 512MB, géré, sécurisé, accessible depuis Render.com

**Étapes:**
1. **Créer un compte** sur https://www.mongodb.com/cloud/atlas/register
2. **Créer un cluster gratuit** (M0 Sandbox)
3. **Configurer la sécurité:**
   - Créer un utilisateur de base de données
   - Autoriser l'accès depuis toutes les IPs (`0.0.0.0/0`)
4. **Obtenir l'URL de connexion** format : 
   ```
   mongodb+srv://username:password@cluster.xxxxx.mongodb.net/claire_marcus?retryWrites=true&w=majority
   ```

### Option 2: Railway PostgreSQL (Alternative)

**Avantages:** Intégration facile avec notre stack, support pour plusieurs types de bases

**Étapes:**
1. Créer compte sur https://railway.app
2. Créer nouveau projet → Add PostgreSQL
3. Obtenir l'URL de connexion

### Option 3: Local MongoDB (Développement uniquement)

Pour les tests locaux seulement, pas pour la production.

## Configuration Recommandée : MongoDB Atlas

### Étape 1: Créer le Cluster
1. Aller sur https://cloud.mongodb.com
2. Créer un compte gratuit
3. Créer un cluster M0 (gratuit)
4. Choisir la région la plus proche de votre backend

### Étape 2: Configurer la Sécurité
1. **Database Access** → **Add New Database User**
   - Username: `claire-marcus-user`
   - Password: générer un mot de passe sécurisé
   - Role: `Read and write to any database`

2. **Network Access** → **Add IP Address**
   - IP Address: `0.0.0.0/0` (ou l'IP de Render si connue)
   - Comment: "Render.com access"

### Étape 3: Obtenir l'URL de Connexion
1. **Clusters** → **Connect** → **Connect your application**
2. Driver: **Python**
3. Version: **4.0 or later**
4. Copier l'URL de connexion

### Étape 4: Configuration sur Render.com
Variables d'environnement à ajouter :
```
MONGO_URL = mongodb+srv://username:password@cluster.xxxxx.mongodb.net/claire_marcus?retryWrites=true&w=majority
DB_NAME = claire_marcus
```

## Collections à Créer

```javascript
// users - Utilisateurs enregistrés
{
  "user_id": "uuid",
  "email": "string",
  "password_hash": "string",
  "first_name": "string",
  "last_name": "string",
  "business_name": "string",
  "subscription_status": "trial|active|expired",
  "trial_days_remaining": "number",
  "created_at": "datetime",
  "updated_at": "datetime"
}

// business_profiles - Profils d'entreprise
{
  "profile_id": "uuid",
  "user_id": "uuid",
  "business_name": "string",
  "business_type": "string",
  "target_audience": "string",
  "brand_tone": "string",
  "posting_frequency": "string",
  "preferred_platforms": ["array"],
  "hashtags_primary": ["array"],
  "hashtags_secondary": ["array"],
  "website_url": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}

// content_notes - Notes de contenu
{
  "note_id": "uuid",
  "user_id": "uuid",
  "business_id": "uuid",
  "content": "string",
  "description": "string",
  "priority": "high|normal|low",
  "created_at": "datetime"
}

// generated_posts - Posts générés
{
  "post_id": "uuid",
  "user_id": "uuid",
  "business_id": "uuid",
  "content": "string",
  "platform": "string",
  "status": "generated|approved|published",
  "hashtags": ["array"],
  "scheduled_for": "datetime",
  "created_at": "datetime"
}
```

## Test de Connexion

Une fois configuré, testez avec :
```python
from pymongo import MongoClient
import os

mongo_url = os.getenv("MONGO_URL")
client = MongoClient(mongo_url)
db = client[os.getenv("DB_NAME", "claire_marcus")]

# Test de connexion
try:
    client.admin.command('ismaster')
    print("✅ MongoDB connexion réussie")
except Exception as e:
    print(f"❌ Erreur MongoDB : {e}")
```

## Prochaine Étape

Une fois MongoDB configuré, nous pourrons :
1. Remplacer le mode démo par de vraies données
2. Implémenter l'authentification complète avec JWT
3. Ajouter la persistance des données utilisateur