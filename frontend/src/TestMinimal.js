import React from 'react';

function TestMinimal() {
  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#f0f0f0',
      minHeight: '100vh',
      fontSize: '18px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>🎉 TEST MINIMAL</h1>
      <p style={{ color: '#666' }}>Si vous voyez ce message, React fonctionne !</p>
      <div style={{
        backgroundColor: '#4CAF50',
        color: 'white',
        padding: '10px',
        borderRadius: '5px',
        marginTop: '20px'
      }}>
        ✅ React 18 est opérationnel
      </div>
      <div style={{
        backgroundColor: '#2196F3',
        color: 'white',
        padding: '10px',
        borderRadius: '5px',
        marginTop: '10px'
      }}>
        📱 Test iPhone - Version Minimale
      </div>
    </div>
  );
}

export default TestMinimal;