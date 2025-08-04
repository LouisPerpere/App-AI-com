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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-6">
      <Card className="w-full max-w-4xl shadow-2xl border-0 bg-white/80 backdrop-blur-lg">
        <CardHeader className="text-center pb-8">
          <div className="mx-auto mb-4 w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Configuration de votre entreprise
          </CardTitle>
          <CardDescription className="text-lg text-gray-600 mt-2">
            Quelques informations pour personnaliser vos publications
          </CardDescription>
          
          {subscriptionStatus && (
            <Alert className="mt-4 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
              <Crown className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-700 font-medium">
                {subscriptionStatus.message} - {subscriptionStatus.days_left} jours restants
              </AlertDescription>
            </Alert>
          )}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="business_name">Nom de l'entreprise</Label>
                <Input
                  id="business_name"
                  placeholder="Mon Restaurant"
                  value={profileForm.business_name}
                  onChange={(e) => setProfileForm({...profileForm, business_name: e.target.value})}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="business_type">Type d'activité</Label>
                <Select onValueChange={(value) => setProfileForm({...profileForm, business_type: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="restaurant">Restaurant</SelectItem>
                    <SelectItem value="retail">Commerce de détail</SelectItem>
                    <SelectItem value="services">Services</SelectItem>
                    <SelectItem value="freelance">Freelance</SelectItem>
                    <SelectItem value="ecommerce">E-commerce</SelectItem>
                    <SelectItem value="other">Autre</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="target_audience">Audience cible</Label>
              <Textarea
                id="target_audience"
                placeholder="Décrivez votre audience cible (âge, intérêts, localisation...)"
                value={profileForm.target_audience}
                onChange={(e) => setProfileForm({...profileForm, target_audience: e.target.value})}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="brand_tone">Ton de marque</Label>
                <Select onValueChange={(value) => setProfileForm({...profileForm, brand_tone: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">Professionnel</SelectItem>
                    <SelectItem value="casual">Décontracté</SelectItem>
                    <SelectItem value="friendly">Amical</SelectItem>
                    <SelectItem value="luxury">Luxueux</SelectItem>
                    <SelectItem value="fun">Amusant</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="posting_frequency">Fréquence de publication</Label>
                <Select onValueChange={(value) => setProfileForm({...profileForm, posting_frequency: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Quotidien</SelectItem>
                    <SelectItem value="3x_week">3x par semaine</SelectItem>
                    <SelectItem value="weekly">Hebdomadaire</SelectItem>
                    <SelectItem value="bi_weekly">Bi-hebdomadaire</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Réseaux sociaux préférés</Label>
              <div className="flex flex-wrap gap-3">
                {['facebook', 'instagram', 'linkedin'].map((platform) => (
                  <label key={platform} className="flex items-center space-x-2 cursor-pointer">
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
                      className="rounded"
                    />
                    <span className="capitalize font-medium">{platform}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Hashtags Section */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Hashtags prioritaires (toujours inclus)</Label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {profileForm.hashtags_primary.map((hashtag) => (
                    <Badge key={hashtag} variant="secondary" className="bg-purple-100 text-purple-800">
                      {hashtag}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="ml-1 h-4 w-4 p-0 hover:bg-purple-200"
                        onClick={() => removeHashtag('primary', hashtag)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
                <div className="flex space-x-2">
                  <Input
                    placeholder="Ajouter un hashtag prioritaire"
                    value={newPrimaryHashtag}
                    onChange={(e) => setNewPrimaryHashtag(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHashtag('primary', newPrimaryHashtag))}
                  />
                  <Button
                    type="button"
                    onClick={() => addHashtag('primary', newPrimaryHashtag)}
                    disabled={!newPrimaryHashtag.trim()}
                  >
                    Ajouter
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Hashtags secondaires (selon contexte)</Label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {profileForm.hashtags_secondary.map((hashtag) => (
                    <Badge key={hashtag} variant="outline" className="border-blue-200 text-blue-600">
                      {hashtag}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="ml-1 h-4 w-4 p-0 hover:bg-blue-100"
                        onClick={() => removeHashtag('secondary', hashtag)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
                <div className="flex space-x-2">
                  <Input
                    placeholder="Ajouter un hashtag secondaire"
                    value={newSecondaryHashtag}
                    onChange={(e) => setNewSecondaryHashtag(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHashtag('secondary', newSecondaryHashtag))}
                  />
                  <Button
                    type="button"
                    onClick={() => addHashtag('secondary', newSecondaryHashtag)}
                    disabled={!newSecondaryHashtag.trim()}
                  >
                    Ajouter
                  </Button>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="budget_range">Budget publicitaire mensuel</Label>
              <Select onValueChange={(value) => setProfileForm({...profileForm, budget_range: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionnez..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0-100">0€ - 100€</SelectItem>
                  <SelectItem value="100-500">100€ - 500€</SelectItem>
                  <SelectItem value="500-1000">500€ - 1000€</SelectItem>
                  <SelectItem value="1000+">1000€+</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button type="submit" className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
              Créer mon profil
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );

  const Dashboard = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="w-12 h-12">
                <AvatarImage src={businessProfile?.logo_url ? `${BACKEND_URL}${businessProfile.logo_url}` : ""} />
                <AvatarFallback className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
                  <Building className="w-6 h-6" />
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">PostCraft</h1>
                <p className="text-sm text-gray-600">{businessProfile?.business_name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {subscriptionStatus && (
                <Badge 
                  variant={subscriptionStatus.active ? "default" : "destructive"}
                  className={subscriptionStatus.active ? "bg-green-100 text-green-800" : ""}
                >
                  {subscriptionStatus.message}
                </Badge>
              )}
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                {generatedPosts.filter(p => p.status === 'pending').length} posts en attente
              </Badge>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="library" className="space-y-6">
          <TabsList className="grid grid-cols-5 w-full max-w-2xl mx-auto">
            <TabsTrigger value="library" className="flex items-center space-x-2">
              <ImageIcon className="w-4 h-4" />
              <span>Bibliothèque</span>
            </TabsTrigger>
            <TabsTrigger value="notes" className="flex items-center space-x-2">
              <Edit className="w-4 h-4" />
              <span>Notes</span>
            </TabsTrigger>
            <TabsTrigger value="posts" className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Posts</span>
            </TabsTrigger>
            <TabsTrigger value="calendar" className="flex items-center space-x-2">
              <CalendarIcon className="w-4 h-4" />
              <span>Calendrier</span>
            </TabsTrigger>
            <TabsTrigger value="social" className="flex items-center space-x-2">
              <Target className="w-4 h-4" />
              <span>Social</span>
            </TabsTrigger>
          </TabsList>

          {/* Library Tab */}
          <TabsContent value="library" className="space-y-6">
            {/* Galerie des contenus uploadés */}
            {(pendingContent.length > 0 || generatedPosts.some(p => p.visual_url)) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <ImageIcon className="w-5 h-5" />
                    <span>Vos contenus</span>
                  </CardTitle>
                  <CardDescription>
                    Cliquez sur une miniature pour ajouter du contexte et générer des posts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    {/* Contenus en attente de description */}
                    {pendingContent.map((content) => (
                      <Dialog key={content.id}>
                        <DialogTrigger asChild>
                          <div className="group relative aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105">
                            <img
                              src={`${BACKEND_URL}${content.visual_url || '/uploads/' + content.file_path.split('/').pop()}`}
                              alt="Contenu"
                              className="w-full h-full object-cover"
                            />
                            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200" />
                            <div className="absolute top-2 right-2">
                              <Badge variant="secondary" className="bg-orange-100 text-orange-600 text-xs">
                                Nouveau
                              </Badge>
                            </div>
                          </div>
                        </DialogTrigger>
                        <DialogContent className="max-w-4xl w-full h-[80vh]">
                          <DialogHeader>
                            <DialogTitle>Ajouter du contexte à votre contenu</DialogTitle>
                          </DialogHeader>
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
                            {/* Image en grand */}
                            <div className="flex items-center justify-center bg-gray-50 rounded-lg overflow-hidden">
                              <img
                                src={`${BACKEND_URL}${content.visual_url || '/uploads/' + content.file_path.split('/').pop()}`}
                                alt="Contenu"
                                className="max-w-full max-h-full object-contain"
                              />
                            </div>
                            
                            {/* Zone de texte et actions */}
                            <div className="flex flex-col space-y-4">
                              <form onSubmit={async (e) => {
                                e.preventDefault();
                                const formData = new FormData(e.target);
                                const description = formData.get('description');
                                
                                try {
                                  setIsGeneratingPosts(true);
                                  await axios.post(`${API}/content/${content.id}/describe`, { description });
                                  toast.success('Posts générés avec succès !');
                                  loadPendingContent();
                                  loadGeneratedPosts();
                                  // Fermer le dialog
                                  document.querySelector('[data-state="open"]')?.click();
                                } catch (error) {
                                  toast.error('Erreur lors de la génération');
                                } finally {
                                  setIsGeneratingPosts(false);
                                }
                              }} className="flex-1 flex flex-col space-y-4">
                                <div className="space-y-2">
                                  <Label htmlFor="description">Décrivez ce contenu</Label>
                                  <Textarea
                                    id="description"
                                    name="description"
                                    placeholder="Décrivez en détail ce contenu : produit, service, événement, ambiance, personnes, lieu, contexte particulier... Plus vous donnez de détails, meilleurs seront les posts générés !"
                                    className="min-h-[200px] resize-none"
                                    required
                                  />
                                </div>
                                
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                  <h4 className="font-medium text-blue-900 mb-2">💡 Conseils pour une bonne description</h4>
                                  <ul className="text-sm text-blue-700 space-y-1">
                                    <li>• Décrivez le produit/service en détail</li>
                                    <li>• Mentionnez l'ambiance, les couleurs, l'émotion</li>
                                    <li>• Ajoutez le contexte (promotion, nouveauté, saison...)</li>
                                    <li>• Précisez votre public cible pour ce contenu</li>
                                  </ul>
                                </div>
                                
                                <Button 
                                  type="submit" 
                                  disabled={isGeneratingPosts} 
                                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                                  size="lg"
                                >
                                  {isGeneratingPosts ? (
                                    <>
                                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                                      Génération en cours...
                                    </>
                                  ) : (
                                    <>
                                      <Sparkles className="w-4 h-4 mr-2" />
                                      Générer mes posts IA
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
                        <div key={post.id} className="group relative aspect-square bg-gray-100 rounded-lg overflow-hidden">
                          <img
                            src={`${BACKEND_URL}${post.visual_url}`}
                            alt="Contenu généré"
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200" />
                          <div className="absolute top-2 right-2">
                            <Badge 
                              variant={post.status === 'posted' ? 'default' : 'secondary'}
                              className={`text-xs ${
                                post.status === 'posted' 
                                  ? 'bg-green-100 text-green-600' 
                                  : post.status === 'approved'
                                  ? 'bg-blue-100 text-blue-600'
                                  : 'bg-gray-100 text-gray-600'
                              }`}
                            >
                              {post.status === 'posted' ? 'Publié' : 
                               post.status === 'approved' ? 'Approuvé' : 
                               'En attente'}
                            </Badge>
                          </div>
                        </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Section d'upload */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="w-5 h-5" />
                  <span>Ajouter du contenu</span>
                </CardTitle>
                <CardDescription>
                  Uploadez vos photos et vidéos pour créer de nouveaux posts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-400 transition-colors">
                  <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <div className="space-y-2">
                    <p className="text-lg font-medium text-gray-700">
                      Glissez vos fichiers ici ou
                    </p>
                    <Button
                      variant="outline"
                      onClick={() => document.getElementById('file-input').click()}
                      className="mx-2"
                    >
                      Parcourir
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
                  <p className="text-sm text-gray-500 mt-2">
                    Formats supportés: JPG, PNG, MP4, MOV (max 10 fichiers)
                  </p>
                </div>

                {selectedFiles.length > 0 && (
                  <div className="space-y-4">
                    <h4 className="font-medium">Fichiers sélectionnés ({selectedFiles.length})</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="relative">
                          <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                            {file.type.startsWith('image/') ? (
                              <img
                                src={URL.createObjectURL(file)}
                                alt={file.name}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center">
                                <FileText className="w-8 h-8 text-gray-400" />
                              </div>
                            )}
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-500 text-white hover:bg-red-600"
                            onClick={() => setSelectedFiles(selectedFiles.filter((_, i) => i !== index))}
                          >
                            <X className="w-3 h-3" />
                          </Button>
                          <p className="text-xs text-gray-600 mt-1 truncate">{file.name}</p>
                        </div>
                      ))}
                    </div>
                    <Button
                      onClick={handleBatchUpload}
                      disabled={isUploading}
                      className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    >
                      {isUploading ? 'Upload en cours...' : `Uploader ${selectedFiles.length} fichier(s)`}
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
          <TabsContent value="notes" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Edit className="w-5 h-5" />
                  <span>Notes et informations</span>
                </CardTitle>
                <CardDescription>
                  Ajoutez des informations importantes à intégrer dans vos posts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <form onSubmit={async (e) => {
                  e.preventDefault();
                  try {
                    await axios.post(`${API}/notes`, noteForm);
                    setNoteForm({ title: '', content: '', priority: 'normal' });
                    toast.success('Note ajoutée !');
                    loadNotes();
                  } catch (error) {
                    toast.error('Erreur lors de l\'ajout de la note');
                  }
                }} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      placeholder="Titre de la note"
                      value={noteForm.title}
                      onChange={(e) => setNoteForm({...noteForm, title: e.target.value})}
                      required
                    />
                    <Select 
                      value={noteForm.priority} 
                      onValueChange={(value) => setNoteForm({...noteForm, priority: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="high">Priorité haute</SelectItem>
                        <SelectItem value="normal">Priorité normale</SelectItem>
                        <SelectItem value="low">Priorité basse</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Textarea
                    placeholder="Contenu de la note (ex: fermeture exceptionnelle, nouvelle offre, événement...)"
                    value={noteForm.content}
                    onChange={(e) => setNoteForm({...noteForm, content: e.target.value})}
                    required
                  />
                  <Button type="submit" className="w-full">
                    <Edit className="w-4 h-4 mr-2" />
                    Ajouter la note
                  </Button>
                </form>
              </CardContent>
            </Card>

            {notes.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Notes enregistrées</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {notes.map((note) => (
                      <div key={note.id} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <h4 className="font-medium">{note.title}</h4>
                              <Badge 
                                variant={note.priority === 'high' ? 'destructive' : note.priority === 'normal' ? 'default' : 'secondary'}
                              >
                                {note.priority === 'high' ? 'Haute' : note.priority === 'normal' ? 'Normale' : 'Basse'}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600">{note.content}</p>
                            <p className="text-xs text-gray-400 mt-2">
                              {new Date(note.created_at).toLocaleDateString('fr-FR')}
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