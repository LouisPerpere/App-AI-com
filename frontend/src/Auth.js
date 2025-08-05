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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthPage = ({ onAuthSuccess }) => {
  const [activeTab, setActiveTab] = useState('login');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

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
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/login`, {
        email: loginForm.email,
        password: loginForm.password
      });

      // Store tokens
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      
      // Set axios default header immediately
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      
      toast.success('Connexion réussie ! 🎉');
      
      // Call auth success callback
      onAuthSuccess();
    } catch (error) {
      console.error('Login error:', error);
      setError(error.response?.data?.detail || 'Erreur de connexion');
      toast.error('Erreur de connexion');
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
      const response = await axios.post(`${API}/auth/register`, {
        email: registerForm.email,
        password: registerForm.password,
        first_name: registerForm.first_name,
        last_name: registerForm.last_name
      });

      toast.success('Compte créé avec succès ! 🎉');
      
      // Auto login after registration
      const loginResponse = await axios.post(`${API}/auth/login`, {
        email: registerForm.email,
        password: registerForm.password
      });

      localStorage.setItem('access_token', loginResponse.data.access_token);
      localStorage.setItem('refresh_token', loginResponse.data.refresh_token);
      
      onAuthSuccess();
    } catch (error) {
      console.error('Registration error:', error);
      setError(error.response?.data?.detail || 'Erreur lors de la création du compte');
      toast.error('Erreur de création de compte');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-12 items-center">
        
        {/* Left Section - Marketing Copy */}
        <div className="space-y-8 text-center lg:text-left">
          {/* Logo and Title */}
          <div className="space-y-4">
            <div className="inline-flex items-center space-x-3 bg-white p-4 rounded-2xl shadow-lg">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl flex items-center justify-center">
                <Sparkles className="w-7 h-7 text-white animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  PostCraft
                </h1>
                <p className="text-sm text-gray-500 font-medium">by SocialGénie</p>
              </div>
            </div>
          </div>

          {/* Hero Content */}
          <div className="space-y-6">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 leading-tight">
              Explosez votre présence sur les 
              <span className="block bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 bg-clip-text text-transparent animate-pulse">
                réseaux sociaux 🚀
              </span>
            </h2>
            
            <p className="text-xl text-gray-600 leading-relaxed max-w-2xl">
              Créez, planifiez et publiez des contenus <strong>engageants</strong> qui convertissent. 
              Boostez votre succès en quelques clics ! ⚡
            </p>
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
    </div>
  );
};

export default AuthPage;