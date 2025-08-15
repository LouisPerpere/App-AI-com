// Solution: Clear localStorage and force clean reload
console.log('🧹 CLEANING FRONTEND CACHE AND LOCALSTORAGE');

// Clear all localStorage related to business profile
const keysToRemove = [
  'claire_marcus_business_profile_cache',
  'business_name',
  'business_description', 
  'target_audience',
  'email',
  'website_url',
  'budget_range',
  'business_type',
  'access_token',
  'user_data'
];

keysToRemove.forEach(key => {
  localStorage.removeItem(key);
  console.log(`🗑️ Removed ${key}`);
});

// Clear any cached business profile data
localStorage.removeItem('businessProfile');
localStorage.removeItem('editBusinessName');
localStorage.removeItem('editBusinessDescription');

console.log('✅ LocalStorage cleaned');
console.log('🔄 Please refresh the page (F5) and login again to test clean state');

// You can copy/paste this in the browser console to clean everything