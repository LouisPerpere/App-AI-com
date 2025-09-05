// Script de test pour diagnostiquer le problème d'upload
// Exécuter dans la console du navigateur

function testUploadRefs() {
  console.log('🔍 DIAGNOSTIC UPLOAD REFS:');
  
  // Vérifier si les refs existent
  const refs = window.uploadTitleRefs || {};
  console.log('uploadTitleRefs:', refs);
  
  // Tester les valeurs actuelles
  Object.keys(refs).forEach(index => {
    const ref = refs[index];
    const value = ref?.current?.value || '';
    console.log(`Ref[${index}]:`, { ref, value, element: ref?.current });
  });
  
  // Vérifier les éléments DOM directement
  const titleInputs = document.querySelectorAll('input[placeholder="Facultatif"]');
  console.log('Title inputs found:', titleInputs.length);
  
  titleInputs.forEach((input, i) => {
    console.log(`Input ${i}:`, { value: input.value, placeholder: input.placeholder });
  });
}

// Tester après upload
function testAfterUpload() {
  console.log('🔄 Testing refs after upload...');
  testUploadRefs();
}

console.log('✅ Test functions loaded. Use testUploadRefs() and testAfterUpload()');