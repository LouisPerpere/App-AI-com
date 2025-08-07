import React, { useState } from 'react';
import axios from 'axios';

const TestAuth = () => {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://claire-marcus-api.onrender.com';
  const API = `${BACKEND_URL}/api`;

  console.log('🔧 TEST AUTH - BACKEND_URL:', BACKEND_URL);
  console.log('🔧 TEST AUTH - API:', API);

  const testConnection = async () => {
    setLoading(true);
    setResult('Testing...');

    try {
      // Test health endpoint first
      const healthResponse = await axios.get(`${API}/health`);
      console.log('✅ Health check success:', healthResponse.data);

      // Test registration
      const registerResponse = await axios.post(`${API}/auth/register`, {
        email: 'test.debug@claire-marcus.com',
        password: 'TestDebug123!',
        business_name: 'Debug Test Business'
      });
      console.log('✅ Registration success:', registerResponse.data);

      setResult(`✅ SUCCESS!\n\nHealth: ${JSON.stringify(healthResponse.data, null, 2)}\n\nRegister: ${JSON.stringify(registerResponse.data, null, 2)}`);

    } catch (error) {
      console.error('❌ Test error:', error);
      setResult(`❌ ERROR:\n\n${error.message}\n\nResponse: ${error.response?.data ? JSON.stringify(error.response.data, null, 2) : 'No response data'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>🔧 DEBUG: Test API Connection</h2>
      <p><strong>Backend URL:</strong> {BACKEND_URL}</p>
      <p><strong>API URL:</strong> {API}</p>
      
      <button 
        onClick={testConnection}
        disabled={loading}
        style={{ 
          padding: '10px 20px', 
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: loading ? 'not-allowed' : 'pointer',
          margin: '20px 0'
        }}
      >
        {loading ? 'Testing...' : 'Test API Connection'}
      </button>

      <pre style={{ 
        backgroundColor: '#f8f9fa', 
        padding: '15px', 
        borderRadius: '5px',
        whiteSpace: 'pre-wrap',
        fontSize: '12px',
        maxHeight: '400px',
        overflow: 'auto'
      }}>
        {result || 'Click button to test API connection...'}
      </pre>
    </div>
  );
};

export default TestAuth;