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
axios.defaults.withCredentials = true;

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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://claire-marcus-api.onrender.com';
const API = `${BACKEND_URL}/api`;

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
            src={content.thumb_url || content.url}
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
            {content.thumb_url ? (
              <img 
                src={content.thumb_url}
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
  const location = useLocation();
  
  // State management
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeStep, setActiveStep] = useState('onboarding');
  const [businessProfile, setBusinessProfile] = useState(null);
  const [activeTab, setActiveTab] = useState('entreprise');
  const [pendingContent, setPendingContent] = useState([]);
  const [notes, setNotes] = useState([]);
  const [showPaymentPage, setShowPaymentPage] = useState(false);
  
  // Form states
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSavingBusinessInfo, setIsSavingBusinessInfo] = useState(false);
  const [isSavingMarketingInfo, setIsSavingMarketingInfo] = useState(false);

  // Configure axios defaults
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      setIsAuthenticated(false);
      return;
    }

    // Set axios header before making request
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

    try {
      const response = await axios.get(`${API}/auth/me`, {
        timeout: 15000,
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setUser(response.data);
      setIsAuthenticated(true);
      setActiveStep('dashboard');
      
      // Load business profile
      loadBusinessProfile();
      
    } catch (error) {
      console.error('Auth check failed:', error);
      
      // Only remove token if it's actually invalid
      if (error.response?.status === 401 || error.response?.status === 403) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
      }
      
      setIsAuthenticated(false);
    }
  };

  const handleAuthSuccess = async () => {
    setActiveStep('dashboard');
    await checkAuth();
  };

  const loadBusinessProfile = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    try {
      const response = await axios.get(`${API}/business-profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBusinessProfile(response.data);
      setActiveStep('dashboard');
    } catch (error) {
      console.log('Business profile fetch error:', error.response?.status);
      
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        setIsAuthenticated(false);
        setUser(null);
        setActiveStep('login');
      } else if (error.response?.status === 404) {
        setActiveStep('dashboard');
      } else {
        setActiveStep('dashboard');
      }
    }
  };

  const loadPendingContent = async () => {
    try {
      const response = await axios.get(`${API}/content/pending`, {
        params: { limit: 24 },
        headers: { 
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        }
      });
      
      const data = response.data;
      setPendingContent(data.content || []);
      
    } catch (error) {
      console.error('Error loading pending content:', error);
    }
  };

  const loadNotes = async () => {
    try {
      const response = await axios.get(`${API}/notes`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });  
      
      const notesData = response.data.notes || response.data || [];
      setNotes(notesData);
    } catch (error) {
      console.error('Error loading notes:', error);
      setNotes([]);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
    setBusinessProfile(null);
    setActiveStep('onboarding');
  };

  const handleSaveBusinessInfo = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    setIsSavingBusinessInfo(true);
    
    try {
      // Récupérer les valeurs des champs
      const businessName = document.getElementById('business_name_edit')?.value;
      const businessType = document.getElementById('business_type_edit')?.value;
      const businessDescription = document.getElementById('business_description_edit')?.value;
      const brandTone = document.getElementById('brand_tone_edit')?.value;
      
      // Récupérer la valeur du rythme de publications (select)
      const postingFrequency = document.getElementById('posting_frequency_edit')?.value;

      const updateData = {
        business_name: businessName,
        business_type: businessType,
        business_description: businessDescription,
        brand_tone: brandTone,
        posting_frequency: postingFrequency
      };

      const response = await axios.put(`${API}/business-profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        toast.success('Informations sauvegardées avec succès !');
        // Recharger le profil pour mettre à jour l'affichage
        await loadBusinessProfile();
      } else {
        toast.error('Erreur lors de la sauvegarde');
      }
    } catch (error) {
      console.error('Save business info error:', error);
      toast.error('Erreur lors de la sauvegarde des informations');
    } finally {
      setIsSavingBusinessInfo(false);
    }
  };

  const handleSaveMarketingInfo = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    setIsSavingMarketingInfo(true);
    
    try {
      // Récupérer les valeurs des champs marketing
      const email = document.getElementById('business_email_edit')?.value;
      const websiteUrl = document.getElementById('business_website_edit')?.value;
      const targetAudience = document.getElementById('target_audience_edit')?.value;

      const updateData = {
        email: email,
        website_url: websiteUrl,
        target_audience: targetAudience
      };

      const response = await axios.put(`${API}/business-profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        toast.success('Informations marketing sauvegardées avec succès !');
        // Recharger le profil pour mettre à jour l'affichage
        await loadBusinessProfile();
      } else {
        toast.error('Erreur lors de la sauvegarde');
      }
    } catch (error) {
      console.error('Save marketing info error:', error);
      toast.error('Erreur lors de la sauvegarde des informations marketing');
    } finally {
      setIsSavingMarketingInfo(false);
    }
  };

  // Auto-sauvegarde silencieuse (sans toast de confirmation)
  const handleAutoSave = async (fieldType = 'business') => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      let updateData = {};
      
      if (fieldType === 'business') {
        // Récupérer tous les champs business
        const businessName = document.getElementById('business_name_edit')?.value;
        const businessType = document.getElementById('business_type_edit')?.value;
        const businessDescription = document.getElementById('business_description_edit')?.value;
        const brandTone = document.getElementById('brand_tone_edit')?.value;
        const postingFrequency = document.getElementById('posting_frequency_edit')?.value;
        
        updateData = {
          business_name: businessName,
          business_type: businessType,
          business_description: businessDescription,
          brand_tone: brandTone,
          posting_frequency: postingFrequency
        };
      } else if (fieldType === 'marketing') {
        // Récupérer tous les champs marketing
        const email = document.getElementById('business_email_edit')?.value;
        const websiteUrl = document.getElementById('business_website_edit')?.value;
        const targetAudience = document.getElementById('target_audience_edit')?.value;
        
        updateData = {
          email: email,
          website_url: websiteUrl,
          target_audience: targetAudience
        };
      }

      await axios.put(`${API}/business-profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Auto-sauvegarde silencieuse - pas de toast de confirmation
      console.log('Auto-sauvegarde réussie:', fieldType);
      
    } catch (error) {
      console.error('Auto-save error:', error);
      // En cas d'erreur, on peut afficher un toast discret
      toast.error('Erreur auto-sauvegarde');
    }
  };

  const handleBatchUpload = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    const formData = new FormData();
    
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

    try {
      await axios.post(`${API}/content/batch-upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        },
      });
      
      toast.success('Fichiers uploadés avec succès !');
      setSelectedFiles([]);
      loadPendingContent();
    } catch (error) {
      toast.error('Erreur lors de l\'upload');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  // Show auth page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  // Show payment page if requested
  if (showPaymentPage) {
    return (
      <PaymentPage 
        onSuccess={() => {
          setShowPaymentPage(false);
          checkAuth();
        }}
        onCancel={() => setShowPaymentPage(false)}
      />
    );
  }

  // Show admin dashboard for admin users
  if (user?.is_admin) {
    return <AdminDashboard user={user} onLogout={handleLogout} />;
  }

  const Dashboard = () => (
    <div className="min-h-screen bg-pattern">
      <div className="card-glass border-0 border-b border-purple-100/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="w-14 h-14 ring-4 ring-purple-200/50">
                <AvatarImage src={businessProfile?.logo_url ? `${BACKEND_URL}${businessProfile.logo_url}` : ""} />
                <AvatarFallback className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 text-white text-lg font-bold">
                  <div className="logo-cm text-white text-lg">
                    <span className="logo-c">C</span>
                    <span className="logo-m">M</span>
                  </div>
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 bg-clip-text text-transparent">
                  Claire et Marcus
                </h1>
                <p className="text-base text-gray-600 font-medium truncate">{businessProfile?.business_name || 'Mon entreprise'}</p>
                <div className="text-sm text-gray-500">
                  <p className="text-purple-600 font-semibold">Claire rédige, Marcus programme. Vous respirez.</p>
                </div>
              </div>
            </div>
            <div className="flex items-center">
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="text-gray-500 hover:text-red-600 p-2"
                title="Déconnexion"
              >
                <LogOut className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs 
          value={activeTab} 
          onValueChange={setActiveTab} 
          className="space-y-8"
        >
          <div className="overflow-x-auto">
            <TabsList className="grid grid-cols-8 w-full max-w-5xl mx-auto bg-white/80 backdrop-blur-lg p-2 rounded-2xl shadow-xl min-w-max">
              <TabsTrigger value="entreprise" className="tab-sexy">
                <Building className="w-5 h-5" />
                <span className="ml-2 font-semibold">Entreprise</span>
              </TabsTrigger>
              <TabsTrigger value="analyse" className="tab-sexy">
                <Search className="w-5 h-5" />
                <span className="ml-2 font-semibold">Analyse</span>
              </TabsTrigger>
              <TabsTrigger value="bibliotheque" className="tab-sexy">
                <ImageIcon className="w-5 h-5" />
                <span className="ml-2 font-semibold">Bibliothèque</span>
              </TabsTrigger>
              <TabsTrigger value="notes" className="tab-sexy">
                <Edit className="w-5 h-5" />
                <span className="ml-2 font-semibold">Notes</span>
              </TabsTrigger>
              <TabsTrigger value="posts" className="tab-sexy">
                <FileText className="w-5 h-5" />
                <span className="ml-2 font-semibold">Posts</span>
              </TabsTrigger>
              <TabsTrigger value="calendar" className="tab-sexy">
                <CalendarIcon className="w-5 h-5" />
                <span className="ml-2 font-semibold">Calendrier</span>
              </TabsTrigger>
              <TabsTrigger value="social" className="tab-sexy">
                <Users className="w-5 h-5" />
                <span className="ml-2 font-semibold">Social</span>
              </TabsTrigger>
              <TabsTrigger value="reglages" className="tab-sexy">
                <Cog className="w-5 h-5" />
                <span className="ml-2 font-semibold">Réglages</span>
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="entreprise" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center">
                    <Building className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    Profil d'entreprise ✨
                  </span>
                </CardTitle>
                <CardDescription className="text-lg text-gray-600">
                  Gérez les informations de votre entreprise et personnalisez votre stratégie 🎯
                </CardDescription>
              </CardHeader>
              <CardContent>
                {businessProfile ? (
                  <div className="space-y-6">
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200">
                      <h3 className="text-lg font-bold text-blue-800 mb-4">Informations de l'entreprise (Modifiables)</h3>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="business_name_edit" className="block text-sm font-medium text-gray-700 mb-2">
                            Nom de l'entreprise
                          </label>
                          <input
                            id="business_name_edit"
                            type="text"
                            defaultValue={businessProfile?.business_name || 'Mon entreprise'}
                            placeholder="Nom de votre entreprise"
                            onBlur={() => handleAutoSave('business')}
                            className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            style={{
                              fontSize: '16px',
                              lineHeight: '1.5',
                              WebkitAppearance: 'none',
                              WebkitBorderRadius: '8px',
                              borderRadius: '8px',
                              boxShadow: 'none',
                              WebkitBoxShadow: 'none',
                              touchAction: 'manipulation',
                              userSelect: 'text',
                              WebkitUserSelect: 'text',
                              WebkitTouchCallout: 'default'
                            }}
                            autoComplete="organization"
                            autoCorrect="on"
                            autoCapitalize="words"
                            spellCheck="true"
                            inputMode="text"
                            enterKeyHint="next"
                          />
                        </div>
                        <div>
                          <label htmlFor="business_type_edit" className="block text-sm font-medium text-gray-700 mb-2">
                            Type d'entreprise
                          </label>
                          <input
                            id="business_type_edit"
                            type="text"
                            defaultValue={businessProfile?.business_type || 'service'}
                            placeholder="Ex: restaurant, commerce, service, etc."
                            onBlur={() => handleAutoSave('business')}
                            className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            style={{
                              fontSize: '16px',
                              lineHeight: '1.5',
                              WebkitAppearance: 'none',
                              WebkitBorderRadius: '8px',
                              borderRadius: '8px',
                              boxShadow: 'none',
                              WebkitBoxShadow: 'none',
                              touchAction: 'manipulation',
                              userSelect: 'text',
                              WebkitUserSelect: 'text',
                              WebkitTouchCallout: 'default'
                            }}
                            autoComplete="off"
                            autoCorrect="on"
                            autoCapitalize="words"
                            spellCheck="true"
                            inputMode="text"
                            enterKeyHint="next"
                          />
                        </div>
                      </div>
                      <div className="mt-4">
                        <label htmlFor="business_description_edit" className="block text-sm font-medium text-gray-700 mb-2">
                          Description de l'activité
                        </label>
                        <textarea
                          id="business_description_edit"
                          defaultValue={businessProfile?.business_description || ''}
                          placeholder="Décrivez votre activité, vos services ou produits..."
                          onBlur={() => handleAutoSave('business')}
                          className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation',
                            userSelect: 'text',
                            WebkitUserSelect: 'text',
                            WebkitTouchCallout: 'default',
                            minHeight: '100px'
                          }}
                          rows={4}
                          autoComplete="off"
                          autoCorrect="on"
                          autoCapitalize="sentences"
                          spellCheck="true"
                          inputMode="text"
                          enterKeyHint="enter"
                        />
                      </div>
                      
                      {/* Ton de marque */}
                      <div className="mt-4">
                        <label htmlFor="brand_tone_edit" className="block text-sm font-medium text-gray-700 mb-2">
                          Ton de marque
                        </label>
                        <select
                          id="brand_tone_edit"
                          defaultValue={businessProfile?.brand_tone || 'professionnel'}
                          onChange={() => handleAutoSave('business')}
                          className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation'
                          }}
                        >
                          <option value="professionnel">👔 Professionnel</option>
                          <option value="luxe">💎 Luxe</option>
                          <option value="simple">🎯 Simple</option>
                          <option value="humouristique">😄 Humoristique</option>
                          <option value="proximite">🤝 Proximité</option>
                          <option value="amical">😊 Amical</option>
                          <option value="moderne">⚡ Moderne</option>
                          <option value="traditionnel">🏛️ Traditionnel</option>
                          <option value="creatif">🎨 Créatif</option>
                          <option value="technique">🔧 Technique</option>
                        </select>
                      </div>

                      {/* Rythme de publications */}
                      <div className="mt-4">
                        <label htmlFor="posting_frequency_edit" className="block text-sm font-medium text-gray-700 mb-2">
                          Rythme de publications
                        </label>
                        <select
                          id="posting_frequency_edit"
                          defaultValue={businessProfile?.posting_frequency || 'hebdomadaire'}
                          onChange={() => handleAutoSave('business')}
                          className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation'
                          }}
                        >
                          <option value="quotidien">📅 Quotidien (tous les jours)</option>
                          <option value="3_semaine">🔥 3 fois par semaine</option>
                          <option value="hebdomadaire">📋 Hebdomadaire (1 fois par semaine)</option>
                          <option value="2_mois">📆 2 fois par mois</option>
                          <option value="mensuel">🗓️ Mensuel (1 fois par mois)</option>
                        </select>
                      </div>
                      
                      <div className="mt-4">
                        <Button
                          type="button"
                          onClick={handleSaveBusinessInfo}
                          disabled={isSavingBusinessInfo}
                          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
                        >
                          {isSavingBusinessInfo ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                              Sauvegarde...
                            </>
                          ) : (
                            <>
                              💾 Sauvegarder les informations
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                    
                    {/* Section Contact et Marketing */}
                    <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200">
                      <h3 className="text-lg font-bold text-purple-800 mb-4">Contact et Marketing</h3>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="business_email_edit" className="block text-sm font-medium text-gray-700 mb-2">
                            Email professionnel
                          </label>
                          <input
                            id="business_email_edit"
                            type="email"
                            defaultValue={businessProfile?.email || ''}
                            placeholder="contact@votre-entreprise.com"
                            onBlur={() => handleAutoSave('marketing')}
                            className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none"
                            style={{
                              fontSize: '16px',
                              lineHeight: '1.5',
                              WebkitAppearance: 'none',
                              WebkitBorderRadius: '8px',
                              borderRadius: '8px',
                              boxShadow: 'none',
                              WebkitBoxShadow: 'none',
                              touchAction: 'manipulation',
                              userSelect: 'text',
                              WebkitUserSelect: 'text',
                              WebkitTouchCallout: 'default'
                            }}
                            autoComplete="email"
                            autoCorrect="off"
                            autoCapitalize="off"
                            spellCheck="false"
                            inputMode="email"
                            enterKeyHint="next"
                          />
                        </div>
                        <div>
                          <label htmlFor="business_website_edit" className="block text-sm font-medium text-gray-700 mb-2">
                            Site web
                          </label>
                          <input
                            id="business_website_edit"
                            type="url"
                            defaultValue={businessProfile?.website_url || ''}
                            placeholder="https://votre-site.com"
                            onBlur={() => handleAutoSave('marketing')}
                            className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none"
                            style={{
                              fontSize: '16px',
                              lineHeight: '1.5',
                              WebkitAppearance: 'none',
                              WebkitBorderRadius: '8px',
                              borderRadius: '8px',
                              boxShadow: 'none',
                              WebkitBoxShadow: 'none',
                              touchAction: 'manipulation',
                              userSelect: 'text',
                              WebkitUserSelect: 'text',
                              WebkitTouchCallout: 'default'
                            }}
                            autoComplete="url"
                            autoCorrect="off"
                            autoCapitalize="off"
                            spellCheck="false"
                            inputMode="url"
                            enterKeyHint="go"
                          />
                        </div>
                      </div>
                      <div className="mt-4">
                        <label htmlFor="target_audience_edit" className="block text-sm font-medium text-gray-700 mb-2">
                          Audience cible
                        </label>
                        <textarea
                          id="target_audience_edit"
                          defaultValue={businessProfile?.target_audience || ''}
                          placeholder="Décrivez votre audience cible (âge, centres d'intérêt, localisation...)"
                          className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none resize-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation',
                            userSelect: 'text',
                            WebkitUserSelect: 'text',
                            WebkitTouchCallout: 'default',
                            minHeight: '80px'
                          }}
                          rows={3}
                          autoComplete="off"
                          autoCorrect="on"
                          autoCapitalize="sentences"
                          spellCheck="true"
                          inputMode="text"
                          enterKeyHint="enter"
                        />
                      </div>
                      <div className="mt-4">
                        <Button
                          type="button"
                          onClick={handleSaveMarketingInfo}
                          disabled={isSavingMarketingInfo}
                          className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded-lg"
                        >
                          {isSavingMarketingInfo ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                              Sauvegarde...
                            </>
                          ) : (
                            <>
                              💾 Sauvegarder le marketing
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-20 card-glass rounded-3xl">
                    <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                      <Building className="w-12 h-12 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-700 mb-4">Créez votre profil d'entreprise 🏢</h3>
                    <p className="text-xl text-gray-500 mb-8">Configurez votre profil pour des posts sur mesure ! 🚀</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analyse" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
                    <Search className="w-6 h-6 text-white" />
                  </div>
                  🌐 Analyse de Site Web
                </CardTitle>
                <CardDescription>
                  Analysez votre site web pour optimiser votre contenu et stratégie social media
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Champ URL du site avec input HTML natif */}
                <div className="space-y-2">
                  <label htmlFor="website_analysis_url_native" className="block text-sm font-medium text-gray-700">
                    URL de votre site web
                  </label>
                  <input
                    id="website_analysis_url_native"
                    type="url"
                    placeholder="https://votre-site.com"
                    className="w-full p-4 border border-gray-300 rounded-lg bg-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none"
                    style={{
                      fontSize: '16px',
                      lineHeight: '1.5',
                      WebkitAppearance: 'none',
                      WebkitBorderRadius: '8px',
                      borderRadius: '8px',
                      boxShadow: 'none',
                      WebkitBoxShadow: 'none',
                      touchAction: 'manipulation',
                      userSelect: 'text',
                      WebkitUserSelect: 'text'
                    }}
                    autoComplete="url"
                    autoCorrect="off"
                    autoCapitalize="off"
                    spellCheck="false"
                    inputMode="url"
                    enterKeyHint="go"
                  />
                </div>

                {/* Bouton d'analyse */}
                <div className="flex gap-3">
                  <Button
                    type="button"
                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-6 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2"
                  >
                    <Search className="w-4 h-4" />
                    <span>Analyser le site</span>
                  </Button>
                </div>

                {/* Message si pas d'analyse */}
                <div className="text-center py-8 text-gray-500">
                  <Search className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-lg mb-2">Aucune analyse disponible</p>
                  <p className="text-sm">Entrez l'URL de votre site web et cliquez sur "Analyser le site" pour commencer</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="bibliotheque" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
                    <ImageIcon className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    Bibliothèque de contenus ✨
                  </span>
                </CardTitle>
                <CardDescription className="text-lg text-gray-600">
                  Uploadez et gérez vos contenus pour créer des posts extraordinaires 🎨
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Upload Section */}
                <div className="mb-8">
                  <input
                    type="file"
                    multiple
                    accept="image/*,video/*"
                    onChange={(e) => setSelectedFiles(Array.from(e.target.files))}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="block border-2 border-dashed border-purple-300 rounded-3xl p-8 text-center hover:border-purple-500 hover:bg-gradient-to-br hover:from-purple-100 hover:to-pink-100 transition-all duration-300 bg-gradient-to-br from-purple-50 to-pink-50 cursor-pointer transform hover:scale-[1.02]"
                  >
                    <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                      <Upload className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Uploadez vos contenus 📁</h3>
                    <p className="text-gray-600 mb-4">Glissez-déposez vos fichiers ou cliquez partout ici pour sélectionner</p>
                    <p className="text-sm text-purple-600 font-medium">📱 Images • 🎬 Vidéos</p>
                  </label>

                  {/* Selected Files Preview */}
                  {selectedFiles.length > 0 && (
                    <div className="mt-6">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-gray-900">
                          {selectedFiles.length} fichier{selectedFiles.length > 1 ? 's' : ''} sélectionné{selectedFiles.length > 1 ? 's' : ''}
                        </h4>
                        <Button
                          onClick={handleBatchUpload}
                          disabled={isUploading}
                          className="btn-gradient-primary"
                        >
                          {isUploading ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                              Upload en cours...
                            </>
                          ) : (
                            <>
                              <Upload className="w-4 h-4 mr-2" />
                              Uploader {selectedFiles.length} fichier{selectedFiles.length > 1 ? 's' : ''}
                            </>
                          )}
                        </Button>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {selectedFiles.map((file, index) => (
                          <div key={index} className="relative group">
                            <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden border-2 border-purple-200">
                              {file.type.startsWith('image/') ? (
                                <img 
                                  src={URL.createObjectURL(file)} 
                                  alt={file.name}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100">
                                  <FileText className="w-8 h-8 text-purple-600" />
                                </div>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-2 truncate">{file.name}</p>
                            <button
                              onClick={() => setSelectedFiles(prev => prev.filter((_, i) => i !== index))}
                              className="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Content Gallery */}
                {pendingContent.length > 0 ? (
                  <div>
                    <h4 className="text-xl font-semibold text-gray-900 flex items-center mb-4">
                      <ImageIcon className="w-6 h-6 mr-2 text-purple-600" />
                      Vos contenus ({pendingContent.length})
                    </h4>
                    <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                      {pendingContent.map((content) => (
                        <ContentThumbnail
                          key={content.id}
                          content={content}
                          isSelectionMode={false}
                          isSelected={false}
                          onContentClick={() => {}}
                          onToggleSelection={() => {}}
                        />
                      ))}
                    </div>
                    <div className="text-center mt-6">
                      <Button
                        onClick={loadPendingContent}
                        variant="outline"
                        className="text-purple-600 border-purple-300 hover:bg-purple-50"
                      >
                        <ChevronRight className="w-4 h-4 mr-2 rotate-90" />
                        Recharger le contenu
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 card-glass rounded-3xl border-2 border-dashed border-purple-300">
                    <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                      <ImageIcon className="w-12 h-12 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-700 mb-4">Votre bibliothèque de contenus 📚</h3>
                    <p className="text-xl text-gray-500">Uploadez vos premiers contenus pour voir votre succès exploser ! 🚀</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notes" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center">
                    <Edit className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    Notes et informations ✨
                  </span>
                </CardTitle>
                <CardDescription className="text-lg text-gray-600">
                  Ajoutez des informations importantes pour créer des posts qui cartonnent ! 🎯
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Add New Note Section */}
                <div className="mb-8">
                  <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-3xl p-6 border-2 border-indigo-200">
                    <div className="flex items-center mb-4">
                      <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center mr-3">
                        <Edit className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900">Ajouter une nouvelle note</h3>
                    </div>
                    
                    <div className="space-y-4">
                      {/* Titre de la note avec input HTML natif */}
                      <div className="space-y-2">
                        <label htmlFor="note_title_native" className="block text-sm font-medium text-gray-700">
                          Titre de la note
                        </label>
                        <input
                          id="note_title_native"
                          type="text"
                          placeholder="Ex: Nouvelle promotion, Événement spécial..."
                          className="w-full p-4 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation',
                            userSelect: 'text',
                            WebkitUserSelect: 'text'
                          }}
                          autoComplete="off"
                          autoCorrect="off"
                          autoCapitalize="off"
                          spellCheck="false"
                          inputMode="text"
                          enterKeyHint="next"
                        />
                      </div>
                      
                      {/* Contenu de la note avec textarea HTML native */}
                      <div className="space-y-2">
                        <label htmlFor="note_content_native" className="block text-sm font-medium text-gray-700">
                          Contenu
                        </label>
                        <textarea
                          id="note_content_native"
                          placeholder="Décrivez les détails importants que vous voulez voir apparaître dans vos posts..."
                          className="w-full p-4 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation',
                            userSelect: 'text',
                            WebkitUserSelect: 'text',
                            minHeight: '120px'
                          }}
                          rows={5}
                          autoComplete="off"
                          autoCorrect="on"
                          autoCapitalize="sentences"
                          spellCheck="true"
                          inputMode="text"
                          enterKeyHint="enter"
                        />
                      </div>
                      
                      {/* Priorité avec input HTML natif */}
                      <div className="space-y-2">
                        <label htmlFor="note_priority_native" className="block text-sm font-medium text-gray-700">
                          Priorité
                        </label>
                        <input
                          id="note_priority_native"
                          type="text"
                          placeholder="low / medium / high"
                          className="w-full p-4 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation',
                            userSelect: 'text',
                            WebkitUserSelect: 'text'
                          }}
                          autoComplete="off"
                          autoCorrect="off"
                          autoCapitalize="off"
                          spellCheck="false"
                          inputMode="text"
                          enterKeyHint="done"
                        />
                      </div>
                      
                      <Button
                        type="button"
                        className="btn-gradient-primary w-full mt-6"
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Ajouter cette note
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="text-center py-12 card-glass rounded-3xl border-2 border-dashed border-indigo-300">
                  <div className="w-24 h-24 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <Edit className="w-12 h-12 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">Vos notes apparaîtront ici 📝</h3>
                  <p className="text-xl text-gray-500">Ajoutez votre première note pour commencer ! ✍️</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="posts" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-2xl flex items-center justify-center">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                    Posts engageants générés pour vous 🚀
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-20 card-glass rounded-3xl">
                  <div className="w-24 h-24 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <FileText className="w-12 h-12 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">Centre de gestion des posts 📊</h3>
                  <p className="text-xl text-gray-500">Vos posts générés apparaîtront ici ! 🎪</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="calendar" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center">
                    <CalendarIcon className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                    Calendrier de publication 📅
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-20 card-glass rounded-3xl">
                  <div className="w-24 h-24 bg-gradient-to-r from-orange-500 to-red-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <CalendarIcon className="w-12 h-12 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">Calendrier interactif 🎯</h3>
                  <p className="text-xl text-gray-500">Planification avancée bientôt disponible ! 🚀</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="social" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl flex items-center justify-center">
                    <Target className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent">
                    Comptes sociaux connectés 🌐
                  </span>
                </CardTitle>
                <CardDescription className="text-lg text-gray-600">
                  Connectez vos comptes sociaux pour publier automatiquement ⚡
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-20 card-glass rounded-3xl">
                  <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-teal-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <Target className="w-12 h-12 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">Réseaux sociaux 🌐</h3>
                  <p className="text-xl text-gray-500">Connectez vos comptes pour publier automatiquement ! 📱</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reglages" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-gray-500 to-gray-600 rounded-2xl flex items-center justify-center">
                    <Settings className="w-6 h-6 text-white" />
                  </div>
                  <span>Réglages</span>
                </CardTitle>
                <CardDescription>
                  Gérez votre profil, abonnement et paramètres de compte
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                      <Crown className="w-4 h-4 text-purple-600" />
                    </div>
                    Abonnement actuel
                  </h3>
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100">
                    <div>
                      <div className="font-semibold text-gray-900">Période d'essai</div>
                      <div className="text-sm text-gray-600">1 mois gratuit</div>
                    </div>
                    <Badge className="badge-info">Actif</Badge>
                  </div>
                  <Button 
                    className="mt-4 btn-gradient-primary w-full"
                    onClick={() => setShowPaymentPage(true)}
                  >
                    <CreditCard className="w-4 h-4 mr-2" />
                    Voir les abonnements
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );

  return (
    <div className="App">
      <Dashboard />
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