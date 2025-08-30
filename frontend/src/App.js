import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import axios from 'axios';
import AuthPage from './Auth';
import TestAuth from './TestAuth';
import PaymentPage from './PaymentPage';
import AdminDashboard from './AdminDashboard';
import FacebookCallback from './FacebookCallback';

// Configure axios for cross-site authentication (ChatGPT fix)
// Do not use cookies for cross-site requests; rely on Authorization header
axios.defaults.withCredentials = false;

// Import UI components
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { Alert, AlertDescription } from './components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Label } from './components/ui/label';

// Import icons
import { Building, Sparkles, Crown, Upload, ImageIcon, FileText, X, Edit, CalendarIcon, Target, LogOut, Check, Send, Clock, ChevronLeft, ChevronRight, CreditCard, Settings, Globe, Save, Search, Users, Cog, Trash } from 'lucide-react';

// Import toast for notifications
import { toast } from 'react-hot-toast';

// Use ONLY process.env for Netlify/CRA compatibility (avoid import.meta)
// Normalize backend URL (trim, remove trailing slashes and any trailing /api)
const getBackendURL = () => {
  let envURL = process.env.REACT_APP_BACKEND_URL;
  if (!envURL || envURL === 'undefined') return '';
  // Remove surrounding quotes if mistakenly added in Netlify env
  envURL = envURL.trim().replace(/^['"]|['"]$/g, '');
  envURL = envURL.replace(/\/+$/, '');
  envURL = envURL.replace(/\/api$/, '');
  return envURL;
};
const BACKEND_URL = getBackendURL();
const API = `${BACKEND_URL}/api`;
console.log('🔧 APP DEBUG - BACKEND_URL:', BACKEND_URL);
console.log('🔧 APP DEBUG - API:', API);

// Récupérer le token depuis localStorage, avec fallback pour Safari navigation privée
const getAccessToken = () => {
  try {
    const raw = localStorage.getItem('access_token');
    if (raw) return raw;
  } catch (e) {
    console.warn('⚠️ localStorage inaccessible, utilisation du token mémoire');
  }
  return window.__ACCESS_TOKEN || null;
};

// Helper to build API thumbnail URL
const buildThumbUrl = (id) => `${API}/content/${id}/thumb?token=${getAccessToken() || ''}`;

// Subscription plans data
const SUBSCRIPTION_PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    monthlyPrice: 14.99,
    yearlyPrice: 149.99,
    features: ['4 posts par mois', '1 réseau social', 'Programmation automatique', 'Support par email'],
    color: 'blue',
    popular: false,
    badge: null
  },
  {
    id: 'rocket',
    name: 'Rocket',
    monthlyPrice: 29.99,
    yearlyPrice: 299.99,
    features: ['Posts illimités', 'Tous les réseaux sociaux', 'Analytics avancés', 'Support prioritaire', 'Calendrier de contenu'],
    color: 'purple',
    popular: true,
    badge: 'Plus populaire'
  },
  {
    id: 'pro',
    name: 'Pro',
    monthlyPrice: 199.99,
    yearlyPrice: 1999.99,
    features: ['Posts illimités', 'Tous les réseaux sociaux', 'Gestion multi-comptes', 'Support dédié', 'Analytics complets', 'Community management'],
    color: 'gold',
    popular: false,
    badge: 'Community Managers'
  }
];

// Free trial plan (shown separately)
const FREE_TRIAL_PLAN = {
  name: 'Essai Gratuit',
  duration: '1 mois offert',
  features: ['Posts illimités', '1 réseau social', 'Découverte complète', 'Support par email'],
  color: 'green'
};

// Optimized Content Thumbnail Component (prevents unnecessary re-renders)
const ContentThumbnail = React.memo(({ 
  content, 
  isSelectionMode, 
  isSelected, 
  onContentClick, 
  onToggleSelection 
}) => {
  const handleClick = useCallback(() => {
    if (isSelectionMode) {
      onToggleSelection(content.id);
    } else {
      onContentClick(content);
    }
  }, [isSelectionMode, content, onContentClick, onToggleSelection]);

  return (
    <div 
      className={`relative group transform hover:scale-105 transition-all duration-200 ${
        isSelectionMode ? 'cursor-pointer' : 'cursor-pointer'
      }`}
      onClick={handleClick}
    >
      <div className={`aspect-square bg-gray-100 rounded-xl overflow-hidden border-2 transition-colors shadow-md hover:shadow-lg ${
        isSelectionMode && isSelected
          ? 'border-purple-500 ring-2 ring-purple-200'
          : 'border-purple-200 hover:border-purple-400'
      }`}>
        {content.file_type?.startsWith('image/') ? (
          <img 
            src={`${API}/content/${content.id}/thumb`}
            alt={content.filename}
            className="w-full h-full object-cover"
            loading="lazy"
            onError={(e) => {
              // Fallback hierarchy: thumb_url -> url
              if (content.url && e.currentTarget.src !== content.url) {
                e.currentTarget.src = content.url;
              }
            }}
          />
        ) : content.file_type?.startsWith('video/') ? (
          <div className="relative w-full h-full">
            {
              // Always request via API; if 404, fallback to icon
              true ? (
              <img 
                src={`${API}/content/${content.id}/thumb`}
                alt={content.filename}
                className="w-full h-full object-cover"
                loading="lazy"
                onError={(e) => {
                  // Fallback to video icon if thumbnail fails
                  e.currentTarget.style.display = 'none';
                  e.currentTarget.parentElement.querySelector('.video-icon').style.display = 'flex';
                }}
              />
            ) : (
              <div className="video-icon w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-indigo-100">
                <div className="text-center">
                  <FileText className="w-8 h-8 text-blue-600 mx-auto mb-1" />
                  <span className="text-xs text-blue-800">VIDEO</span>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100">
            <FileText className="w-6 h-6 text-purple-600" />
          </div>
        )}
        
        {/* Selection checkbox */}
        {isSelectionMode && (
          <div className="absolute top-2 left-2">
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
              isSelected
                ? 'bg-purple-500 border-purple-500'
                : 'bg-white border-gray-300'
            }`}>
              {isSelected && (
                <Check className="w-3 h-3 text-white" />
              )}
            </div>
          </div>
        )}
      </div>
      
      <p className="text-xs text-gray-600 mt-1 truncate text-center">{content.filename}</p>
      {Boolean(content.description?.trim()) && !isSelectionMode && (
        <Badge className="absolute top-1 right-1 bg-green-100 text-green-800 text-xs px-1 py-0">
          💬
        </Badge>
      )}
    </div>
  );
});

function MainApp() {
  // Simple implementation with FORCE DASHBOARD approach
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeStep, setActiveStep] = useState('dashboard'); // FORCE DASHBOARD DIRECTLY
  
  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
      // Simple user mock for now
      setUser({ name: 'User' });
      setActiveStep('dashboard'); // FORCE DASHBOARD
    }
  }, []);

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
    setUser({ name: 'User' });
    setActiveStep('dashboard'); // FORCE DASHBOARD IMMEDIATELY
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
    setUser(null);
    setActiveStep('onboarding');
  };

  // Show auth page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  // Simple dashboard placeholder
  return (
    <div className="min-h-screen bg-pattern">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Claire et Marcus Dashboard</h1>
          <button 
            onClick={handleLogout}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            Se déconnecter
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-2">Entreprise</h3>
            <p className="text-gray-600">Gérez votre profil d'entreprise</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-2">Bibliothèque</h3>
            <p className="text-gray-600">Vos contenus uploadés</p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-2">Notes</h3>
            <p className="text-gray-600">Vos notes et informations</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/auth/facebook/callback" element={<FacebookCallback />} />
        <Route path="/*" element={<MainApp />} />
      </Routes>
    </Router>
  );
}

export default App;