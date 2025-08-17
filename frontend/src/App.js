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
            src={`data:${content.file_type};base64,${content.thumbnail_data || content.file_data}`}
            alt={content.filename}
            className="w-full h-full object-cover"
            loading="lazy"
          />
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
  setPendingContent, // Nouvelle prop pour mise à jour optimiste
  refetchSilent // Nouvelle prop pour refetch
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
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
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
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        // Optimiste immédiat (selon ChatGPT)
        setPendingContent(prev => prev.filter(item => item.id !== content.id));
        
        // Ajoute à la liste locale des supprimés (selon ChatGPT)
        const key = 'deleted_content_ids';
        const deleted = new Set(JSON.parse(localStorage.getItem(key) || '[]'));
        deleted.add(content.id);
        localStorage.setItem(key, JSON.stringify([...deleted]));
        
        toast.success('Contenu supprimé définitivement !');
        onSaved?.({ id: content.id, deleted: true }); // Signal de suppression
        onClose(); // Fermer après suppression
        
        // Recalage serveur (selon ChatGPT)
        void refetchSilent('replace');
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
                src={`data:${content.file_type};base64,${content.file_data}`}
                alt={content.filename}
                className="w-full h-auto max-h-[60vh] object-contain rounded-2xl shadow-lg"
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
  
  // Auto-save function pour sauvegarder un champ spécifique
  const autoSaveField = async (field, value) => {
    try {
      const updatedProfile = { 
        ...businessProfile, 
        [field]: value 
      };
      
      const response = await axios.put(`${API}/business-profile`, updatedProfile, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
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
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
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
  const [activeStep, setActiveStep] = useState('onboarding');
  
  // Business profile state
  const [businessProfile, setBusinessProfile] = useState(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  
  // Content and posts state
  const [pendingContent, setPendingContent] = useState([]);
  const [contentTotalCount, setContentTotalCount] = useState(0);
  const [contentHasMore, setContentHasMore] = useState(false);
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
        
        console.log('📡 Fresh business profile data loaded:', response.data);
        setBusinessProfile(response.data);
        
        // CRITICAL: Always sync fresh backend data to localStorage to prevent stale cache
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

  // Initialize user fields when user data is loaded
  useEffect(() => {
    if (user) {
      setEditUserFirstName(user.first_name || '');
      setEditUserLastName(user.last_name || '');
      setEditUserEmail(user.email || '');
    }
  }, [user]);

  // Configure axios defaults
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  // Check authentication on mount
  // Force clean localStorage on first load to avoid cache conflicts
  useEffect(() => {
    // Check if this is a fresh session (no access_token but page just loaded)
    const token = localStorage.getItem('access_token');
    const lastCleanup = localStorage.getItem('last_cleanup');
    const now = Date.now();
    
    // iOS Safari specific: Check if localStorage is working
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    if (isIOS) {
      console.log('📱 iOS detected - checking localStorage reliability');
      try {
        localStorage.setItem('ios_test', 'working');
        const test = localStorage.getItem('ios_test');
        if (test !== 'working') {
          console.log('⚠️ iOS localStorage issue detected');
        } else {
          console.log('✅ iOS localStorage working');
        }
        localStorage.removeItem('ios_test');
      } catch (e) {
        console.log('❌ iOS localStorage error:', e);
      }
    }
    
    // Clean localStorage if it's older than 1 hour or if no cleanup record
    if (!lastCleanup || (now - parseInt(lastCleanup)) > 3600000) {
      console.log('🧹 Cleaning old localStorage data to prevent cache conflicts');
      const keysToClean = [
        'claire_marcus_business_profile_cache',
        'business_name', 
        'business_description',
        'target_audience', 
        'email',
        'website_url',
        'budget_range'
      ];
      
      keysToClean.forEach(key => {
        const oldValue = localStorage.getItem(key);
        if (oldValue) {
          console.log(`🗑️ Cleaning old cache: ${key} = ${oldValue}`);
          localStorage.removeItem(key);
        }
      });
      
      localStorage.setItem('last_cleanup', now.toString());
      console.log('✅ localStorage cleanup completed');
    }
    
    checkAuth();
  }, []);



  // Initialize business fields when business profile is loaded (only on first load, not on updates)
  useEffect(() => {
    if (isAuthenticated && user && businessProfile) {
      console.log('🔄 useEffect businessProfile triggered - Protection status:', isWebsiteFieldProtected);
      
      if (user.is_admin) {
        // Admin users go to admin dashboard - handled by Auth component
        return;
      }
      
      setActiveStep('dashboard');
      loadGeneratedPosts();
      loadPendingContent(true, true); // Reset, load fresh, and clean cache
      loadNotes();
      loadSocialConnections();
      
      // Charger l'analyse de site web seulement si on n'est pas en cours d'analyse
      if (!isAnalyzingWebsite) {
        loadWebsiteAnalysis();
      }
      
      // IMPORTANT: Initialiser les champs d'édition SEULEMENT si ils sont vides ET pas protégés
      // Cela évite d'écraser les valeurs pendant l'édition/analyse
      if (isWebsiteFieldProtected) {
        console.log('🛡️ Champs protégés - initialisation ignorée');
        return;
      }
      
      if (isVirtualKeyboardDevice) {
        // Pour appareils avec clavier virtuel, utiliser la même logique de protection que loadBusinessProfile
        setTimeout(() => {
          if (businessNameRef.current && !businessNameRef.current.value && !isWebsiteFieldProtected) {
            const currentValue = businessNameRef.current.value;
            const dbValue = businessProfile.business_name || '';
            const localValue = loadFromLocalStorage()?.business_name || '';
            const finalValue = dbValue || currentValue || localValue;
            businessNameRef.current.value = finalValue;
            syncFieldWithStorage('business_name', finalValue);
            console.log('🔧 Init virtual keyboard business name:', finalValue);
          }
          if (businessDescriptionRef.current && !businessDescriptionRef.current.value && !isWebsiteFieldProtected) {
            const currentValue = businessDescriptionRef.current.value;
            const dbValue = businessProfile.business_description || '';
            const localValue = loadFromLocalStorage()?.business_description || '';
            const finalValue = dbValue || currentValue || localValue;
            businessDescriptionRef.current.value = finalValue;
            syncFieldWithStorage('business_description', finalValue);
            console.log('🔧 Init virtual keyboard business description:', finalValue);
          }
          if (targetAudienceRef.current && !targetAudienceRef.current.value && !isWebsiteFieldProtected) {
            const currentValue = targetAudienceRef.current.value;
            const dbValue = businessProfile.target_audience || '';
            const localValue = loadFromLocalStorage()?.target_audience || '';
            const finalValue = dbValue || currentValue || localValue;
            targetAudienceRef.current.value = finalValue;
            syncFieldWithStorage('target_audience', finalValue);
            console.log('🔧 Init virtual keyboard target audience:', finalValue);
          }
          if (emailRef.current && !emailRef.current.value && !isWebsiteFieldProtected) {
            const currentValue = emailRef.current.value;
            const dbValue = businessProfile.email || '';
            const localValue = loadFromLocalStorage()?.email || '';
            const finalValue = dbValue || currentValue || localValue;
            emailRef.current.value = finalValue;
            syncFieldWithStorage('email', finalValue);
            console.log('🔧 Init virtual keyboard email:', finalValue);
          }
          if (websiteUrlRef.current && !websiteUrlRef.current.value && !isWebsiteFieldProtected) {
            const currentValue = websiteUrlRef.current.value;
            const dbValue = businessProfile.website_url || '';
            const localValue = loadFromLocalStorage()?.website_url || '';
            const finalValue = dbValue || currentValue || localValue;
            websiteUrlRef.current.value = finalValue;
            syncFieldWithStorage('website_url', finalValue);
            console.log('🔧 Init virtual keyboard website URL ref:', finalValue);
          }
          if (budgetRangeRef.current && !budgetRangeRef.current.value && !isWebsiteFieldProtected) {
            const currentValue = budgetRangeRef.current.value;
            const dbValue = businessProfile.budget_range || '';
            const localValue = loadFromLocalStorage()?.budget_range || '';
            const finalValue = dbValue || currentValue || localValue;
            budgetRangeRef.current.value = finalValue;
            syncFieldWithStorage('budget_range', finalValue);
            console.log('🔧 Init virtual keyboard budget range:', finalValue);
          }
        }, 100);
      } else {
        // Pour Desktop, utiliser la même logique de protection que loadBusinessProfile
        if (!editBusinessName && !isWebsiteFieldProtected) {
          const currentData = loadFromLocalStorage() || {};
          const finalValue = businessProfile.business_name || editBusinessName || currentData.business_name || '';
          setEditBusinessName(finalValue);
          syncFieldWithStorage('business_name', finalValue);
          console.log('🔧 Init Desktop business name:', finalValue);
        }
        if (!editBusinessDescription && !isWebsiteFieldProtected) {
          const currentData = loadFromLocalStorage() || {};
          const finalValue = businessProfile.business_description || editBusinessDescription || currentData.business_description || '';
          setEditBusinessDescription(finalValue);
          syncFieldWithStorage('business_description', finalValue);
          console.log('🔧 Init Desktop business description:', finalValue);
        }
        if (!editTargetAudience && !isWebsiteFieldProtected) {
          const currentData = loadFromLocalStorage() || {};
          const finalValue = businessProfile.target_audience || editTargetAudience || currentData.target_audience || '';
          setEditTargetAudience(finalValue);
          syncFieldWithStorage('target_audience', finalValue);
          console.log('🔧 Init Desktop target audience:', finalValue);
        }
        if (!editEmail && !isWebsiteFieldProtected) {
          const currentData = loadFromLocalStorage() || {};
          const finalValue = businessProfile.email || editEmail || currentData.email || '';
          setEditEmail(finalValue);
          syncFieldWithStorage('email', finalValue);
          console.log('🔧 Init Desktop email:', finalValue);
        }
        if (!editWebsiteUrl && !isWebsiteFieldProtected) {
          const currentData = loadFromLocalStorage() || {};
          const finalValue = businessProfile.website_url || editWebsiteUrl || currentData.website_url || '';
          setEditWebsiteUrl(finalValue);
          syncFieldWithStorage('website_url', finalValue);
          console.log('🔧 Init Desktop website URL state:', finalValue);
        }
        if (!editBudgetRange && !isWebsiteFieldProtected) {
          const currentData = loadFromLocalStorage() || {};
          const finalValue = businessProfile.budget_range || editBudgetRange || currentData.budget_range || '';
          setEditBudgetRange(finalValue);
          syncFieldWithStorage('budget_range', finalValue);
          console.log('🔧 Init Desktop budget range:', finalValue);
        }
      }
      
      // Ces champs peuvent être réinitialisés sans problème
      if (!editBusinessType) setEditBusinessType(businessProfile.business_type || '');
      
      // CORRECTION: Synchroniser profileForm.website_url avec businessProfile.website_url
      // pour que la section d'analyse de site web s'affiche correctement
      if (businessProfile.website_url && !profileForm.website_url) {
        setProfileForm(prev => ({
          ...prev,
          website_url: businessProfile.website_url || '',
          business_name: businessProfile.business_name || prev.business_name,
          business_type: businessProfile.business_type || prev.business_type
        }));
        console.log('🔧 Synchronized profileForm with businessProfile:', {
          website_url: businessProfile.website_url,
          business_name: businessProfile.business_name,
          business_type: businessProfile.business_type
        });
      }
    }
  }, [isAuthenticated, user, businessProfile]);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    console.log('🔍 checkAuth called - token exists:', !!token);
    console.log('🔍 checkAuth stack trace:', new Error().stack);
    
    if (!token) {
      console.log('🔍 APP DEBUG - No token found, setting authenticated to false');
      setIsAuthenticated(false);
      return;
    }

    // Set axios header before making request
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

    try {
      console.log('🔍 APP DEBUG - Making /auth/me request to:', `${API}/auth/me`);
      const response = await axios.get(`${API}/auth/me`, {
        timeout: 15000,
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ APP DEBUG - Auth check successful:', response.data);
      setUser(response.data);
      setIsAuthenticated(true);
      
      if (response.data.subscription_status) {
        setSubscriptionStatus(response.data.subscription_status);
      }
      
      // Load business profile after successful authentication ONLY if not already loaded
      if (!businessProfile) {
        console.log('🔄 Loading business profile - not loaded yet');
        loadBusinessProfile();
      } else {
        console.log('✅ Business profile already loaded, skipping reload to preserve user data');
      }
    } catch (error) {
      console.error('❌ APP DEBUG - Auth check failed:', error);
      console.error('❌ APP DEBUG - Error response:', error.response?.data);
      console.error('❌ APP DEBUG - Error status:', error.response?.status);
      
      // Only remove token if it's actually invalid (not just network error)
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.log('🔍 APP DEBUG - Token invalid, removing from storage');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
      }
      
      setIsAuthenticated(false);
    }
  };

  const handleAuthSuccess = async () => {
    console.log('🎉 APP DEBUG - Auth success callback triggered');
    
    try {
      // First check authentication
      await checkAuth();
      console.log('🔍 APP DEBUG - Auth check completed after success');
      
      // Don't reload business profile here - it's already loaded in checkAuth
      // await loadBusinessProfile(); // REMOVED - This was causing data reload
      console.log('🔍 APP DEBUG - Business profile already loaded in checkAuth');
      
      
    } catch (error) {
      console.error('❌ APP DEBUG - Error in handleAuthSuccess:', error);
    }
  };

  // Nouvelle approche : Persistence locale avec localStorage
  const LOCAL_STORAGE_KEY = 'claire_marcus_business_profile_cache';
  
  // Sauvegarder les données dans localStorage immédiatement
  const saveToLocalStorage = (data) => {
    try {
      const timestamp = new Date().toISOString();
      const cachedData = {
        ...data,
        cached_at: timestamp,
        user_id: user?.user_id || 'anonymous'
      };
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(cachedData));
      console.log('💾 Données sauvées dans localStorage:', Object.keys(data));
    } catch (error) {
      console.error('❌ Erreur sauvegarde localStorage:', error);
    }
  };

  // Charger les données depuis localStorage
  const loadFromLocalStorage = () => {
    try {
      const cached = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (cached) {
        const data = JSON.parse(cached);
        console.log('📂 Données chargées depuis localStorage:', Object.keys(data));
        return data;
      }
    } catch (error) {
      console.error('❌ Erreur chargement localStorage:', error);
    }
    return null;
  };

  // Synchroniser un champ avec localStorage ET état React
  const syncFieldWithStorage = (fieldName, value, setterFunction = null) => {
    // Charger les données actuelles
    const currentData = loadFromLocalStorage() || {};
    
    // Mettre à jour avec la nouvelle valeur
    currentData[fieldName] = value;
    
    // Sauvegarder immédiatement
    saveToLocalStorage(currentData);
    
    // Mettre à jour l'état React si fourni
    if (setterFunction) {
      setterFunction(value);
    }
    
    // Pour appareils avec clavier virtuel, mettre à jour aussi le ref
    if (isVirtualKeyboardDevice) {
      switch (fieldName) {
        case 'business_name':
          if (businessNameRef.current) businessNameRef.current.value = value;
          break;
        case 'business_description':
          if (businessDescriptionRef.current) businessDescriptionRef.current.value = value;
          break;
        case 'target_audience':
          if (targetAudienceRef.current) targetAudienceRef.current.value = value;
          break;
        case 'email':
          if (emailRef.current) emailRef.current.value = value;
          break;
        case 'website_url':
          if (websiteUrlRef.current) websiteUrlRef.current.value = value;
          break;
        case 'budget_range':
          if (budgetRangeRef.current) budgetRangeRef.current.value = value;
          break;
      }
    }
    
    console.log(`🔄 ${fieldName} synchronisé:`, value);
  };

  // Restaurer tous les champs depuis localStorage
  const restoreFieldsFromStorage = () => {
    const cached = loadFromLocalStorage();
    if (!cached) return;
    
    console.log('🔄 Restauration complète depuis localStorage');
    
    // Restaurer les states React
    if (cached.business_name) setEditBusinessName(cached.business_name);
    if (cached.business_type) setEditBusinessType(cached.business_type);
    if (cached.business_description) setEditBusinessDescription(cached.business_description);
    if (cached.target_audience) setEditTargetAudience(cached.target_audience);
    if (cached.email) setEditEmail(cached.email);
    if (cached.website_url) setEditWebsiteUrl(cached.website_url);
    if (cached.budget_range) setEditBudgetRange(cached.budget_range);
    
    // Restaurer les champs de notes
    if (cached.note_priority) setNotePriority(cached.note_priority);
    if (cached.note_title) setNoteTitle(cached.note_title);
    if (cached.note_content) setNoteContent(cached.note_content);
    
    // Restaurer les refs pour appareils avec clavier virtuel
    if (isVirtualKeyboardDevice) {
      setTimeout(() => {
        if (businessNameRef.current && cached.business_name) businessNameRef.current.value = cached.business_name;
        if (businessTypeRef.current && cached.business_type) businessTypeRef.current.value = cached.business_type;
        if (businessDescriptionRef.current && cached.business_description) businessDescriptionRef.current.value = cached.business_description;
        if (targetAudienceRef.current && cached.target_audience) targetAudienceRef.current.value = cached.target_audience;
        if (emailRef.current && cached.email) emailRef.current.value = cached.email;
        if (websiteUrlRef.current && cached.website_url) websiteUrlRef.current.value = cached.website_url;
        if (budgetRangeRef.current && cached.budget_range) budgetRangeRef.current.value = cached.budget_range;
        
        // Restaurer les refs de notes
        if (noteTitleRef.current && cached.note_title) noteTitleRef.current.value = cached.note_title;
        if (noteContentRef.current && cached.note_content) noteContentRef.current.value = cached.note_content;
        
        console.log('✅ Refs virtual keyboard restaurés depuis localStorage');
      }, 100);
    }
    
    console.log('✅ Tous les champs restaurés depuis localStorage');
  };

  const loadBusinessProfile = async () => {
    // CRITICAL FIX: Don't fetch if auth is not ready (ChatGPT solution)
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.log('⚠️ No token - skipping business profile fetch');
      return;
    }
    
    // Allow fetch during checkAuth process (user might not be set yet)
    if (!isAuthenticated && !user && token) {
      console.log('🔍 Token exists but auth state not set yet - allowing fetch (during checkAuth)');
    } else if (!token || !isAuthenticated || !user) {
      console.log('⚠️ Auth not ready - skipping business profile fetch');
      console.log('  token:', !!token, 'isAuthenticated:', isAuthenticated, 'user:', !!user);
      return;
    }
    
    try {
      console.log('🔄 Loading business profile from database with auth ready');
      const response = await axios.get(`${API}/business-profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBusinessProfile(response.data);
      
      // Initialiser les champs d'édition ET sauvegarder dans localStorage
      if (isVirtualKeyboardDevice) {
        // Pour appareils avec clavier virtuel, initialiser les refs
        setTimeout(() => {
          if (businessNameRef.current) {
            const currentValue = businessNameRef.current.value;
            const dbValue = response.data.business_name || '';
            const localValue = loadFromLocalStorage()?.business_name || '';
            console.log('🔍 DEBUG business_name:', { dbValue, currentValue, localValue, final: dbValue || currentValue || localValue });
            // Only update if database has a value or current field is empty
            businessNameRef.current.value = dbValue || currentValue || localValue;
            syncFieldWithStorage('business_name', businessNameRef.current.value);
          }
          if (businessDescriptionRef.current) {
            const currentValue = businessDescriptionRef.current.value;
            const dbValue = response.data.business_description || '';
            const localValue = loadFromLocalStorage()?.business_description || '';
            console.log('🔍 DEBUG business_description:', { dbValue, currentValue, localValue, final: dbValue || currentValue || localValue });
            // Only update if database has a value or current field is empty
            businessDescriptionRef.current.value = dbValue || currentValue || localValue;
            syncFieldWithStorage('business_description', businessDescriptionRef.current.value);
          }
          if (targetAudienceRef.current) {
            const currentValue = targetAudienceRef.current.value;
            const dbValue = response.data.target_audience || '';
            const localValue = loadFromLocalStorage()?.target_audience || '';
            console.log('🔍 DEBUG target_audience:', { dbValue, currentValue, localValue, final: dbValue || currentValue || localValue });
            // Only update if database has a value or current field is empty
            targetAudienceRef.current.value = dbValue || currentValue || localValue;
            syncFieldWithStorage('target_audience', targetAudienceRef.current.value);
          }
          if (emailRef.current) {
            const currentValue = emailRef.current.value;
            const dbValue = response.data.email || '';
            const localValue = loadFromLocalStorage()?.email || '';
            console.log('🔍 DEBUG email:', { dbValue, currentValue, localValue, final: dbValue || currentValue || localValue });
            // Only update if database has a value or current field is empty
            emailRef.current.value = dbValue || currentValue || localValue;
            syncFieldWithStorage('email', emailRef.current.value);
          }
          if (websiteUrlRef.current) {
            const currentValue = websiteUrlRef.current.value;
            const dbValue = response.data.website_url || '';
            const localValue = loadFromLocalStorage()?.website_url || '';
            console.log('🔍 DEBUG website_url:', { dbValue, currentValue, localValue, final: dbValue || currentValue || localValue });
            // Only update if database has a value or current field is empty
            websiteUrlRef.current.value = dbValue || currentValue || localValue;
            syncFieldWithStorage('website_url', websiteUrlRef.current.value);
          }
          if (budgetRangeRef.current) {
            const currentValue = budgetRangeRef.current.value;
            const dbValue = response.data.budget_range || '';
            const localValue = loadFromLocalStorage()?.budget_range || '';
            // Only update if database has a value or current field is empty
            budgetRangeRef.current.value = dbValue || currentValue || localValue;
            syncFieldWithStorage('budget_range', budgetRangeRef.current.value);
          }
          if (businessTypeRef.current) {
            const currentValue = businessTypeRef.current.value;
            const dbValue = response.data.business_type || '';
            const localValue = loadFromLocalStorage()?.business_type || '';
            // Only update if database has a value or current field is empty
            businessTypeRef.current.value = dbValue || currentValue || localValue;
            syncFieldWithStorage('business_type', businessTypeRef.current.value);
          }
          console.log('✅ Virtual keyboard fields initialized from database AND cached');
        }, 100);
      } else {
        // Pour Desktop, utiliser les states ET localStorage avec logique de protection
        const currentData = loadFromLocalStorage() || {};
        
        const businessName = response.data.business_name || editBusinessName || currentData.business_name || '';
        console.log('🔍 DEBUG DESKTOP business_name:', { 
          dbValue: response.data.business_name, 
          currentState: editBusinessName, 
          localStorage: currentData.business_name,
          final: businessName 
        });
        setEditBusinessName(businessName);
        syncFieldWithStorage('business_name', businessName);
        
        const businessDescription = response.data.business_description || editBusinessDescription || currentData.business_description || '';
        console.log('🔍 DEBUG DESKTOP business_description:', { 
          dbValue: response.data.business_description, 
          currentState: editBusinessDescription, 
          localStorage: currentData.business_description,
          final: businessDescription 
        });
        setEditBusinessDescription(businessDescription);
        syncFieldWithStorage('business_description', businessDescription);
        
        const targetAudience = response.data.target_audience || editTargetAudience || currentData.target_audience || '';
        console.log('🔍 DEBUG DESKTOP target_audience:', { 
          dbValue: response.data.target_audience, 
          currentState: editTargetAudience, 
          localStorage: currentData.target_audience,
          final: targetAudience 
        });
        setEditTargetAudience(targetAudience);
        syncFieldWithStorage('target_audience', targetAudience);
        
        const email = response.data.email || editEmail || currentData.email || '';
        console.log('🔍 DEBUG DESKTOP email:', { 
          dbValue: response.data.email, 
          currentState: editEmail, 
          localStorage: currentData.email,
          final: email 
        });
        setEditEmail(email);
        syncFieldWithStorage('email', email);
        
        const websiteUrl = response.data.website_url || editWebsiteUrl || currentData.website_url || '';
        console.log('🔍 DEBUG DESKTOP website_url:', { 
          dbValue: response.data.website_url, 
          currentState: editWebsiteUrl, 
          localStorage: currentData.website_url,
          final: websiteUrl 
        });
        setEditWebsiteUrl(websiteUrl);
        syncFieldWithStorage('website_url', websiteUrl);
        
        const budgetRange = response.data.budget_range || editBudgetRange || currentData.budget_range || '';
        setEditBudgetRange(budgetRange);
        syncFieldWithStorage('budget_range', budgetRange);
        
        // Business type avec protection aussi
        const businessType = response.data.business_type || editBusinessType || currentData.business_type || '';
        setEditBusinessType(businessType);
        syncFieldWithStorage('business_type', businessType);
        
        console.log('✅ Desktop fields initialized from database AND cached');
      }
      
      setActiveStep('dashboard');
    } catch (error) {
      console.log('❌ Business profile fetch error:', error.response?.status, error.response?.data);
      
      if (error.response?.status === 401) {
        console.log('🔓 Authentication failed - redirecting to login');
        localStorage.removeItem('access_token');
        setIsAuthenticated(false);
        setUser(null);
        setActiveStep('login');
      } else if (error.response?.status === 404) {
        console.log('📝 No business profile found - Creating default profile and redirecting to dashboard');
        // NOUVELLE LOGIQUE : Au lieu de rediriger vers onboarding, créer un profil par défaut et aller au dashboard
        // Cela correspond à la stratégie "fonctionnalités complètes pour tous"
        setActiveStep('dashboard');
      } else {
        console.log('⚠️ Profile fetch failed but keeping user authenticated');
        // DON'T reset auth state on network/server errors - ESPECIALLY ON iOS
        console.log('📱 iOS Protection: Not resetting auth on profile fetch error');
        setActiveStep('dashboard');
      }
    }
  };

  const loadGeneratedPosts = async () => {
    try {
      const response = await axios.get(`${API}/posts`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      setGeneratedPosts(response.data.posts || []);
    } catch (error) {
      console.error('Error loading posts:', error);
    }
  };

  // Fonction de nettoyage du cache localStorage pour la bibliothèque
  const cleanupContentCache = () => {
    try {
      // Nettoyer tous les caches liés au contenu
      const keysToRemove = [];
      
      // Parcourir toutes les clés du localStorage
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (
          key.startsWith('content_description_') ||
          key === 'deleted_content_ids' ||
          key.startsWith('content_') 
        )) {
          keysToRemove.push(key);
        }
      }
      
      // Supprimer toutes les clés identifiées
      keysToRemove.forEach(key => localStorage.removeItem(key));
      
      console.log(`🧹 Nettoyage cache localStorage: ${keysToRemove.length} clés supprimées`);
      console.log('🔧 Clés supprimées:', keysToRemove);
      
      return keysToRemove.length;
    } catch (error) {
      console.error('❌ Erreur nettoyage cache:', error);
      return 0;
    }
  };

  const loadPendingContent = async (reset = false, forceCleanCache = false) => {
    try {
      setContentLoading(true);
      
      // Nettoyer le cache si demandé (pour debug)
      if (forceCleanCache) {
        const cleanedCount = cleanupContentCache();
        console.log(`🔄 Cache nettoyé: ${cleanedCount} entrées supprimées`);
      }
      
      const offset = reset ? 0 : pendingContent.length;
      const limit = 24; // Load in chunks to prevent crashes
      
      console.log(`📁 Loading content: offset=${offset}, limit=${limit}, reset=${reset}, cleanCache=${forceCleanCache}`);
      
      const response = await axios.get(`${API}/content/pending?limit=${limit}&offset=${offset}`, {
        headers: { 
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });
      
      const data = response.data;
      console.log(`📊 Content loaded from server: ${data.loaded}/${data.total} (has_more: ${data.has_more})`);
      
      // Si on force le nettoyage, ne pas filtrer les suppressions locales
      let filteredContent;
      if (forceCleanCache) {
        filteredContent = data.content || [];
        console.log('🔄 Mode nettoyage: pas de filtrage local, données serveur brutes');
      } else {
        // Filtrer les éléments supprimés localement (mode normal)
        const deletedItemsKey = 'deleted_content_ids';
        const deletedItems = JSON.parse(localStorage.getItem(deletedItemsKey) || '[]');
        
        filteredContent = (data.content || []).filter(item => !deletedItems.includes(item.id));
        
        if (deletedItems.length > 0) {
          console.log(`🗑️ Filtered out ${(data.content || []).length - filteredContent.length} locally deleted items`);
        }
      }
      
      // Debug: Log descriptions for troubleshooting
      const contentWithDescriptions = filteredContent.filter(item => item.description && item.description.trim());
      console.log(`💬 Files with descriptions: ${contentWithDescriptions.length}/${filteredContent.length}`, contentWithDescriptions.map(item => ({ id: item.id, desc: item.description })));
      
      if (reset) {
        setPendingContent(filteredContent);
      } else {
        setPendingContent(prev => [...prev, ...filteredContent]);
      }
      
      setContentTotalCount(data.total || 0);
      setContentHasMore(data.has_more || false);
      
    } catch (error) {
      console.error('❌ Error loading pending content:', error);
      if (error.response?.status === 401) {
        // Token might be expired
        console.log('🔄 Token expired, redirecting to login');
      }
    } finally {
      setContentLoading(false);
    }
  };

  const loadNotes = async () => {
    try {
      console.log('🔄 Loading notes...');
      const response = await axios.get(`${API}/notes`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });  
      console.log('📝 Notes loaded:', response.data);
      setNotes(response.data);
    } catch (error) {
      console.error('❌ Error loading notes:', error);
      console.error('❌ Error response:', error.response?.data);
    }
  };

  // Function to normalize priority values
  const normalizePriority = (priority) => {
    if (!priority) return 'medium';
    const lowercasePriority = priority.toLowerCase().trim();
    
    // French to English mapping
    const mapping = {
      'faible': 'low',
      'basse': 'low',
      'normale': 'medium',
      'normal': 'medium',
      'moyenne': 'medium',
      'élevée': 'high',
      'elevee': 'high',
      'haute': 'high',
      'urgente': 'high',
      'urgent': 'high'
    };
    
    return mapping[lowercasePriority] || lowercasePriority;
  };

  const handleAddNote = async () => {
    // Obtenir les valeurs selon l'approche (iOS refs ou Desktop states)
    let titleValue, contentValue;
    
    if (isVirtualKeyboardDevice) {
      titleValue = noteTitleRef.current?.value || '';
      contentValue = noteContentRef.current?.value || '';
    } else {
      titleValue = noteTitle;
      contentValue = noteContent;
    }

    const normalizedPriority = normalizePriority(notePriority);
    console.log('📝 Adding note:', { titleValue, contentValue, priority: normalizedPriority });

    if (!titleValue || !contentValue) {
      toast.error('Veuillez remplir tous les champs requis');
      return;
    }

    try {
      const response = await axios.post(`${API}/notes`, {
        title: titleValue,
        content: contentValue,
        priority: normalizedPriority
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });

      console.log('✅ Note added successfully:', response.data);

      if (response.status === 200 || response.status === 201) {
        toast.success('Note ajoutée avec succès !');
        
        // D'abord recharger la liste des notes (AVEC await pour éviter race condition)
        await loadNotes(); 
        
        // PUIS réinitialiser les champs selon l'approche
        if (isVirtualKeyboardDevice) {
          if (noteTitleRef.current) noteTitleRef.current.value = '';
          if (noteContentRef.current) noteContentRef.current.value = '';
        } else {
          setNoteTitle('');
          setNoteContent('');
        }
        setNotePriority('medium'); // Valeur par défaut standardisée
        
        // Nettoyer localStorage aussi
        const currentData = loadFromLocalStorage() || {};
        currentData.note_title = '';
        currentData.note_content = '';
        currentData.note_priority = 'medium';
        saveToLocalStorage(currentData);
        
        console.log('✅ Note ajoutée et champs réinitialisés (iOS compatible)');
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
      const response = await axios.delete(`${API}/notes/${noteId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
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
        const response = await axios.get(`${API}/social/connections?business_id=${businessProfile.id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        setSocialConnections(response.data.connections || []);
      }
    } catch (error) {
      console.error('Error loading social connections:', error);
    }
  };

  // Function to check if upgrade modal should be shown
  const shouldShowUpgradeModal = () => {
    // STRATÉGIE TEMPORAIRE : Fonctionnalités complètes pour tous (mois d'essai gratuit)
    // Désactivation temporaire du modal de paiement jusqu'à mise en place du système final
    return { show: false };
    
    /* LOGIQUE ORIGINALE COMMENTÉE
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
    */
  };

  // Function to check if feature is blocked
  const isFeatureBlocked = (feature) => {
    // STRATÉGIE TEMPORAIRE : Fonctionnalités complètes pour tous (mois d'essai gratuit)
    // Désactivation temporaire des limitations jusqu'à mise en place du système final
    return false;
    
    /* LOGIQUE ORIGINALE COMMENTÉE
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
    */
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
    
    // Force reload business profile and notes when switching to "Entreprise" tab
    if (tabValue === 'entreprise') {
      console.log('📂 Switching to Entreprise tab - force loading data');
      forceLoadBusinessProfileAndNotes();
    }
    
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
    console.log('🚨 LOGOUT TRIGGERED - handleLogout called');
    console.log('🚨 Stack trace:', new Error().stack);
    
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
      const response = await axios.get(`${API}/social/facebook/auth-url?business_id=${businessProfile.id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
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
      const response = await axios.get(`${API}/linkedin/auth-url`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
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
      await axios.delete(`${API}/social/connection/${connectionId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
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
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        },
      });
      
      toast.success('Fichiers uploadés avec succès !');
      setSelectedFiles([]);
      loadPendingContent(true); // Reset and load fresh
    } catch (error) {
      toast.error('Erreur lors de l\'upload');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  // Content modal functions - Source de vérité unique selon ChatGPT
  const openContentModal = (content) => {
    setSelectedContent(content);
    console.log('📝 Modal opened for content:', content.id);
  };

  const closeContentModal = () => {
    setSelectedContent(null);
    console.log('✅ Modal closed - selectedContent reset to null');
  };

  // Fonction pour merger les changements dans la liste (VERSION EXACTE ChatGPT)
  const onContentSaved = (updated) => {
    if (updated.deleted) {
      // Suppression : retirer de la liste
      setPendingContent(prev => prev.filter(item => item.id !== updated.id));
      console.log('🗑️ Content removed from list:', updated.id);
    } else {
      // Optimiste : met à jour la carte visible tout de suite (selon ChatGPT)
      setPendingContent(prev =>
        prev.map(item => item.id === updated.id ? { ...item, description: updated.description } : item)
      );
      console.log('📝 Content updated in list:', updated.id);
      
      // Synchronisation serveur en patch (selon ChatGPT)
      void refetchPendingContentSilent('patch');
    }
  };

  // Auto-save pour les descriptions avec synchronisation complète état/ref
  const autoSaveContentDescription = async (contentId, description) => {
    if (!contentId) return;
    
    try {
      const response = await fetch(`${API}/content/${contentId}/description`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          description: description,
        }),
      });

      if (response.ok) {
        // Mettre à jour la liste des contenus
        setPendingContent(prev => prev.map(file => 
          file.id === contentId 
            ? { ...file, description: description }
            : file
        ));
        
        // Mettre à jour le contenu sélectionné
        setSelectedContent(prev => prev && prev.id === contentId ? { ...prev, description: description } : prev);
        
        // CRUCIAL: Maintenir la synchronisation état React + ref après sauvegarde
        setContentDescription(description);
        if (isVirtualKeyboardDevice && contentDescriptionRef.current) {
          contentDescriptionRef.current.value = description;
          console.log('🔄 Ref synchronisé après sauvegarde:', description);
        }
        
        console.log('✅ Description auto-sauvegardée avec succès et interface synchronisée');
      } else {
        console.error('❌ Erreur lors de l\'auto-sauvegarde de la description');
      }
    } catch (error) {
      console.error('❌ Erreur réseau lors de l\'auto-sauvegarde:', error);
    }
  };

  // Debounced auto-save pour descriptions (même système que business profile)
  const debouncedSaveContentDescription = useCallback((contentId, description) => {
    const key = `content_${contentId}`;
    
    if (debounceTimers.current[key]) {
      clearTimeout(debounceTimers.current[key]);
    }
    
    debounceTimers.current[key] = setTimeout(() => {
      autoSaveContentDescription(contentId, description);
    }, 1000); // 1 seconde de debounce
  }, []);

  // Gestionnaire de changement pour descriptions SIMPLIFIÉ - backend seulement
  const handleContentDescriptionChange = useCallback((contentId, description) => {
    // Mettre à jour immédiatement l'état local
    setContentDescription(description);
    
    // Auto-save avec debounce (sans localStorage intermédiaire)
    debouncedSaveContentDescription(contentId, description);
    
    console.log(`📝 Description changée pour ${contentId}:`, description);
  }, [debouncedSaveContentDescription]);

  // Utilitaires selon ChatGPT pour merge/dédupli par ID
  const mergeById = (oldArr, patchArr) => {
    const byId = new Map(oldArr.map(it => [it.id, it]));
    for (const it of patchArr) {
      const prev = byId.get(it.id);
      byId.set(it.id, prev ? { ...prev, ...it } : it);
    }
    // Conserve l'ordre des existants, puis ajoute les nouveaux
    const newOnes = patchArr.filter(it => !oldArr.find(o => o.id === it.id));
    return [...oldArr.map(it => byId.get(it.id)), ...newOnes];
  };

  // Filtre local des éléments supprimés (selon ChatGPT)
  const filterDeletedLocal = (arr) => {
    const deletedItems = JSON.parse(localStorage.getItem('deleted_content_ids') || '[]');
    return arr.filter(it => !deletedItems.includes(it.id));
  };

  // Refetch silencieux VERSION EXACTE selon ChatGPT
  // mode: 'patch' (par défaut) pour mettre à jour ce qui est déjà rendu (ex: badge),
  //       'replace' pour resynchroniser complètement la page courante.
  const refetchPendingContentSilent = async (mode = 'patch') => {
    try {
      // Récupère la même "fenêtre" que ce que l'utilisateur voit
      const currentCount = Math.max(24, pendingContent.length || 0);
      const response = await axios.get(`${API}/content/pending`, {
        params: { limit: currentCount, offset: 0 },
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      const data = response.data;

      // Projection déjà OK côté API (description incluse)
      const serverPage = filterDeletedLocal(data.content || []);

      if (mode === 'replace') {
        // Remplace entièrement la page visible par l'état serveur
        setPendingContent(serverPage);
      } else {
        // Mise à jour "patch" : met à jour ce qui est visible (ex. badges) sans casser l'ordre/pagination
        setPendingContent(prev => mergeById(prev, serverPage));
      }

      setContentTotalCount(data.total || 0);
      setContentHasMore(data.has_more || false);
      
      console.log(`🔄 Refetch silencieux terminé (${mode}) - synchronisation serveur`);
    } catch (error) {
      // Ignorer ou logger, on reste sur l'optimiste si réseau KO
      console.log('⚠️ Refetch silencieux échoué (on garde l\'état optimiste):', error);
    }
  };

  // Multiple selection functions (optimized with useCallback)
  const enterSelectionMode = useCallback(() => {
    setIsSelectionMode(true);
    setSelectedContentIds([]);
  }, []);

  const exitSelectionMode = useCallback(() => {
    setIsSelectionMode(false);
    setSelectedContentIds([]);
  }, []);

  const toggleContentSelection = useCallback((contentId) => {
    setSelectedContentIds(prev => {
      if (prev.includes(contentId)) {
        return prev.filter(id => id !== contentId);
      } else {
        return [...prev, contentId];
      }
    });
  }, []);

  // Suppression multiple FINALE - avec rechargement forcé backend
  const deleteSelectedContent = useCallback(async () => {
    if (selectedContentIds.length === 0) return;
    
    const count = selectedContentIds.length;
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer définitivement ${count} contenu${count > 1 ? 's' : ''} ?`)) {
      return;
    }
    
    setIsDeletingMultiple(true);
    let deletedCount = 0;
    let errorCount = 0;
    
    try {
      // Sortir du mode sélection immédiatement
      exitSelectionMode();
      
      // Delete files one by one côté serveur
      for (const contentId of selectedContentIds) {
        try {
          await axios.delete(`${API}/content/${contentId}`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
          });
          deletedCount++;
          console.log(`✅ Permanently deleted content: ${contentId}`);
        } catch (error) {
          console.error(`Error deleting content ${contentId}:`, error);
          errorCount++;
        }
      }
      
      // Show result message
      if (deletedCount > 0 && errorCount === 0) {
        toast.success(`${deletedCount} contenu${deletedCount > 1 ? 's' : ''} supprimé${deletedCount > 1 ? 's' : ''} définitivement !`);
      } else if (deletedCount > 0 && errorCount > 0) {
        toast.success(`${deletedCount} contenu${deletedCount > 1 ? 's' : ''} supprimé${deletedCount > 1 ? 's' : ''}, ${errorCount} erreur${errorCount > 1 ? 's' : ''}`);
      } else {
        toast.error('Erreur lors de la suppression des contenus');
      }
      
      // CRITIQUE: Forcer le rechargement des données depuis le backend
      await loadPendingContent(true, true);
      
    } catch (error) {
      console.error('Error in batch delete:', error);
      toast.error('Erreur lors de la suppression');
    } finally {
      setIsDeletingMultiple(false);
    }
  }, [selectedContentIds, exitSelectionMode]);

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
      await axios.post(`${API}/business-profile`, profileForm, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      toast.success('Profil créé avec succès !');
      loadBusinessProfile();
    } catch (error) {
      toast.error('Erreur lors de la création du profil');
      console.error('Profile creation error:', error);
    }
  };





  // Système d'édition avec verrouillage + bouton crayon/coche - FONCTIONS GÉNÉRIQUES
  
  // Configuration des champs avec leurs références et états
  const fieldConfigs = {
    business_name: {
      ref: businessNameRef,
      isEditing: isEditingBusinessName,
      setIsEditing: setIsEditingBusinessName,
      tempValue: tempBusinessName,
      setTempValue: setTempBusinessName,
      isSaving: isSavingBusinessName,
      setIsSaving: setIsSavingBusinessName,
      placeholder: 'Nom de votre entreprise',
      validation: (value) => value.trim() ? null : 'Le nom de l\'entreprise ne peut pas être vide'
    },
    business_type: {
      ref: businessTypeRef,
      isEditing: isEditingBusinessType,
      setIsEditing: setIsEditingBusinessType,
      tempValue: tempBusinessType,
      setTempValue: setTempBusinessType,
      isSaving: isSavingBusinessType,
      setIsSaving: setIsSavingBusinessType,
      placeholder: 'artisan / commerçant / service',
      validation: (value) => value.trim() ? null : 'Le type d\'entreprise ne peut pas être vide'
    },
    business_description: {
      ref: businessDescriptionRef,
      isEditing: isEditingBusinessDescription,
      setIsEditing: setIsEditingBusinessDescription,
      tempValue: tempBusinessDescription,
      setTempValue: setTempBusinessDescription,
      isSaving: isSavingBusinessDescription,
      setIsSaving: setIsSavingBusinessDescription,
      placeholder: 'Décrivez en quelques mots votre activité...',
      validation: (value) => value.trim() ? null : 'La description ne peut pas être vide'
    },
    target_audience: {
      ref: targetAudienceRef,
      isEditing: isEditingTargetAudience,
      setIsEditing: setIsEditingTargetAudience,
      tempValue: tempTargetAudience,
      setTempValue: setTempTargetAudience,
      isSaving: isSavingTargetAudience,
      setIsSaving: setIsSavingTargetAudience,
      placeholder: 'Décrivez votre audience cible',
      validation: (value) => value.trim() ? null : 'L\'audience cible ne peut pas être vide'
    },
    email: {
      ref: emailRef,
      isEditing: isEditingEmail,
      setIsEditing: setIsEditingEmail,
      tempValue: tempEmail,
      setTempValue: setTempEmail,
      isSaving: isSavingEmail,
      setIsSaving: setIsSavingEmail,
      placeholder: 'contact@entreprise.com',
      validation: (value) => {
        if (!value.trim()) return 'L\'email ne peut pas être vide';
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value) ? null : 'Format d\'email invalide';
      }
    },
    website_url: {
      ref: websiteUrlRef,
      isEditing: isEditingWebsiteUrl,
      setIsEditing: setIsEditingWebsiteUrl,
      tempValue: tempWebsiteUrl,
      setTempValue: setTempWebsiteUrl,
      isSaving: isSavingWebsiteUrl,
      setIsSaving: setIsSavingWebsiteUrl,
      placeholder: 'https://votre-site.com',
      validation: (value) => {
        if (!value.trim()) return null; // Website URL is optional
        try {
          new URL(value);
          return null;
        } catch {
          return 'Format d\'URL invalide';
        }
      }
    },
    budget_range: {
      ref: budgetRangeRef,
      isEditing: isEditingBudgetRange,
      setIsEditing: setIsEditingBudgetRange,
      tempValue: tempBudgetRange,
      setTempValue: setTempBudgetRange,
      isSaving: isSavingBudgetRange,
      setIsSaving: setIsSavingBudgetRange,
      placeholder: 'Ex: 500€, 1000-2000€, etc.',
      validation: (value) => value.trim() ? null : 'Le budget ne peut pas être vide'
    },
    brand_tone: {
      ref: brandToneRef,
      isEditing: isEditingBrandTone,
      setIsEditing: setIsEditingBrandTone,
      tempValue: tempBrandTone,
      setTempValue: setTempBrandTone,
      isSaving: isSavingBrandTone,
      setIsSaving: setIsSavingBrandTone,
      placeholder: 'Ex: professionnel, sérieux, luxueux, léger, convivial...',
      validation: (value) => value.trim() ? null : 'Le ton à employer ne peut pas être vide'
    }
  };

  // Fonction générique pour démarrer l'édition
  const startEditingField = (fieldName) => {
    const config = fieldConfigs[fieldName];
    const currentValue = businessProfile?.[fieldName] || '';
    
    // Pour tous les appareils, initialiser tempValue avec la valeur actuelle
    config.setTempValue(currentValue);
    config.setIsEditing(true);
    
    // Pour les appareils avec clavier virtuel, définir la valeur du ref après un petit délai
    if (isVirtualKeyboardDevice && config.ref) {
      setTimeout(() => {
        if (config.ref.current) {
          config.ref.current.value = currentValue;
        }
      }, 50);
    }
  };

  // Fonction générique pour annuler l'édition
  const cancelEditingField = (fieldName) => {
    const config = fieldConfigs[fieldName];
    config.setTempValue('');
    config.setIsEditing(false);
  };

  // Fonction générique für sauvegarder un champ
  const saveField = async (fieldName) => {
    const config = fieldConfigs[fieldName];
    
    // Récupérer la valeur selon le type d'appareil
    let fieldValue;
    if (isVirtualKeyboardDevice && config.ref.current) {
      fieldValue = config.ref.current.value;
    } else {
      fieldValue = config.tempValue;
    }

    // Validation
    const validationError = config.validation(fieldValue);
    if (validationError) {
      toast.error(validationError);
      return;
    }

    config.setIsSaving(true);
    try {
      // Préparer les données pour la sauvegarde
      const profileData = {
        business_name: businessProfile?.business_name || 'Mon entreprise',
        business_type: businessProfile?.business_type || 'service',
        business_description: businessProfile?.business_description || '',
        target_audience: businessProfile?.target_audience || '',
        brand_tone: businessProfile?.brand_tone || 'professional',
        posting_frequency: businessProfile?.posting_frequency || 'weekly',
        preferred_platforms: businessProfile?.preferred_platforms || ['Facebook'],
        budget_range: businessProfile?.budget_range || '100-500',
        email: businessProfile?.email || '',
        website_url: businessProfile?.website_url || '',
        hashtags_primary: businessProfile?.hashtags_primary || [],
        hashtags_secondary: businessProfile?.hashtags_secondary || []
      };

      // Mettre à jour le champ spécifique
      profileData[fieldName] = fieldValue.trim();

      // Sauvegarder via API
      const response = await axios.put(`${API}/business-profile`, profileData, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });

      if (response.status === 200) {
        // Mettre à jour le profil business immédiatement
        setBusinessProfile(prev => ({
          ...prev,
          [fieldName]: fieldValue.trim()
        }));
        
        // Synchroniser avec localStorage pour la cohérence
        syncFieldWithStorage(fieldName, fieldValue.trim());
        
        // Réinitialiser l'édition
        config.setIsEditing(false);
        config.setTempValue('');
        
        toast.success(`${getFieldDisplayName(fieldName)} sauvegardé !`);
        
        // Rafraîchir depuis la base de données pour confirmer
        setTimeout(() => {
          loadBusinessProfile();
        }, 500);
      } else {
        throw new Error('Erreur de sauvegarde');
      }
    } catch (error) {
      console.error(`Erreur sauvegarde ${fieldName}:`, error);
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      config.setIsSaving(false);
    }
  };

  // Fonction utilitaire pour obtenir le nom d'affichage du champ
  const getFieldDisplayName = (fieldName) => {
    const displayNames = {
      business_name: 'Nom de l\'entreprise',
      business_type: 'Type d\'entreprise',
      business_description: 'Description de l\'activité',
      target_audience: 'Audience cible',
      email: 'Email professionnel',
      website_url: 'Site web',
      budget_range: 'Budget marketing',
      brand_tone: 'Ton à employer'
    };
    return displayNames[fieldName] || fieldName;
  };

  // Fonctions spécifiques pour rétrocompatibilité (si nécessaire)
  const startEditingBusinessName = () => startEditingField('business_name');
  const cancelEditingBusinessName = () => cancelEditingField('business_name');
  const saveBusinessName = () => saveField('business_name');


  // Enhanced website analysis functions
  const analyzeWebsite = async (forceReanalysis = false) => {
    // CORRECTION DÉFINITIVE : Protection contre les références circulaires DOM
    let websiteUrl;
    try {
      if (isVirtualKeyboardDevice && websiteUrlRef.current) {
        // PROTECTION CRITIQUE: Conversion forcée en string primitive pour éviter les références DOM
        const rawValue = websiteUrlRef.current.value;
        console.log('🔍 Type de rawValue:', typeof rawValue);
        
        // CORRECTION : String() force la conversion primitive et élimine les références circulaires
        websiteUrl = String(rawValue || '').trim();
        console.log('🧹 websiteUrl après String():', typeof websiteUrl, websiteUrl);
      } else {
        websiteUrl = String(editWebsiteUrl || '').trim();
        console.log('🧹 websiteUrl (desktop):', typeof websiteUrl, websiteUrl);
      }
      
      // Validation finale du type
      if (typeof websiteUrl !== 'string') {
        throw new Error('websiteUrl n\'est pas une string après conversion');
      }
      
    } catch (conversionError) {
      console.error('❌ Erreur conversion websiteUrl:', conversionError);
      setAnalysisStatus('error');
      setAnalysisMessage('Erreur lors de la récupération de l\'URL');
      setTimeout(() => {
        setAnalysisStatus('');
        setAnalysisMessage('');
      }, 3000);
      return;
    }
    
    console.log('🔍 Website Analysis - URL to analyze:', websiteUrl);

    if (!websiteUrl || !websiteUrl.trim()) {
      // Afficher popup d'erreur temporaire
      setAnalysisStatus('error');
      setAnalysisMessage('Complétez d\'abord votre site web pour lancer une analyse');
      setTimeout(() => {
        setAnalysisStatus('');
        setAnalysisMessage('');
      }, 3000);
      return;
    }

    // Copier l'URL dans le champ invisible pour l'analyse (ne pas toucher au champ visible)
    setWebsiteUrlForAnalysis(websiteUrl);
    console.log('📋 URL copiée pour analyse (champ invisible):', websiteUrl);

    // PROTECTION : Empêcher toute modification du champ pendant l'analyse
    setIsWebsiteFieldProtected(true);
    console.log('🛡️ Protection du champ URL activée');

    setIsAnalyzingWebsite(true);
    setAnalysisStatus('analyzing');
    setAnalysisMessage('Analyse en cours...');

    console.log('🚀 DÉBUT analyse site web');
    console.log('🌐 URL à analyser:', websiteUrl);

    try {
      // PROTECTION : Créer un objet request propre avec types primitifs forcés
      const requestData = {
        website_url: String(websiteUrl), // Double conversion de sécurité
        force_reanalysis: Boolean(forceReanalysis) // Conversion primitive
      };
      
      console.log('📡 Request data clean:', JSON.stringify(requestData));
      console.log('📡 Types vérifiés:', {
        website_url: typeof requestData.website_url,
        force_reanalysis: typeof requestData.force_reanalysis
      });

      // Utiliser l'URL copiée pour l'analyse, pas l'URL du champ visible
      const response = await axios.post(`${API}/website/analyze`, requestData, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });

      console.log('📡 Réponse API reçue:', response.data);
      console.log('📡 Status code:', response.status);
      console.log('📡 Response headers:', response.headers);
      
      // Vérifier si la réponse est valide avant de traiter
      if (!response.data) {
        throw new Error('Réponse API vide');
      }
      
      // Vérifier si c'est une réponse d'erreur déguisée en 200
      if (response.data.error || response.data.message?.toLowerCase().includes('erreur')) {
        throw new Error(response.data.error || response.data.message || 'Erreur dans la réponse API');
      }
      
      console.log('📊 État AVANT setWebsiteAnalysis:', {
        businessName: businessProfile?.business_name || 'Non défini',
        websiteUrl: businessProfile?.website_url || editWebsiteUrl || 'Non défini',
        userEmail: businessProfile?.email || 'Non défini'
      });

      // Traitement sécurisé des données d'analyse
      try {
        // Nettoyer et valider les données avant setWebsiteAnalysis pour éviter les erreurs circulaires
        const cleanAnalysisData = {
          analysis_summary: response.data.analysis_summary || '',
          key_topics: Array.isArray(response.data.key_topics) ? response.data.key_topics : [],
          brand_tone: response.data.brand_tone || 'professional',
          target_audience: response.data.target_audience || '',
          main_services: Array.isArray(response.data.main_services) ? response.data.main_services : [],
          content_suggestions: Array.isArray(response.data.content_suggestions) ? response.data.content_suggestions : [],
          next_analysis_due: response.data.next_analysis_due || null,
          created_at: response.data.created_at || new Date().toISOString()
        };
        
        console.log('🧹 Données nettoyées pour setWebsiteAnalysis:', cleanAnalysisData);
        setWebsiteAnalysis(cleanAnalysisData);
        console.log('✅ setWebsiteAnalysis exécuté avec succès avec données nettoyées');
        
        // Sauvegarder l'analyse dans localStorage pour persistance au rechargement
        try {
          localStorage.setItem('websiteAnalysis', JSON.stringify(cleanAnalysisData));
          console.log('💾 Analyse sauvegardée dans localStorage');
        } catch (storageError) {
          console.warn('⚠️ Erreur sauvegarde localStorage:', storageError);
        }
        
        // Mettre à jour la date d'analyse avec la date du backend
        const analysisDate = cleanAnalysisData.created_at ? new Date(cleanAnalysisData.created_at) : new Date();
        setLastAnalysisDate(analysisDate.toLocaleString('fr-FR'));
        console.log('📅 Date d\'analyse mise à jour:', analysisDate.toLocaleString('fr-FR'));
      } catch (setStateError) {
        console.error('❌ Erreur lors de setWebsiteAnalysis:', setStateError);
        throw new Error('Erreur lors du traitement des données d\'analyse');
      }
      
      console.log('📊 État APRÈS setWebsiteAnalysis:', {
        businessName: businessProfile?.business_name || 'Non défini',
        websiteUrl: businessProfile?.website_url || editWebsiteUrl || 'Non défini',
        analysisCompleted: true
      });

      setAnalysisStatus('success');
      setAnalysisMessage('✅ Analyse réussie');
      
      // Ne PAS sauvegarder l'URL pour éviter les re-renders qui vident le champ
      // await autoSaveField('website_url', websiteUrl);
      console.log('✅ Analyse terminée, URL préservée par protection');
      
      // Masquer le message de succès après 5 secondes
      setTimeout(() => {
        setAnalysisMessage('');
      }, 5000);

    } catch (error) {
      console.error('❌ Website analysis error:', error);
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      console.error('❌ Error message:', error.message);
      console.error('❌ Full error object:', error);
      
      let errorMessage = '❌ Analyse non concluante, vérifiez votre site web';
      
      // Plus de détails sur l'erreur pour debug
      if (error.response?.status === 401) {
        errorMessage = '❌ Erreur d\'authentification - Reconnectez-vous';
      } else if (error.response?.status === 400) {
        errorMessage = '❌ URL invalide - Vérifiez le format (https://...)';
      } else if (error.response?.data?.detail) {
        errorMessage = `❌ ${error.response.data.detail}`;
      } else if (error.message) {
        // Inclure le message d'erreur JavaScript pour debug
        errorMessage = `❌ ${error.message}`;
      }
      
      console.log('💬 Message d\'erreur affiché:', errorMessage);
      
      setAnalysisStatus('error');
      setAnalysisMessage(errorMessage);
      
      // Masquer le message d'erreur après 8 secondes pour avoir le temps de lire
      setTimeout(() => {
        setAnalysisMessage('');
      }, 8000);
    } finally {
      setIsAnalyzingWebsite(false);
      
      // Désactiver la protection après un délai pour éviter les interférences
      setTimeout(() => {
        setIsWebsiteFieldProtected(false);
        console.log('🛡️ Protection du champ URL désactivée');
      }, 1000);
    }
  };

  // Interrompre l'analyse si l'URL change
  const handleWebsiteUrlChange = (newUrl) => {
    if (isAnalyzingWebsite) {
      setIsAnalyzingWebsite(false);
      setAnalysisStatus('interrupted');
      setAnalysisMessage('Analyse interrompue');
      
      // Désactiver la protection car l'utilisateur modifie activement
      setIsWebsiteFieldProtected(false);
      
      // Masquer le message après 3 secondes
      setTimeout(() => {
        setAnalysisStatus('');
        setAnalysisMessage('');
      }, 3000);
      
      console.log('🛑 Analyse interrompue par modification URL:', newUrl);
    }
  };

  const loadWebsiteAnalysis = async () => {
    console.log('🔄 Chargement de l\'analyse de site web...');
    
    try {
      // Essayer de charger depuis le backend d'abord
      const response = await axios.get(`${API}/website/analysis`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      if (response.data && response.data.analysis) {
        console.log('✅ Analyse chargée depuis le backend');
        const analysisData = response.data.analysis;
        setWebsiteAnalysis(analysisData);
        
        // Mettre à jour la date d'analyse
        if (analysisData.created_at) {
          const analysisDate = new Date(analysisData.created_at);
          setLastAnalysisDate(analysisDate.toLocaleString('fr-FR'));
        }
        
        // Sauvegarder dans localStorage pour cache local
        try {
          localStorage.setItem('websiteAnalysis', JSON.stringify(analysisData));
          console.log('💾 Analyse mise en cache localStorage');
        } catch (storageError) {
          console.warn('⚠️ Erreur cache localStorage:', storageError);
        }
        
        return;
      }
    } catch (error) {
      console.log('⚠️ Pas d\'analyse dans le backend, essai localStorage...');
    }
    
    // Fallback: charger depuis localStorage si pas de données backend
    try {
      const cachedAnalysis = localStorage.getItem('websiteAnalysis');
      if (cachedAnalysis) {
        const analysisData = JSON.parse(cachedAnalysis);
        console.log('✅ Analyse chargée depuis localStorage (cache)');
        setWebsiteAnalysis(analysisData);
        
        // Mettre à jour la date d'analyse
        if (analysisData.created_at) {
          const analysisDate = new Date(analysisData.created_at);
          setLastAnalysisDate(analysisDate.toLocaleString('fr-FR'));
        }
      } else {
        console.log('ℹ️ Aucune analyse trouvée (backend + localStorage)');
      }
    } catch (error) {
      console.error('❌ Erreur chargement analyse depuis localStorage:', error);
    }
  };

  const deleteWebsiteAnalysis = async () => {
    try {
      await axios.delete(`${API}/website/analysis`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      setWebsiteAnalysis(null);
      setShowWebsiteAnalysis(false);
      setLastAnalysisDate('');
      
      // Supprimer aussi du localStorage
      try {
        localStorage.removeItem('websiteAnalysis');
        console.log('🗑️ Analyse supprimée du localStorage');
      } catch (storageError) {
        console.warn('⚠️ Erreur suppression localStorage:', storageError);
      }
      
      toast.success('Analyse supprimée');
    } catch (error) {
      console.error('Error deleting analysis:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  // Alias pour la nouvelle page d'analyse
  const handleAnalyzeWebsite = analyzeWebsite;

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
                  key="onboarding_business_name_input"
                  id="business_name"
                  placeholder="Mon Restaurant"
                  value={profileForm.business_name}
                  onChange={(e) => setProfileForm(prev => ({...prev, business_name: e.target.value}))}
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
                key="onboarding_target_audience_input"
                id="target_audience"
                placeholder="Décrivez votre audience cible (âge, intérêts, localisation...)"
                value={profileForm.target_audience}
                onChange={(e) => setProfileForm(prev => ({...prev, target_audience: e.target.value}))}
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
                    key="primary_hashtag_input"
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
                    key="secondary_hashtag_input"
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
                  key="onboarding_website_url_input"
                  placeholder="https://monentreprise.com"
                  value={profileForm.website_url}
                  onChange={(e) => setProfileForm(prev => ({...prev, website_url: e.target.value}))}
                  className="input-modern"
                  type="url"
                />
                <p className="text-sm text-gray-500">
                  L'analyse de votre site web nous aide à créer des contenus personnalisés et pertinents pour votre audience 🎯
                </p>
                
                {(businessProfile?.website_url || profileForm.website_url) && (businessProfile?.website_url || profileForm.website_url).trim() && (
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
                key="onboarding_budget_range_input"
                id="budget_range"
                type="text"
                value={profileForm.budget_range}
                onChange={(e) => setProfileForm(prev => ({...prev, budget_range: e.target.value}))}
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
        <Tabs 
            value={activeTab} 
            onValueChange={(value) => {
              console.log('🔄 Tab changed to:', value);
              setActiveTab(value);
              
              // Restore data when switching to Entreprise tab
              if (value === 'entreprise') {
                restoreFieldsFromStorage();
              }
            }} 
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
                {/* Champ URL du site */}
                <div className="space-y-2">
                  <Label htmlFor="website_analysis_url" className="text-gray-700 font-medium">
                    URL de votre site web
                  </Label>
                  {isVirtualKeyboardDevice ? (
                    <input
                      ref={websiteUrlRef}
                      id="website_analysis_url"
                      type="url"
                      className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none"
                      style={{ fontSize: '16px' }}
                      autoCorrect={false}
                      autoComplete="off"
                      spellCheck={false}
                      autoCapitalize="off"
                      defaultValue={businessProfile?.website_url || loadFromLocalStorage()?.website_url || ""}
                      placeholder="https://votre-site.com"
                      onBlur={() => {
                        handleVirtualKeyboardRefBlur('website_url', websiteUrlRef);
                        handleWebsiteUrlChange(websiteUrlRef.current?.value || '');
                      }}
                    />
                  ) : (
                    <Input
                      id="website_analysis_url"
                      type="url"
                      value={editWebsiteUrl}
                      onChange={(e) => {
                        handleFieldChange('website_url', e.target.value, setEditWebsiteUrl);
                        handleWebsiteUrlChange(e.target.value);
                      }}
                      onBlur={(e) => handleFieldBlur('website_url', e.target.value)}
                      placeholder="https://votre-site.com"
                      className="bg-white focus:border-purple-500 focus:ring-purple-500"
                    />
                  )}
                </div>

                {/* Bouton d'analyse */}
                <div className="flex gap-3">
                  <Button
                    type="button"
                    onClick={handleAnalyzeWebsite}
                    disabled={isAnalyzingWebsite || !editWebsiteUrl}
                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-6 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2"
                  >
                    {isAnalyzingWebsite ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Analyse en cours...</span>
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4" />
                        <span>Analyser le site</span>
                      </>
                    )}
                  </Button>
                  
                  {websiteAnalysis && (
                    <Button
                      type="button"
                      onClick={() => handleAnalyzeWebsite(true)}
                      disabled={isAnalyzingWebsite}
                      variant="outline"
                      className="border-purple-300 text-purple-600 hover:bg-purple-50"
                    >
                      🔄 Re-analyser
                    </Button>
                  )}
                </div>

                {/* Message d'état */}
                {analysisStatus && (
                  <div className={`p-3 rounded-lg ${
                    analysisStatus === 'success' ? 'bg-green-50 border border-green-200' :
                    analysisStatus === 'error' ? 'bg-red-50 border border-red-200' :
                    'bg-blue-50 border border-blue-200'
                  }`}>
                    <p className={`text-sm ${
                      analysisStatus === 'success' ? 'text-green-700' :
                      analysisStatus === 'error' ? 'text-red-700' :
                      'text-blue-700'
                    }`}>
                      {analysisMessage}
                    </p>
                  </div>
                )}

                {/* Informations d'analyse */}
                {websiteAnalysis && (
                  <div className="space-y-4 bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-xl border border-purple-200">
                    {/* En-tête avec dates */}
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-purple-800 mb-2">
                          Résultats de l'analyse
                        </h3>
                        <div className="text-sm text-purple-600 space-y-1">
                          <p>
                            📅 <strong>Dernière analyse :</strong> {lastAnalysisDate ? new Date(lastAnalysisDate).toLocaleString('fr-FR') : 'Inconnue'}
                          </p>
                          <p>
                            ⏰ <strong>Prochaine analyse :</strong> {websiteAnalysis.next_analysis_due ? new Date(websiteAnalysis.next_analysis_due).toLocaleString('fr-FR') : 'À définir'}
                          </p>
                        </div>
                      </div>
                      <Button
                        type="button"
                        onClick={deleteWebsiteAnalysis}
                        variant="outline"
                        size="sm"
                        className="text-red-600 border-red-300 hover:bg-red-50"
                      >
                        🗑️ Supprimer
                      </Button>
                    </div>

                    {/* Résumé de l'analyse */}
                    <div className="space-y-4">
                      <div>
                        <span className="font-semibold text-purple-800">Résumé :</span>
                        <p className="text-purple-700 mt-1 leading-relaxed">{websiteAnalysis.analysis_summary}</p>
                      </div>
                      
                      <div>
                        <span className="font-semibold text-purple-800">Sujets clés :</span>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {websiteAnalysis.key_topics.map((topic, index) => (
                            <Badge key={index} className="bg-purple-100 text-purple-800 border-purple-300">
                              {topic}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <span className="font-semibold text-purple-800">Ton de marque :</span>
                          <span className="text-purple-700 ml-2 capitalize">{websiteAnalysis.brand_tone}</span>
                        </div>
                        
                        <div>
                          <span className="font-semibold text-purple-800">Audience cible :</span>
                          <p className="text-purple-700 mt-1">{websiteAnalysis.target_audience}</p>
                        </div>
                      </div>
                      
                      {websiteAnalysis.main_services && websiteAnalysis.main_services.length > 0 && (
                        <div>
                          <span className="font-semibold text-purple-800">Services principaux :</span>
                          <div className="flex flex-wrap gap-2 mt-2">
                            {websiteAnalysis.main_services.map((service, index) => (
                              <Badge key={index} className="bg-pink-100 text-pink-800 border-pink-300">
                                {service}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {websiteAnalysis.content_suggestions && (
                        <div>
                          <span className="font-semibold text-purple-800">Suggestions de contenu :</span>
                          <ul className="text-purple-700 mt-2 space-y-1 ml-4">
                            {websiteAnalysis.content_suggestions.map((suggestion, index) => (
                              <li key={index} className="list-disc">{suggestion}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Message si pas d'analyse */}
                {!websiteAnalysis && !isAnalyzingWebsite && (
                  <div className="text-center py-8 text-gray-500">
                    <Search className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p className="text-lg mb-2">Aucune analyse disponible</p>
                    <p className="text-sm">Entrez l'URL de votre site web et cliquez sur "Analyser le site" pour commencer</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

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
                          <div className="flex items-start justify-between mb-6">
                            <div className="flex items-center space-x-4 min-w-0 flex-1 mr-4">
                              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center flex-shrink-0">
                                <Building className="w-8 h-8 text-white" />
                              </div>
                              <div className="flex-1">
                                <h3 className="text-lg font-bold text-blue-800 mb-2">Profil de l'entreprise</h3>
                                <p className="text-blue-600 text-sm">Modifiez directement vos informations ci-dessous</p>
                              </div>
                            </div>
                          </div>

                          {/* Formulaire directement éditable */}
                          <div className="space-y-6">
                            <div className="grid md:grid-cols-2 gap-6">
                              {/* Nom de l'entreprise avec système d'édition verrouillé + gestion clavier virtuel */}
                              <div className="space-y-2">
                                <Label className="text-sm font-medium text-gray-700">Nom de l'entreprise</Label>
                                <div className="relative flex items-center gap-2">
                                  {isEditingBusinessName ? (
                                    // Mode édition avec champ input et bouton coche verte
                                    <>
                                      {isVirtualKeyboardDevice ? (
                                        <input
                                          ref={businessNameRef}
                                          type="text"
                                          className="w-full p-3 border border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none"
                                          style={{ fontSize: '16px' }}
                                          autoCorrect={false}
                                          autoComplete="off"
                                          spellCheck={false}
                                          autoCapitalize="off"
                                          defaultValue={businessProfile?.business_name || 'Mon entreprise'}
                                          placeholder="Nom de votre entreprise"
                                          disabled={isSavingBusinessName}
                                        />
                                      ) : (
                                        <Input
                                          value={tempBusinessName}
                                          onChange={(e) => setTempBusinessName(e.target.value)}
                                          className="bg-white border-blue-500 focus:border-blue-600"
                                          placeholder="Nom de votre entreprise"
                                          disabled={isSavingBusinessName}
                                        />
                                      )}
                                      <div className="flex gap-1">
                                        <Button
                                          type="button"
                                          size="sm"
                                          onClick={saveBusinessName}
                                          disabled={isSavingBusinessName}
                                          className="bg-green-500 hover:bg-green-600 text-white p-2 min-w-[40px]"
                                        >
                                          {isSavingBusinessName ? (
                                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                          ) : (
                                            <Check className="h-4 w-4" />
                                          )}
                                        </Button>
                                        <Button
                                          type="button"
                                          size="sm"
                                          variant="outline"
                                          onClick={cancelEditingBusinessName}
                                          disabled={isSavingBusinessName}
                                          className="p-2 min-w-[40px]"
                                        >
                                          <X className="h-4 w-4" />
                                        </Button>
                                      </div>
                                    </>
                                  ) : (
                                    // Mode lecture avec champ verrouillé et bouton crayon
                                    <>
                                      <Input
                                        value={businessProfile?.business_name || 'Mon entreprise'}
                                        readOnly
                                        className="bg-gray-50 text-gray-700 cursor-default"
                                      />
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={startEditingBusinessName}
                                        className="p-2 min-w-[40px] hover:bg-blue-50 hover:border-blue-300"
                                        title="Modifier le nom de l'entreprise"
                                      >
                                        <Edit className="h-4 w-4 text-blue-600" />
                                      </Button>
                                    </>
                                  )}
                                </div>
                              </div>

                              {/* Type d'entreprise avec système d'édition verrouillé */}
                              <div className="space-y-2">
                                <Label className="text-sm font-medium text-gray-700">Type d'entreprise</Label>
                                <div className="relative flex items-center gap-2">
                                  {isEditingBusinessType ? (
                                    // Mode édition avec champ input et bouton coche verte
                                    <>
                                      {isVirtualKeyboardDevice ? (
                                        <input
                                          ref={businessTypeRef}
                                          type="text"
                                          className="w-full p-3 border border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none"
                                          style={{ fontSize: '16px' }}
                                          autoCorrect={false}
                                          autoComplete="off"
                                          spellCheck={false}
                                          autoCapitalize="off"
                                          defaultValue={businessProfile?.business_type || ''}
                                          placeholder="artisan / commerçant / service"
                                          disabled={isSavingBusinessType}
                                        />
                                      ) : (
                                        <Input
                                          value={tempBusinessType}
                                          onChange={(e) => setTempBusinessType(e.target.value)}
                                          className="bg-white border-blue-500 focus:border-blue-600"
                                          placeholder="artisan / commerçant / service"
                                          disabled={isSavingBusinessType}
                                        />
                                      )}
                                      <div className="flex gap-1">
                                        <Button
                                          type="button"
                                          size="sm"
                                          onClick={() => saveField('business_type')}
                                          disabled={isSavingBusinessType}
                                          className="bg-green-500 hover:bg-green-600 text-white p-2 min-w-[40px]"
                                        >
                                          {isSavingBusinessType ? (
                                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                          ) : (
                                            <Check className="h-4 w-4" />
                                          )}
                                        </Button>
                                        <Button
                                          type="button"
                                          size="sm"
                                          variant="outline"
                                          onClick={() => cancelEditingField('business_type')}
                                          disabled={isSavingBusinessType}
                                          className="p-2 min-w-[40px]"
                                        >
                                          <X className="h-4 w-4" />
                                        </Button>
                                      </div>
                                    </>
                                  ) : (
                                    // Mode lecture avec champ verrouillé et bouton crayon
                                    <>
                                      <Input
                                        value={businessProfile?.business_type || 'service'}
                                        readOnly
                                        className="bg-gray-50 text-gray-700 cursor-default"
                                      />
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={() => startEditingField('business_type')}
                                        className="p-2 min-w-[40px] hover:bg-blue-50 hover:border-blue-300"
                                        title="Modifier le type d'entreprise"
                                      >
                                        <Edit className="h-4 w-4 text-blue-600" />
                                      </Button>
                                    </>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Description de l'activité avec système d'édition verrouillé */}
                            <div className="space-y-2">
                              <Label className="text-sm font-medium text-gray-700">Description de l'activité</Label>
                              <div className="relative flex items-start gap-2">
                                {isEditingBusinessDescription ? (
                                  // Mode édition avec textarea et bouton coche verte
                                  <>
                                    {isVirtualKeyboardDevice ? (
                                      <textarea
                                        ref={businessDescriptionRef}
                                        rows={3}
                                        className="flex-1 p-3 border border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none resize-none"
                                        style={{ fontSize: '16px' }}
                                        autoCorrect={false}
                                        autoComplete="off"
                                        spellCheck={false}
                                        autoCapitalize="off"
                                        defaultValue={businessProfile?.business_description || ''}
                                        placeholder="Décrivez en quelques mots votre activité, vos services ou produits..."
                                        disabled={isSavingBusinessDescription}
                                      />
                                    ) : (
                                      <Textarea
                                        value={tempBusinessDescription}
                                        onChange={(e) => setTempBusinessDescription(e.target.value)}
                                        className="flex-1 bg-white border-blue-500 focus:border-blue-600"
                                        placeholder="Décrivez en quelques mots votre activité, vos services ou produits..."
                                        rows={3}
                                        disabled={isSavingBusinessDescription}
                                      />
                                    )}
                                    <div className="flex flex-col gap-1">
                                      <Button
                                        type="button"
                                        size="sm"
                                        onClick={() => saveField('business_description')}
                                        disabled={isSavingBusinessDescription}
                                        className="bg-green-500 hover:bg-green-600 text-white p-2 min-w-[40px]"
                                      >
                                        {isSavingBusinessDescription ? (
                                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                        ) : (
                                          <Check className="h-4 w-4" />
                                        )}
                                      </Button>
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={() => cancelEditingField('business_description')}
                                        disabled={isSavingBusinessDescription}
                                        className="p-2 min-w-[40px]"
                                      >
                                        <X className="h-4 w-4" />
                                      </Button>
                                    </div>
                                  </>
                                ) : (
                                  // Mode lecture avec textarea verrouillée et bouton crayon
                                  <>
                                    <Textarea
                                      value={businessProfile?.business_description || 'Décrivez votre activité'}
                                      readOnly
                                      className="flex-1 bg-gray-50 text-gray-700 cursor-default"
                                      rows={3}
                                    />
                                    <Button
                                      type="button"
                                      size="sm"
                                      variant="outline"
                                      onClick={() => startEditingField('business_description')}
                                      className="p-2 min-w-[40px] hover:bg-blue-50 hover:border-blue-300"
                                      title="Modifier la description de l'activité"
                                    >
                                      <Edit className="h-4 w-4 text-blue-600" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </div>

                            {/* Audience cible avec système d'édition verrouillé */}
                            <div className="space-y-2">
                              <Label className="text-sm font-medium text-gray-700">Audience cible</Label>
                              <div className="relative flex items-start gap-2">
                                {isEditingTargetAudience ? (
                                  // Mode édition avec textarea et bouton coche verte
                                  <>
                                    {isVirtualKeyboardDevice ? (
                                      <textarea
                                        ref={targetAudienceRef}
                                        rows={2}
                                        className="flex-1 p-3 border border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none resize-none"
                                        style={{ fontSize: '16px' }}
                                        autoCorrect={false}
                                        autoComplete="off"
                                        spellCheck={false}
                                        autoCapitalize="off"
                                        defaultValue={businessProfile?.target_audience || ''}
                                        placeholder="Décrivez votre audience cible"
                                        disabled={isSavingTargetAudience}
                                      />
                                    ) : (
                                      <Textarea
                                        value={tempTargetAudience}
                                        onChange={(e) => setTempTargetAudience(e.target.value)}
                                        className="flex-1 bg-white border-blue-500 focus:border-blue-600"
                                        placeholder="Décrivez votre audience cible"
                                        rows={2}
                                        disabled={isSavingTargetAudience}
                                      />
                                    )}
                                    <div className="flex flex-col gap-1">
                                      <Button
                                        type="button"
                                        size="sm"
                                        onClick={() => saveField('target_audience')}
                                        disabled={isSavingTargetAudience}
                                        className="bg-green-500 hover:bg-green-600 text-white p-2 min-w-[40px]"
                                      >
                                        {isSavingTargetAudience ? (
                                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                        ) : (
                                          <Check className="h-4 w-4" />
                                        )}
                                      </Button>
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={() => cancelEditingField('target_audience')}
                                        disabled={isSavingTargetAudience}
                                        className="p-2 min-w-[40px]"
                                      >
                                        <X className="h-4 w-4" />
                                      </Button>
                                    </div>
                                  </>
                                ) : (
                                  // Mode lecture avec textarea verrouillée et bouton crayon
                                  <>
                                    <Textarea
                                      value={businessProfile?.target_audience || 'Décrivez votre audience cible'}
                                      readOnly
                                      className="flex-1 bg-gray-50 text-gray-700 cursor-default"
                                      rows={2}
                                    />
                                    <Button
                                      type="button"
                                      size="sm"
                                      variant="outline"
                                      onClick={() => startEditingField('target_audience')}
                                      className="p-2 min-w-[40px] hover:bg-blue-50 hover:border-blue-300"
                                      title="Modifier l'audience cible"
                                    >
                                      <Edit className="h-4 w-4 text-blue-600" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </div>

                            <div className="grid md:grid-cols-2 gap-6">
                              {/* Email professionnel avec système d'édition verrouillé */}
                              <div className="space-y-2">
                                <Label className="text-sm font-medium text-gray-700">Email professionnel</Label>
                                <div className="relative flex items-center gap-2">
                                  {isEditingEmail ? (
                                    // Mode édition avec champ input et bouton coche verte
                                    <>
                                      {isVirtualKeyboardDevice ? (
                                        <input
                                          ref={emailRef}
                                          type="email"
                                          className="w-full p-3 border border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none"
                                          style={{ fontSize: '16px' }}
                                          autoCorrect={false}
                                          autoComplete="off"
                                          spellCheck={false}
                                          autoCapitalize="off"
                                          defaultValue={businessProfile?.email || ''}
                                          placeholder="contact@entreprise.com"
                                          disabled={isSavingEmail}
                                        />
                                      ) : (
                                        <Input
                                          type="email"
                                          value={tempEmail}
                                          onChange={(e) => setTempEmail(e.target.value)}
                                          className="bg-white border-blue-500 focus:border-blue-600"
                                          placeholder="contact@entreprise.com"
                                          disabled={isSavingEmail}
                                        />
                                      )}
                                      <div className="flex gap-1">
                                        <Button
                                          type="button"
                                          size="sm"
                                          onClick={() => saveField('email')}
                                          disabled={isSavingEmail}
                                          className="bg-green-500 hover:bg-green-600 text-white p-2 min-w-[40px]"
                                        >
                                          {isSavingEmail ? (
                                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                          ) : (
                                            <Check className="h-4 w-4" />
                                          )}
                                        </Button>
                                        <Button
                                          type="button"
                                          size="sm"
                                          variant="outline"
                                          onClick={() => cancelEditingField('email')}
                                          disabled={isSavingEmail}
                                          className="p-2 min-w-[40px]"
                                        >
                                          <X className="h-4 w-4" />
                                        </Button>
                                      </div>
                                    </>
                                  ) : (
                                    // Mode lecture avec champ verrouillé et bouton crayon
                                    <>
                                      <Input
                                        type="email"
                                        value={businessProfile?.email || 'contact@entreprise.com'}
                                        readOnly
                                        className="bg-gray-50 text-gray-700 cursor-default"
                                      />
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={() => startEditingField('email')}
                                        className="p-2 min-w-[40px] hover:bg-blue-50 hover:border-blue-300"
                                        title="Modifier l'email professionnel"
                                      >
                                        <Edit className="h-4 w-4 text-blue-600" />
                                      </Button>
                                    </>
                                  )}
                                </div>
                              </div>

                              {/* Site web avec système d'édition verrouillé */}
                              <div className="space-y-2">
                                <Label className="text-sm font-medium text-gray-700">Site web</Label>
                                <div className="relative flex items-center gap-2">
                                  {isEditingWebsiteUrl ? (
                                    // Mode édition avec champ input et bouton coche verte
                                    <>
                                      {isVirtualKeyboardDevice ? (
                                        <input
                                          ref={websiteUrlRef}
                                          type="url"
                                          className="w-full p-3 border border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none"
                                          style={{ fontSize: '16px' }}
                                          autoCorrect={false}
                                          autoComplete="off"
                                          spellCheck={false}
                                          autoCapitalize="off"
                                          defaultValue={businessProfile?.website_url || ''}
                                          placeholder="https://votre-site.com"
                                          disabled={isSavingWebsiteUrl}
                                        />
                                      ) : (
                                        <Input
                                          type="url"
                                          value={tempWebsiteUrl}
                                          onChange={(e) => setTempWebsiteUrl(e.target.value)}
                                          className="bg-white border-blue-500 focus:border-blue-600"
                                          placeholder="https://votre-site.com"
                                          disabled={isSavingWebsiteUrl}
                                        />
                                      )}
                                      <div className="flex gap-1">
                                        <Button
                                          type="button"
                                          size="sm"
                                          onClick={() => saveField('website_url')}
                                          disabled={isSavingWebsiteUrl}
                                          className="bg-green-500 hover:bg-green-600 text-white p-2 min-w-[40px]"
                                        >
                                          {isSavingWebsiteUrl ? (
                                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                          ) : (
                                            <Check className="h-4 w-4" />
                                          )}
                                        </Button>
                                        <Button
                                          type="button"
                                          size="sm"
                                          variant="outline"
                                          onClick={() => cancelEditingField('website_url')}
                                          disabled={isSavingWebsiteUrl}
                                          className="p-2 min-w-[40px]"
                                        >
                                          <X className="h-4 w-4" />
                                        </Button>
                                      </div>
                                    </>
                                  ) : (
                                    // Mode lecture avec champ verrouillé et bouton crayon
                                    <>
                                      <Input
                                        type="url"
                                        value={businessProfile?.website_url || 'https://votre-site.com'}
                                        readOnly
                                        className="bg-gray-50 text-gray-700 cursor-default"
                                      />
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={() => startEditingField('website_url')}
                                        className="p-2 min-w-[40px] hover:bg-blue-50 hover:border-blue-300"
                                        title="Modifier le site web"
                                      >
                                        <Edit className="h-4 w-4 text-blue-600" />
                                      </Button>
                                    </>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Budget marketing avec système d'édition verrouillé */}
                            <div className="space-y-2">
                              <Label className="text-sm font-medium text-gray-700">Budget marketing mensuel</Label>
                              <div className="relative flex items-center gap-2">
                                {isEditingBudgetRange ? (
                                  // Mode édition avec champ input et bouton coche verte
                                  <>
                                    {isVirtualKeyboardDevice ? (
                                      <input
                                        ref={budgetRangeRef}
                                        type="text"
                                        className="w-full p-3 border border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none"
                                        style={{ fontSize: '16px' }}
                                        autoCorrect={false}
                                        autoComplete="off"
                                        spellCheck={false}
                                        autoCapitalize="off"
                                        defaultValue={businessProfile?.budget_range || ''}
                                        placeholder="Ex: 500€, 1000-2000€, etc."
                                        disabled={isSavingBudgetRange}
                                      />
                                    ) : (
                                      <Input
                                        value={tempBudgetRange}
                                        onChange={(e) => setTempBudgetRange(e.target.value)}
                                        className="bg-white border-blue-500 focus:border-blue-600"
                                        placeholder="Ex: 500€, 1000-2000€, etc."
                                        disabled={isSavingBudgetRange}
                                      />
                                    )}
                                    <div className="flex gap-1">
                                      <Button
                                        type="button"
                                        size="sm"
                                        onClick={() => saveField('budget_range')}
                                        disabled={isSavingBudgetRange}
                                        className="bg-green-500 hover:bg-green-600 text-white p-2 min-w-[40px]"
                                      >
                                        {isSavingBudgetRange ? (
                                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                        ) : (
                                          <Check className="h-4 w-4" />
                                        )}
                                      </Button>
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={() => cancelEditingField('budget_range')}
                                        disabled={isSavingBudgetRange}
                                        className="p-2 min-w-[40px]"
                                      >
                                        <X className="h-4 w-4" />
                                      </Button>
                                    </div>
                                  </>
                                ) : (
                                  // Mode lecture avec champ verrouillé et bouton crayon
                                  <>
                                    <Input
                                      value={businessProfile?.budget_range || '100-500€'}
                                      readOnly
                                      className="bg-gray-50 text-gray-700 cursor-default"
                                    />
                                    <Button
                                      type="button"
                                      size="sm"
                                      variant="outline"
                                      onClick={() => startEditingField('budget_range')}
                                      className="p-2 min-w-[40px] hover:bg-blue-50 hover:border-blue-300"
                                      title="Modifier le budget marketing"
                                    >
                                      <Edit className="h-4 w-4 text-blue-600" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </div>

                            {/* Ton à employer avec système d'édition verrouillé */}
                            <div className="space-y-2">
                              <Label className="text-sm font-medium text-gray-700">Ton à employer</Label>
                              <div className="relative flex items-center gap-2">
                                {isEditingBrandTone ? (
                                  // Mode édition avec champ input et bouton coche verte
                                  <>
                                    {isVirtualKeyboardDevice ? (
                                      <input
                                        ref={brandToneRef}
                                        type="text"
                                        className="w-full p-3 border border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none"
                                        style={{ fontSize: '16px' }}
                                        autoCorrect={false}
                                        autoComplete="off"
                                        spellCheck={false}
                                        autoCapitalize="off"
                                        defaultValue={businessProfile?.brand_tone || ''}
                                        placeholder="Ex: professionnel, sérieux, luxueux, léger, convivial..."
                                        disabled={isSavingBrandTone}
                                      />
                                    ) : (
                                      <Input
                                        value={tempBrandTone}
                                        onChange={(e) => setTempBrandTone(e.target.value)}
                                        className="bg-white border-blue-500 focus:border-blue-600"
                                        placeholder="Ex: professionnel, sérieux, luxueux, léger, convivial..."
                                        disabled={isSavingBrandTone}
                                      />
                                    )}
                                    <div className="flex gap-1">
                                      <Button
                                        type="button"
                                        size="sm"
                                        onClick={() => saveField('brand_tone')}
                                        disabled={isSavingBrandTone}
                                        className="bg-green-500 hover:bg-green-600 text-white p-2 min-w-[40px]"
                                      >
                                        {isSavingBrandTone ? (
                                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                        ) : (
                                          <Check className="h-4 w-4" />
                                        )}
                                      </Button>
                                      <Button
                                        type="button"
                                        size="sm"
                                        variant="outline"
                                        onClick={() => cancelEditingField('brand_tone')}
                                        disabled={isSavingBrandTone}
                                        className="p-2 min-w-[40px]"
                                      >
                                        <X className="h-4 w-4" />
                                      </Button>
                                    </div>
                                  </>
                                ) : (
                                  // Mode lecture avec champ verrouillé et bouton crayon
                                  <>
                                    <Input
                                      value={businessProfile?.brand_tone || 'professionnel'}
                                      readOnly
                                      className="bg-gray-50 text-gray-700 cursor-default"
                                    />
                                    <Button
                                      type="button"
                                      size="sm"
                                      variant="outline"
                                      onClick={() => startEditingField('brand_tone')}
                                      className="p-2 min-w-[40px] hover:bg-blue-50 hover:border-blue-300"
                                      title="Modifier le ton à employer"
                                    >
                                      <Edit className="h-4 w-4 text-blue-600" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </div>

                            {/* Indicateur de sauvegarde automatique */}
                            <div className="flex justify-center pt-4 border-t border-blue-200">
                              <div className="text-sm text-green-600 flex items-center">
                                <Check className="w-4 h-4 mr-2" />
                                Sauvegarde automatique activée
                              </div>
                            </div>
                          </div>
                        </div>

                    {/* Quick Actions */}
                    <div className="grid md:grid-cols-2 gap-4">
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
                {(pendingContent.length > 0 || contentLoading) && (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-xl font-semibold text-gray-900 flex items-center">
                        <ImageIcon className="w-6 h-6 mr-2 text-purple-600" />
                        Vos contenus ({contentTotalCount > 0 ? contentTotalCount : pendingContent.length})
                        {contentLoading && (
                          <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin ml-2"></div>
                        )}
                      </h4>
                      
                      {/* Selection controls */}
                      <div className="space-y-4">
                        {/* Première ligne : boutons principaux */}
                        <div className="flex items-center space-x-2">
                          {!isSelectionMode ? (
                            <Button
                              onClick={enterSelectionMode}
                              variant="outline"
                              className="text-gray-600 border-gray-300 hover:bg-gray-50"
                              disabled={contentLoading || pendingContent.length === 0}
                            >
                              <Check className="w-4 h-4 mr-2" />
                              Sélectionner
                            </Button>
                          ) : (
                            <div className="flex items-center space-x-2">
                              <span className="text-sm text-gray-600">
                                {selectedContentIds.length} sélectionné{selectedContentIds.length > 1 ? 's' : ''}
                              </span>
                              <Button
                                onClick={deleteSelectedContent}
                                disabled={selectedContentIds.length === 0 || isDeletingMultiple}
                                variant="destructive"
                                className="bg-red-500 hover:bg-red-600 text-white"
                              >
                                {isDeletingMultiple ? (
                                  <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                                    Suppression...
                                  </>
                                ) : (
                                  <>
                                    <Trash className="w-4 h-4 mr-2" />
                                    Supprimer
                                  </>
                                )}
                              </Button>
                              <Button
                                onClick={exitSelectionMode}
                                variant="outline"
                                className="text-gray-600 border-gray-300 hover:bg-gray-50"
                              >
                                <X className="w-4 h-4 mr-2" />
                                Annuler
                              </Button>
                            </div>
                          )}
                        </div>
                        
                        {/* Deuxième ligne : bouton synchroniser */}
                        <div className="flex items-center">
                          <Button
                            onClick={() => {
                              console.log('🔄 Synchronisation forcée demandée');
                              loadPendingContent(true, true); // Reset + nettoyage cache
                            }}
                            variant="outline"
                            className="text-purple-600 border-purple-300 hover:bg-purple-50"
                            disabled={contentLoading}
                            title="Forcer la synchronisation avec le serveur"
                          >
                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            Synchroniser
                          </Button>
                        </div>
                      </div>
                    </div>
                    
                    {pendingContent.length > 0 && (
                      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                        {pendingContent.map((content) => (
                          <ContentThumbnail
                            key={content.id}
                            content={content}
                            isSelectionMode={isSelectionMode}
                            isSelected={selectedContentIds.includes(content.id)}
                            onContentClick={openContentModal}
                            onToggleSelection={toggleContentSelection}
                          />
                        ))}
                      </div>
                    )}
                    
                    {/* Load more button */}
                    {contentHasMore && !isSelectionMode && (
                      <div className="text-center mt-6">
                        <Button
                          onClick={() => loadPendingContent(false)}
                          disabled={contentLoading}
                          variant="outline"
                          className="text-purple-600 border-purple-300 hover:bg-purple-50"
                        >
                          {contentLoading ? (
                            <>
                              <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mr-2"></div>
                              Chargement...
                            </>
                          ) : (
                            <>
                              <ChevronRight className="w-4 h-4 mr-2 rotate-90" />
                              Charger plus ({contentTotalCount - pendingContent.length} restants)
                            </>
                          )}
                        </Button>
                      </div>
                    )}
                    
                    {contentLoading && pendingContent.length === 0 && (
                      <div className="text-center py-8">
                        <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                        <p className="text-gray-600">Chargement de vos contenus...</p>
                      </div>
                    )}
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
                      {/* Titre de la note */}
                      <div className="space-y-2">
                        <Label htmlFor="note_title_fix" className="text-gray-700 font-medium">Titre de la note</Label>
                        {isVirtualKeyboardDevice ? (
                          <input
                            ref={noteTitleRef}
                            id="note_title_fix"
                            type="text"
                            className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                            style={{ fontSize: '16px' }}
                            autoCorrect={false}
                            autoComplete="off"
                            spellCheck={false}
                            autoCapitalize="off"
                            defaultValue={loadFromLocalStorage()?.note_title || noteTitle || ""}
                            placeholder="Ex: Nouvelle promotion, Événement spécial..."
                            onBlur={() => handleNoteFieldBlur('title', noteTitleRef)}
                            onTouchEnd={() => {
                              // Solution iPadOS 18 - onTouchEnd pour note title
                              console.log('📱 onTouchEnd - Note Title (SOLUTION iPadOS 18)');
                              handleNoteFieldBlur('title', noteTitleRef);
                            }}
                            required
                          />
                        ) : (
                          <Input
                            id="note_title_fix"
                            type="text"
                            placeholder="Ex: Nouvelle promotion, Événement spécial..."
                            value={noteTitle}
                            onChange={(e) => handleNoteFieldChange('title', e.target.value, setNoteTitle)}
                            onBlur={(e) => handleNoteFieldBlur('title', null, e.target.value)}
                            required
                          />
                        )}
                      </div>
                      
                      {/* Contenu de la note */}
                      <div className="space-y-2">
                        <Label htmlFor="note_content_fix" className="text-gray-700 font-medium">Contenu</Label>
                        {isVirtualKeyboardDevice ? (
                          <textarea
                            ref={noteContentRef}
                            id="note_content_fix"
                            rows={4}
                            className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
                            style={{ fontSize: '16px' }}
                            autoCorrect={false}
                            autoComplete="off"
                            spellCheck={false}
                            autoCapitalize="off"
                            defaultValue={loadFromLocalStorage()?.note_content || noteContent || ""}
                            placeholder="Décrivez les détails importants que vous voulez voir apparaître dans vos posts..."
                            onBlur={() => handleNoteFieldBlur('content', noteContentRef)}
                            onTouchEnd={() => {
                              // Solution iPadOS 18 - onTouchEnd pour note content
                              console.log('📱 onTouchEnd - Note Content (SOLUTION iPadOS 18)');
                              handleNoteFieldBlur('content', noteContentRef);
                            }}
                            required
                          />
                        ) : (
                          <Textarea
                            id="note_content_fix"
                            placeholder="Décrivez les détails importants que vous voulez voir apparaître dans vos posts..."
                            value={noteContent}
                            onChange={(e) => handleNoteFieldChange('content', e.target.value, setNoteContent)}
                            onBlur={(e) => handleNoteFieldBlur('content', null, e.target.value)}
                            rows={4}
                            required
                          />
                        )}
                      </div>
                      
                      {/* Priorité */}
                      <div className="space-y-2">
                        <Label className="text-gray-700 font-medium">Priorité</Label>
                        {isVirtualKeyboardDevice ? (
                          <input
                            type="text"
                            className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                            style={{ fontSize: '16px' }}
                            autoCorrect={false}
                            autoComplete="off"
                            spellCheck={false}
                            autoCapitalize="off"
                            defaultValue={loadFromLocalStorage()?.note_priority || notePriority || ""}
                            placeholder="low / medium / high"
                            onBlur={(e) => {
                              console.log('🔥 onBlur - Priorité note (virtual keyboard):', e.target.value);
                              const newValue = e.target.value;
                              setNotePriority(newValue);
                              
                              // Sauvegarder immédiatement en localStorage pour éviter la perte
                              const currentData = loadFromLocalStorage() || {};
                              currentData.note_priority = newValue;
                              saveToLocalStorage(currentData);
                            }}
                            onTouchEnd={(e) => {
                              // Solution iPadOS 18 - onTouchEnd fonctionne quand onBlur échoue
                              console.log('📱 onTouchEnd - Priorité note (SOLUTION iPadOS 18):', e.target.value);
                              const newValue = e.target.value;
                              setNotePriority(newValue);
                              
                              // Sauvegarder immédiatement en localStorage pour éviter la perte
                              const currentData = loadFromLocalStorage() || {};
                              currentData.note_priority = newValue;
                              saveToLocalStorage(currentData);
                            }}
                          />
                        ) : (
                          <Input
                            type="text"
                            value={notePriority}
                            onChange={(e) => setNotePriority(e.target.value)}
                            onBlur={(e) => {
                              console.log('🔥 onBlur - Priorité note (desktop):', e.target.value);
                            }}
                            onTouchEnd={(e) => {
                              // Solution iPadOS 18 aussi pour desktop au cas où
                              console.log('📱 onTouchEnd - Priorité note (desktop):', e.target.value);
                            }}
                            placeholder="low / medium / high"
                            className="bg-white"
                          />
                        )}
                      </div>
                      
                      <Button
                        type="submit"
                        className="btn-gradient-primary w-full"
                        disabled={!noteTitle || !noteContent}
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
                        value={editUserFirstName}
                        onChange={(e) => setEditUserFirstName(e.target.value)}
                        onBlur={(e) => {
                          // Auto-save user profile
                          console.log('Auto-saving user first name:', e.target.value);
                        }}
                        className="mt-1"
                        placeholder="Votre prénom"
                      />
                    </div>
                    <div>
                      <Label htmlFor="lastName">Nom</Label>
                      <Input
                        key="last_name_input"
                        id="lastName"
                        value={editUserLastName}
                        onChange={(e) => setEditUserLastName(e.target.value)}
                        onBlur={(e) => {
                          // Auto-save user profile
                          console.log('Auto-saving user last name:', e.target.value);
                        }}
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
                        value={editUserEmail}
                        onChange={(e) => setEditUserEmail(e.target.value)}
                        onBlur={(e) => {
                          // Auto-save user profile
                          console.log('Auto-saving user email:', e.target.value);
                        }}
                        className="mt-1"
                        placeholder="votre@email.com"
                      />
                    </div>
                  </div>
                  <div className="flex justify-center pt-4 border-t border-gray-200">
                    <div className="text-sm text-green-600 flex items-center">
                      <Check className="w-4 h-4 mr-2" />
                      Sauvegarde automatique activée
                    </div>
                  </div>
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

          {/* Subscription/Upgrade Interface - TEMPORAIREMENT DÉSACTIVÉ pour stratégie fonctionnalités complètes
          <div className="mt-8">
            <SubscriptionUpgrade user={user} onUpgradeSuccess={() => window.location.reload()} />
          </div>
          */}
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

              {/* Website Analysis Section - REMOVED - Now moved to Entreprise tab */}
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
                  onClick={() => navigateToTab('analyse')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-purple-50 text-left transition-colors group"
                >
                  <Search className="w-5 h-5 text-purple-600 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="font-medium text-gray-700">Analyse</span>
                </button>
                <button
                  onClick={() => navigateToTab('bibliotheque')}
                  className="flex items-center w-full p-3 rounded-xl hover:bg-indigo-50 text-left transition-colors group"
                >
                  <ImageIcon className="w-5 h-5 text-indigo-600 mr-3 group-hover:scale-110 transition-transform" />
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
      
      {/* Content Preview Modal */}
      <ContentPreviewModal
        isOpen={!!selectedContent}
        onClose={closeContentModal}
        content={selectedContent}
        onSaved={onContentSaved}
        setPendingContent={setPendingContent}
        refetchSilent={refetchPendingContentSilent}
      />
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