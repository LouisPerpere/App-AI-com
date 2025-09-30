import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Alert, AlertDescription } from './components/ui/alert';
import { Eye, EyeOff, LogIn, UserPlus, Sparkles, Shield, Zap, Users, Building, Upload, FileText, Send, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

// Fonction robuste pour obtenir l'URL backend avec fallback
const getBackendURL = () => {
  // Tentative 1: Variables d'environnement standard
  if (import.meta.env?.REACT_APP_BACKEND_URL) {
    return import.meta.env.REACT_APP_BACKEND_URL;
  }
  
  // Tentative 2: Process.env (fallback)
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  
  // Tentative 3: Détection automatique URL courante
  if (typeof window !== 'undefined') {
    const currentUrl = window.location.origin;
    if (currentUrl.includes('insta-automate-2.preview.emergentagent.com')) {
      return 'https://social-pub-hub.preview.emergentagent.com';
    }
  }
  
  // Fallback final: URL hardcodée pour garantir fonctionnement
  return 'https://social-pub-hub.preview.emergentagent.com';
};

const BACKEND_URL = getBackendURL();
const API = `${BACKEND_URL}/api`;

console.log('🔍 AUTH DEBUG - API URL:', API);

// Ping backend to wake Render free instance (can take 20-40s)
const pingBackend = async (maxWaitMs = 60000) => {
  const start = Date.now();
  let lastErr = null;
  while (Date.now() - start < maxWaitMs) {
    try {
      const res = await axios.get(`${API}/health`, { 
        timeout: 12000, 
        withCredentials: false 
      });
      if (res?.status === 200) return true;
    } catch (e) {
      lastErr = e;
      // short pause then retry
      await new Promise(r => setTimeout(r, 1500));
    }
  }
  console.warn('⚠️ Backend ping timeout after', maxWaitMs, 'ms', lastErr?.message);
  return false;
};
// Composant Accordéon discret pour Mentions Légales
const LegalAccordion = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="max-w-md mx-auto mt-6 mb-4 px-4">
      {/* Bouton accordéon discret */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-center space-x-2 text-xs text-gray-500 hover:text-gray-700 transition-colors py-2"
      >
        <span>Mentions légales</span>
        <svg 
          className={`w-3 h-3 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {/* Contenu extensible */}
      {isOpen && (
        <div className="mt-2 p-3 bg-gray-50 border rounded-lg text-xs text-gray-600 space-y-2">
          <div>
            <strong>EI Fou De Vanille</strong> • SIRET 952 513 661 00019
          </div>
          <div>
            44 Rue De Lorraine, 94700 Maisons Alfort • RCS Créteil
          </div>
          <div>
            Responsable : Alexandra Perpere • 
            <a href="mailto:contact@claire-marcus.com" className="text-purple-600 ml-1">
              Contact
            </a>
          </div>
          <div>
            Hébergement : <a href="https://emergentagent.com" target="_blank" rel="noopener noreferrer" className="text-purple-600">Emergent</a> (Paris)
          </div>
          <div className="text-center pt-2 border-t border-gray-200">
            © {new Date().getFullYear()} Claire & Marcus - TVA Non Applicable
          </div>
        </div>
      )}
    </div>
  );
};

const AuthPage = ({ onAuthSuccess }) => {
  const [activeTab, setActiveTab] = useState('login');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showConnecting, setShowConnecting] = useState(false);

  // Login form state
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });

  // Register form state
  const [registerForm, setRegisterForm] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: ''
  });

  const handleLogin = async (e) => {
    console.log('🔥 handleLogin called!', e);
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      console.log('🚀 LOGIN START - API URL:', API);
      console.log('🚀 LOGIN DATA:', { email: loginForm.email });
      console.log('🔍 Form values:', loginForm);

      // SIMPLIFICATION TEMPORAIRE - pas de pingBackend
      console.log('⏳ Making direct login request...');

      const response = await axios.post(`${API}/auth/login-robust`, {
        email: loginForm.email,
        password: loginForm.password
      }, {
        timeout: 15000,
        withCredentials: false,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('✅ LOGIN SUCCESS:', response.status, response.data);

      // Store tokens with better error handling
      const accessToken = response.data.access_token || response.data.token;
      const refreshToken = response.data.refresh_token;

      if (!accessToken) {
        throw new Error('No access token received from server');
      }

      // Store tokens with Safari Private fallback
      try {
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
          localStorage.setItem('refresh_token', refreshToken);
        }
      } catch (storageErr) {
        console.warn('⚠️ localStorage unavailable, using in-memory token fallback');
        window.__ACCESS_TOKEN = accessToken;
        if (refreshToken) window.__REFRESH_TOKEN = refreshToken;
      }
      
      // Set axios default header (no cookies)
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      axios.defaults.withCredentials = false;
      
      console.log('🎉 LOGIN COMPLETE - Calling onAuthSuccess()');
      toast.success('Connexion réussie ! 🎉');
      
      // Small delay to ensure defaults and state are applied before navigation
      await new Promise(r => setTimeout(r, 100));
      
      // Call auth success callback with user data
      try {
        console.log('🔄 About to call onAuthSuccess callback with user data...');
        const userData = {
          userId: response.data.user_id,
          email: response.data.email,
          firstName: response.data.first_name,
          lastName: response.data.last_name,
          businessName: response.data.business_name,
          subscriptionStatus: response.data.subscription_status
        };
        await onAuthSuccess(userData);
        console.log('✅ onAuthSuccess callback completed successfully');
      } catch (callbackError) {
        console.error('❌ ERROR in onAuthSuccess callback:', callbackError);
        // Continue anyway - don't let callback errors break login
      } finally {
        setShowConnecting(false);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('❌ LOGIN ERROR:', error);
      console.error('❌ LOGIN ERROR RESPONSE:', error.response?.data);
      console.error('❌ LOGIN ERROR STATUS:', error.response?.status);
      
      let errorMessage = 'Erreur de connexion';
      
      if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || error.response.data?.message || `Erreur ${error.response.status}`;
      } else if (error.request) {
        // Request was made but no response
        errorMessage = 'Impossible de contacter le serveur. Vérifiez votre connexion internet.';
      } else {
        // Something else happened
        errorMessage = error.message || 'Erreur inattendue';
      }
      
      setShowConnecting(false);
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      setIsLoading(false);
      return;
    }

    try {
      console.log('🚀 REGISTRATION START - API URL:', API);
      console.log('🚀 REGISTRATION DATA:', {
        email: registerForm.email,
        password: registerForm.password.substring(0, 3) + '***',
        business_name: `${registerForm.first_name} ${registerForm.last_name}`
      });

      const response = await axios.post(`${API}/auth/register`, {
        email: registerForm.email,
        password: registerForm.password,
        business_name: `${registerForm.first_name} ${registerForm.last_name}`
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('✅ REGISTRATION SUCCESS:', response.status, response.data);
      toast.success('Compte créé avec succès ! 🎉');
      
      console.log('🔄 AUTO-LOGIN START - Making API call to:', `${API}/auth/login-robust`);
      
      // Auto login after registration
      const loginResponse = await axios.post(`${API}/auth/login-robust`, {
        email: registerForm.email,
        password: registerForm.password
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('✅ AUTO-LOGIN SUCCESS:', loginResponse.status, loginResponse.data);

      // Store tokens with better error handling
      const accessToken = loginResponse.data.access_token || loginResponse.data.token;
      const refreshToken = loginResponse.data.refresh_token;

      if (!accessToken) {
        throw new Error('No access token received after registration');
      }

      localStorage.setItem('access_token', accessToken);
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      
      console.log('🎉 REGISTRATION COMPLETE - Calling onAuthSuccess()');
      onAuthSuccess();
    } catch (error) {
      console.error('❌ REGISTRATION ERROR:', error);
      console.error('❌ REGISTRATION ERROR RESPONSE:', error.response?.data);
      console.error('❌ REGISTRATION ERROR STATUS:', error.response?.status);
      
      let errorMessage = 'Erreur lors de la création du compte';
      
      if (error.response) {
        // Server responded with error
        if (error.response.status === 422) {
          errorMessage = 'Données invalides. Vérifiez vos informations.';
        } else if (error.response.status === 409) {
          errorMessage = 'Un compte existe déjà avec cette adresse email.';
        } else {
          errorMessage = error.response.data?.detail || error.response.data?.message || `Erreur ${error.response.status}`;
        }
      } else if (error.request) {
        // Request was made but no response
        errorMessage = 'Impossible de contacter le serveur. Vérifiez votre connexion internet.';
      } else {
        // Something else happened
        errorMessage = error.message || 'Erreur inattendue lors de la création du compte';
      }
      
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 flex items-center justify-center p-4">
      {/* Connection Modal */}
      {showConnecting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm text-center border border-purple-100">
            <div className="mx-auto mb-4 w-12 h-12 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center animate-pulse">
              <span className="text-white text-lg font-bold">CM</span>
            </div>
            <p className="text-gray-900 font-semibold mb-2">Connexion en cours…</p>
            <p className="text-gray-600 text-sm">Merci de patienter quelques instants, nous appelons Claire et Marcus.</p>
          </div>
        </div>
      )}
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-12 items-center">
        
        {/* Left Section - Marketing Copy */}
        <div className="space-y-8 text-center lg:text-left">
          {/* Logo and Title */}
          <div className="space-y-4">
            <div className="inline-flex items-center space-x-3 bg-white p-4 rounded-2xl shadow-lg">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl flex items-center justify-center">
                <div className="logo-cm">
                  <span className="logo-c">C</span>
                  <span className="logo-m">M</span>
                </div>
              </div>
              <div>
                <h1 className="claire-marcus-title bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Claire et Marcus
                </h1>
                <div className="text-sm text-gray-500 claire-marcus-subtitle">
                  <p>Claire rédige, Marcus programme.</p>
                  <p className="text-purple-600 font-bold text-base mt-1 breathing-text">Vous respirez.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Hero Content */}
          <div className="space-y-6">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 leading-tight">
              Libérez-vous des 
              <span className="block bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 bg-clip-text text-transparent animate-pulse">
                réseaux sociaux 🚀
              </span>
            </h2>
            
            <p className="text-xl text-gray-600 leading-relaxed max-w-2xl">
              Décrivez votre business, uploadez vos photos et vidéos, et <strong>laissez la magie opérer</strong> ! 
              On crée les posts pour vous, vous les validez et on les programme directement ✨
            </p>
          </div>

          {/* How It Works Section - Moved up and improved */}
          <div className="bg-gradient-to-br from-indigo-50 via-white to-purple-50 rounded-3xl p-8 border-2 border-purple-100 shadow-lg">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-3 flex items-center justify-center">
                <Sparkles className="w-6 h-6 mr-3 text-purple-600" />
                Comment ça fonctionne ?
                <Sparkles className="w-6 h-6 ml-3 text-purple-600" />
              </h3>
              <p className="text-gray-600 font-medium">4 étapes simples pour gagner du temps et de l'énergie</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Step 1 */}
              <div className="flex items-center space-x-4 p-4 bg-white rounded-2xl shadow-sm border border-purple-100">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-lg font-bold shadow-lg">
                  1
                </div>
                <div className="flex items-center space-x-3 flex-1">
                  <Building className="w-6 h-6 text-purple-600 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-gray-900 text-sm">Profil entreprise</p>
                    <p className="text-xs text-gray-600">Décrivez votre activité</p>
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-center space-x-4 p-4 bg-white rounded-2xl shadow-sm border border-purple-100">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-lg font-bold shadow-lg">
                  2
                </div>
                <div className="flex items-center space-x-3 flex-1">
                  <Upload className="w-6 h-6 text-purple-600 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-gray-900 text-sm">Upload contenus</p>
                    <p className="text-xs text-gray-600">Photos, vidéos, notes</p>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-center space-x-4 p-4 bg-white rounded-2xl shadow-sm border border-purple-100">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-lg font-bold shadow-lg">
                  3
                </div>
                <div className="flex items-center space-x-3 flex-1">
                  <FileText className="w-6 h-6 text-purple-600 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-gray-900 text-sm">On génère & vous validez</p>
                    <p className="text-xs text-gray-600">Posts optimisés à approuver</p>
                  </div>
                </div>
              </div>

              {/* Step 4 */}
              <div className="flex items-center space-x-4 p-4 bg-white rounded-2xl shadow-sm border border-purple-100">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-lg font-bold shadow-lg">
                  4
                </div>
                <div className="flex items-center space-x-3 flex-1">
                  <Send className="w-6 h-6 text-purple-600 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-gray-900 text-sm">Publication automatique</p>
                    <p className="text-xs text-gray-600">On s'occupe de tout !</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 text-center">
              <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full font-bold shadow-lg">
                <CheckCircle className="w-5 h-5 mr-2" />
                Simple, efficace, et vous fait gagner du temps !
              </div>
            </div>
          </div>

          {/* Feature Highlights */}
          <div className="grid sm:grid-cols-2 gap-6 pt-4">
            <div className="flex items-start space-x-4 p-4 bg-white/80 backdrop-blur-sm rounded-2xl border border-purple-100">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Contenu Viral</h3>
                <p className="text-sm text-gray-600">Des posts qui captivent et convertissent vos audiences</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4 p-4 bg-white/80 backdrop-blur-sm rounded-2xl border border-green-100">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Boost Express</h3>
                <p className="text-sm text-gray-600">Programmation ultra-rapide sur tous vos réseaux</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4 p-4 bg-white/80 backdrop-blur-sm rounded-2xl border border-blue-100">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <Users className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Multi-plateformes</h3>
                <p className="text-sm text-gray-600">Facebook, Instagram, LinkedIn en un seul endroit</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4 p-4 bg-white/80 backdrop-blur-sm rounded-2xl border border-orange-100">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1">1 mois offert</h3>
                <p className="text-sm text-gray-600">Testez sans engagement, résultats garantis !</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Section - Auth Forms */}
        <div className="max-w-md w-full mx-auto">
          <Card className="shadow-2xl border-0 bg-white/95 backdrop-blur-sm">
            <CardHeader className="space-y-2 text-center pb-8">
              <CardTitle className="text-2xl font-bold text-gray-900">
                Bienvenue
              </CardTitle>
              <CardDescription className="text-base text-gray-600">
                Connectez-vous ou créez votre compte pour commencer
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-2 bg-gray-100 p-1 rounded-xl h-12">
                  <TabsTrigger value="login" className="rounded-lg font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm">
                    Se connecter
                  </TabsTrigger>
                  <TabsTrigger value="register" className="rounded-lg font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm">
                    Créer un compte
                  </TabsTrigger>
                </TabsList>

                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertDescription className="text-red-700 text-sm">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                <TabsContent value="login" className="space-y-4">
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="login-email" className="text-gray-700 font-medium">Email</Label>
                      <Input
                        id="login-email"
                        type="email"
                        placeholder="votre@email.com"
                        value={loginForm.email}
                        onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                        required
                        className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="login-password" className="text-gray-700 font-medium">Mot de passe</Label>
                      <div className="relative">
                        <Input
                          id="login-password"
                          type={showPassword ? 'text' : 'password'}
                          placeholder="••••••••"
                          value={loginForm.password}
                          onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                          required
                          className="h-12 pr-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                        />
                        <button
                          type="button"
                          className="absolute inset-y-0 right-0 pr-3 flex items-center"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? (
                            <EyeOff className="h-5 w-5 text-gray-400" />
                          ) : (
                            <Eye className="h-5 w-5 text-gray-400" />
                          )}
                        </button>
                      </div>
                    </div>
                    
                    <Button 
                      type="submit" 
                      className="w-full h-12 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Connexion...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <LogIn className="w-5 h-5" />
                          <span>Se connecter</span>
                        </div>
                      )}
                    </Button>
                  </form>
                  
                  <p className="text-center text-sm text-gray-500">
                    Mot de passe oublié ? 
                    <button className="text-purple-600 hover:text-purple-700 font-medium ml-1">
                      Cliquez ici
                    </button>
                  </p>
                </TabsContent>

                <TabsContent value="register" className="space-y-4">
                  <form onSubmit={handleRegister} className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-2">
                        <Label htmlFor="register-firstname" className="text-gray-700 font-medium">Prénom</Label>
                        <Input
                          id="register-firstname"
                          type="text"
                          placeholder="John"
                          value={registerForm.first_name}
                          onChange={(e) => setRegisterForm({ ...registerForm, first_name: e.target.value })}
                          required
                          className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="register-lastname" className="text-gray-700 font-medium">Nom</Label>
                        <Input
                          id="register-lastname"
                          type="text"
                          placeholder="Doe"
                          value={registerForm.last_name}
                          onChange={(e) => setRegisterForm({ ...registerForm, last_name: e.target.value })}
                          required
                          className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="register-email" className="text-gray-700 font-medium">Email</Label>
                      <Input
                        id="register-email"
                        type="email"
                        placeholder="votre@email.com"
                        value={registerForm.email}
                        onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                        required
                        className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="register-password" className="text-gray-700 font-medium">Mot de passe</Label>
                      <div className="relative">
                        <Input
                          id="register-password"
                          type={showPassword ? 'text' : 'password'}
                          placeholder="••••••••"
                          value={registerForm.password}
                          onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                          required
                          className="h-12 pr-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                        />
                        <button
                          type="button"
                          className="absolute inset-y-0 right-0 pr-3 flex items-center"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? (
                            <EyeOff className="h-5 w-5 text-gray-400" />
                          ) : (
                            <Eye className="h-5 w-5 text-gray-400" />
                          )}
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="register-confirmpassword" className="text-gray-700 font-medium">Confirmer le mot de passe</Label>
                      <Input
                        id="register-confirmpassword"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={registerForm.confirmPassword}
                        onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                        required
                        className="h-12 border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                      />
                    </div>
                    
                    <Button 
                      type="submit" 
                      className="w-full h-12 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Création...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <UserPlus className="w-5 h-5" />
                          <span>Créer mon compte</span>
                        </div>
                      )}
                    </Button>
                  </form>
                  
                  <p className="text-xs text-gray-500 text-center leading-relaxed">
                    En créant un compte, vous acceptez nos{' '}
                    <button className="text-purple-600 hover:text-purple-700 font-medium">
                      conditions d'utilisation
                    </button>{' '}
                    et notre{' '}
                    <button className="text-purple-600 hover:text-purple-700 font-medium">
                      politique de confidentialité
                    </button>
                  </p>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* Accordéon Mentions Légales - Discret en bas */}
      <LegalAccordion />
    </div>
  );
};

export default AuthPage;