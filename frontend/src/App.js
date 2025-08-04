import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import axios from 'axios';
import AuthPage from './Auth';
import AdminDashboard from './AdminDashboard';
import FacebookCallback from './FacebookCallback';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Calendar } from './components/ui/calendar';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Label } from './components/ui/label';
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { Alert, AlertDescription } from './components/ui/alert';
import { 
  Upload, Calendar as CalendarIcon, Check, X, Edit, Sparkles, Target, TrendingUp, 
  ChevronLeft, ChevronRight, Clock, Send, Image as ImageIcon, FileText, Building,
  LogOut, User, Settings, Crown
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function MainApp() {
  const location = useLocation();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [activeStep, setActiveStep] = useState('onboarding');
  const [businessProfile, setBusinessProfile] = useState(null);
  const [generatedPosts, setGeneratedPosts] = useState([]);
  const [pendingContent, setPendingContent] = useState([]);
  const [notes, setNotes] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isGeneratingPosts, setIsGeneratingPosts] = useState(false);
  const [currentPostIndex, setCurrentPostIndex] = useState(0);
  const [socialConnections, setSocialConnections] = useState([]);
  const [isConnectingSocial, setIsConnectingSocial] = useState(false);

  // Business profile form state
  const [profileForm, setProfileForm] = useState({
    business_name: '',
    business_type: '',
    target_audience: '',
    brand_tone: '',
    posting_frequency: '',
    preferred_platforms: [],
    budget_range: '',
    hashtags_primary: [],
    hashtags_secondary: []
  });

  // Note form state
  const [noteForm, setNoteForm] = useState({
    title: '',
    content: '',
    priority: 'normal'
  });

  // Hashtag management state
  const [newPrimaryHashtag, setNewPrimaryHashtag] = useState('');
  const [newSecondaryHashtag, setNewSecondaryHashtag] = useState('');

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // Check if token is valid and get user info
      const userResponse = await axios.get(`${API}/auth/me`);
      setUser(userResponse.data);
      setIsAuthenticated(true);

      // Check if user is admin
      if (userResponse.data.is_admin) {
        setActiveStep('admin');
        setIsLoading(false);
        return;
      }

      // Get subscription status
      const subResponse = await axios.get(`${API}/auth/subscription-status`);
      setSubscriptionStatus(subResponse.data);

      // Check if user has business profile
      try {
        const profileResponse = await axios.get(`${API}/business-profile`);
        setBusinessProfile(profileResponse.data);
        setActiveStep('dashboard');
        loadGeneratedPosts();
        loadPendingContent();
        loadNotes();
        loadSocialConnections();
      } catch (error) {
        // No business profile found, show onboarding
        setActiveStep('onboarding');
      }

    } catch (error) {
      console.log('Auth check failed:', error);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setIsLoading(false);
    }
  };

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
    checkAuthStatus();
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
    setBusinessProfile(null);
    setActiveStep('onboarding');
    toast.success('Déconnexion réussie');
  };

  const loadGeneratedPosts = async () => {
    try {
      const response = await axios.get(`${API}/generated-posts`);
      setGeneratedPosts(response.data);
    } catch (error) {
      console.error('Error loading posts:', error);
    }
  };

  const loadPendingContent = async () => {
    try {
      const response = await axios.get(`${API}/content/pending-description`);
      setPendingContent(response.data);
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

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/business-profile`, profileForm);
      setBusinessProfile(response.data);
      setActiveStep('dashboard');
      toast.success('Profil d\'entreprise créé avec succès !');
    } catch (error) {
      console.error('Error creating profile:', error);
      toast.error('Erreur lors de la création du profil');
    }
  };

  const handleLogoUpload = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/business-profile/logo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setBusinessProfile({...businessProfile, logo_url: response.data.logo_url});
      toast.success('Logo mis à jour !');
    } catch (error) {
      console.error('Error uploading logo:', error);
      toast.error('Erreur lors de l\'upload du logo');
    }
  };

  const addHashtag = (type, hashtag) => {
    if (hashtag.trim() && !hashtag.startsWith('#')) {
      hashtag = '#' + hashtag.trim();
    }
    
    if (type === 'primary' && hashtag && !profileForm.hashtags_primary.includes(hashtag)) {
      setProfileForm({
        ...profileForm,
        hashtags_primary: [...profileForm.hashtags_primary, hashtag]
      });
      setNewPrimaryHashtag('');
    } else if (type === 'secondary' && hashtag && !profileForm.hashtags_secondary.includes(hashtag)) {
      setProfileForm({
        ...profileForm,
        hashtags_secondary: [...profileForm.hashtags_secondary, hashtag]
      });
      setNewSecondaryHashtag('');
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

  const handleBatchUpload = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Veuillez sélectionner au moins un fichier');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      await axios.post(`${API}/upload-content-batch`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast.success(`${selectedFiles.length} fichiers uploadés avec succès !`);
      setSelectedFiles([]);
      loadPendingContent();
    } catch (error) {
      console.error('Error uploading files:', error);
      toast.error('Erreur lors de l\'upload des fichiers');
    } finally {
      setIsUploading(false);
    }
  };

  // Show loading screen
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center mx-auto">
            <Sparkles className="w-8 h-8 text-white animate-pulse" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">PostCraft</h1>
          <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }

  // Show auth page if not authenticated
  if (!isAuthenticated) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  // Show admin dashboard if user is admin
  if (user && user.is_admin && activeStep === 'admin') {
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

            {/* Hashtags Section */}
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
      {/* Header */}
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

          {/* Library Tab */}
          <TabsContent value="library" className="space-y-8">
            {/* Galerie des contenus uploadés */}
            {(pendingContent.length > 0 || generatedPosts.some(p => p.visual_url)) && (
              <Card className="card-gradient">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-3 text-2xl">
                    <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
                      <ImageIcon className="w-6 h-6 text-white" />
                    </div>
                    <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                      Vos contenus magiques ✨
                    </span>
                  </CardTitle>
                  <CardDescription className="text-lg text-gray-600">
                    Cliquez sur une miniature pour ajouter du contexte et créer des posts extraordinaires
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
                    {/* Contenus en attente de description */}
                    {pendingContent.map((content) => (
                      <Dialog key={content.id}>
                        <DialogTrigger asChild>
                          <div className="thumbnail-hover group relative aspect-square bg-gradient-to-br from-purple-50 to-pink-50 cursor-pointer">
                            <img
                              src={`${BACKEND_URL}${content.visual_url || '/uploads/' + content.file_path.split('/').pop()}`}
                              alt="Contenu"
                              className="w-full h-full object-cover"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300" />
                            <div className="absolute top-3 right-3">
                              <Badge className="badge-warning animate-pulse">
                                ✨ Nouveau
                              </Badge>
                            </div>
                            <div className="absolute bottom-3 left-3 right-3 opacity-0 group-hover:opacity-100 transition-all duration-300">
                              <p className="text-white font-semibold text-sm">Cliquez pour décrire ✍️</p>
                            </div>
                          </div>
                        </DialogTrigger>
                        <DialogContent className="max-w-6xl w-full h-[85vh] card-glass">
                          <DialogHeader>
                            <DialogTitle className="text-2xl bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                              🎨 Donnez vie à votre contenu
                            </DialogTitle>
                          </DialogHeader>
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
                            {/* Image en grand */}
                            <div className="flex items-center justify-center bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl overflow-hidden">
                              <img
                                src={`${BACKEND_URL}${content.visual_url || '/uploads/' + content.file_path.split('/').pop()}`}
                                alt="Contenu"
                                className="max-w-full max-h-full object-contain rounded-2xl"
                              />
                            </div>
                            
                            {/* Zone de texte et actions */}
                            <div className="flex flex-col space-y-6">
                              <form onSubmit={async (e) => {
                                e.preventDefault();
                                const formData = new FormData(e.target);
                                const description = formData.get('description');
                                
                                try {
                                  setIsGeneratingPosts(true);
                                  await axios.post(`${API}/content/${content.id}/describe`, { description });
                                  toast.success('🎉 Posts créés avec succès !');
                                  loadPendingContent();
                                  loadGeneratedPosts();
                                  // Fermer le dialog
                                  document.querySelector('[data-state="open"]')?.click();
                                } catch (error) {
                                  toast.error('Erreur lors de la création');
                                } finally {
                                  setIsGeneratingPosts(false);
                                }
                              }} className="flex-1 flex flex-col space-y-6">
                                <div className="space-y-3">
                                  <Label htmlFor="description" className="text-xl font-semibold text-gray-700">
                                    ✍️ Décrivez ce contenu
                                  </Label>
                                  <Textarea
                                    id="description"
                                    name="description"
                                    placeholder="Décrivez en détail ce contenu : produit, service, événement, ambiance, personnes, lieu, contexte particulier... Plus vous donnez de détails, plus vos posts seront exceptionnels ! 🚀"
                                    className="input-modern min-h-[200px] resize-none text-lg"
                                    required
                                  />
                                </div>
                                
                                <div className="card-gradient p-6 rounded-2xl">
                                  <h4 className="font-bold text-purple-900 mb-3 text-lg">💡 Conseils pour une description parfaite</h4>
                                  <ul className="text-purple-700 space-y-2 font-medium">
                                    <li>• 🎯 Décrivez le produit/service en détail</li>
                                    <li>• 🌈 Mentionnez l'ambiance, les couleurs, l'émotion</li>
                                    <li>• 🎪 Ajoutez le contexte (promotion, nouveauté, saison...)</li>
                                    <li>• 👥 Précisez votre public cible pour ce contenu</li>
                                  </ul>
                                </div>
                                
                                <Button 
                                  type="submit" 
                                  disabled={isGeneratingPosts} 
                                  className="w-full h-16 text-xl font-bold btn-gradient-primary"
                                  size="lg"
                                >
                                  {isGeneratingPosts ? (
                                    <>
                                      <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin mr-3"></div>
                                      ✨ Création en cours...
                                    </>
                                  ) : (
                                    <>
                                      <Sparkles className="w-6 h-6 mr-3" />
                                      🚀 Créer mes posts magiques
                                    </>
                                  )}
                                </Button>
                              </form>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    ))}
                    
                    {/* Contenus déjà traités (posts générés) */}
                    {generatedPosts
                      .filter(post => post.visual_url)
                      .slice(0, 12) // Limiter à 12 pour ne pas surcharger
                      .map((post) => (
                        <div key={post.id} className="thumbnail-hover group relative aspect-square">
                          <img
                            src={`${BACKEND_URL}${post.visual_url}`}
                            alt="Contenu généré"
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300" />
                          <div className="absolute top-3 right-3">
                            <Badge 
                              className={`${
                                post.status === 'posted' 
                                  ? 'badge-success' 
                                  : post.status === 'approved'
                                  ? 'badge-info'
                                  : 'badge-warning'
                              }`}
                            >
                              {post.status === 'posted' ? '✅ Publié' : 
                               post.status === 'approved' ? '👍 Approuvé' : 
                               '⏳ En attente'}
                            </Badge>
                          </div>
                        </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Section d'upload */}
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center">
                    <Upload className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Ajouter du contenu
                  </span>
                </CardTitle>
                <CardDescription className="text-lg text-gray-600">
                  Uploadez vos photos et vidéos pour créer de nouveaux posts spectaculaires 🎬
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="upload-zone p-12 text-center">
                  <div className="space-y-4">
                    <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto animate-float">
                      <ImageIcon className="w-10 h-10 text-white" />
                    </div>
                    <div className="space-y-3">
                      <p className="text-2xl font-bold text-gray-700">
                        Glissez vos fichiers ici ou
                      </p>
                      <Button
                        variant="outline"
                        onClick={() => document.getElementById('file-input').click()}
                        className="btn-gradient-secondary text-lg px-8 py-4"
                      >
                        📁 Parcourir
                      </Button>
                      <input
                        id="file-input"
                        type="file"
                        multiple
                        accept="image/*,video/*"
                        className="hidden"
                        onChange={(e) => setSelectedFiles(Array.from(e.target.files))}
                      />
                    </div>
                    <p className="text-lg text-gray-500 font-medium">
                      📸 Formats supportés: JPG, PNG, MP4, MOV (max 10 fichiers)
                    </p>
                  </div>
                </div>

                {selectedFiles.length > 0 && (
                  <div className="space-y-6">
                    <h4 className="text-xl font-bold text-gray-700">
                      📋 Fichiers sélectionnés ({selectedFiles.length})
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="relative thumbnail-hover">
                          <div className="aspect-square bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl overflow-hidden">
                            {file.type.startsWith('image/') ? (
                              <img
                                src={URL.createObjectURL(file)}
                                alt={file.name}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100">
                                <FileText className="w-12 h-12 text-purple-600" />
                              </div>
                            )}
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-red-500 text-white hover:bg-red-600 hover:scale-110"
                            onClick={() => setSelectedFiles(selectedFiles.filter((_, i) => i !== index))}
                          >
                            <X className="w-4 h-4" />
                          </Button>
                          <p className="text-sm text-gray-600 mt-2 truncate font-medium">{file.name}</p>
                        </div>
                      ))}
                    </div>
                    <Button
                      onClick={handleBatchUpload}
                      disabled={isUploading}
                      className="w-full h-16 text-xl font-bold btn-gradient-primary"
                    >
                      {isUploading ? '⏳ Upload en cours...' : `🚀 Uploader ${selectedFiles.length} fichier(s)`}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Posts Tab */}
          <TabsContent value="posts" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-5 h-5" />
                    <span>Posts générés</span>
                  </div>
                  <Badge variant="secondary">
                    {generatedPosts.length} posts
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {generatedPosts.length > 0 ? (
                  <div className="space-y-4">
                    {/* Carousel Navigation */}
                    <div className="flex items-center justify-between">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPostIndex(Math.max(0, currentPostIndex - 1))}
                        disabled={currentPostIndex === 0}
                      >
                        <ChevronLeft className="w-4 h-4" />
                        Précédent
                      </Button>
                      <span className="text-sm text-gray-500">
                        {currentPostIndex + 1} / {generatedPosts.length}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPostIndex(Math.min(generatedPosts.length - 1, currentPostIndex + 1))}
                        disabled={currentPostIndex === generatedPosts.length - 1}
                      >
                        Suivant
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>

                    {/* Current Post */}
                    {generatedPosts[currentPostIndex] && (
                      <Card className="border-2">
                        <CardContent className="p-6">
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="space-y-4">
                              <div className="flex items-center justify-between">
                                <Badge 
                                  variant={generatedPosts[currentPostIndex].platform === 'facebook' ? 'default' : 'secondary'}
                                  className={`capitalize ${
                                    generatedPosts[currentPostIndex].platform === 'facebook' 
                                      ? 'bg-blue-100 text-blue-800' 
                                      : generatedPosts[currentPostIndex].platform === 'instagram'
                                      ? 'bg-pink-100 text-pink-800'
                                      : 'bg-blue-100 text-blue-800'
                                  }`}
                                >
                                  {generatedPosts[currentPostIndex].platform}
                                </Badge>
                                <Badge variant={
                                  generatedPosts[currentPostIndex].status === 'pending' ? 'secondary' :
                                  generatedPosts[currentPostIndex].status === 'approved' ? 'default' :
                                  generatedPosts[currentPostIndex].status === 'posted' ? 'success' : 'destructive'
                                }>
                                  {generatedPosts[currentPostIndex].status}
                                </Badge>
                              </div>
                              
                              <div className="bg-gray-50 p-4 rounded-lg">
                                <h4 className="font-medium mb-2">Contenu du post</h4>
                                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                                  {generatedPosts[currentPostIndex].post_text}
                                </p>
                              </div>

                              <div>
                                <h4 className="font-medium mb-2">Hashtags</h4>
                                <div className="flex flex-wrap gap-2">
                                  {generatedPosts[currentPostIndex].hashtags?.map((hashtag, idx) => (
                                    <Badge key={idx} variant="outline" className="text-blue-600">
                                      #{hashtag}
                                    </Badge>
                                  ))}
                                </div>
                              </div>

                              <div className="flex items-center space-x-2 text-sm text-gray-500">
                                <Clock className="w-4 h-4" />
                                <span>
                                  Programmé pour le {new Date(generatedPosts[currentPostIndex].scheduled_date).toLocaleDateString('fr-FR')} 
                                  à {generatedPosts[currentPostIndex].scheduled_time}
                                </span>
                              </div>
                            </div>

                            <div className="space-y-4">
                              {generatedPosts[currentPostIndex].visual_url && (
                                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                                  <img
                                    src={`${BACKEND_URL}${generatedPosts[currentPostIndex].visual_url}`}
                                    alt="Contenu"
                                    className="w-full h-full object-cover"
                                  />
                                </div>
                              )}

                              <div className="flex space-x-2">
                                {generatedPosts[currentPostIndex].status === 'pending' && (
                                  <Button
                                    variant="default"
                                    className="flex-1 bg-green-600 hover:bg-green-700"
                                    onClick={async () => {
                                      try {
                                        await axios.put(`${API}/posts/${generatedPosts[currentPostIndex].id}/approve`);
                                        toast.success('Post approuvé !');
                                        loadGeneratedPosts();
                                      } catch (error) {
                                        toast.error('Erreur lors de l\'approbation');
                                      }
                                    }}
                                  >
                                    <Check className="w-4 h-4 mr-2" />
                                    Approuver
                                  </Button>
                                )}
                                
                                {(generatedPosts[currentPostIndex].status === 'approved' || generatedPosts[currentPostIndex].status === 'pending') && (
                                  <Button
                                    variant="outline"
                                    className="flex-1"
                                    onClick={async () => {
                                      try {
                                        await axios.post(`${API}/posts/${generatedPosts[currentPostIndex].id}/publish`);
                                        toast.success('Post publié !');
                                        loadGeneratedPosts();
                                      } catch (error) {
                                        toast.error('Erreur lors de la publication');
                                      }
                                    }}
                                  >
                                    <Send className="w-4 h-4 mr-2" />
                                    Publier maintenant
                                  </Button>
                                )}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">Aucun post généré pour le moment</p>
                    <p className="text-sm text-gray-400">Uploadez du contenu pour commencer</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notes Tab */}
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
              <CardContent className="space-y-6">
                <form onSubmit={async (e) => {
                  e.preventDefault();
                  try {
                    await axios.post(`${API}/notes`, noteForm);
                    setNoteForm({ title: '', content: '', priority: 'normal' });
                    toast.success('✨ Note ajoutée avec succès !');
                    loadNotes();
                  } catch (error) {
                    toast.error('Erreur lors de l\'ajout de la note');
                  }
                }} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Input
                      placeholder="📝 Titre de la note"
                      value={noteForm.title}
                      onChange={(e) => setNoteForm({...noteForm, title: e.target.value})}
                      required
                      className="input-modern text-lg"
                    />
                    <Select 
                      value={noteForm.priority} 
                      onValueChange={(value) => setNoteForm({...noteForm, priority: value})}
                    >
                      <SelectTrigger className="input-modern">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="card-glass">
                        <SelectItem value="high">🔥 Priorité haute</SelectItem>
                        <SelectItem value="normal">⚡ Priorité normale</SelectItem>
                        <SelectItem value="low">💫 Priorité basse</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Textarea
                    placeholder="💬 Contenu de la note (ex: fermeture exceptionnelle, nouvelle offre, événement spécial...)"
                    value={noteForm.content}
                    onChange={(e) => setNoteForm({...noteForm, content: e.target.value})}
                    required
                    className="input-modern min-h-[120px] text-lg"
                  />
                  <Button type="submit" className="w-full h-14 text-xl font-bold btn-gradient-primary">
                    <Edit className="w-6 h-6 mr-3" />
                    ✨ Ajouter la note magique
                  </Button>
                </form>
              </CardContent>
            </Card>

            {notes.length > 0 && (
              <Card className="card-gradient">
                <CardHeader>
                  <CardTitle className="text-2xl bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    📚 Vos notes enregistrées
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {notes.map((note) => (
                      <div key={note.id} className="card-glass p-6 hover:shadow-2xl transition-all duration-300">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-3">
                              <h4 className="text-xl font-bold text-gray-800">{note.title}</h4>
                              <Badge 
                                className={`${note.priority === 'high' ? 'badge-warning' : note.priority === 'normal' ? 'badge-info' : 'badge-success'}`}
                              >
                                {note.priority === 'high' ? '🔥 Haute' : note.priority === 'normal' ? '⚡ Normale' : '💫 Basse'}
                              </Badge>
                            </div>
                            <p className="text-lg text-gray-700 leading-relaxed">{note.content}</p>
                            <p className="text-sm text-gray-500 mt-4 font-medium">
                              📅 {new Date(note.created_at).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Calendar Tab */}
          <TabsContent value="calendar" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CalendarIcon className="w-5 h-5" />
                  <span>Calendrier de publication</span>
                </CardTitle>
                <CardDescription>
                  Planifiez et gérez vos publications à venir
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <CalendarIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Calendrier de publication</p>
                  <p className="text-sm text-gray-400">Fonctionnalité en développement</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Social Tab */}
          <TabsContent value="social" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5" />
                  <span>Comptes sociaux connectés</span>
                </CardTitle>
                <CardDescription>
                  Connectez vos comptes Facebook et Instagram pour publier automatiquement
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Connexion Facebook */}
                <div className="border rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold text-lg">f</span>
                      </div>
                      <div>
                        <h3 className="font-semibold">Facebook</h3>
                        <p className="text-sm text-gray-500">Connectez vos pages Facebook</p>
                      </div>
                    </div>
                    <Button
                      onClick={connectFacebook}
                      disabled={isConnectingSocial}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {isConnectingSocial ? 'Connexion...' : 'Connecter Facebook'}
                    </Button>
                  </div>

                  {/* Pages Facebook connectées */}
                  {socialConnections.filter(conn => conn.platform === 'facebook').length > 0 && (
                    <div className="space-y-3">
                      <h4 className="font-medium text-sm text-gray-700">Pages connectées :</h4>
                      {socialConnections
                        .filter(conn => conn.platform === 'facebook')
                        .map((connection) => (
                          <div key={connection.id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                            <div className="flex items-center space-x-3">
                              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                <span className="text-blue-600 font-bold text-sm">f</span>
                              </div>
                              <div>
                                <p className="font-medium">{connection.page_name}</p>
                                <p className="text-xs text-gray-500">
                                  Connecté le {new Date(connection.connected_at).toLocaleDateString('fr-FR')}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline" className="bg-green-50 text-green-600 border-green-200">
                                Actif
                              </Badge>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => disconnectSocialAccount(connection.id)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                    </div>
                  )}
                </div>

                {/* Instagram */}
                <div className="border rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                        <ImageIcon className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold">Instagram</h3>
                        <p className="text-sm text-gray-500">Connectez vos comptes Instagram Business</p>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-orange-100 text-orange-600">
                      Via Facebook
                    </Badge>
                  </div>

                  {/* Comptes Instagram connectés */}
                  {socialConnections.filter(conn => conn.platform === 'instagram').length > 0 ? (
                    <div className="space-y-3">
                      <h4 className="font-medium text-sm text-gray-700">Comptes connectés :</h4>
                      {socialConnections
                        .filter(conn => conn.platform === 'instagram')
                        .map((connection) => (
                          <div key={connection.id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                            <div className="flex items-center space-x-3">
                              <div className="w-8 h-8 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center">
                                <ImageIcon className="w-4 h-4 text-purple-600" />
                              </div>
                              <div>
                                <p className="font-medium">@{connection.platform_username}</p>
                                <p className="text-xs text-gray-500">
                                  Connecté le {new Date(connection.connected_at).toLocaleDateString('fr-FR')}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline" className="bg-green-50 text-green-600 border-green-200">
                                Actif
                              </Badge>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => disconnectSocialAccount(connection.id)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-gray-500">
                      <p className="text-sm">Aucun compte Instagram connecté</p>
                      <p className="text-xs mt-1">Connectez d'abord une page Facebook avec un compte Instagram Business lié</p>
                    </div>
                  )}
                </div>

                {/* Instructions */}
                <Alert className="bg-blue-50 border-blue-200">
                  <Target className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-700">
                    <strong>Comment connecter vos comptes :</strong>
                    <br />
                    1. Cliquez sur "Connecter Facebook" pour autoriser l'accès à vos pages
                    <br />
                    2. Les comptes Instagram Business liés à vos pages Facebook seront automatiquement connectés
                    <br />
                    3. Vous pourrez ensuite publier directement depuis l'onglet "Posts"
                  </AlertDescription>
                </Alert>

                {/* État sans connexions */}
                {socialConnections.length === 0 && (
                  <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
                    <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun compte connecté</h3>
                    <p className="text-gray-500 mb-4">
                      Connectez vos comptes Facebook et Instagram pour commencer à publier automatiquement
                    </p>
                    <Button
                      onClick={connectFacebook}
                      disabled={isConnectingSocial}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {isConnectingSocial ? 'Connexion...' : 'Connecter mon premier compte'}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
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