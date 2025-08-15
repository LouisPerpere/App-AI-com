// Test de connexion simplifié - à coller dans la console navigateur (F12)

console.log('🧪 Test de login simplifié');

// Test 1: Vérifier si le backend est accessible
fetch('http://localhost:8001/api/diag')
  .then(r => r.json())
  .then(data => {
    console.log('✅ Backend accessible:', data);
    
    // Test 2: Tenter login
    return fetch('http://localhost:8001/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'lperpere@yahoo.fr',
        password: 'L@Reunion974!'
      })
    });
  })
  .then(r => r.json())
  .then(data => {
    console.log('✅ Login response:', data);
    
    if (data.access_token) {
      console.log('✅ Token obtenu:', data.access_token.substring(0, 20) + '...');
      
      // Test 3: Utiliser le token pour récupérer le profil
      return fetch('http://localhost:8001/api/business-profile', {
        headers: { 'Authorization': `Bearer ${data.access_token}` }
      });
    } else {
      throw new Error('Pas de token dans la réponse');
    }
  })
  .then(r => r.json())
  .then(profile => {
    console.log('✅ Profil business récupéré:', profile);
    console.log('🎉 TOUT FONCTIONNE - Le problème est ailleurs');
  })
  .catch(error => {
    console.log('❌ Erreur détectée:', error);
  });