import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Enhanced debug component to troubleshoot authentication issues
const DebugAuth = () => {
  const [debugInfo, setDebugInfo] = useState({});
  const [testResult, setTestResult] = useState('');
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const envURL = process.env.REACT_APP_BACKEND_URL;
    const BACKEND_URL = (envURL && envURL.trim() && envURL !== 'undefined') ? envURL : 'https://claire-marcus-api.onrender.com';
    const API = `${BACKEND_URL}/api`;

    setDebugInfo({
      REACT_APP_BACKEND_URL_RAW: envURL,
      BACKEND_URL_FINAL: BACKEND_URL,
      API_URL: API,
      NODE_ENV: process.env.NODE_ENV,
      IS_ENV_UNDEFINED: envURL === 'undefined',
      IS_ENV_EMPTY: !envURL || envURL.trim() === '',
      ALL_REACT_APP_VARS: Object.keys(process.env).filter(key => key.startsWith('REACT_APP_')),
      USING_FALLBACK: !envURL || envURL.trim() === '' || envURL === 'undefined'
    });
  }, []);

  const testBackendHealth = async () => {
    try {
      setTestResult('🔍 Testing backend health...');
      const envURL = process.env.REACT_APP_BACKEND_URL;
      const BACKEND_URL = (envURL && envURL.trim() && envURL !== 'undefined') ? envURL : 'https://claire-marcus-api.onrender.com';
      const API = `${BACKEND_URL}/api`;
      
      console.log('🔍 Testing backend at:', API);
      
      // Test with a simple login attempt (expect 401 or 422)
      const response = await axios.post(`${API}/auth/login`, {
        email: 'health@check.test',
        password: 'healthcheck'
      }, { 
        timeout: 15000,
        validateStatus: () => true // Accept all status codes
      });
      
      if (response.status === 200 || response.status === 401 || response.status === 422) {
        setTestResult(`✅ Backend HEALTHY: Status ${response.status} - API is responding correctly`);
      } else {
        setTestResult(`⚠️ Backend responds but with unexpected status: ${response.status}`);
      }
    } catch (error) {
      if (error.response) {
        if (error.response.status === 401 || error.response.status === 422) {
          setTestResult(`✅ Backend HEALTHY: Expected error ${error.response.status} - API is working`);
        } else {
          setTestResult(`⚠️ Backend error: ${error.response.status} - ${error.response.data?.detail || 'Unknown error'}`);
        }
      } else if (error.request) {
        setTestResult(`❌ Backend UNREACHABLE: ${error.message} - Check network connection`);
      } else {
        setTestResult(`❌ Request error: ${error.message}`);
      }
    }
  };

  const testFullRegistration = async () => {
    try {
      setTestResult('🔍 Testing full registration flow...');
      const envURL = process.env.REACT_APP_BACKEND_URL;
      const BACKEND_URL = (envURL && envURL.trim() && envURL !== 'undefined') ? envURL : 'https://claire-marcus-api.onrender.com';
      const API = `${BACKEND_URL}/api`;
      
      const timestamp = Date.now();
      const testEmail = `debug.${timestamp}@test.com`;
      
      // Step 1: Registration
      const regResponse = await axios.post(`${API}/auth/register`, {
        email: testEmail,
        password: 'DebugTest123!',
        business_name: 'Debug Test Business'
      }, { timeout: 15000 });
      
      console.log('Registration response:', regResponse.data);
      
      // Step 2: Auto-login
      const loginResponse = await axios.post(`${API}/auth/login`, {
        email: testEmail,
        password: 'DebugTest123!'
      }, { timeout: 15000 });
      
      console.log('Login response:', loginResponse.data);
      
      const accessToken = loginResponse.data.access_token || loginResponse.data.token;
      
      if (accessToken) {
        setTestResult(`🎉 FULL FLOW SUCCESS: Registration + Login working! Token received: ${accessToken.substring(0, 20)}...`);
      } else {
        setTestResult(`⚠️ Registration OK but no token received in login response`);
      }
    } catch (error) {
      if (error.response) {
        setTestResult(`❌ Registration failed: ${error.response.status} - ${error.response.data?.detail || 'Unknown error'}`);
      } else if (error.request) {
        setTestResult(`❌ Network error during registration: ${error.message}`);
      } else {
        setTestResult(`❌ Registration error: ${error.message}`);
      }
    }
  };

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          background: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '50%',
          width: '40px',
          height: '40px',
          cursor: 'pointer',
          fontSize: '16px',
          zIndex: 9999
        }}
        title="Show Debug Panel"
      >
        🔍
      </button>
    );
  }

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'white', 
      border: '2px solid #ccc', 
      padding: '15px',
      maxWidth: '450px',
      fontSize: '12px',
      zIndex: 9999,
      borderRadius: '8px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      maxHeight: '80vh',
      overflowY: 'auto'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h3 style={{ margin: '0', color: '#333' }}>🔍 Auth Debug Panel</h3>
        <button
          onClick={() => setIsVisible(false)}
          style={{ background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer' }}
          title="Hide Panel"
        >
          ✕
        </button>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>Environment Analysis:</strong>
        <pre style={{ 
          fontSize: '10px', 
          background: debugInfo.USING_FALLBACK ? '#ffe6e6' : '#e6ffe6', 
          padding: '8px', 
          margin: '5px 0',
          borderRadius: '4px',
          border: debugInfo.USING_FALLBACK ? '1px solid #ff9999' : '1px solid #99ff99'
        }}>
          {JSON.stringify(debugInfo, null, 2)}
        </pre>
        {debugInfo.USING_FALLBACK && (
          <div style={{ 
            background: '#fff3cd', 
            border: '1px solid #ffeaa7',
            padding: '8px',
            borderRadius: '4px',
            fontSize: '11px',
            marginTop: '5px'
          }}>
            ⚠️ <strong>PROBLEM DETECTED:</strong> Using fallback URL. Please set REACT_APP_BACKEND_URL in Netlify environment variables.
          </div>
        )}
      </div>

      <div style={{ marginBottom: '10px' }}>
        <button 
          onClick={testBackendHealth}
          style={{ 
            margin: '5px', 
            padding: '8px 12px', 
            background: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
        >
          🏥 Test Backend Health
        </button>
        
        <button 
          onClick={testFullRegistration}
          style={{ 
            margin: '5px', 
            padding: '8px 12px', 
            background: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px'
          }}
        >
          🚀 Test Full Flow
        </button>
      </div>

      {testResult && (
        <div style={{ 
          background: testResult.includes('❌') ? '#ffe6e6' : 
                     testResult.includes('⚠️') ? '#fff3cd' : '#e6ffe6',
          padding: '8px',
          borderRadius: '4px',
          fontSize: '11px',
          marginTop: '10px',
          border: testResult.includes('❌') ? '1px solid #ff9999' : 
                  testResult.includes('⚠️') ? '1px solid #ffeaa7' : '1px solid #99ff99'
        }}>
          <strong>Test Result:</strong><br />
          {testResult}
        </div>
      )}
    </div>
  );
};

export default DebugAuth;