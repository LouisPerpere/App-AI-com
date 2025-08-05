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
import { Building, Sparkles, Crown, Upload, ImageIcon, FileText, X, Edit, CalendarIcon, Target, LogOut, Check, Send, Clock, ChevronLeft, ChevronRight } from 'lucide-react';

// Import toast for notifications
import { toast } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    budget_range: ''
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
              
              <Button
                variant="outline"
                size="lg"
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900 border-2 rounded-xl px-6"
              >
                <LogOut className="w-5 h-5 mr-2" />
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="library" className="space-y-8">
          <TabsList className="grid grid-cols-5 w-full max-w-3xl mx-auto bg-white/80 backdrop-blur-lg p-2 rounded-2xl shadow-xl">
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
                  <p className="text-xl text-gray-500">Uploadez vos premiers contenus pour voir la magie opérer ! 🪄</p>
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
                  Ajoutez des informations importantes pour enrichir vos posts automatiquement 🎯
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
                    Posts générés automatiquement 🚀
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
                  Connectez vos comptes Facebook et Instagram pour publier automatiquement ✨
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
          {user.subscription_status === 'trial' || user.subscription_status === 'expired' ? (
            <div className="mt-8">
              <SubscriptionUpgrade user={user} onUpgradeSuccess={() => window.location.reload()} />
            </div>
          ) : null}
        </Tabs>
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