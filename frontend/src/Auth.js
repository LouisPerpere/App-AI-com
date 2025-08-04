import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Alert, AlertDescription } from './components/ui/alert';
import { Eye, EyeOff, LogIn, UserPlus, Sparkles, Shield, Zap, Users } from 'lucide-react';
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
      
      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;

      toast.success('Connexion réussie !');
      onAuthSuccess();

    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.detail || 'Erreur de connexion';
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

    // Validation
    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      setIsLoading(false);
      return;
    }

    if (registerForm.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      setIsLoading(false);
      return;
    }

    try {
      // Register user
      await axios.post(`${API}/auth/register`, {
        email: registerForm.email,
        password: registerForm.password,
        first_name: registerForm.first_name,
        last_name: registerForm.last_name
      });

      toast.success('Compte créé avec succès !');

      // Auto-login after registration
      const loginResponse = await axios.post(`${API}/auth/login`, {
        email: registerForm.email,
        password: registerForm.password
      });

      // Store tokens
      localStorage.setItem('access_token', loginResponse.data.access_token);
      localStorage.setItem('refresh_token', loginResponse.data.refresh_token);
      
      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${loginResponse.data.access_token}`;

      onAuthSuccess();

    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error.response?.data?.detail || 'Erreur lors de la création du compte';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const LoginForm = () => (
    <form onSubmit={handleLogin} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="login-email">Email</Label>
        <Input
          id="login-email"
          type="email"
          placeholder="votre@email.com"
          value={loginForm.email}
          onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
          required
          className="h-12"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="login-password">Mot de passe</Label>
        <div className="relative">
          <Input
            id="login-password"
            type={showPassword ? "text" : "password"}
            placeholder="••••••••"
            value={loginForm.password}
            onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
            required
            className="h-12 pr-12"
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-2 top-2 h-8 w-8 p-0"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}

      <Button 
        type="submit" 
        disabled={isLoading}
        className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
      >
        {isLoading ? (
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Connexion...</span>
          </div>
        ) : (
          <>
            <LogIn className="w-5 h-5 mr-2" />
            Se connecter
          </>
        )}
      </Button>

      <div className="text-center">
        <Button variant="link" className="text-sm text-gray-600">
          Mot de passe oublié ?
        </Button>
      </div>
    </form>
  );

  const RegisterForm = () => (
    <form onSubmit={handleRegister} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="first-name">Prénom</Label>
          <Input
            id="first-name"
            type="text"
            placeholder="Jean"
            value={registerForm.first_name}
            onChange={(e) => setRegisterForm({...registerForm, first_name: e.target.value})}
            required
            className="h-12"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="last-name">Nom</Label>
          <Input
            id="last-name"
            type="text"
            placeholder="Dupont"
            value={registerForm.last_name}
            onChange={(e) => setRegisterForm({...registerForm, last_name: e.target.value})}
            required
            className="h-12"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="register-email">Email</Label>
        <Input
          id="register-email"
          type="email"
          placeholder="votre@email.com"
          value={registerForm.email}
          onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
          required
          className="h-12"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="register-password">Mot de passe</Label>
        <div className="relative">
          <Input
            id="register-password"
            type={showPassword ? "text" : "password"}
            placeholder="••••••••"
            value={registerForm.password}
            onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
            required
            className="h-12 pr-12"
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-2 top-2 h-8 w-8 p-0"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirm-password">Confirmer le mot de passe</Label>
        <Input
          id="confirm-password"
          type={showPassword ? "text" : "password"}
          placeholder="••••••••"
          value={registerForm.confirmPassword}
          onChange={(e) => setRegisterForm({...registerForm, confirmPassword: e.target.value})}
          required
          className="h-12"
        />
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}

      <Button 
        type="submit" 
        disabled={isLoading}
        className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
      >
        {isLoading ? (
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Création...</span>
          </div>
        ) : (
          <>
            <UserPlus className="w-5 h-5 mr-2" />
            Créer mon compte
          </>
        )}
      </Button>

      <div className="text-center text-sm text-gray-600">
        En créant un compte, vous acceptez nos{' '}
        <Button variant="link" className="p-0 h-auto text-sm">
          conditions d'utilisation
        </Button>
      </div>
    </form>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-6">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        
        {/* Left side - Branding */}
        <div className="space-y-8 text-center lg:text-left">
          <div className="space-y-6">
            <div className="flex items-center justify-center lg:justify-start space-x-3">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  PostCraft
                </h1>
                <p className="text-gray-600">by SocialGénie</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-gray-900">
                Automatisez vos réseaux sociaux avec l'IA
              </h2>
              <p className="text-xl text-gray-600">
                Créez, planifiez et publiez automatiquement des posts engageants pour votre entreprise
              </p>
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                <Zap className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Génération IA</h3>
                <p className="text-sm text-gray-600">Posts naturels et engageants</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <Shield className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Automatisation</h3>
                <p className="text-sm text-gray-600">Publication programmée</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                <Users className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Multi-plateformes</h3>
                <p className="text-sm text-gray-600">Facebook, Instagram, LinkedIn</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">14 jours gratuits</h3>
                <p className="text-sm text-gray-600">Essai sans engagement</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right side - Auth forms */}
        <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-lg">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-2xl">Bienvenue</CardTitle>
            <CardDescription>
              Connectez-vous ou créez votre compte pour commencer
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-2 h-12">
                <TabsTrigger value="login" className="h-10">Se connecter</TabsTrigger>
                <TabsTrigger value="register" className="h-10">Créer un compte</TabsTrigger>
              </TabsList>
              
              <TabsContent value="login">
                <LoginForm />
              </TabsContent>
              
              <TabsContent value="register">
                <RegisterForm />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AuthPage;