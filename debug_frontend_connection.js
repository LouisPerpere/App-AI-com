console.log('🔍 DEBUGGING FRONTEND BACKEND CONNECTION');
console.log('Backend URL from env:', process.env.REACT_APP_BACKEND_URL);
console.log('Current API calls will go to:', process.env.REACT_APP_BACKEND_URL);

// Test simple pour vérifier la connexion
fetch(process.env.REACT_APP_BACKEND_URL + '/api/auth/me', {
  headers: { 'Authorization': 'Bearer invalid_token' }
})
.then(response => {
  console.log('✅ Backend response status:', response.status);
  console.log('✅ Backend accessible at:', process.env.REACT_APP_BACKEND_URL);
  return response.text();
})
.then(data => {
  console.log('Backend response:', data);
})
.catch(error => {
  console.log('❌ Backend connection error:', error);
});

// Affichez l'URL réelle utilisée
console.log('🎯 BACKEND URL UTILISÉ:', process.env.REACT_APP_BACKEND_URL);