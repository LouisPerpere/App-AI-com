import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import axios from 'axios';
import AuthPage from './Auth';
import TestAuth from './TestAuth';
import PaymentPage from './PaymentPage';
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
import { Building, Sparkles, Crown, Upload, ImageIcon, FileText, X, Edit, CalendarIcon, Target, LogOut, Check, Send, Clock, ChevronLeft, ChevronRight, CreditCard, Settings, Globe } from 'lucide-react';

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
          <div className="relative rounded-2xl p-6 pt-8 border-4 border-green-400 bg-gradient-to-b from-green-50 to-white shadow-lg">
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 z-10">
              <Badge className="bg-green-500 text-white px-4 py-1.5 text-xs font-bold rounded-full shadow-md">🎉 Actuellement actif</Badge>
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
                Profitez de votre mois gratuit pour découvrir Claire et Marcus ! 🚀
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

// Upgrade Modal Component
const UpgradeModal = ({ isOpen, onClose, user, canClose = true, title = "Débloquez Claire et Marcus Premium" }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl max-w-6xl w-full max-h-[90vh] overflow-y-auto relative">
        {canClose && (
          <button
            onClick={onClose}
            className="absolute top-6 right-6 w-10 h-10 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-colors z-10"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        )}

        <div className="p-8">
          {/* Header */}
          <div className="text-center space-y-4 mb-8">
            <div className="w-20 h-20 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mx-auto">
              <Crown className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              {title}
            </h2>
            {user?.subscription_status === 'expired' ? (
              <div className="bg-red-50 border border-red-200 rounded-2xl p-4">
                <p className="text-red-800 font-medium">
                  ⚠️ Votre période d'essai a expiré. Choisissez un plan pour continuer à utiliser Claire et Marcus.
                </p>
              </div>
            ) : (
              <p className="text-gray-600 max-w-2xl mx-auto">
                Votre essai gratuit se termine bientôt ! Continuez à faire grandir votre présence en ligne sans interruption.
              </p>
            )}
          </div>

          {/* Benefits Section */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl">
              <div className="w-12 h-12 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Gain de temps</h3>
              <p className="text-sm text-gray-600">Jusqu'à 10h économisées par semaine sur la gestion de vos réseaux sociaux</p>
            </div>
            <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl">
              <div className="w-12 h-12 bg-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Target className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Plus d'engagement</h3>
              <p className="text-sm text-gray-600">Contenu optimisé par IA pour maximiser vos interactions et votre portée</p>
            </div>
            <div className="text-center p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl">
              <div className="w-12 h-12 bg-green-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Croissance automatique</h3>
              <p className="text-sm text-gray-600">Présence constante et professionnelle qui fait grandir votre business</p>
            </div>
          </div>

          {/* Subscription Plans */}
          <SubscriptionUpgrade user={user} onUpgradeSuccess={() => window.location.reload()} />
        </div>
      </div>
    </div>
  );
};

function MainApp() {
  const location = useLocation();
  
  // Optimized user form handler
  const handleUserChange = useCallback((field, value) => {
    setUser(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Optimized form handlers to prevent input bugs
  const handleEditProfileChange = useCallback((field, value) => {
    console.log(`🔧 Profile field changed: ${field} =`, value); // Debug log
    setEditProfileForm(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);
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
  const [showPaymentPage, setShowPaymentPage] = useState(false);
  
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
  const [activeTab, setActiveTab] = useState('entreprise');
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeModalDismissed, setUpgradeModalDismissed] = useState(false);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [editProfileForm, setEditProfileForm] = useState({
    business_name: '',
    business_type: '',
    business_description: '',
    target_audience: '',
    brand_tone: '',
    posting_frequency: '',
    preferred_platforms: [],
    budget_range: '',
    email: '',
    website_url: '',
    hashtags_primary: [],
    hashtags_secondary: []
  });
  
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

  const handleAddNote = async () => {
    if (!noteForm.title || !noteForm.content) {
      toast.error('Veuillez remplir tous les champs requis');
      return;
    }

    try {
      const response = await axios.post(`${API}/notes`, {
        title: noteForm.title,
        content: noteForm.content,
        priority: noteForm.priority
      });

      if (response.status === 200 || response.status === 201) {
        toast.success('Note ajoutée avec succès !');
        setNoteForm({ title: '', content: '', priority: 'normal' });
        loadNotes(); // Recharger la liste des notes
      }
    } catch (error) {
      console.error('Error adding note:', error);
      toast.error('Erreur lors de l\'ajout de la note');
    }
  };

  const handleDeleteNote = async (noteId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) {
      return;
    }

    try {
      const response = await axios.delete(`${API}/notes/${noteId}`);
      
      if (response.status === 200 || response.status === 204) {
        toast.success('Note supprimée avec succès !');
        loadNotes(); // Recharger la liste des notes
      }
    } catch (error) {
      console.error('Error deleting note:', error);
      toast.error('Erreur lors de la suppression de la note');
    }
  };

  const generatePosts = async () => {
    if (notes.length === 0) {
      toast.error('Aucune note disponible pour générer des posts');
      return;
    }

    setIsGeneratingPosts(true);
    try {
      const response = await axios.post(`${API}/posts/generate`, {
        notes: notes,
        business_profile: businessProfile
      });

      if (response.status === 200 || response.status === 201) {
        toast.success('Posts générés avec succès !');
        loadGeneratedPosts(); // Recharger la liste des posts générés
        // Optionnel: passer à l'onglet Posts pour voir les résultats
        setTimeout(() => {
          document.querySelector('[value="posts"]')?.click();
        }, 1000);
      }
    } catch (error) {
      console.error('Error generating posts:', error);
      toast.error('Erreur lors de la génération des posts');
    } finally {
      setIsGeneratingPosts(false);
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

  // Function to check if upgrade modal should be shown
  const shouldShowUpgradeModal = () => {
    if (!user || upgradeModalDismissed) return false;
    
    const now = new Date();
    const trialEndDate = user.trial_end_date ? new Date(user.trial_end_date) : null;
    
    // Case 1: Trial expired - must show modal (no close button)
    if (user.subscription_status === 'expired') {
      return { show: true, canClose: false, title: "Votre essai gratuit a expiré" };
    }
    
    // Case 2: Last week before expiration - show daily (with close button)
    if (trialEndDate) {
      const daysUntilExpiration = Math.ceil((trialEndDate - now) / (1000 * 60 * 60 * 24));
      const lastShownToday = localStorage.getItem('upgradeModalLastShown');
      const today = now.toDateString();
      
      if (daysUntilExpiration <= 7 && daysUntilExpiration > 0) {
        if (lastShownToday !== today) {
          localStorage.setItem('upgradeModalLastShown', today);
          return { show: true, canClose: true, title: `Plus que ${daysUntilExpiration} jour${daysUntilExpiration > 1 ? 's' : ''} d'essai gratuit` };
        }
      }
    }
    
    // Case 3: Before validating second-to-last post of trial (based on posting frequency)
    if (user.subscription_status === 'trial' && businessProfile) {
      const frequency = businessProfile.posting_frequency || 'weekly';
      
      // Calculate total posts expected based on frequency (normalized mapping)
      const getPostsPerMonth = (freq) => {
        const normalizedFreq = freq.toLowerCase().replace(/[/\s]/g, '_');
        const postsPerMonth = {
          'daily': 30,
          '3x_week': 12,
          'bi_weekly': 8,  // bi-weekly = 2x per month
          'weekly': 4,
          'monthly': 1
        };
        return postsPerMonth[normalizedFreq] || 4; // Default to weekly if unknown
      };
      
      const totalExpectedPosts = getPostsPerMonth(frequency);
      const triggerAtPost = Math.max(1, totalExpectedPosts - 1); // Before last post
      
      const approvedPostsCount = generatedPosts.filter(post => post.status === 'approved').length;
      
      if (approvedPostsCount >= triggerAtPost) {
        const hasShownForSecondLastPost = localStorage.getItem('upgradeModalShownForSecondLastPost');
        if (!hasShownForSecondLastPost) {
          localStorage.setItem('upgradeModalShownForSecondLastPost', 'true');
          
          // Create frequency display text
          const getFrequencyText = (freq) => {
            const normalizedFreq = freq.toLowerCase().replace(/[/\s]/g, '_');
            const frequencyTexts = {
              'daily': 'publication quotidienne',
              '3x_week': '3 publications par semaine',
              'bi_weekly': 'publication bi-hebdomadaire', 
              'weekly': 'publication hebdomadaire',
              'monthly': 'publication mensuelle'
            };
            return frequencyTexts[normalizedFreq] || 'publication hebdomadaire';
          };
          
          return { 
            show: true, 
            canClose: true, 
            title: `Plus qu'un post gratuit ! (${approvedPostsCount}/${totalExpectedPosts})`,
            subtitle: `Avec ${getFrequencyText(frequency)}, vous approchez de la limite de votre essai gratuit.`
          };
        }
      }
    }
    
    return { show: false };
  };

  // Function to check if feature is blocked
  const isFeatureBlocked = (feature) => {
    if (!user) return true;
    
    // If trial expired, block everything
    if (user.subscription_status === 'expired') return true;
    
    // If on trial, allow everything
    if (user.subscription_status === 'trial') return false;
    
    // Check plan limitations
    const plan = user.subscription_plan;
    
    switch (feature) {
      case 'upload':
        return plan === 'free';
      case 'post_creation':
        if (plan === 'free') return true;
        if (plan === 'starter') {
          const monthlyPosts = generatedPosts.filter(post => {
            const postDate = new Date(post.created_at);
            const now = new Date();
            return postDate.getMonth() === now.getMonth() && postDate.getFullYear() === now.getFullYear();
          }).length;
          return monthlyPosts >= 4;
        }
        return false;
      case 'multi_platform':
        return plan === 'starter' || plan === 'free';
      case 'analytics':
        return plan === 'free';
      default:
        return false;
    }
  };

  // Check modal conditions on component mount and when user changes
  useEffect(() => {
    if (user) {
      const modalCondition = shouldShowUpgradeModal();
      if (modalCondition.show && !showUpgradeModal) {
        setShowUpgradeModal(true);
        // Store modal configuration in state or use context
        window.upgradeModalConfig = modalCondition;
      }
    }
  }, [user, generatedPosts, showUpgradeModal]);

  const navigateToTab = (tabValue) => {
    setActiveTab(tabValue);
    setShowBurgerMenu(false);
    
    // Scroll to center the active tab in the horizontal navigation
    setTimeout(() => {
      // Try multiple selectors to find the tab
      let activeTabElement = document.querySelector(`[role="tab"][value="${tabValue}"]`) ||
                           document.querySelector(`[data-value="${tabValue}"]`);
      
      if (!activeTabElement) {
        // Fallback: find by text content
        const tabElements = document.querySelectorAll('[role="tab"]');
        for (let tab of tabElements) {
          const text = tab.textContent.toLowerCase().trim();
          const searchValue = tabValue.toLowerCase();
          
          if (text.includes(searchValue) || 
              (tabValue === 'bibliotheque' && text.includes('bibliothèque')) ||
              (tabValue === 'calendar' && text.includes('calendrier')) ||
              (tabValue === 'entreprise' && text.includes('entreprise')) ||
              (tabValue === 'notes' && text.includes('notes')) ||
              (tabValue === 'posts' && text.includes('posts')) ||
              (tabValue === 'social' && text.includes('social')) ||
              (tabValue === 'reglages' && text.includes('réglages'))) {
            activeTabElement = tab;
            break;
          }
        }
      }
      
      if (activeTabElement) {
        // Scroll the tab container to center the active tab
        const tabContainer = activeTabElement.closest('.overflow-x-auto');
        if (tabContainer) {
          const containerRect = tabContainer.getBoundingClientRect();
          const tabRect = activeTabElement.getBoundingClientRect();
          const scrollLeft = tabRect.left - containerRect.left - (containerRect.width / 2) + (tabRect.width / 2);
          
          tabContainer.scrollTo({
            left: tabContainer.scrollLeft + scrollLeft,
            behavior: 'smooth'
          });
        } else {
          // Fallback to scrollIntoView
          activeTabElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest', 
            inline: 'center' 
          });
        }
      }
    }, 100);
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

  // LinkedIn connection function
  const connectLinkedIn = async () => {
    try {
      setIsConnectingSocial(true);
      const response = await axios.get(`${API}/linkedin/auth-url`);
      
      // Open LinkedIn OAuth window
      const popup = window.open(
        response.data.auth_url,
        'linkedin-auth',
        'width=600,height=600,scrollbars=yes,resizable=yes'
      );
      
      // Listen for popup closure or message
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          setIsConnectingSocial(false);
          // Refresh social connections
          loadSocialConnections();
        }
      }, 1000);
      
    } catch (error) {
      console.error('Error connecting LinkedIn:', error);
      toast.error('Erreur lors de la connexion LinkedIn');
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

  // Initialize edit form when entering edit mode
  const initializeEditForm = () => {
    if (businessProfile) {
      setEditProfileForm({
        business_name: businessProfile.business_name || '',
        business_type: businessProfile.business_type || '',
        business_description: businessProfile.business_description || '',
        target_audience: businessProfile.target_audience || '',
        brand_tone: businessProfile.brand_tone || '',
        posting_frequency: businessProfile.posting_frequency || '',
        preferred_platforms: businessProfile.preferred_platforms || [],
        budget_range: businessProfile.budget_range || '',
        email: businessProfile.email || '',
        website_url: businessProfile.website_url || '',
        hashtags_primary: businessProfile.hashtags_primary || [],
        hashtags_secondary: businessProfile.hashtags_secondary || []
      });
    }
  };

  // Handle profile editing
  const handleEditProfile = () => {
    initializeEditForm();
    setIsEditingProfile(true);
  };

  // Handle profile update form submission
  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setIsUpdatingProfile(true);
    
    try {
      const response = await axios.put(`${API}/business-profile`, editProfileForm, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      setBusinessProfile(response.data);
      setIsEditingProfile(false);
      toast.success('Profil mis à jour avec succès !');
      
      // If website URL changed, clear existing analysis
      if (websiteAnalysis && editProfileForm.website_url !== businessProfile.website_url) {
        setWebsiteAnalysis(null);
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Erreur lors de la mise à jour du profil');
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  // Handle cancelling profile edit
  const handleCancelEditProfile = () => {
    setIsEditingProfile(false);
    setEditProfileForm({
      business_name: '',
      business_type: '',
      business_description: '',
      target_audience: '',
      brand_tone: '',
      posting_frequency: '',
      preferred_platforms: [],
      budget_range: '',
      email: '',
      website_url: '',
      hashtags_primary: [],
      hashtags_secondary: []
    });
  };

  // Handle platform selection in edit form
  const handlePlatformToggle = (platform) => {
    setEditProfileForm(prev => ({
      ...prev,
      preferred_platforms: prev.preferred_platforms.includes(platform)
        ? prev.preferred_platforms.filter(p => p !== platform)
        : [...prev.preferred_platforms, platform]
    }));
  };

  // Handle hashtag input changes
  const handleHashtagChange = (type, value) => {
    const tags = value.split(',').map(tag => tag.trim().replace('#', ''));
    setEditProfileForm(prev => ({
      ...prev,
      [type]: tags
    }));
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

  // Show payment page if requested
  if (showPaymentPage) {
    return (
      <PaymentPage 
        onSuccess={() => {
          setShowPaymentPage(false);
          // Reload subscription data
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
              <Input
                id="budget_range"
                type="text"
                value={profileForm.budget_range}
                onChange={(e) => setProfileForm({...profileForm, budget_range: e.target.value})}
                placeholder="Ex: 500€, 1000€, 2500€..."
                className="input-modern"
              />
              <p className="text-sm text-gray-500">Saisissez le montant que vous souhaitez investir en publicité par mois</p>
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
                  <div className="logo-cm text-white text-xl">
                    <span className="logo-c">C</span>
                    <span className="logo-m">M</span>
                  </div>
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="claire-marcus-main-title bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 bg-clip-text text-transparent">
                  Claire et Marcus
                </h1>
                <p className="text-lg text-gray-600 font-medium">{businessProfile?.business_name}</p>
                <div className="text-sm text-gray-500 claire-marcus-subtitle">
                  <p>Claire rédige, Marcus programme.</p>
                  <p className="text-purple-600 font-bold text-base mt-1 breathing-text">Vous respirez.</p>
                </div>
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
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <div className="overflow-x-auto">
            <TabsList className="grid grid-cols-7 w-full max-w-5xl mx-auto bg-white/80 backdrop-blur-lg p-2 rounded-2xl shadow-xl min-w-max">
              <TabsTrigger value="entreprise" className="tab-sexy">
                <Building className="w-5 h-5" />
                <span className="ml-2 font-semibold">Entreprise</span>
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
                <Target className="w-5 h-5" />
                <span className="ml-2 font-semibold">Social</span>
              </TabsTrigger>
              <TabsTrigger value="reglages" className="tab-sexy">
                <Settings className="w-5 h-5" />
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
                    {!isEditingProfile ? (
                      <>
                        {/* Current Business Profile Display */}
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center space-x-4 min-w-0 flex-1 mr-4">
                              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center flex-shrink-0">
                                <Building className="w-8 h-8 text-white" />
                              </div>
                              <div className="min-w-0">
                                <h3 className="text-2xl font-bold text-blue-800 break-words">{businessProfile.business_name}</h3>
                                <p className="text-blue-600 capitalize">{businessProfile.business_type}</p>
                              </div>
                            </div>
                            <Button
                              onClick={handleEditProfile}
                              className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 flex-shrink-0 whitespace-nowrap"
                            >
                              ⚙️ Modifier le profil
                            </Button>
                          </div>
                          
                          <div className="grid md:grid-cols-2 gap-6">
                            <div>
                              <h4 className="font-semibold text-blue-800 mb-2">📊 Informations générales</h4>
                              <div className="space-y-2 text-sm">
                                <p><span className="font-medium">Audience cible :</span> {businessProfile.target_audience}</p>
                                {businessProfile.business_description && (
                                  <p><span className="font-medium">Description :</span> {businessProfile.business_description}</p>
                                )}
                                <p><span className="font-medium">Ton de marque :</span> {businessProfile.brand_tone}</p>
                                <p><span className="font-medium">Budget :</span> {businessProfile.budget_range}</p>
                                {businessProfile.email && (
                                  <p><span className="font-medium">Email :</span> {businessProfile.email}</p>
                                )}
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
                      </>
                    ) : (
                      <>
                        {/* Business Profile Edit Form */}
                        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 border-2 border-purple-200">
                          <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center space-x-3">
                              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-xl flex items-center justify-center">
                                <Edit className="w-6 h-6 text-white" />
                              </div>
                              <div>
                                <h3 className="text-2xl font-bold text-purple-800">Modifier le profil d'entreprise</h3>
                                <p className="text-purple-600">Mettez à jour vos informations</p>
                              </div>
                            </div>
                            <Button
                              onClick={handleCancelEditProfile}
                              variant="outline"
                              className="border-purple-300 text-purple-700 hover:bg-purple-100"
                            >
                              ❌ Annuler
                            </Button>
                          </div>

                          <form onSubmit={handleUpdateProfile} className="space-y-6">
                            {/* Basic Information */}
                            <div className="grid md:grid-cols-2 gap-6">
                              <div className="space-y-4">
                                <h4 className="font-semibold text-purple-800 mb-3">📊 Informations de base</h4>
                                
                                <div className="space-y-2">
                                  <Label htmlFor="business_name" className="text-sm font-medium text-gray-700">
                                    Nom de l'entreprise *
                                  </Label>
                                  <Input
                                    key="business_name_input"
                                    id="business_name"
                                    value={editProfileForm.business_name}
                                    onChange={(e) => handleEditProfileChange('business_name', e.target.value)}
                                    placeholder="Nom de votre entreprise"
                                    required
                                  />
                                </div>

                                <div className="space-y-2">
                                  <Label htmlFor="business_type" className="text-sm font-medium text-gray-700">
                                    Type d'entreprise *
                                  </Label>
                                  <Select value={editProfileForm.business_type} onValueChange={(value) => setEditProfileForm(prev => ({...prev, business_type: value}))}>
                                    <SelectTrigger>
                                      <SelectValue placeholder="Sélectionnez le type" />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="restaurant">Restaurant</SelectItem>
                                      <SelectItem value="shop">Commerce</SelectItem>
                                      <SelectItem value="service">Service</SelectItem>
                                      <SelectItem value="freelance">Freelance</SelectItem>
                                      <SelectItem value="agency">Agence</SelectItem>
                                      <SelectItem value="ecommerce">E-commerce</SelectItem>
                                      <SelectItem value="saas">SaaS</SelectItem>
                                      <SelectItem value="consulting">Conseil</SelectItem>
                                      <SelectItem value="healthcare">Santé</SelectItem>
                                      <SelectItem value="education">Éducation</SelectItem>
                                      <SelectItem value="fitness">Sport/Fitness</SelectItem>
                                      <SelectItem value="beauty">Beauté</SelectItem>
                                      <SelectItem value="other">Autre</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>

                                <div className="space-y-2">
                                  <Label htmlFor="target_audience" className="text-sm font-medium text-gray-700">
                                    Audience cible *
                                  </Label>
                                  <Textarea
                                    key="target_audience_input"
                                    id="target_audience"
                                    value={editProfileForm.target_audience}
                                    onChange={(e) => handleEditProfileChange('target_audience', e.target.value)}
                                    placeholder="Décrivez votre audience cible"
                                    rows={3}
                                    required
                                  />
                                </div>

                                <div className="space-y-2">
                                  <Label htmlFor="brand_tone" className="text-sm font-medium text-gray-700">
                                    Ton de marque *
                                  </Label>
                                  <Select value={editProfileForm.brand_tone} onValueChange={(value) => setEditProfileForm(prev => ({...prev, brand_tone: value}))}>
                                    <SelectTrigger>
                                      <SelectValue placeholder="Sélectionnez le ton" />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="professional">Professionnel</SelectItem>
                                      <SelectItem value="casual">Décontracté</SelectItem>
                                      <SelectItem value="friendly">Amical</SelectItem>
                                      <SelectItem value="authoritative">Autoritaire</SelectItem>
                                      <SelectItem value="playful">Enjoué</SelectItem>
                                      <SelectItem value="inspiring">Inspirant</SelectItem>
                                      <SelectItem value="educational">Éducatif</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>

                                <div className="space-y-2">
                                  <Label htmlFor="business_description" className="text-sm font-medium text-gray-700">
                                    Décrivez votre activité *
                                  </Label>
                                  <Textarea
                                    key="business_description_input"
                                    id="business_description"
                                    value={editProfileForm.business_description}
                                    onChange={(e) => handleEditProfileChange('business_description', e.target.value)}
                                    placeholder="Décrivez en quelques mots votre activité, vos services ou produits..."
                                    rows={3}
                                    required
                                  />
                                  <p className="text-xs text-gray-500">
                                    Cette description sera utilisée pour générer du contenu personnalisé
                                  </p>
                                </div>
                              </div>

                              <div className="space-y-4">
                                <h4 className="font-semibold text-purple-800 mb-3">🌐 Stratégie digitale</h4>
                                
                                <div className="space-y-2">
                                  <Label htmlFor="posting_frequency" className="text-sm font-medium text-gray-700">
                                    Fréquence de publication *
                                  </Label>
                                  <Select value={editProfileForm.posting_frequency} onValueChange={(value) => setEditProfileForm(prev => ({...prev, posting_frequency: value}))}>
                                    <SelectTrigger>
                                      <SelectValue placeholder="Sélectionnez la fréquence" />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="daily">Quotidien</SelectItem>
                                      <SelectItem value="3x_week">3 fois par semaine</SelectItem>
                                      <SelectItem value="weekly">Hebdomadaire</SelectItem>
                                      <SelectItem value="bi_weekly">Bi-hebdomadaire</SelectItem>
                                      <SelectItem value="monthly">Mensuel</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>

                                <div className="space-y-2">
                                  <Label className="text-sm font-medium text-gray-700">
                                    Réseaux sociaux préférés *
                                  </Label>
                                  <div className="grid grid-cols-2 gap-2">
                                    {['Facebook', 'Instagram', 'LinkedIn', 'Twitter', 'TikTok', 'YouTube'].map((platform) => (
                                      <label key={platform} className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                          type="checkbox"
                                          checked={editProfileForm.preferred_platforms.includes(platform)}
                                          onChange={() => handlePlatformToggle(platform)}
                                          className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                                        />
                                        <span className="text-sm text-gray-700">{platform}</span>
                                      </label>
                                    ))}
                                  </div>
                                </div>

                                <div className="space-y-2">
                                  <Label htmlFor="budget_range" className="text-sm font-medium text-gray-700">
                                    Budget marketing mensuel
                                  </Label>
                                  <Input
                                    id="budget_range"
                                    value={editProfileForm.budget_range}
                                    onChange={(e) => setEditProfileForm(prev => ({...prev, budget_range: e.target.value}))}
                                    placeholder="Ex: 500€, 1000-2000€, etc."
                                  />
                                </div>
                              </div>
                            </div>

                            {/* Additional Information */}
                            <div className="grid md:grid-cols-2 gap-6 pt-4 border-t border-purple-200">
                              <div className="space-y-4">
                                <h4 className="font-semibold text-purple-800 mb-3">📧 Contact & Web</h4>
                                
                                <div className="space-y-2">
                                  <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                                    Email professionnel
                                  </Label>
                                  <Input
                                    id="email"
                                    type="email"
                                    value={editProfileForm.email}
                                    onChange={(e) => setEditProfileForm(prev => ({...prev, email: e.target.value}))}
                                    placeholder="contact@entreprise.com"
                                  />
                                </div>

                                <div className="space-y-2">
                                  <Label htmlFor="website_url" className="text-sm font-medium text-gray-700">
                                    Site web
                                  </Label>
                                  <Input
                                    key="website_url_input"
                                    id="website_url"
                                    type="url"
                                    value={editProfileForm.website_url}
                                    onChange={(e) => handleEditProfileChange('website_url', e.target.value)}
                                    placeholder="https://votre-site.com"
                                  />
                                </div>
                              </div>

                              <div className="space-y-4">
                                <h4 className="font-semibold text-purple-800 mb-3">#️⃣ Hashtags</h4>
                                
                                <div className="space-y-2">
                                  <Label htmlFor="hashtags_primary" className="text-sm font-medium text-gray-700">
                                    Hashtags principaux
                                  </Label>
                                  <Input
                                    id="hashtags_primary"
                                    value={editProfileForm.hashtags_primary.join(', ')}
                                    onChange={(e) => handleHashtagChange('hashtags_primary', e.target.value)}
                                    placeholder="restaurant, gastronomie, paris"
                                  />
                                  <p className="text-xs text-gray-500">Séparez par des virgules</p>
                                </div>

                                <div className="space-y-2">
                                  <Label htmlFor="hashtags_secondary" className="text-sm font-medium text-gray-700">
                                    Hashtags secondaires
                                  </Label>
                                  <Input
                                    id="hashtags_secondary"
                                    value={editProfileForm.hashtags_secondary.join(', ')}
                                    onChange={(e) => handleHashtagChange('hashtags_secondary', e.target.value)}
                                    placeholder="cuisine, chef, bistronomie"
                                  />
                                  <p className="text-xs text-gray-500">Hashtags complémentaires</p>
                                </div>
                              </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex justify-end space-x-4 pt-6 border-t border-purple-200">
                              <Button
                                type="button"
                                onClick={handleCancelEditProfile}
                                variant="outline"
                                className="border-gray-300 text-gray-700 hover:bg-gray-100"
                              >
                                Annuler
                              </Button>
                              <Button
                                type="submit"
                                disabled={isUpdatingProfile}
                                className="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600"
                              >
                                {isUpdatingProfile ? (
                                  <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                                    Mise à jour...
                                  </>
                                ) : (
                                  <>
                                    <Check className="w-4 h-4 mr-2" />
                                    Sauvegarder les modifications
                                  </>
                                )}
                              </Button>
                            </div>
                          </form>
                        </div>
                      </>
                    )}

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
                        onClick={handleEditProfile}
                        className="h-16 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 flex-col"
                      >
                        <Edit className="w-6 h-6 mb-1" />
                        Modifier profil
                      </Button>
                      <Button
                        onClick={() => setShowPaymentPage(true)}
                        className="h-16 bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 flex-col"
                      >
                        <CreditCard className="w-6 h-6 mb-1" />
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

                {/* Website Analysis Section */}
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                      <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                        <Globe className="w-4 h-4 text-purple-600" />
                      </div>
                      Analyse de votre site web
                    </h3>
                    <Button
                      onClick={() => setShowWebsiteAnalysis(true)}
                      className="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white"
                      size="sm"
                    >
                      <Globe className="w-4 h-4 mr-2" />
                      Analyser mon site
                    </Button>
                  </div>
                  
                  {websiteAnalysis ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-green-600">✅ Analyse terminée</span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => analyzeWebsite(true)}
                          disabled={isAnalyzingWebsite}
                        >
                          {isAnalyzingWebsite ? '🔄 Analyse...' : '🔄 Re-analyser'}
                        </Button>
                      </div>
                      <p className="text-sm text-gray-600">
                        Dernière analyse : {new Date(websiteAnalysis.analyzed_at).toLocaleDateString('fr-FR')}
                      </p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowWebsiteAnalysis(true)}
                        className="text-blue-600 hover:bg-blue-50"
                      >
                        👁️ Voir les détails
                      </Button>
                    </div>
                  ) : (
                    <div className="text-center py-4">
                      <p className="text-gray-600 text-sm mb-3">
                        Analysez votre site web pour générer du contenu personnalisé
                      </p>
                      <Button
                        onClick={() => setShowWebsiteAnalysis(true)}
                        variant="outline"
                        className="text-purple-600 border-purple-200 hover:bg-purple-50"
                      >
                        <Sparkles className="w-4 h-4 mr-2" />
                        Commencer l'analyse
                      </Button>
                    </div>
                  )}
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
                  {isFeatureBlocked('upload') ? (
                    <div className="border-2 border-dashed border-red-300 rounded-3xl p-8 text-center bg-gradient-to-br from-red-50 to-pink-50">
                      <div className="w-16 h-16 bg-gradient-to-r from-red-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 opacity-50">
                        <Upload className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">Fonctionnalité bloquée 🔒</h3>
                      <p className="text-gray-600 mb-4">L'upload de contenus nécessite un abonnement actif</p>
                      <Button 
                        onClick={() => setShowUpgradeModal(true)}
                        className="btn-gradient-primary"
                      >
                        <Crown className="w-4 h-4 mr-2" />
                        Débloquer maintenant
                      </Button>
                    </div>
                  ) : (
                    <>
                      <input
                        type="file"
                        multiple
                        accept="image/*,video/*,audio/*"
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
                        <p className="text-sm text-purple-600 font-medium">📱 Images • 🎬 Vidéos • 🎵 Audio</p>
                      </label>
                    </>
                  )}

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

                {/* Uploaded Content Gallery */}
                {pendingContent.length > 0 && (
                  <div>
                    <h4 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                      <ImageIcon className="w-6 h-6 mr-2 text-purple-600" />
                      Vos contenus ({pendingContent.length})
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      {pendingContent.map((content) => (
                        <div key={content.id} className="relative group cursor-pointer">
                          <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden border-2 border-purple-200 hover:border-purple-400 transition-colors">
                            {content.file_type?.startsWith('image/') ? (
                              <img 
                                src={`data:${content.file_type};base64,${content.file_data}`}
                                alt={content.filename}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100">
                                <FileText className="w-8 h-8 text-purple-600" />
                              </div>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-2 truncate">{content.filename}</p>
                          {content.description && (
                            <Badge className="mt-1 bg-green-100 text-green-800 text-xs">
                              Avec description
                            </Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {pendingContent.length === 0 && selectedFiles.length === 0 && (
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
                    
                    <form onSubmit={(e) => {
                      e.preventDefault();
                      handleAddNote();
                    }} className="space-y-4">
                      <div>
                        <Label htmlFor="note-title" className="text-gray-700 font-medium">Titre de la note</Label>
                        <Input
                          id="note-title"
                          placeholder="Ex: Nouvelle promotion, Événement spécial..."
                          value={noteForm.title}
                          onChange={(e) => setNoteForm({...noteForm, title: e.target.value})}
                          className="mt-1 border-indigo-200 focus:border-indigo-500"
                          required
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="note-content" className="text-gray-700 font-medium">Contenu</Label>
                        <textarea
                          id="note-content"
                          placeholder="Décrivez les détails importants que vous voulez voir apparaître dans vos posts..."
                          value={noteForm.content}
                          onChange={(e) => setNoteForm({...noteForm, content: e.target.value})}
                          className="mt-1 w-full min-h-[120px] p-3 border border-indigo-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 resize-y"
                          required
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="note-priority" className="text-gray-700 font-medium">Priorité</Label>
                        <select
                          id="note-priority"
                          value={noteForm.priority}
                          onChange={(e) => setNoteForm({...noteForm, priority: e.target.value})}
                          className="mt-1 w-full p-3 border border-indigo-200 rounded-lg focus:border-indigo-500"
                        >
                          <option value="low">🟢 Faible - Information complémentaire</option>
                          <option value="medium">🟡 Moyenne - Information importante</option>
                          <option value="high">🔴 Haute - À mentionner absolument</option>
                        </select>
                      </div>
                      
                      <Button
                        type="submit"
                        className="btn-gradient-primary w-full"
                        disabled={!noteForm.title || !noteForm.content}
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Ajouter cette note
                      </Button>
                    </form>
                  </div>
                </div>

                {/* Notes List */}
                {notes.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                        <FileText className="w-6 h-6 mr-2 text-indigo-600" />
                        Vos notes ({notes.length})
                      </h3>
                      <Button
                        onClick={generatePosts}
                        disabled={isGeneratingPosts || notes.length === 0}
                        className="btn-gradient-secondary"
                      >
                        {isGeneratingPosts ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                            Génération...
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4 mr-2" />
                            Générer des posts
                          </>
                        )}
                      </Button>
                    </div>
                    
                    <div className="grid gap-4">
                      {notes.map((note) => (
                        <div key={note.id} className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 p-6 hover:shadow-lg transition-all">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center space-x-3">
                              <div className={`w-3 h-3 rounded-full ${
                                note.priority === 'high' ? 'bg-red-500' :
                                note.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                              }`}></div>
                              <h4 className="text-lg font-semibold text-gray-900">{note.title}</h4>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge className={`text-xs ${
                                note.priority === 'high' ? 'bg-red-100 text-red-800' :
                                note.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                              }`}>
                                {note.priority === 'high' ? '🔴 Haute' : 
                                 note.priority === 'medium' ? '🟡 Moyenne' : '🟢 Faible'}
                              </Badge>
                              <Button
                                onClick={() => handleDeleteNote(note.id)}
                                variant="ghost"
                                size="sm"
                                className="text-red-600 hover:text-red-800 hover:bg-red-50"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                          
                          <p className="text-gray-700 leading-relaxed mb-3">{note.content}</p>
                          
                          <div className="text-xs text-gray-500 flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            Ajoutée le {new Date(note.created_at).toLocaleDateString('fr-FR')} à {new Date(note.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {notes.length === 0 && (
                  <div className="text-center py-12 card-glass rounded-3xl border-2 border-dashed border-indigo-300">
                    <div className="w-24 h-24 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                      <Edit className="w-12 h-12 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-700 mb-4">Gestionnaire de notes 📝</h3>
                    <p className="text-xl text-gray-500">Ajoutez vos premières notes pour personnaliser vos posts ! ✍️</p>
                  </div>
                )}
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
                {socialConnections && socialConnections.length > 0 ? (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-900">Comptes connectés:</h3>
                    {socialConnections.map((connection, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                            <Check className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{connection.platform}</p>
                            <p className="text-sm text-gray-600">@{connection.platform_username}</p>
                          </div>
                        </div>
                        <Badge className="bg-green-100 text-green-800">Actif</Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-8">
                    {/* Connection Cards */}
                    <div className="grid md:grid-cols-3 gap-6">
                      {/* Facebook Card */}
                      <div className="text-center p-6 card-glass rounded-2xl border-2 border-dashed border-blue-300">
                        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                          <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                          </svg>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-2">Facebook</h3>
                        <p className="text-sm text-gray-600 mb-4">Connectez votre page Facebook</p>
                        <Button
                          onClick={connectFacebook}
                          disabled={isConnectingSocial}
                          className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
                        >
                          {isConnectingSocial ? '⏳ Connexion...' : '🔗 Connecter'}
                        </Button>
                      </div>

                      {/* Instagram Card */}
                      <div className="text-center p-6 card-glass rounded-2xl border-2 border-dashed border-pink-300">
                        <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                          <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                          </svg>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-2">Instagram</h3>
                        <p className="text-sm text-gray-600 mb-4">Via Facebook Business</p>
                        <Button
                          onClick={connectFacebook}
                          disabled={isConnectingSocial}
                          className="w-full bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700"
                        >
                          {isConnectingSocial ? '⏳ Connexion...' : '🔗 Connecter'}
                        </Button>
                      </div>

                      {/* LinkedIn Card */}
                      <div className="text-center p-6 card-glass rounded-2xl border-2 border-dashed border-blue-300">
                        <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
                          <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                          </svg>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-2">LinkedIn</h3>
                        <p className="text-sm text-gray-600 mb-4">Publiez sur votre profil professionnel</p>
                        <Button
                          onClick={connectLinkedIn}
                          disabled={isConnectingSocial}
                          className="w-full bg-gradient-to-r from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900"
                        >
                          {isConnectingSocial ? '⏳ Connexion...' : '🔗 Connecter'}
                        </Button>
                      </div>
                    </div>

                    <div className="text-center">
                      <h3 className="text-xl font-bold text-gray-900 mb-4">Comment ça fonctionne ? 🤔</h3>
                      <div className="grid md:grid-cols-3 gap-6 text-left">
                        <div className="flex items-start space-x-3">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-blue-600 font-bold text-sm">1</span>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900">Connectez</h4>
                            <p className="text-sm text-gray-600">Cliquez sur "Connecter" et autorisez l'accès</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-purple-600 font-bold text-sm">2</span>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900">Validez</h4>
                            <p className="text-sm text-gray-600">Approuvez vos posts avant publication</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-green-600 font-bold text-sm">3</span>
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900">Publiez</h4>
                            <p className="text-sm text-gray-600">Vos posts sont publiés automatiquement</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="reglages" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center space-x-3 text-2xl">
                      <div className="w-10 h-10 bg-gradient-to-r from-gray-500 to-gray-600 rounded-2xl flex items-center justify-center">
                        <Settings className="w-6 h-6 text-white" />
                      </div>
                      <span>Réglages</span>
                    </CardTitle>
                    <CardDescription>
                      Gérez votre profil, abonnement et paramètres de compte
                    </CardDescription>
                  </div>
                  {/* Always visible payment button */}
                  <Button
                    onClick={() => setShowPaymentPage(true)}
                    className="bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white"
                  >
                    <CreditCard className="w-4 h-4 mr-2" />
                    Voir Abonnements
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* User Profile Section */}
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                      <Building className="w-4 h-4 text-blue-600" />
                    </div>
                    Informations personnelles
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="firstName">Prénom</Label>
                      <Input
                        key="first_name_input"
                        id="firstName"
                        value={user?.first_name || ''}
                        onChange={(e) => handleUserChange('first_name', e.target.value)}
                        className="mt-1"
                        placeholder="Votre prénom"
                      />
                    </div>
                    <div>
                      <Label htmlFor="lastName">Nom</Label>
                      <Input
                        key="last_name_input"
                        id="lastName"
                        value={user?.last_name || ''}
                        onChange={(e) => handleUserChange('last_name', e.target.value)}
                        className="mt-1"
                        placeholder="Votre nom"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        key="email_input"
                        id="email"
                        type="email"
                        value={user?.email || ''}
                        onChange={(e) => handleUserChange('email', e.target.value)}
                        className="mt-1"
                        placeholder="votre@email.com"
                      />
                    </div>
                  </div>
                  <Button className="mt-4 btn-gradient-primary">
                    <Check className="w-4 h-4 mr-2" />
                    Sauvegarder les modifications
                  </Button>
                </div>

                {/* Subscription Section */}
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                      <Crown className="w-4 h-4 text-purple-600" />
                    </div>
                    Abonnement actuel
                  </h3>
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100">
                    <div>
                      <div className="font-semibold text-gray-900">
                        {user?.subscription_plan === 'trial' ? 'Période d\'essai' : 
                         user?.subscription_plan === 'starter' ? 'Plan Starter' :
                         user?.subscription_plan === 'rocket' ? 'Plan Rocket' :
                         user?.subscription_plan === 'pro' ? 'Plan Pro' : 'Plan Gratuit'}
                      </div>
                      <div className="text-sm text-gray-600">
                        {user?.subscription_status === 'trial' ? '1 mois gratuit' :
                         user?.subscription_plan === 'starter' ? '€14.99/mois • 4 posts/mois • 1 réseau' :
                         user?.subscription_plan === 'rocket' ? '€29.99/mois • Posts illimités • Tous réseaux' :
                         user?.subscription_plan === 'pro' ? '€199.99/mois • Multi-comptes • Communautés' : 'Fonctionnalités limitées'}
                      </div>
                    </div>
                    <Badge variant={user?.subscription_status === 'active' ? 'default' : 'secondary'}>
                      {user?.subscription_status === 'active' ? 'Actif' : 
                       user?.subscription_status === 'trial' ? 'Essai' : 'Inactif'}
                    </Badge>
                  </div>
                  <Button className="mt-4 btn-gradient-primary w-full">
                    <CreditCard className="w-4 h-4 mr-2" />
                    Changer d'abonnement
                  </Button>
                </div>

                {/* Payment Method Section */}
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
                      <CreditCard className="w-4 h-4 text-green-600" />
                    </div>
                    Moyen de paiement
                  </h3>
                  <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-6 bg-gradient-to-r from-blue-600 to-blue-800 rounded flex items-center justify-center">
                          <span className="text-xs text-white font-bold">VISA</span>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">•••• •••• •••• 4242</div>
                          <div className="text-sm text-gray-500">Expire 12/25</div>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        Modifier
                      </Button>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="text-sm text-blue-800">
                      💡 <strong>Sécurisé</strong> : Vos données de paiement sont chiffrées et protégées par Stripe.
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Subscription/Upgrade Interface - Now always visible */}
          <div className="mt-8">
            <SubscriptionUpgrade user={user} onUpgradeSuccess={() => window.location.reload()} />
          </div>
        </Tabs>
      </div>

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => {
          const config = window.upgradeModalConfig || { canClose: true };
          if (config.canClose) {
            setShowUpgradeModal(false);
            setUpgradeModalDismissed(true);
          }
        }}
        user={user}
        canClose={window.upgradeModalConfig?.canClose !== false}
        title={window.upgradeModalConfig?.title || "Débloquez Claire et Marcus Premium"}
      />

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
                  onClick={() => navigateToTab('entreprise')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-blue-50 text-left transition-colors group"
                >
                  <Building className="w-5 h-5 text-blue-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Entreprise</span>
                </button>
                <button
                  onClick={() => navigateToTab('bibliotheque')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-purple-50 text-left transition-colors group"
                >
                  <ImageIcon className="w-5 h-5 text-purple-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Bibliothèque</span>
                </button>
                <button
                  onClick={() => navigateToTab('notes')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-green-50 text-left transition-colors group"
                >
                  <FileText className="w-5 h-5 text-green-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Notes</span>
                </button>
                <button
                  onClick={() => navigateToTab('posts')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-orange-50 text-left transition-colors group"
                >
                  <Send className="w-5 h-5 text-orange-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Posts</span>
                </button>
                <button
                  onClick={() => navigateToTab('calendar')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-indigo-50 text-left transition-colors group"
                >
                  <CalendarIcon className="w-5 h-5 text-indigo-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Calendrier</span>
                </button>
                <button
                  onClick={() => navigateToTab('social')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-red-50 text-left transition-colors group"
                >
                  <Target className="w-5 h-5 text-red-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Social</span>
                </button>
                <button
                  onClick={() => navigateToTab('reglages')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-gray-50 text-left transition-colors group"
                >
                  <Settings className="w-5 h-5 text-gray-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Réglages</span>
                </button>
                <button
                  onClick={() => {
                    setShowPaymentPage(true);
                    setShowBurgerMenu(false);
                  }}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-green-50 text-left transition-colors group"
                >
                  <CreditCard className="w-5 h-5 text-green-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Abonnements</span>
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