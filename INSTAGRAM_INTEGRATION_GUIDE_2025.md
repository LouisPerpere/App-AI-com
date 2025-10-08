# Guide d'Intégration Instagram 2025 - Claire & Marcus

## 🎯 Problème Résolu

L'URL d'autorisation Facebook/Instagram générait une erreur car nous utilisions l'ancienne API Instagram Basic Display qui a été dépréciée en décembre 2024. La solution consiste à migrer vers l'**Instagram Graph API 2025** avec les nouveaux paramètres et scopes.

## ✅ Corrections Appliquées

### 1. Migration vers Instagram Graph API 2025
- **Ancien endpoint**: `https://www.facebook.com/v23.0/dialog/oauth`
- **Nouveau endpoint**: `https://api.instagram.com/oauth/authorize`

### 2. Nouveaux Scopes (Obligatoires depuis décembre 2024)
- **Anciens scopes (dépréciés)**: `instagram_basic`, `instagram_content_publish`
- **Nouveaux scopes**: 
  - `instagram_business_basic`
  - `instagram_business_content_publishing`
  - `instagram_business_manage_comments`
  - `instagram_business_manage_messages`

### 3. Paramètres OAuth Corrigés
- **response_type**: `code` (au lieu de `token`)
- **URL de redirection mise à jour**: `https://post-restore.preview.emergentagent.com/api/social/instagram/callback`

## 🔗 Nouvelle URL d'Autorisation Générée

L'API génère maintenant cette URL correcte :

```
https://api.instagram.com/oauth/authorize?client_id=1115451684022643&redirect_uri=https%3A%2F%2Finsta-automate-3.preview.emergentagent.com%2Fapi%2Fsocial%2Finstagram%2Fcallback&scope=instagram_business_basic%2Cinstagram_business_content_publishing%2Cinstagram_business_manage_comments%2Cinstagram_business_manage_messages&response_type=code&state=RANDOM_STATE
```

## 📋 Configuration Facebook Developer Requise

Pour que cette URL fonctionne, vous devez configurer votre application Facebook Developer :

### Étape 1: Accéder à Facebook Developer
1. Aller sur [developers.facebook.com](https://developers.facebook.com)
2. Sélectionner votre application "Claire & Marcus" (ID: 1115451684022643)

### Étape 2: Configurer Instagram Graph API
1. Dans le menu latéral, cliquer sur "Produits"
2. Ajouter le produit "Instagram Graph API" si pas déjà fait
3. Aller dans les paramètres Instagram Graph API

### Étape 3: Configurer les URI de Redirection
1. Dans "Instagram Graph API" > "Paramètres"
2. Ajouter cette URI de redirection **EXACTEMENT** :
   ```
   https://post-restore.preview.emergentagent.com/api/social/instagram/callback
   ```

### Étape 4: Vérifier les Permissions
1. S'assurer que les permissions suivantes sont activées :
   - `instagram_business_basic`
   - `instagram_business_content_publishing`
   - `instagram_business_manage_comments`

## 🧪 Test de l'Intégration

### Endpoint de Test Disponible
```bash
curl "https://post-restore.preview.emergentagent.com/api/social/instagram/test-auth"
```

### Test Manuel
1. Utiliser l'URL générée par l'API
2. L'autoriser dans Facebook/Instagram
3. Vérifier que le callback fonctionne

## 🔧 Diagnostic en Cas de Problème

### Erreurs Communes et Solutions

1. **"Invalid redirect URI"**
   - Vérifier que l'URI de redirection est configurée EXACTEMENT dans Facebook Developer
   - L'URI doit correspondre caractère par caractère

2. **"Invalid scope"**
   - S'assurer d'utiliser les nouveaux scopes 2025
   - Vérifier que l'app Facebook a les permissions Instagram Graph API

3. **"App not configured for Instagram"**
   - Ajouter le produit Instagram Graph API dans Facebook Developer
   - Associer votre compte Instagram Business à une page Facebook

## 📞 Instructions pour l'Utilisateur

1. **Configurer Facebook Developer** avec les URI de redirection ci-dessus
2. **Tester la nouvelle URL** d'autorisation générée par l'API
3. **Vérifier** que votre compte Instagram est bien un compte Business lié à une page Facebook

## 🚀 Prochaines Étapes

Une fois l'autorisation fonctionnelle :
1. Implémenter le bouton "Valider" pour publication automatique
2. Ajouter le système de planification
3. Créer le tableau de bord d'analytiques

---

**Note**: Cette migration était nécessaire suite à la dépréciation de l'Instagram Basic Display API en décembre 2024. Tous les développeurs doivent maintenant utiliser Instagram Graph API 2025.