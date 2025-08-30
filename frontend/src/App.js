// Backend URL configuration
const getBackendURL = () => {
  let envURL = process.env.REACT_APP_BACKEND_URL || 'https://claire-marcus-api.onrender.com';
  envURL = envURL.trim().replace(/\/+$/, '');
  envURL = envURL.replace(/\/api$/, '');
  return envURL;
};

const BACKEND_URL = getBackendURL();
const API = `${BACKEND_URL}/api`;

// Token management
const getAccessToken = () => {
  try {
    return localStorage.getItem('access_token') || window.__ACCESS_TOKEN || '';
  } catch (error) {
    return window.__ACCESS_TOKEN || '';
  }
};

// Content URL builders
const buildThumbUrl = (id) => `${API}/content/${id}/thumb?token=${getAccessToken() || ''}`;
const buildOriginalUrl = (id) => `${API}/content/${id}/file?token=${getAccessToken() || ''}`;