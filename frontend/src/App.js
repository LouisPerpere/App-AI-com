import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import axios from 'axios';
import AuthPage from './Auth';
import AdminDashboard from './AdminDashboard';
import FacebookCallback from './FacebookCallback';

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
import { Building, Sparkles, Crown, Upload, ImageIcon, FileText, X, Edit, CalendarIcon, Target, LogOut, Check, Send, Clock, ChevronLeft, ChevronRight, CreditCard } from 'lucide-react';

// Import toast for notifications
import { toast } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
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

// Subscription upgrade component
const SubscriptionUpgrade = ({ user, onUpgradeSuccess }) => {
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [isYearly, setIsYearly] = useState(false);
  const [promoCode, setPromoCode] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState(null);

  // Check for payment return from Stripe
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const paymentSuccess = urlParams.get('payment_success');
    const paymentCancelled = urlParams.get('payment_cancelled');

    if (sessionId) {
      setPaymentStatus('checking');
      pollPaymentStatus(sessionId);
    } else if (paymentSuccess) {
      setPaymentStatus('success');
    } else if (paymentCancelled) {
      setPaymentStatus('cancelled');
    }
  }, []);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    
    if (attempts >= maxAttempts) {
      setPaymentStatus('timeout');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/payments/v1/checkout/status/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.payment_status === 'paid') {
        setPaymentStatus('success');
        setTimeout(() => {
          onUpgradeSuccess();
        }, 2000);
        return;
      } else if (response.data.status === 'expired') {
        setPaymentStatus('expired');
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), 2000);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setPaymentStatus('error');
    }
  };

  const handleUpgrade = async (planId) => {
    if (!planId) return;

    setIsProcessing(true);
    setSelectedPlan(planId);

    try {
      const token = localStorage.getItem('access_token');
      const packageId = `${planId}_${isYearly ? 'yearly' : 'monthly'}`;

      const response = await axios.post(`${API}/payments/v1/checkout/session`, {
        package_id: packageId,
        origin_url: window.location.origin,
        promo_code: promoCode || undefined
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.url) {
        // Redirect to Stripe
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Payment error:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors du paiement');
      setIsProcessing(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  // Payment status displays
  if (paymentStatus === 'checking') {
    return (
      <Card className="card-gradient">
        <CardContent className="text-center py-12">
          <div className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <h3 className="text-xl font-bold text-gray-700">Vérification du paiement...</h3>
          <p className="text-gray-500">Veuillez patienter pendant que nous confirmons votre paiement</p>
        </CardContent>
      </Card>
    );
  }

  if (paymentStatus === 'success') {
    return (
      <Card className="card-gradient border-green-200">
        <CardContent className="text-center py-12">
          <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-green-700">Paiement réussi ! 🎉</h3>
          <p className="text-gray-600">Votre abonnement a été activé avec succès</p>
        </CardContent>
      </Card>
    );
  }

  if (paymentStatus === 'cancelled') {
    return (
      <Card className="card-gradient border-yellow-200">
        <CardContent className="text-center py-12">
          <div className="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-yellow-700">Paiement annulé</h3>
          <p className="text-gray-600">Vous pouvez réessayer à tout moment</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="card-gradient border-2 border-purple-200">
      <CardHeader className="text-center">
        <CardTitle className="flex items-center justify-center space-x-3 text-2xl">
          <Crown className="w-8 h-8 text-purple-600" />
          <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Passez au niveau supérieur ! 🚀
          </span>
        </CardTitle>
        <CardDescription className="text-lg">
          {user.subscription_status === 'trial' 
            ? 'Votre essai arrive à terme. Choisissez un plan pour continuer.'
            : 'Réactivez votre abonnement pour continuer à utiliser nos services.'
          }
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Billing toggle */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <span className={`text-lg ${!isYearly ? 'font-bold text-purple-600' : 'text-gray-500'}`}>
            Mensuel
          </span>
          <div 
            className="relative w-14 h-7 bg-gray-200 rounded-full cursor-pointer transition-colors"
            onClick={() => setIsYearly(!isYearly)}
            style={{ backgroundColor: isYearly ? '#9333ea' : '#e5e7eb' }}
          >
            <div 
              className="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-md transition-transform"
              style={{ transform: isYearly ? 'translateX(28px)' : 'translateX(0px)' }}
            />
          </div>
          <span className={`text-lg ${isYearly ? 'font-bold text-purple-600' : 'text-gray-500'}`}>
            Annuel <span className="text-green-600 text-sm">(2 mois gratuits)</span>
          </span>
        </div>

        {/* Plans grid */}
        <div className="space-y-6 mb-8">
          {/* Free Trial Plan */}
          <div className="relative rounded-2xl p-6 border-4 border-green-400 bg-gradient-to-b from-green-50 to-white shadow-lg">
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <Badge className="bg-green-500 text-white px-4 py-2 text-sm font-bold">🎉 Actuellement actif</Badge>
            </div>
            
            <div className="text-center mb-4">
              <h3 className="text-2xl font-bold text-green-800">{FREE_TRIAL_PLAN.name}</h3>
              <div className="mt-2">
                <span className="text-3xl font-bold text-green-600">GRATUIT</span>
                <span className="text-gray-500 ml-2">({FREE_TRIAL_PLAN.duration})</span>
              </div>
            </div>

            <ul className="space-y-3 mb-6">
              {FREE_TRIAL_PLAN.features.map((feature, index) => (
                <li key={index} className="flex items-start">
                  <Check className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-sm text-gray-700 font-medium">{feature}</span>
                </li>
              ))}
            </ul>
            
            <div className="text-center">
              <p className="text-sm text-green-700 font-medium">
                Profitez de votre mois gratuit pour découvrir PostCraft ! 🚀
              </p>
            </div>
          </div>

          {/* Paid Plans */}
          <div className="grid md:grid-cols-3 gap-6">
            {SUBSCRIPTION_PLANS.map((plan) => {
              const price = isYearly ? plan.yearlyPrice : plan.monthlyPrice;
              const monthlyEquivalent = isYearly ? plan.yearlyPrice / 12 : plan.monthlyPrice;
              
              return (
                <div
                  key={plan.id}
                  className={`relative rounded-2xl p-6 border-2 cursor-pointer transition-all hover:shadow-lg ${
                    plan.popular ? 'border-purple-500 bg-gradient-to-b from-purple-50 to-white' : 
                    plan.id === 'pro' ? 'border-yellow-400 bg-gradient-to-b from-yellow-50 to-white' :
                    'border-gray-200 hover:border-purple-300'
                  } ${selectedPlan === plan.id ? 'ring-2 ring-purple-500' : ''}`}
                  onClick={() => setSelectedPlan(plan.id)}
                >
                  {plan.badge && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <Badge className={`px-3 py-1 text-white ${
                        plan.popular ? 'bg-purple-500' : 
                        plan.id === 'pro' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`}>
                        {plan.badge}
                      </Badge>
                    </div>
                  )}
                  
                  <div className="text-center mb-4">
                    <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                    <div className="mt-2">
                      <span className="text-3xl font-bold text-gray-900">
                        {formatPrice(price)}
                      </span>
                      <span className="text-gray-500">
                        {isYearly ? '/an' : '/mois'}
                      </span>
                      {isYearly && (
                        <div className="text-sm text-green-600">
                          {formatPrice(monthlyEquivalent)}/mois
                        </div>
                      )}
                    </div>
                  </div>

                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                        <span className="text-sm text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>

        {/* Promo code input */}
        <div className="mb-6">
          <Label htmlFor="promo">Code promo (optionnel)</Label>
          <Input
            id="promo"
            placeholder="Entrez votre code promo"
            value={promoCode}
            onChange={(e) => setPromoCode(e.target.value)}
            className="mt-1"
          />
        </div>

        {/* Upgrade button */}
        {selectedPlan && (
          <div className="text-center">
            <Button
              onClick={() => handleUpgrade(selectedPlan)}
              disabled={isProcessing}
              className="btn-gradient-primary h-14 px-8 text-lg font-bold"
            >
              {isProcessing ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Redirection vers le paiement...
                </>
              ) : (
                <>
                  <CreditCard className="w-5 h-5 mr-2" />
                  Passer à {SUBSCRIPTION_PLANS.find(p => p.id === selectedPlan)?.name}
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

function MainApp() {
  const location = useLocation();
  
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeStep, setActiveStep] = useState('onboarding');
  
  // Business profile state
  const [businessProfile, setBusinessProfile] = useState(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  
  // Content and posts state
  const [pendingContent, setPendingContent] = useState([]);
  const [generatedPosts, setGeneratedPosts] = useState([]);
  const [notes, setNotes] = useState([]);
  const [currentPostIndex, setCurrentPostIndex] = useState(0);
  const [socialConnections, setSocialConnections] = useState([]);
  
  // Form states
  const [profileForm, setProfileForm] = useState({
    business_name: '',
    business_type: '',
    target_audience: '',
    brand_tone: '',
    posting_frequency: '',
    preferred_platforms: [],
    hashtags_primary: [],
    hashtags_secondary: [],
    budget_range: '',
    website_url: ''
  });
  
  const [noteForm, setNoteForm] = useState({
    title: '',
    content: '',
    priority: 'normal'
  });
  
  // UI states
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isGeneratingPosts, setIsGeneratingPosts] = useState(false);
  const [isConnectingSocial, setIsConnectingSocial] = useState(false);
  const [websiteAnalysis, setWebsiteAnalysis] = useState(null);
  const [isAnalyzingWebsite, setIsAnalyzingWebsite] = useState(false);
  const [showWebsiteAnalysis, setShowWebsiteAnalysis] = useState(false);
  const [showBurgerMenu, setShowBurgerMenu] = useState(false);
  
  // Hashtag management
  const [newPrimaryHashtag, setNewPrimaryHashtag] = useState('');
  const [newSecondaryHashtag, setNewSecondaryHashtag] = useState('');

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

  // Load data when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      if (user.is_admin) {
        // Admin users go to admin dashboard - handled by Auth component
        return;
      }
      
      if (!businessProfile) {
        loadBusinessProfile();
      } else {
        setActiveStep('dashboard');
        loadGeneratedPosts();
        loadPendingContent();
        loadNotes();
        loadSocialConnections();
        loadWebsiteAnalysis();
      }
    }
  }, [isAuthenticated, user, businessProfile]);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsAuthenticated(false);
      return;
    }

    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
      setIsAuthenticated(true);
      
      if (response.data.subscription_status) {
        setSubscriptionStatus(response.data.subscription_status);
      }
    } catch (error) {
      localStorage.removeItem('access_token');
      delete axios.defaults.headers.common['Authorization'];
      setIsAuthenticated(false);
    }
  };

  const loadBusinessProfile = async () => {
    try {
      const response = await axios.get(`${API}/business-profile`);
      setBusinessProfile(response.data);
      setActiveStep('dashboard');
    } catch (error) {
      if (error.response?.status === 404) {
        setActiveStep('onboarding');
      }
    }
  };

  const loadGeneratedPosts = async () => {
    try {
      const response = await axios.get(`${API}/posts`);
      setGeneratedPosts(response.data.posts || []);
    } catch (error) {
      console.error('Error loading posts:', error);
    }
  };

  const loadPendingContent = async () => {
    try {
      const response = await axios.get(`${API}/content/pending`);
      setPendingContent(response.data.content || []);
    } catch (error) {
      console.error('Error loading pending content:', error);
    }
  };

  const loadNotes = async () => {
    try {
      const response = await axios.get(`${API}/notes`);  
      setNotes(response.data);
    } catch (error) {
      console.error('Error loading notes:', error);
    }
  };

  const loadSocialConnections = async () => {
    try {
      if (businessProfile?.id) {
        const response = await axios.get(`${API}/social/connections?business_id=${businessProfile.id}`);
        setSocialConnections(response.data.connections || []);
      }
    } catch (error) {
      console.error('Error loading social connections:', error);
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

  const connectFacebook = async () => {
    if (!businessProfile?.id) {
      toast.error('Profil d\'entreprise requis');
      return;
    }

    try {
      setIsConnectingSocial(true);
      const response = await axios.get(`${API}/social/facebook/auth-url?business_id=${businessProfile.id}`);
      
      // Ouvrir la fenêtre d'authentification Facebook
      window.open(response.data.authorization_url, 'facebook-auth', 'width=600,height=600');
      
      // Écouter le message de retour
      const handleMessage = (event) => {
        if (event.data.type === 'FACEBOOK_AUTH_SUCCESS') {
          toast.success('Compte Facebook connecté avec succès !');
          loadSocialConnections();
          window.removeEventListener('message', handleMessage);
        } else if (event.data.type === 'FACEBOOK_AUTH_ERROR') {
          toast.error('Erreur lors de la connexion Facebook');
          console.error('Facebook auth error:', event.data.error);
        }
        setIsConnectingSocial(false);
      };

      window.addEventListener('message', handleMessage);
      
    } catch (error) {
      console.error('Error initiating Facebook connection:', error);
      toast.error('Erreur lors de l\'initialisation de la connexion Facebook');
      setIsConnectingSocial(false);
    }
  };

  const disconnectSocialAccount = async (connectionId) => {
    try {
      await axios.delete(`${API}/social/connection/${connectionId}`);
      toast.success('Compte déconnecté');
      loadSocialConnections();
    } catch (error) {
      console.error('Error disconnecting account:', error);
      toast.error('Erreur lors de la déconnexion');
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

  const addHashtag = (type, hashtag) => {
    if (!hashtag.trim()) return;
    
    const cleanHashtag = hashtag.replace('#', '').trim();
    const currentHashtags = type === 'primary' ? profileForm.hashtags_primary : profileForm.hashtags_secondary;
    
    if (!currentHashtags.includes(cleanHashtag)) {
      if (type === 'primary') {
        setProfileForm({
          ...profileForm,
          hashtags_primary: [...currentHashtags, cleanHashtag]
        });
        setNewPrimaryHashtag('');
      } else {
        setProfileForm({
          ...profileForm,
          hashtags_secondary: [...currentHashtags, cleanHashtag]
        });
        setNewSecondaryHashtag('');
      }
    }
  };

  const removeHashtag = (type, hashtag) => {
    if (type === 'primary') {
      setProfileForm({
        ...profileForm,
        hashtags_primary: profileForm.hashtags_primary.filter(h => h !== hashtag)
      });
    } else {
      setProfileForm({
        ...profileForm,
        hashtags_secondary: profileForm.hashtags_secondary.filter(h => h !== hashtag)
      });
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/business-profile`, profileForm);
      toast.success('Profil créé avec succès !');
      loadBusinessProfile();
    } catch (error) {
      toast.error('Erreur lors de la création du profil');
      console.error('Profile creation error:', error);
    }
  };

  // Website analysis functions
  const analyzeWebsite = async (forceReanalysis = false) => {
    if (!profileForm.website_url || !profileForm.website_url.trim()) {
      toast.error('Veuillez d\'abord renseigner l\'URL de votre site web');
      return;
    }

    setIsAnalyzingWebsite(true);
    try {
      const response = await axios.post(`${API}/website/analyze`, {
        website_url: profileForm.website_url,
        force_reanalysis: forceReanalysis
      });

      setWebsiteAnalysis(response.data);
      setShowWebsiteAnalysis(true);
      toast.success('Analyse du site web terminée ! ✨');
    } catch (error) {
      console.error('Website analysis error:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'analyse du site web');
    } finally {
      setIsAnalyzingWebsite(false);
    }
  };

  const loadWebsiteAnalysis = async () => {
    try {
      const response = await axios.get(`${API}/website/analysis`);
      if (response.data) {
        setWebsiteAnalysis(response.data);
      }
    } catch (error) {
      // Ignore error if no analysis exists
      console.log('No website analysis found');
    }
  };

  const deleteWebsiteAnalysis = async () => {
    try {
      await axios.delete(`${API}/website/analysis`);
      setWebsiteAnalysis(null);
      setShowWebsiteAnalysis(false);
      toast.success('Analyse supprimée');
    } catch (error) {
      console.error('Error deleting analysis:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  // Show auth page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage onAuthSuccess={checkAuth} />;
  }

  // Show admin dashboard for admin users
  if (user?.is_admin) {
    return <AdminDashboard user={user} onLogout={handleLogout} />;
  }

  const OnboardingForm = () => (
    <div className="min-h-screen bg-pattern bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-6">
      <Card className="w-full max-w-4xl card-glass animate-float">
        <CardHeader className="text-center pb-8">
          <div className="mx-auto mb-4 w-20 h-20 bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 rounded-3xl flex items-center justify-center animate-glow">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <CardTitle className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 bg-clip-text text-transparent">
            Configuration de votre entreprise
          </CardTitle>
          <CardDescription className="text-xl text-gray-600 mt-2 font-medium">
            Quelques informations pour personnaliser vos publications magiques ✨
          </CardDescription>
          
          {subscriptionStatus && (
            <Alert className="mt-4 card-gradient border-green-200">
              <Crown className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700 font-medium">
                {subscriptionStatus.message} - {subscriptionStatus.days_left} jours restants
              </AlertDescription>
            </Alert>
          )}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileSubmit} className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <Label htmlFor="business_name" className="text-gray-700 font-semibold">Nom de l'entreprise</Label>
                <Input
                  id="business_name"
                  placeholder="Mon Restaurant"
                  value={profileForm.business_name}
                  onChange={(e) => setProfileForm({...profileForm, business_name: e.target.value})}
                  required
                  className="input-modern"
                />
              </div>
              <div className="space-y-3">
                <Label htmlFor="business_type" className="text-gray-700 font-semibold">Type d'activité</Label>
                <Select onValueChange={(value) => setProfileForm({...profileForm, business_type: value})}>
                  <SelectTrigger className="input-modern">
                    <SelectValue placeholder="Sélectionnez..." />
                  </SelectTrigger>
                  <SelectContent className="card-glass">
                    <SelectItem value="restaurant">🍽️ Restaurant</SelectItem>
                    <SelectItem value="retail">🛍️ Commerce de détail</SelectItem>
                    <SelectItem value="services">⚡ Services</SelectItem>
                    <SelectItem value="freelance">💼 Freelance</SelectItem>
                    <SelectItem value="ecommerce">📦 E-commerce</SelectItem>
                    <SelectItem value="other">🌟 Autre</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-3">
              <Label htmlFor="target_audience" className="text-gray-700 font-semibold">Audience cible</Label>
              <Textarea
                id="target_audience"
                placeholder="Décrivez votre audience cible (âge, intérêts, localisation...)"
                value={profileForm.target_audience}
                onChange={(e) => setProfileForm({...profileForm, target_audience: e.target.value})}
                required
                className="input-modern min-h-[100px]"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <Label htmlFor="brand_tone" className="text-gray-700 font-semibold">Ton de marque</Label>
                <Select onValueChange={(value) => setProfileForm({...profileForm, brand_tone: value})}>
                  <SelectTrigger className="input-modern">
                    <SelectValue placeholder="Sélectionnez..." />
                  </SelectTrigger>
                  <SelectContent className="card-glass">
                    <SelectItem value="professional">👔 Professionnel</SelectItem>
                    <SelectItem value="casual">😊 Décontracté</SelectItem>
                    <SelectItem value="friendly">🤝 Amical</SelectItem>
                    <SelectItem value="luxury">💎 Luxueux</SelectItem>
                    <SelectItem value="fun">🎉 Amusant</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-3">
                <Label htmlFor="posting_frequency" className="text-gray-700 font-semibold">Fréquence de publication</Label>
                <Select onValueChange={(value) => setProfileForm({...profileForm, posting_frequency: value})}>
                  <SelectTrigger className="input-modern">
                    <SelectValue placeholder="Sélectionnez..." />
                  </SelectTrigger>
                  <SelectContent className="card-glass">
                    <SelectItem value="daily">📅 Quotidien</SelectItem>
                    <SelectItem value="3x_week">📈 3x par semaine</SelectItem>
                    <SelectItem value="weekly">📊 Hebdomadaire</SelectItem>
                    <SelectItem value="bi_weekly">📋 Bi-hebdomadaire</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-4">
              <Label className="text-gray-700 font-semibold">Réseaux sociaux préférés</Label>
              <div className="flex flex-wrap gap-4">
                {['facebook', 'instagram', 'linkedin'].map((platform) => (
                  <label key={platform} className="flex items-center space-x-3 cursor-pointer card-gradient p-4 rounded-2xl hover:shadow-lg transition-all duration-200">
                    <input
                      type="checkbox"
                      checked={profileForm.preferred_platforms.includes(platform)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setProfileForm({
                            ...profileForm,
                            preferred_platforms: [...profileForm.preferred_platforms, platform]
                          });
                        } else {
                          setProfileForm({
                            ...profileForm,
                            preferred_platforms: profileForm.preferred_platforms.filter(p => p !== platform)
                          });
                        }
                      }}
                      className="rounded-lg w-5 h-5 text-purple-600"
                    />
                    <span className="capitalize font-semibold text-gray-700">
                      {platform === 'facebook' ? '📘 Facebook' : 
                       platform === 'instagram' ? '📷 Instagram' : 
                       '💼 LinkedIn'}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              <div className="space-y-4">
                <Label className="text-gray-700 font-semibold">✨ Hashtags prioritaires (toujours inclus)</Label>
                <div className="flex flex-wrap gap-3 mb-4">
                  {profileForm.hashtags_primary.map((hashtag) => (
                    <Badge key={hashtag} className="badge-info">
                      {hashtag}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="ml-2 h-4 w-4 p-0 hover:bg-white/20"
                        onClick={() => removeHashtag('primary', hashtag)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
                <div className="flex space-x-3">
                  <Input
                    placeholder="Ajouter un hashtag prioritaire"
                    value={newPrimaryHashtag}
                    onChange={(e) => setNewPrimaryHashtag(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHashtag('primary', newPrimaryHashtag))}
                    className="input-modern"
                  />
                  <Button
                    type="button"
                    onClick={() => addHashtag('primary', newPrimaryHashtag)}
                    disabled={!newPrimaryHashtag.trim()}
                    className="btn-gradient-secondary px-6"
                  >
                    Ajouter
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <Label className="text-gray-700 font-semibold">🎯 Hashtags secondaires (selon contexte)</Label>
                <div className="flex flex-wrap gap-3 mb-4">
                  {profileForm.hashtags_secondary.map((hashtag) => (
                    <Badge key={hashtag} className="badge-warning">
                      {hashtag}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="ml-2 h-4 w-4 p-0 hover:bg-white/20"
                        onClick={() => removeHashtag('secondary', hashtag)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
                <div className="flex space-x-3">
                  <Input
                    placeholder="Ajouter un hashtag secondaire"
                    value={newSecondaryHashtag}
                    onChange={(e) => setNewSecondaryHashtag(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHashtag('secondary', newSecondaryHashtag))}
                    className="input-modern"
                  />
                  <Button
                    type="button"
                    onClick={() => addHashtag('secondary', newSecondaryHashtag)}
                    disabled={!newSecondaryHashtag.trim()}
                    className="btn-gradient-secondary px-6"
                  >
                    Ajouter
                  </Button>
                </div>
              </div>
            </div>

            {/* Website URL Section */}
            <div className="space-y-4">
              <Label className="text-gray-700 font-semibold">🌐 Site web de votre entreprise</Label>
              <div className="space-y-3">
                <Input
                  placeholder="https://monentreprise.com"
                  value={profileForm.website_url}
                  onChange={(e) => setProfileForm({...profileForm, website_url: e.target.value})}
                  className="input-modern"
                  type="url"
                />
                <p className="text-sm text-gray-500">
                  L'analyse de votre site web nous aide à créer des contenus personnalisés et pertinents pour votre audience 🎯
                </p>
                
                {profileForm.website_url && profileForm.website_url.trim() && (
                  <div className="flex space-x-3">
                    <Button
                      type="button"
                      onClick={() => analyzeWebsite(false)}
                      disabled={isAnalyzingWebsite}
                      className="btn-gradient-secondary flex-1"
                    >
                      {isAnalyzingWebsite ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                          Analyse en cours...
                        </>
                      ) : (
                        <>
                          🔍 Analyser le site
                        </>
                      )}
                    </Button>
                    
                    {websiteAnalysis && (
                      <Button
                        type="button"
                        onClick={() => analyzeWebsite(true)}
                        disabled={isAnalyzingWebsite}
                        variant="outline"
                        className="px-4"
                      >
                        🔄 Relancer l'analyse
                      </Button>
                    )}
                  </div>
                )}

                {/* Website Analysis Results */}
                {websiteAnalysis && (
                  <div className="mt-4 p-4 border-2 border-green-200 bg-green-50 rounded-xl">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-semibold text-green-800 flex items-center">
                        ✅ Analyse terminée
                        <Badge className="ml-2 bg-green-600">
                          {new Date(websiteAnalysis.last_analyzed).toLocaleDateString('fr-FR')}
                        </Badge>
                      </h4>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowWebsiteAnalysis(!showWebsiteAnalysis)}
                        className="text-green-700 hover:bg-green-100"
                      >
                        {showWebsiteAnalysis ? '🔼 Masquer' : '🔽 Voir détails'}
                      </Button>
                    </div>
                    
                    {showWebsiteAnalysis && (
                      <div className="space-y-3 text-sm">
                        <div>
                          <span className="font-semibold text-green-800">Résumé :</span>
                          <p className="text-green-700 mt-1">{websiteAnalysis.analysis_summary}</p>
                        </div>
                        
                        <div>
                          <span className="font-semibold text-green-800">Sujets clés :</span>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {websiteAnalysis.key_topics.map((topic, index) => (
                              <Badge key={index} className="bg-green-100 text-green-800 border-green-300">
                                {topic}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <span className="font-semibold text-green-800">Ton de marque :</span>
                          <span className="text-green-700 ml-2">{websiteAnalysis.brand_tone}</span>
                        </div>
                        
                        <div>
                          <span className="font-semibold text-green-800">Audience cible :</span>
                          <p className="text-green-700 mt-1">{websiteAnalysis.target_audience}</p>
                        </div>
                        
                        {websiteAnalysis.main_services.length > 0 && (
                          <div>
                            <span className="font-semibold text-green-800">Services principaux :</span>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {websiteAnalysis.main_services.map((service, index) => (
                                <Badge key={index} className="bg-blue-100 text-blue-800 border-blue-300">
                                  {service}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div className="pt-2 border-t border-green-200">
                          <p className="text-xs text-green-600">
                            ⏰ Prochaine analyse automatique : {new Date(websiteAnalysis.next_analysis_due).toLocaleDateString('fr-FR')}
                          </p>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={deleteWebsiteAnalysis}
                            className="text-red-600 hover:bg-red-50 mt-2"
                          >
                            🗑️ Supprimer l'analyse
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <Label htmlFor="budget_range" className="text-gray-700 font-semibold">💰 Budget publicitaire mensuel</Label>
              <Select onValueChange={(value) => setProfileForm({...profileForm, budget_range: value})}>
                <SelectTrigger className="input-modern">
                  <SelectValue placeholder="Sélectionnez..." />
                </SelectTrigger>
                <SelectContent className="card-glass">
                  <SelectItem value="0-100">💵 0€ - 100€</SelectItem>
                  <SelectItem value="100-500">💸 100€ - 500€</SelectItem>
                  <SelectItem value="500-1000">💰 500€ - 1000€</SelectItem>
                  <SelectItem value="1000+">🚀 1000€+</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button type="submit" className="w-full h-14 text-lg font-bold btn-gradient-primary">
              🚀 Créer mon profil magique
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );

  const Dashboard = () => (
    <div className="min-h-screen bg-pattern">
      <div className="card-glass border-0 border-b border-purple-100/50">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <Avatar className="w-16 h-16 ring-4 ring-purple-200/50">
                <AvatarImage src={businessProfile?.logo_url ? `${BACKEND_URL}${businessProfile.logo_url}` : ""} />
                <AvatarFallback className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 text-white text-xl font-bold">
                  <Building className="w-8 h-8" />
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 bg-clip-text text-transparent">
                  PostCraft
                </h1>
                <p className="text-lg text-gray-600 font-medium">{businessProfile?.business_name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {subscriptionStatus && (
                <Badge className={`${subscriptionStatus.active ? "badge-success" : "badge-warning"} px-4 py-2`}>
                  {subscriptionStatus.message}
                </Badge>
              )}
              <Badge className="badge-info px-4 py-2">
                {generatedPosts.filter(p => p.status === 'pending').length} posts en attente
              </Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="entreprise" className="space-y-8">
          <div className="overflow-x-auto">
            <TabsList className="grid grid-cols-6 w-full max-w-4xl mx-auto bg-white/80 backdrop-blur-lg p-2 rounded-2xl shadow-xl min-w-max">
              <TabsTrigger value="entreprise" className="tab-sexy">
                <Building className="w-5 h-5" />
                <span className="ml-2 font-semibold">Entreprise</span>
              </TabsTrigger>
              <TabsTrigger value="library" className="tab-sexy">
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
                <Target className="w-5 h-5" />
                <span className="ml-2 font-semibold">Social</span>
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
                    {/* Current Business Profile Display */}
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-4">
                          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center">
                            <Building className="w-8 h-8 text-white" />
                          </div>
                          <div>
                            <h3 className="text-2xl font-bold text-blue-800">{businessProfile.business_name}</h3>
                            <p className="text-blue-600 capitalize">{businessProfile.business_type}</p>
                          </div>
                        </div>
                        <Button
                          onClick={() => setShowWebsiteAnalysis(true)}
                          className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600"
                        >
                          ⚙️ Modifier
                        </Button>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-semibold text-blue-800 mb-2">📊 Informations générales</h4>
                          <div className="space-y-2 text-sm">
                            <p><span className="font-medium">Audience cible :</span> {businessProfile.target_audience}</p>
                            <p><span className="font-medium">Ton de marque :</span> {businessProfile.brand_tone}</p>
                            <p><span className="font-medium">Budget :</span> {businessProfile.budget_range}</p>
                            {businessProfile.website_url && (
                              <p><span className="font-medium">Site web :</span> 
                                <a href={businessProfile.website_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline ml-1">
                                  {businessProfile.website_url}
                                </a>
                              </p>
                            )}
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="font-semibold text-blue-800 mb-2">🌐 Stratégie digitale</h4>
                          <div className="space-y-2 text-sm">
                            <p><span className="font-medium">Fréquence :</span> {businessProfile.posting_frequency}</p>
                            <div>
                              <span className="font-medium">Réseaux sociaux :</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {businessProfile.preferred_platforms?.map((platform, index) => (
                                  <Badge key={index} className="bg-blue-100 text-blue-800 border-blue-300 text-xs">
                                    {platform}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            {businessProfile.hashtags_primary?.length > 0 && (
                              <div>
                                <span className="font-medium">Hashtags principaux :</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {businessProfile.hashtags_primary.slice(0, 3).map((tag, index) => (
                                    <Badge key={index} className="bg-purple-100 text-purple-800 border-purple-300 text-xs">
                                      #{tag}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Website Analysis Status */}
                    {websiteAnalysis && (
                      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-semibold text-green-800 mb-2">🌐 Analyse du site web</h4>
                            <p className="text-sm text-green-700">
                              Dernière analyse : {new Date(websiteAnalysis.last_analyzed).toLocaleDateString('fr-FR')}
                            </p>
                            <p className="text-xs text-green-600 mt-1">
                              Prochaine analyse automatique : {new Date(websiteAnalysis.next_analysis_due).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                          <Button
                            onClick={() => analyzeWebsite(true)}
                            disabled={isAnalyzingWebsite}
                            variant="outline"
                            className="border-green-300 text-green-700 hover:bg-green-100"
                          >
                            {isAnalyzingWebsite ? (
                              <>
                                <div className="w-4 h-4 border-2 border-green-700 border-t-transparent rounded-full animate-spin mr-2"></div>
                                Analyse...
                              </>
                            ) : (
                              <>🔄 Relancer</>
                            )}
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Quick Actions */}
                    <div className="grid md:grid-cols-3 gap-4">
                      <Button
                        onClick={() => setShowWebsiteAnalysis(true)}
                        className="h-16 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 flex-col"
                      >
                        <CreditCard className="w-6 h-6 mb-1" />
                        Modifier profil
                      </Button>
                      <Button
                        onClick={() => window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})}
                        className="h-16 bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 flex-col"
                      >
                        <Crown className="w-6 h-6 mb-1" />
                        Voir abonnements
                      </Button>
                      <Button
                        onClick={() => document.querySelector('[value="social"]').click()}
                        className="h-16 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 flex-col"
                      >
                        <Target className="w-6 h-6 mb-1" />
                        Gérer réseaux sociaux
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-20 card-glass rounded-3xl">
                    <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                      <Building className="w-12 h-12 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-700 mb-4">Créez votre profil d'entreprise 🏢</h3>
                    <p className="text-xl text-gray-500 mb-8">Configurez votre profil pour des posts sur mesure ! 🚀</p>
                    <Button
                      onClick={() => setShowWebsiteAnalysis(true)}
                      className="btn-gradient-primary h-14 px-8 text-lg font-bold"
                    >
                      🚀 Créer mon profil
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="library" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
                    <ImageIcon className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    Bibliothèque magique ✨
                  </span>
                </CardTitle>
                <CardDescription className="text-lg text-gray-600">
                  Uploadez et gérez vos contenus pour créer des posts extraordinaires 🎨
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-20 card-glass rounded-3xl">
                  <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <ImageIcon className="w-12 h-12 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">Votre bibliothèque de contenus 📚</h3>
                  <p className="text-xl text-gray-500">Uploadez vos premiers contenus pour voir votre succès exploser ! 🚀</p>
                </div>
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
                    Notes et informations magiques ✨
                  </span>
                </CardTitle>
                <CardDescription className="text-lg text-gray-600">
                  Ajoutez des informations importantes pour créer des posts qui cartonnent ! 🎯
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-20 card-glass rounded-3xl">
                  <div className="w-24 h-24 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <Edit className="w-12 h-12 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">Gestionnaire de notes 📝</h3>
                  <p className="text-xl text-gray-500">Ajoutez vos premières notes pour personnaliser vos posts ! ✍️</p>
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
                  Connectez vos comptes Facebook et Instagram pour publier en mode turbo ⚡
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-20 card-glass rounded-3xl border-2 border-dashed border-purple-300">
                  <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-teal-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <Target className="w-12 h-12 text-white" />
                  </div>
                  <h3 className="text-3xl font-bold text-gray-900 mb-4">Connexions sociales 🌟</h3>
                  <p className="text-xl text-gray-600 mb-8 max-w-lg mx-auto">
                    Connectez vos comptes Facebook et Instagram pour faire exploser votre présence en ligne ! 🚀
                  </p>
                  <Button
                    onClick={connectFacebook}
                    disabled={isConnectingSocial}
                    className="btn-gradient-primary h-16 px-12 text-xl font-bold"
                  >
                    {isConnectingSocial ? '⏳ Connexion en cours...' : '🔗 Connecter Facebook/Instagram'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Subscription/Upgrade Interface */}
          {user && (user.subscription_status === 'trial' || user.subscription_status === 'expired') ? (
            <div className="mt-8">
              <SubscriptionUpgrade user={user} onUpgradeSuccess={() => window.location.reload()} />
            </div>
          ) : null}
        </Tabs>
      </div>

      {/* Settings Modal for Website Analysis */}
      {showWebsiteAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">⚙️ Paramètres d'entreprise</h2>
                <Button
                  variant="ghost"
                  onClick={() => setShowWebsiteAnalysis(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-6 h-6" />
                </Button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Current Business Info */}
              <div className="bg-gray-50 rounded-xl p-4">
                <h3 className="font-semibold text-gray-800 mb-2">Informations actuelles</h3>
                <p><strong>Entreprise:</strong> {businessProfile?.business_name}</p>
                <p><strong>Type:</strong> {businessProfile?.business_type}</p>
                <p><strong>Site web actuel:</strong> {businessProfile?.website_url || "Non renseigné"}</p>
              </div>

              {/* Website Analysis Section */}
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-800">🌐 Analyse de votre site web</h3>
                <div className="space-y-3">
                  <Input
                    placeholder="https://monentreprise.com"
                    value={profileForm.website_url || businessProfile?.website_url || ''}
                    onChange={(e) => setProfileForm({...profileForm, website_url: e.target.value})}
                    className="input-modern"
                    type="url"
                  />
                  <p className="text-sm text-gray-500">
                    L'analyse de votre site web nous aide à créer des contenus personnalisés et pertinents pour votre audience 🎯
                  </p>
                  
                  {(profileForm.website_url || businessProfile?.website_url) && (
                    <div className="flex space-x-3">
                      <Button
                        type="button"
                        onClick={() => analyzeWebsite(false)}
                        disabled={isAnalyzingWebsite}
                        className="btn-gradient-secondary flex-1"
                      >
                        {isAnalyzingWebsite ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                            Analyse en cours...
                          </>
                        ) : (
                          <>
                            🔍 Analyser le site
                          </>
                        )}
                      </Button>
                      
                      {websiteAnalysis && (
                        <Button
                          type="button"
                          onClick={() => analyzeWebsite(true)}
                          disabled={isAnalyzingWebsite}
                          variant="outline"
                          className="px-4"
                        >
                          🔄 Relancer l'analyse
                        </Button>
                      )}
                    </div>
                  )}

                  {/* Website Analysis Results */}
                  {websiteAnalysis && (
                    <div className="mt-4 p-4 border-2 border-green-200 bg-green-50 rounded-xl">
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="font-semibold text-green-800 flex items-center">
                          ✅ Analyse terminée
                          <Badge className="ml-2 bg-green-600">
                            {new Date(websiteAnalysis.last_analyzed).toLocaleDateString('fr-FR')}
                          </Badge>
                        </h4>
                      </div>
                      
                      <div className="space-y-3 text-sm">
                        <div>
                          <span className="font-semibold text-green-800">Résumé :</span>
                          <p className="text-green-700 mt-1">{websiteAnalysis.analysis_summary}</p>
                        </div>
                        
                        <div>
                          <span className="font-semibold text-green-800">Sujets clés :</span>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {websiteAnalysis.key_topics.map((topic, index) => (
                              <Badge key={index} className="bg-green-100 text-green-800 border-green-300">
                                {topic}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <span className="font-semibold text-green-800">Ton de marque :</span>
                          <span className="text-green-700 ml-2">{websiteAnalysis.brand_tone}</span>
                        </div>
                        
                        <div>
                          <span className="font-semibold text-green-800">Audience cible :</span>
                          <p className="text-green-700 mt-1">{websiteAnalysis.target_audience}</p>
                        </div>
                        
                        {websiteAnalysis.main_services.length > 0 && (
                          <div>
                            <span className="font-semibold text-green-800">Services principaux :</span>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {websiteAnalysis.main_services.map((service, index) => (
                                <Badge key={index} className="bg-blue-100 text-blue-800 border-blue-300">
                                  {service}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div className="pt-2 border-t border-green-200">
                          <p className="text-xs text-green-600">
                            ⏰ Prochaine analyse automatique : {new Date(websiteAnalysis.next_analysis_due).toLocaleDateString('fr-FR')}
                          </p>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={deleteWebsiteAnalysis}
                            className="text-red-600 hover:bg-red-50 mt-2"
                          >
                            🗑️ Supprimer l'analyse
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Floating Burger Menu */}
      <div className="fixed bottom-6 left-6 z-40">
        <div className="relative">
          <Button
            onClick={() => setShowBurgerMenu(!showBurgerMenu)}
            className="w-14 h-14 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-110"
          >
            <div className="flex flex-col space-y-1">
              <div className={`w-4 h-0.5 bg-white transition-all duration-300 ${showBurgerMenu ? 'rotate-45 translate-y-1.5' : ''}`}></div>
              <div className={`w-4 h-0.5 bg-white transition-all duration-300 ${showBurgerMenu ? 'opacity-0' : ''}`}></div>
              <div className={`w-4 h-0.5 bg-white transition-all duration-300 ${showBurgerMenu ? '-rotate-45 -translate-y-1.5' : ''}`}></div>
            </div>
          </Button>

          {/* Menu Items */}
          {showBurgerMenu && (
            <div className="absolute bottom-16 left-0 bg-white rounded-2xl shadow-2xl border border-gray-100 p-4 min-w-[200px] animate-in slide-in-from-bottom-2">
              <div className="space-y-2">
                <button
                  onClick={() => {
                    document.querySelector('[value="entreprise"]').click();
                    setShowBurgerMenu(false);
                  }}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-blue-50 text-left transition-colors group"
                >
                  <Building className="w-5 h-5 text-blue-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Entreprise</span>
                </button>
                <button
                  onClick={() => {
                    document.querySelector('[value="bibliotheque"]').click();
                    setShowBurgerMenu(false);
                  }}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-purple-50 text-left transition-colors group"
                >
                  <ImageIcon className="w-5 h-5 text-purple-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Bibliothèque</span>
                </button>
                <button
                  onClick={() => {
                    document.querySelector('[value="notes"]').click();
                    setShowBurgerMenu(false);
                  }}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-green-50 text-left transition-colors group"
                >
                  <FileText className="w-5 h-5 text-green-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Notes</span>
                </button>
                <button
                  onClick={() => {
                    document.querySelector('[value="posts"]').click();
                    setShowBurgerMenu(false);
                  }}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-orange-50 text-left transition-colors group"
                >
                  <Send className="w-5 h-5 text-orange-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Posts</span>
                </button>
                <button
                  onClick={() => {
                    document.querySelector('[value="calendrier"]').click();
                    setShowBurgerMenu(false);
                  }}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-indigo-50 text-left transition-colors group"
                >
                  <CalendarIcon className="w-5 h-5 text-indigo-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Calendrier</span>
                </button>
                <button
                  onClick={() => {
                    document.querySelector('[value="social"]').click();
                    setShowBurgerMenu(false);
                  }}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-red-50 text-left transition-colors group"
                >
                  <Target className="w-5 h-5 text-red-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Social</span>
                </button>
                <hr className="my-2" />
                <button
                  onClick={() => {
                    handleLogout();
                    setShowBurgerMenu(false);
                  }}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-red-50 text-left transition-colors group"
                >
                  <LogOut className="w-5 h-5 text-red-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Se déconnecter</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="App">
      {activeStep === 'onboarding' ? <OnboardingForm /> : <Dashboard />}
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