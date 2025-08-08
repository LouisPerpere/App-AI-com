import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Debug component to troubleshoot authentication issues
const DebugAuth = () => {
  const [debugInfo, setDebugInfo] = useState({});
  const [testResult, setTestResult] = useState('');

  useEffect(() => {
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://claire-marcus-api.onrender.com';
    const API = `${BACKEND_URL}/api`;

    setDebugInfo({
      REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL,
      BACKEND_URL: BACKEND_URL,
      API: API,
      NODE_ENV: process.env.NODE_ENV,
      ALL_ENV_VARS: Object.keys(process.env).filter(key => key.startsWith('REACT_APP_'))
    });
  }, []);

  const testBackendConnection = async () => {
    try {
      setTestResult('Testing backend connection...');
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://claire-marcus-api.onrender.com';
      const API = `${BACKEND_URL}/api`;
      
      // Test health endpoint if it exists, otherwise test auth/login with invalid data
      const response = await axios.post(`${API}/auth/login`, {
        email: 'test@test.com',
        password: 'invalid'
      }, { timeout: 10000 });
      
      setTestResult(`✅ Backend reachable: ${response.status}`);
    } catch (error) {
      if (error.response) {
        setTestResult(`✅ Backend reachable: ${error.response.status} - ${error.response.data?.detail || 'Expected error'}`);
      } else if (error.request) {
        setTestResult(`❌ Backend not reachable: ${error.message}`);
      } else {
        setTestResult(`❌ Request error: ${error.message}`);
      }
    }
  };

  const testRegistration = async () => {
    try {
      setTestResult('Testing registration endpoint...');
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://claire-marcus-api.onrender.com';
      const API = `${BACKEND_URL}/api`;
      
      const response = await axios.post(`${API}/auth/register`, {
        email: `debug.${Date.now()}@test.com`,
        password: 'DebugTest123!',
        business_name: 'Debug Test'
      }, { timeout: 10000 });
      
      setTestResult(`✅ Registration successful: ${response.status} - User created with token`);
    } catch (error) {
      if (error.response) {
        setTestResult(`⚠️ Registration response: ${error.response.status} - ${error.response.data?.detail || JSON.stringify(error.response.data)}`);
      } else if (error.request) {
        setTestResult(`❌ Registration failed: ${error.message}`);
      } else {
        setTestResult(`❌ Registration error: ${error.message}`);
      }
    }
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'white', 
      border: '2px solid #ccc', 
      padding: '15px',
      maxWidth: '400px',
      fontSize: '12px',
      zIndex: 9999,
      borderRadius: '8px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
    }}>
      <h3 style={{ margin: '0 0 10px 0', color: '#333' }}>🔍 Auth Debug Panel</h3>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>Environment Info:</strong>
        <pre style={{ fontSize: '10px', background: '#f5f5f5', padding: '5px', margin: '5px 0' }}>
          {JSON.stringify(debugInfo, null, 2)}
        </pre>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <button 
          onClick={testBackendConnection}
          style={{ 
            margin: '5px', 
            padding: '5px 10px', 
            background: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test Backend
        </button>
        
        <button 
          onClick={testRegistration}
          style={{ 
            margin: '5px', 
            padding: '5px 10px', 
            background: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test Registration
        </button>
      </div>

      {testResult && (
        <div style={{ 
          background: testResult.includes('❌') ? '#ffe6e6' : testResult.includes('✅') ? '#e6ffe6' : '#fff3cd',
          padding: '8px',
          borderRadius: '4px',
          fontSize: '11px',
          marginTop: '10px'
        }}>
          <strong>Test Result:</strong><br />
          {testResult}
        </div>
      )}
    </div>
  );
};

export default DebugAuth;