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

// Content Preview Modal Component - CORRIGÉ selon ChatGPT
const ContentPreviewModal = ({ 
  isOpen, 
  onClose, 
  content, 
  onSaved,
  setPendingContent, // Pour mise à jour optimiste
  refetchSilent, // Pour refetch
  setServerFetchedCount, // NOUVEAU pour reset pagination (ChatGPT)
  loadPendingContent // NOUVEAU pour reload complet (ChatGPT)
}) => {
  const [desc, setDesc] = useState('');
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Hydrater seulement à l'ouverture/changement de média
  useEffect(() => {
    if (isOpen && content) {
      setDesc(content.description || '');
    }
  }, [isOpen, content?.id]);

  const onSave = async () => {
    if (!content) return;
    
    setSaving(true);
    try {
      const response = await fetch(`${API}/content/${content.id}/description`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAccessToken()}`,
        },
        body: JSON.stringify({ description: desc }),
      });

      if (response.ok) {
        const updated = await response.json();
        
        // 1) Mise à jour optimiste immédiate dans la grille (selon ChatGPT)
        setPendingContent(prev =>
          prev.map(item => item.id === content.id ? { ...item, description: updated.description } : item)
        );
        
        toast.success('Commentaire sauvegardé !');
        onSaved?.(updated); // Laisser le parent merger la liste
        onClose(); // Fermer APRÈS succès
        
        // 2) Refetch silencieux pour resynchroniser (selon ChatGPT)
        void refetchSilent();
        
      } else {
        throw new Error('Erreur sauvegarde');
      }
    } catch (error) {
      console.error('❌ Erreur sauvegarde:', error);
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async () => {
    if (!content) return;
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer définitivement ce contenu ?')) return;
    
    setDeleting(true);
    try {
      const response = await fetch(`${API}/content/${content.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`,
        },
      });

      if (response.ok) {
        // Optimiste immédiat en UI (selon ChatGPT)
        setPendingContent(prev => prev.filter(item => item.id !== content.id));
        
        // Mémorise en local (selon ChatGPT)
        const key = 'deleted_content_ids';
        const setDel = new Set(JSON.parse(localStorage.getItem(key) || '[]'));
        setDel.add(content.id);
        localStorage.setItem(key, JSON.stringify([...setDel]));
        
        toast.success('Contenu supprimé définitivement !');
        onSaved?.({ id: content.id, deleted: true });
        onClose();
        
        // RESET pagination serveur et recharge la 1ʳᵉ page (selon ChatGPT)
        setServerFetchedCount(0);
        await loadPendingContent(true /* reset */, false /* keep cache */);
        
      } else {
        throw new Error('Erreur suppression');
      }
    } catch (error) {
      console.error('❌ Erreur suppression:', error);
      toast.error('Erreur lors de la suppression');
    } finally {
      setDeleting(false);
    }
  };

  if (!isOpen || !content) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto relative">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 w-10 h-10 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-colors z-10"
        >
          <X className="w-5 h-5 text-gray-600" />
        </button>

        <div className="p-8">
          {/* Content preview */}
          <div className="mb-6">
            {content.file_type?.startsWith('image/') ? (
              <img 
                src={content.url}
                alt={content.filename}
                className="w-full h-auto max-h-[60vh] object-contain rounded-2xl shadow-lg"
                onError={(e) => {
                  // Fallback for modal images
                  // No further fallback; keep clean UI
                }}
              />
            ) : (
              <div className="w-full h-64 flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100 rounded-2xl">
                <FileText className="w-16 h-16 text-purple-600" />
              </div>
            )}
            
            {/* File info */}
            <div className="mt-4 text-center">
              <h3 className="text-lg font-semibold text-gray-900 truncate">{content.filename}</h3>
              <p className="text-sm text-gray-500">
                {content.file_type} • {(content.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Commentaire (pour génération de posts)
              </label>
              <textarea
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
                placeholder="Ajouter un commentaire utile pour la génération de posts…"
                className="w-full p-3 border border-gray-300 rounded-lg resize-none h-24 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                maxLength={500}
              />
              <div className="text-xs text-gray-500 mt-1">
                {desc.length}/500 caractères
              </div>
            </div>
            
            <div className="mt-3 flex gap-2">
              <Button
                onClick={onSave}
                disabled={saving}
                className="btn-gradient-primary flex-1"
              >
                {saving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Sauvegarde...
                  </>
                ) : (
                  'Sauvegarder le commentaire'
                )}
              </Button>
              
              <Button
                onClick={onDelete}
                disabled={deleting}
                variant="destructive"
                className="bg-red-500 hover:bg-red-600"
              >
                {deleting ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <Trash className="w-4 h-4" />
                )}
              </Button>
            </div>
        </div>
      </div>
    </div>
  );
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
      const token = getAccessToken();
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
      const token = getAccessToken();
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
  
  // User settings save functions (for Réglages tab)
  const saveUserSettings = async (field, value) => {
    try {
      console.log(`💾 Saving user ${field}:`, value);
      
      const response = await axios.put(`${API}/user/settings`, {
        [field]: value
      }, {
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data.success) {
        console.log(`✅ User ${field} saved successfully`);
        toast.success(`${field} sauvegardé`);
        return true;
      } else {
        console.error(`❌ Failed to save user ${field}:`, response.data.message);
        toast.error(`Erreur sauvegarde ${field}`);
        return false;
      }
    } catch (error) {
      console.error(`❌ Error saving user ${field}:`, error);
      toast.error(`Erreur sauvegarde ${field}`);
      return false;
    }
  };

  const loadUserSettings = async () => {
    try {
      const response = await axios.get(`${API}/user/settings`, {
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data) {
        console.log('📋 Loaded user settings:', response.data);
        setEditUserFirstName(response.data.first_name || '');
        setEditUserLastName(response.data.last_name || '');
        setEditUserEmail(response.data.email || '');
        return response.data;
      }
    } catch (error) {
      console.error('❌ Error loading user settings:', error);
      return null;
    }
  };

  // Auto-save function pour sauvegarder un champ spécifique
  const autoSaveField = async (field, value) => {
    try {
      const updatedProfile = { 
        ...businessProfile, 
        [field]: value 
      };
      
      const response = await axios.put(`${API}/business-profile`, updatedProfile, {
        headers: { Authorization: `Bearer ${getAccessToken()}` }
      });
      
      // Mettre à jour businessProfile avec les données de la réponse pour maintenir la cohérence
      if (response.data) {
        setBusinessProfile(response.data);
        // Aussi sauvegarder en localStorage pour la persistance
        saveToLocalStorage(response.data);
      }
      
      // Silent success - no toast to avoid interrupting user
      console.log(`✅ Field ${field} auto-saved successfully and businessProfile updated`);
    } catch (error) {
      console.error(`❌ Auto-save error for field ${field}:`, error);
      // Only show error toast
      toast.error('Erreur lors de la sauvegarde automatique');
    }
  };

  // Détection améliorée pour tous appareils avec clavier virtuel (iOS, iPadOS, Android tablets)
  const detectVirtualKeyboard = () => {
    // Détection iOS/iPadOS robuste (inclut iPadOS 18+ qui peut masquer l'user agent)
    const isVirtualKeyboardDeviceDevice = /iPad|iPhone|iPod/.test(navigator.userAgent) || 
                       (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1) ||
                       /Mac.*OS.*Touch/.test(navigator.userAgent);
    
    // Détection Android tablets et autres appareils tactiles
    const isAndroidTablet = /Android.*Mobile|Android.*Tablet/.test(navigator.userAgent);
    
    // Détection générale d'appareils tactiles
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    // Détection de la taille d'écran typique des tablets/mobiles
    const isSmallScreen = window.innerWidth <= 1024;
    
    return isVirtualKeyboardDeviceDevice || isAndroidTablet || (isTouchDevice && isSmallScreen);
  };
  
  const isVirtualKeyboardDevice = detectVirtualKeyboard();
  
  // Debounced auto-save pour appareils avec clavier virtuel (évite les conflits)
  const debounceTimers = useRef({});
  
  const debouncedAutoSave = useCallback((field, value, delay = 1000) => {
    if (debounceTimers.current[field]) {
      clearTimeout(debounceTimers.current[field]);
    }
    
    debounceTimers.current[field] = setTimeout(() => {
      autoSaveField(field, value);
    }, delay);
  }, []);

  // Approche RADICALE: Inputs complètement non contrôlés pour appareils virtuels
  // Aucun gestionnaire d'événement pendant la saisie - seulement onBlur pour la sauvegarde
  const handleVirtualKeyboardRefBlur = useCallback((field, ref) => {
    if (ref && ref.current) {
      const value = ref.current.value;
      console.log(`💾 Saving virtual keyboard ${field} on blur:`, value);
      
      // Synchroniser avec localStorage
      const currentData = loadFromLocalStorage() || {};
      currentData[field] = value;
      saveToLocalStorage(currentData);
      
      // Sauvegarder en base de données
      autoSaveField(field, value);
    }
  }, []);

  // Gestionnaire pour desktop (état contrôlé normal)
  const handleFieldChange = useCallback((field, value, setterFunction) => {
    setterFunction(value);
    syncFieldWithStorage(field, value, setterFunction);
    console.log(`🖥️ Desktop Field ${field} changed:`, value);
    console.log(`🔍 localStorage after change:`, loadFromLocalStorage());
  }, []);

  const handleFieldBlur = useCallback((field, value) => {
    console.log(`💾 Saving desktop field ${field} on blur:`, value);
    
    // Synchroniser avec localStorage pour la persistance
    const currentData = loadFromLocalStorage() || {};
    currentData[field] = value;
    saveToLocalStorage(currentData);
    
    // Sauvegarder en base de données
    autoSaveField(field, value);
  }, []);

  // Gestionnaire spécial pour les Notes sur clavier virtuel
  const handleNotesVirtualKeyboardRefChange = useCallback((field, ref, setterFunction) => {
    if (ref && ref.current) {
      const value = ref.current.value;
      // Pour les notes, on met aussi à jour l'état React car il est utilisé ailleurs
      if (setterFunction) {
        setterFunction(value);
      }
      console.log(`📝 Note ${field} updated:`, value);
    }
  }, []);

  // Gestionnaire pour Notes avec support clavier virtuel/Desktop - VERSION CORRIGÉE
  const handleNoteFieldChange = useCallback((field, value, setterFunction, ref = null) => {
    if (isVirtualKeyboardDevice && ref && ref.current) {
      // Pour appareils avec clavier virtuel, la valeur vient du ref
      const actualValue = ref.current.value;
      setterFunction(actualValue);
      console.log(`📱 Virtual keyboard Note ${field}:`, actualValue);
      // PAS d'auto-save sur onChange, uniquement localStorage
    } else {
      // Pour Desktop, utiliser la valeur normale
      setterFunction(value);
      console.log(`🖥️ Desktop Note ${field}:`, value);
      // PAS d'auto-save sur onChange pour éviter le bug clavier
    }
  }, [isVirtualKeyboardDevice]);

  // Gestionnaire onBlur pour les notes
  const handleNoteFieldBlur = useCallback((field, ref, value = null) => {
    let actualValue;
    if (isVirtualKeyboardDevice && ref && ref.current) {
      actualValue = ref.current.value;
    } else {
      actualValue = value;
    }
    console.log(`💾 Saving note ${field} on blur:`, actualValue);
    
    // Sauvegarder en localStorage pour éviter la perte de données
    const currentData = loadFromLocalStorage() || {};
    currentData[`note_${field}`] = actualValue;
    saveToLocalStorage(currentData);
    
    // Mettre à jour l'état React aussi
    if (field === 'title') {
      setNoteTitle(actualValue);
    } else if (field === 'content') {
      setNoteContent(actualValue);
    }
  }, [isVirtualKeyboardDevice]);

  // Auto-save function
  const autoSaveProfile = async (updatedProfile) => {
    try {
      const response = await axios.put(`${API}/business-profile`, updatedProfile, {
        headers: { Authorization: `Bearer ${getAccessToken()}` }
      });
      
      if (response.data && response.data.business_name) {
        setBusinessProfile(response.data);
      }
      
      // Silent success - no toast to avoid interrupting user
      console.log('✅ Profile auto-saved successfully');
    } catch (error) {
      console.error('❌ Auto-save error:', error);
      // Only show error toast
      toast.error('Erreur lors de la sauvegarde automatique');
    }
  };

  // Active step state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeStep, setActiveStep] = useState('dashboard'); // FORCE DASHBOARD DIRECTLY
  
  // Business profile state
  const [businessProfile, setBusinessProfile] = useState(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  
  // Content and posts state
  const [pendingContent, setPendingContent] = useState([]);
  const [contentTotalCount, setContentTotalCount] = useState(0);
  const [contentHasMore, setContentHasMore] = useState(false);
  // NOUVEAU : compteur de ce que le SERVEUR a déjà renvoyé (selon ChatGPT)
  const [serverFetchedCount, setServerFetchedCount] = useState(0);
  const [contentLoading, setContentLoading] = useState(false);
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
    hashtags_primary: [],
    hashtags_secondary: [],
    budget_range: '',
    website_url: ''
  });
  
  // Note form - REFS pour iOS (bypass React state)
  const noteTitleRef = useRef(null);
  const noteContentRef = useRef(null);
  
  // Note form - STATES SÉPARÉS pour Desktop
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [notePriority, setNotePriority] = useState('medium');
  
  // Business profile editing - REFS pour iOS (bypass React state)
  const businessNameRef = useRef(null);
  const businessTypeRef = useRef(null);
  const businessDescriptionRef = useRef(null);
  const targetAudienceRef = useRef(null);
  const emailRef = useRef(null);
  const websiteUrlRef = useRef(null);
  const budgetRangeRef = useRef(null);
  const brandToneRef = useRef(null);
  
  // Business profile editing - STATES SÉPARÉS pour Desktop
  const [editBusinessName, setEditBusinessName] = useState('');
  const [editBusinessType, setEditBusinessType] = useState('');
  const [editBusinessDescription, setEditBusinessDescription] = useState('');
  const [editTargetAudience, setEditTargetAudience] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editWebsiteUrl, setEditWebsiteUrl] = useState('');
  const [editBudgetRange, setEditBudgetRange] = useState('');
  
  // User profile editing - STATES SÉPARÉS pour éviter le bug clavier
  const [editUserFirstName, setEditUserFirstName] = useState('');
  const [editUserLastName, setEditUserLastName] = useState('');
  const [editUserEmail, setEditUserEmail] = useState('');
  
  // UI states
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isGeneratingPosts, setIsGeneratingPosts] = useState(false);
  const [isConnectingSocial, setIsConnectingSocial] = useState(false);
  const [websiteAnalysis, setWebsiteAnalysis] = useState(null);
  const [isAnalyzingWebsite, setIsAnalyzingWebsite] = useState(false);
  const [showWebsiteAnalysis, setShowWebsiteAnalysis] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState(''); // 'analyzing', 'success', 'error', 'interrupted'
  const [analysisMessage, setAnalysisMessage] = useState('');
  const [lastAnalysisDate, setLastAnalysisDate] = useState(null);
  const [websiteUrlForAnalysis, setWebsiteUrlForAnalysis] = useState(''); // Champ invisible pour l'analyse
  const [isWebsiteFieldProtected, setIsWebsiteFieldProtected] = useState(false); // Protection contre les re-renders
  const [showBurgerMenu, setShowBurgerMenu] = useState(false);
  const [activeTab, setActiveTab] = useState('entreprise');
  
  // Content preview modal states - Source de vérité unique
  const [selectedContent, setSelectedContent] = useState(null);
  const [contentDescription, setContentDescription] = useState('');
  const [isSavingDescription, setIsSavingDescription] = useState(false);
  const [isDeletingContent, setIsDeletingContent] = useState(false);
  
  // Multiple selection states
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [selectedContentIds, setSelectedContentIds] = useState([]);
  const [isDeletingMultiple, setIsDeletingMultiple] = useState(false);
  
  // Content description ref for virtual keyboard compatibility
  const contentDescriptionRef = useRef(null);
  
  // Système de verrouillage d'édition avec bouton crayon/coche pour tous les champs
  const [isEditingBusinessName, setIsEditingBusinessName] = useState(false);
  const [tempBusinessName, setTempBusinessName] = useState('');
  const [isSavingBusinessName, setIsSavingBusinessName] = useState(false);
  
  const [isEditingBusinessType, setIsEditingBusinessType] = useState(false);
  const [tempBusinessType, setTempBusinessType] = useState('');
  const [isSavingBusinessType, setIsSavingBusinessType] = useState(false);
  
  const [isEditingBusinessDescription, setIsEditingBusinessDescription] = useState(false);
  const [tempBusinessDescription, setTempBusinessDescription] = useState('');
  const [isSavingBusinessDescription, setIsSavingBusinessDescription] = useState(false);
  
  const [isEditingTargetAudience, setIsEditingTargetAudience] = useState(false);
  const [tempTargetAudience, setTempTargetAudience] = useState('');
  const [isSavingTargetAudience, setIsSavingTargetAudience] = useState(false);
  
  const [isEditingEmail, setIsEditingEmail] = useState(false);
  const [tempEmail, setTempEmail] = useState('');
  const [isSavingEmail, setIsSavingEmail] = useState(false);
  
  const [isEditingWebsiteUrl, setIsEditingWebsiteUrl] = useState(false);
  const [tempWebsiteUrl, setTempWebsiteUrl] = useState('');
  const [isSavingWebsiteUrl, setIsSavingWebsiteUrl] = useState(false);
  
  const [isEditingBudgetRange, setIsEditingBudgetRange] = useState(false);
  const [tempBudgetRange, setTempBudgetRange] = useState('');
  const [isSavingBudgetRange, setIsSavingBudgetRange] = useState(false);
  
  const [isEditingBrandTone, setIsEditingBrandTone] = useState(false);
  const [tempBrandTone, setTempBrandTone] = useState('');
  const [isSavingBrandTone, setIsSavingBrandTone] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeModalDismissed, setUpgradeModalDismissed] = useState(false);
  
  // Hashtag management
  const [newPrimaryHashtag, setNewPrimaryHashtag] = useState('');
  const [newSecondaryHashtag, setNewSecondaryHashtag] = useState('');

  // Force reload business profile and notes with localStorage support
  const forceLoadBusinessProfileAndNotes = useCallback(async () => {
    console.log('🔄 Force loading business profile and notes');
    
    // First restore from localStorage for immediate response
    restoreFieldsFromStorage();
    
    // Then fetch fresh data from database after a delay
    setTimeout(async () => {
      try {
        const response = await axios.get(`${API}/business-profile`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        
        console.log('✅ Fresh data loaded from backend');
        setBusinessProfile(response.data);
        
        // Always sync fresh backend data to localStorage to prevent stale cache
        console.log('🔄 Syncing fresh backend data to localStorage');
        saveToLocalStorage(response.data);
        
        // Force update all fields with fresh backend data to override any stale values
        if (isVirtualKeyboardDevice) {
          // Update refs for virtual keyboard devices
          setTimeout(() => {
            if (businessNameRef.current) businessNameRef.current.value = response.data.business_name || '';
            if (businessDescriptionRef.current) businessDescriptionRef.current.value = response.data.business_description || '';
            if (targetAudienceRef.current) targetAudienceRef.current.value = response.data.target_audience || '';
            if (emailRef.current) emailRef.current.value = response.data.email || '';
            if (websiteUrlRef.current) websiteUrlRef.current.value = response.data.website_url || '';
            if (budgetRangeRef.current) budgetRangeRef.current.value = response.data.budget_range || '';
            console.log('✅ Virtual keyboard refs updated with fresh data');
          }, 100);
        } else {
          // Update states for desktop
          setEditBusinessName(response.data.business_name || '');
          setEditBusinessDescription(response.data.business_description || '');
          setEditTargetAudience(response.data.target_audience || '');
          setEditEmail(response.data.email || '');
          setEditWebsiteUrl(response.data.website_url || '');
          setEditBudgetRange(response.data.budget_range || '');
          console.log('✅ Desktop states updated with fresh data');
        }
        
        setEditBusinessType(response.data.business_type || '');
        
        // Reload notes as well
        await loadNotes();
        
      } catch (error) {
        console.error('❌ Error force loading business profile:', error);
      }
    }, 1000); // 1 second delay for smooth UX
  }, [isVirtualKeyboardDevice]);

  // Enhanced virtual keyboard event handlers
  useEffect(() => {
    if (!isVirtualKeyboardDevice) return;
    
    const handleResize = () => {
      // Ajuster la hauteur du body dynamiquement pour les PWA sur iPad
      document.body.style.height = `${window.innerHeight}px`;
      
      // Scroll to focused input when keyboard appears/disappears
      const activeElement = document.activeElement;
      if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
        setTimeout(() => {
          activeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
      }
    };
    
    const handleFocusIn = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        // Add specific class for focused state
        e.target.classList.add('virtual-keyboard-focused');
        
        // Ajuster la hauteur immédiatement
        document.body.style.height = `${window.innerHeight}px`;
        
        // Ensure element is visible above keyboard
        setTimeout(() => {
          e.target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
      }
    };
    
    const handleFocusOut = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        e.target.classList.remove('virtual-keyboard-focused');
        
        // Restaurer la hauteur normale
        setTimeout(() => {
          document.body.style.height = '100vh';
        }, 300);
      }
    };
    
    // Add event listeners
    window.addEventListener('resize', handleResize);
    document.addEventListener('focusin', handleFocusIn);
    document.addEventListener('focusout', handleFocusOut);
    
    // Initialiser la hauteur
    document.body.style.height = `${window.innerHeight}px`;
    
    return () => {
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('focusin', handleFocusIn);
      document.removeEventListener('focusout', handleFocusOut);
      
      // Restaurer la hauteur normale
      document.body.style.height = '100vh';
    };
  }, [isVirtualKeyboardDevice]);

  // Restaurer les données depuis localStorage au chargement ET forcer le rechargement depuis la DB
  useEffect(() => {
    if (isAuthenticated && user) {
      console.log('🔄 Utilisateur connecté, restauration localStorage + rechargement DB');
      
      // D'abord restaurer depuis localStorage pour une réponse immédiate
      restoreFieldsFromStorage();
      
      // Charger les notes immédiatement
      console.log('🔄 Loading notes for authenticated user');
      loadNotes();
      
      // CRITIQUE: Charger le contenu de la bibliothèque immédiatement
      console.log('📚 Loading pending content for authenticated user');
      loadPendingContent(true, false); // Reset and load fresh content
      
      // Puis recharger depuis la DB pour s'assurer que les données sont à jour
      setTimeout(async () => {
        if (!businessProfile) {
          console.log('📡 Force loading business profile from database');
          loadBusinessProfile();
        } else {
          console.log('📡 Force refresh business profile from database');
          const forceRefreshProfile = async () => {
            try {
              const response = await axios.get(`${API}/business-profile`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
              });
              console.log('🔄 Fresh data from DB:', response.data);
              setBusinessProfile(response.data);
              
              // ✅ IMPORTANT: Sauvegarder aussi en localStorage pour la persistance
              saveToLocalStorage(response.data);
              
              // Re-sync avec localStorage ET champs
              if (isVirtualKeyboardDevice) {
                setTimeout(() => {
                  if (businessNameRef.current) {
                    const dbValue = response.data.business_name || '';
                    const currentValue = businessNameRef.current.value;
                    const localValue = loadFromLocalStorage()?.business_name || '';
                    businessNameRef.current.value = dbValue || currentValue || localValue;
                    // Sync only if we have a meaningful value
                    if (businessNameRef.current.value) {
                      syncFieldWithStorage('business_name', businessNameRef.current.value);
                    }
                  }
                  if (businessTypeRef.current) {
                    const dbValue = response.data.business_type || '';
                    const currentValue = businessTypeRef.current.value;
                    const localValue = loadFromLocalStorage()?.business_type || '';
                    businessTypeRef.current.value = dbValue || currentValue || localValue;
                    if (businessTypeRef.current.value) {
                      syncFieldWithStorage('business_type', businessTypeRef.current.value);
                    }
                  }
                  if (businessDescriptionRef.current) {
                    const dbValue = response.data.business_description || '';
                    const currentValue = businessDescriptionRef.current.value;
                    const localValue = loadFromLocalStorage()?.business_description || '';
                    businessDescriptionRef.current.value = dbValue || currentValue || localValue;
                    if (businessDescriptionRef.current.value) {
                      syncFieldWithStorage('business_description', businessDescriptionRef.current.value);
                    }
                  }
                  if (targetAudienceRef.current) {
                    const dbValue = response.data.target_audience || '';
                    const currentValue = targetAudienceRef.current.value;
                    const localValue = loadFromLocalStorage()?.target_audience || '';
                    targetAudienceRef.current.value = dbValue || currentValue || localValue;
                    if (targetAudienceRef.current.value) {
                      syncFieldWithStorage('target_audience', targetAudienceRef.current.value);
                    }
                  }
                  if (emailRef.current) {
                    const dbValue = response.data.email || '';
                    const currentValue = emailRef.current.value;
                    const localValue = loadFromLocalStorage()?.email || '';
                    emailRef.current.value = dbValue || currentValue || localValue;
                    if (emailRef.current.value) {
                      syncFieldWithStorage('email', emailRef.current.value);
                    }
                  }
                  if (websiteUrlRef.current) {
                    const dbValue = response.data.website_url || '';
                    const currentValue = websiteUrlRef.current.value;
                    const localValue = loadFromLocalStorage()?.website_url || '';
                    websiteUrlRef.current.value = dbValue || currentValue || localValue;
                    if (websiteUrlRef.current.value) {
                      syncFieldWithStorage('website_url', websiteUrlRef.current.value);
                    }
                  }
                  if (budgetRangeRef.current) {
                    const dbValue = response.data.budget_range || '';
                    const currentValue = budgetRangeRef.current.value;
                    const localValue = loadFromLocalStorage()?.budget_range || '';
                    budgetRangeRef.current.value = dbValue || currentValue || localValue;
                    if (budgetRangeRef.current.value) {
                      syncFieldWithStorage('budget_range', budgetRangeRef.current.value);
                    }
                  }
                  console.log('✅ Virtual keyboard refs synced with best available data (DB → Current → LocalStorage)');
                }, 100);
              } else {
                // Desktop mode - preserve data with priority: DB → Current → LocalStorage
                const currentData = loadFromLocalStorage() || {};
                
                const businessName = response.data.business_name || editBusinessName || currentData.business_name || '';
                const businessDescription = response.data.business_description || editBusinessDescription || currentData.business_description || '';
                const targetAudience = response.data.target_audience || editTargetAudience || currentData.target_audience || '';
                const email = response.data.email || editEmail || currentData.email || '';
                const websiteUrl = response.data.website_url || editWebsiteUrl || currentData.website_url || '';
                const budgetRange = response.data.budget_range || editBudgetRange || currentData.budget_range || '';
                
                setEditBusinessName(businessName);
                setEditBusinessDescription(businessDescription);
                setEditTargetAudience(targetAudience);
                setEditEmail(email);
                setEditWebsiteUrl(websiteUrl);
                setEditBudgetRange(budgetRange);
                
                // Sync to localStorage only if we have meaningful values
                if (businessName) syncFieldWithStorage('business_name', businessName);
                if (businessDescription) syncFieldWithStorage('business_description', businessDescription);
                if (targetAudience) syncFieldWithStorage('target_audience', targetAudience);
                if (email) syncFieldWithStorage('email', email);
                if (websiteUrl) syncFieldWithStorage('website_url', websiteUrl);
                if (budgetRange) syncFieldWithStorage('budget_range', budgetRange);
                
                console.log('✅ Desktop states synced with best available data (DB → Current → LocalStorage)');
              }
              
              // Business type (works for both desktop and virtual keyboard)
              const businessType = response.data.business_type || editBusinessType || loadFromLocalStorage()?.business_type || '';
              setEditBusinessType(businessType);
              if (businessType) {
                syncFieldWithStorage('business_type', businessType);
              }
              
              // Only update localStorage with actual data, not empty database response
              const meaningfulData = Object.keys(response.data).reduce((acc, key) => {
                if (response.data[key]) {  // Only include non-empty values
                  acc[key] = response.data[key];
                }
                return acc;
              }, {});
              
              if (Object.keys(meaningfulData).length > 0) {
                console.log('✅ Updating localStorage with meaningful database data:', meaningfulData);
                // Merge with existing localStorage data, don't overwrite everything
                const existingData = loadFromLocalStorage() || {};
                saveToLocalStorage({ ...existingData, ...meaningfulData });
              } else {
                console.log('⚠️ Database returned empty data, preserving localStorage');
              }
            } catch (error) {
              console.error('❌ Error force refreshing profile:', error);
            }
          };
          forceRefreshProfile();
        }
      }, 1000); // Délai de 1 seconde pour laisser le temps à localStorage de se charger
    }
  }, [isAuthenticated, user]);

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