import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Alert, AlertDescription } from './components/ui/alert';
import { Badge } from './components/ui/badge';
import { Check, CreditCard, Sparkles, Zap, Crown, Clock, Users, TrendingUp, Shield } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://claire-marcus-api.onrender.com';
const API = `${BACKEND_URL}/api`;

console.log('💳 PAYMENT PAGE - Backend URL:', BACKEND_URL);

const PaymentPage = ({ onSuccess, onCancel }) => {
  const [packages, setPackages] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [checkingPayment, setCheckingPayment] = useState(false);

  useEffect(() => {
    loadPackages();
    loadCurrentSubscription();
    checkReturnFromStripe();
  }, []);

  const loadPackages = async () => {
    try {
      const response = await axios.get(`${API}/payments/packages`);
      setPackages(response.data.packages);
      console.log('📦 Packages loaded:', response.data);
    } catch (error) {
      console.error('Error loading packages:', error);
      setError('Erreur lors du chargement des forfaits');
    }
  };

  const loadCurrentSubscription = async () => {
    try {
      const response = await axios.get(`${API}/payments/my-subscription`);
      setCurrentSubscription(response.data);
      console.log('📋 Current subscription:', response.data);
    } catch (error) {
      console.error('Error loading subscription:', error);
    }
  };

  const checkReturnFromStripe = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const paymentSuccess = urlParams.get('payment_success');
    const paymentCancelled = urlParams.get('payment_cancelled');

    if (sessionId && paymentSuccess) {
      console.log('🔄 Returning from Stripe, checking payment status...');
      setCheckingPayment(true);
      pollPaymentStatus(sessionId);
    } else if (paymentCancelled) {
      setError('Paiement annulé. Vous pouvez réessayer quand vous le souhaitez.');
    }
  };

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 8;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      setCheckingPayment(false);
      setError('Vérification du paiement expirée. Veuillez vérifier votre email de confirmation.');
      return;
    }

    try {
      console.log(`🔍 Checking payment status (attempt ${attempts + 1})...`);
      const response = await axios.get(`${API}/payments/v1/checkout/status/${sessionId}`);
      const data = response.data;

      console.log('📊 Payment status:', data);

      if (data.payment_status === 'paid') {
        setCheckingPayment(false);
        // Clear URL parameters
        window.history.replaceState({}, '', window.location.pathname);
        
        // Reload subscription data
        await loadCurrentSubscription();
        
        if (onSuccess) {
          onSuccess(data);
        } else {
          window.location.reload(); // Fallback to reload the app
        }
        return;
      } else if (data.status === 'expired') {
        setCheckingPayment(false);
        setError('Session de paiement expirée. Veuillez réessayer.');
        return;
      }

      // Continue polling if still pending
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setCheckingPayment(false);
      setError('Erreur lors de la vérification du paiement. Veuillez réessayer.');
    }
  };

  const initiatePayment = async (packageId) => {
    setLoading(true);
    setError('');

    try {
      console.log('💳 Initiating payment for package:', packageId);
      
      const originUrl = window.location.origin;
      console.log('🌍 Origin URL:', originUrl);

      const response = await axios.post(`${API}/payments/v1/checkout/session`, {
        package_id: packageId,
        origin_url: originUrl
      });

      console.log('✅ Checkout session created:', response.data);

      if (response.data.url) {
        console.log('🔀 Redirecting to Stripe:', response.data.url);
        window.location.href = response.data.url;
      } else {
        throw new Error('Aucune URL de checkout reçue');
      }
    } catch (error) {
      console.error('❌ Payment error:', error);
      setError(error.response?.data?.detail || error.message || 'Erreur lors de la création de la session de paiement');
      setLoading(false);
    }
  };

  const getPackageIcon = (planId) => {
    const icons = {
      starter: <CreditCard className="w-6 h-6" />,
      rocket: <Zap className="w-6 h-6" />,
      pro: <Crown className="w-6 h-6" />
    };
    return icons[planId] || <Sparkles className="w-6 h-6" />;
  };

  const getPackageColor = (planId) => {
    const colors = {
      starter: 'from-blue-500 to-cyan-500',
      rocket: 'from-purple-500 to-pink-500',
      pro: 'from-yellow-500 to-orange-500'
    };
    return colors[planId] || 'from-gray-500 to-gray-600';
  };

  if (checkingPayment) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-indigo-100">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold mb-2">Vérification du paiement...</h3>
            <p className="text-gray-600">Nous vérifions le statut de votre paiement. Veuillez patienter.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choisissez votre forfait 
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent"> Claire et Marcus</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Libérez-vous des réseaux sociaux avec nos forfaits adaptés à vos besoins
          </p>
        </div>

        {error && (
          <Alert className="mb-8 border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {currentSubscription && currentSubscription.subscription_status === 'active' && (
          <Alert className="mb-8 border-green-200 bg-green-50">
            <AlertDescription className="text-green-800">
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4" />
                Abonnement actuel : <strong>{currentSubscription.subscription_plan}</strong>
                {currentSubscription.subscription_ends_at && (
                  <span className="ml-2">
                    (expire le {new Date(currentSubscription.subscription_ends_at).toLocaleDateString()})
                  </span>
                )}
              </div>
            </AlertDescription>
          </Alert>
        )}

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {Object.entries(packages).map(([packageId, pkg]) => (
            <Card key={packageId} className={`relative overflow-hidden border-2 ${pkg.plan_id === 'rocket' ? 'border-purple-500 shadow-2xl transform scale-105' : 'border-gray-200 hover:border-purple-300'} transition-all duration-300`}>
              {pkg.plan_id === 'rocket' && (
                <div className="absolute top-0 left-0 right-0 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-center py-2 text-sm font-semibold">
                  ⭐ LE PLUS POPULAIRE
                </div>
              )}
              
              <CardHeader className={`pb-4 ${pkg.plan_id === 'rocket' ? 'pt-12' : 'pt-6'}`}>
                <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${getPackageColor(pkg.plan_id)} p-3 text-white mb-4`}>
                  {getPackageIcon(pkg.plan_id)}
                </div>
                <CardTitle className="text-2xl">{pkg.name}</CardTitle>
                <CardDescription className="text-gray-600">{pkg.description}</CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-gray-900">€{pkg.amount}</span>
                  <span className="text-gray-600">/mois</span>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <ul className="space-y-3">
                  {pkg.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-green-600" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <div className="pt-4">
                  <Button
                    onClick={() => initiatePayment(packageId)}
                    disabled={loading}
                    className={`w-full h-12 bg-gradient-to-r ${getPackageColor(pkg.plan_id)} hover:opacity-90 text-white font-semibold text-lg transition-all duration-300`}
                  >
                    {loading ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Redirection...
                      </div>
                    ) : (
                      `Choisir ${pkg.name}`
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-12">
          <h2 className="text-2xl font-bold text-center mb-8">Pourquoi choisir Claire et Marcus ?</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <Clock className="w-8 h-8 mx-auto mb-3 text-blue-600" />
              <h3 className="font-semibold mb-2">Gain de temps</h3>
              <p className="text-sm text-gray-600">Automatisez votre présence sociale</p>
            </div>
            <div className="text-center">
              <TrendingUp className="w-8 h-8 mx-auto mb-3 text-green-600" />
              <h3 className="font-semibold mb-2">Croissance</h3>
              <p className="text-sm text-gray-600">Augmentez votre visibilité</p>
            </div>
            <div className="text-center">
              <Users className="w-8 h-8 mx-auto mb-3 text-purple-600" />
              <h3 className="font-semibold mb-2">Engagement</h3>
              <p className="text-sm text-gray-600">Créez du lien avec vos clients</p>
            </div>
            <div className="text-center">
              <Shield className="w-8 h-8 mx-auto mb-3 text-orange-600" />
              <h3 className="font-semibold mb-2">Sécurité</h3>
              <p className="text-sm text-gray-600">Paiements sécurisés par Stripe</p>
            </div>
          </div>
        </div>

        <div className="text-center text-gray-500 text-sm">
          <p>🔒 Paiement 100% sécurisé par Stripe • 🔄 Annulation possible à tout moment</p>
          <p className="mt-2">Tous les forfaits incluent un support client prioritaire</p>
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;