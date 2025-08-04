import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
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
import { Upload, Calendar as CalendarIcon, Check, X, Edit, Sparkles, Target, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeStep, setActiveStep] = useState('onboarding');
  const [businessProfile, setBusinessProfile] = useState(null);
  const [generatedPosts, setGeneratedPosts] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadDescription, setUploadDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  // Business profile form state
  const [profileForm, setProfileForm] = useState({
    business_name: '',
    business_type: '',
    target_audience: '',
    brand_tone: '',
    posting_frequency: '',
    preferred_platforms: [],
    budget_range: ''
  });

  useEffect(() => {
    checkExistingProfile();
  }, []);

  const checkExistingProfile = async () => {
    try {
      const response = await axios.get(`${API}/business-profiles`);
      if (response.data.length > 0) {
        setBusinessProfile(response.data[0]);
        setActiveStep('dashboard');
        loadGeneratedPosts(response.data[0].id);
      }
    } catch (error) {
      console.log('No existing profile found');
    }
  };

  const loadGeneratedPosts = async (businessId) => {
    try {
      const response = await axios.get(`${API}/generated-posts/${businessId}`);
      setGeneratedPosts(response.data);
    } catch (error) {
      console.error('Error loading posts:', error);
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

  const handleFileUpload = async () => {
    if (!selectedFile || !uploadDescription.trim()) {
      toast.error('Veuillez sélectionner un fichier et ajouter une description');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('description', uploadDescription);

    try {
      await axios.post(`${API}/upload-content/${businessProfile.id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast.success('Contenu uploadé et analysé avec succès !');
      setSelectedFile(null);
      setUploadDescription('');
      loadGeneratedPosts(businessProfile.id);
    } catch (error) {
      console.error('Error uploading content:', error);
      toast.error('Erreur lors de l\'upload du contenu');
    } finally {
      setIsUploading(false);
    }
  };

  const handlePostAction = async (postId, action) => {
    try {
      await axios.put(`${API}/post/${postId}/${action}`);
      toast.success(`Post ${action === 'approve' ? 'approuvé' : 'rejeté'} avec succès !`);
      loadGeneratedPosts(businessProfile.id);
    } catch (error) {
      console.error(`Error ${action} post:`, error);
      toast.error(`Erreur lors de l'${action} du post`);
    }
  };

  const OnboardingForm = () => (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-6">
      <Card className="w-full max-w-2xl shadow-2xl border-0 bg-white/80 backdrop-blur-lg">
        <CardHeader className="text-center pb-8">
          <div className="mx-auto mb-4 w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            SocialGénie
          </CardTitle>
          <CardDescription className="text-lg text-gray-600 mt-2">
            Automatisez votre présence sur les réseaux sociaux avec l'IA
          </CardDescription>
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
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SocialGénie</h1>
                <p className="text-sm text-gray-600">{businessProfile?.business_name}</p>
              </div>
            </div>
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              {generatedPosts.filter(p => p.status === 'pending').length} posts en attente
            </Badge>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="upload" className="space-y-8">
          <TabsList className="grid w-full grid-cols-3 h-12">
            <TabsTrigger value="upload" className="flex items-center space-x-2">
              <Upload className="w-4 h-4" />
              <span>Upload Contenu</span>
            </TabsTrigger>
            <TabsTrigger value="posts" className="flex items-center space-x-2">
              <Target className="w-4 h-4" />
              <span>Posts Générés</span>
            </TabsTrigger>
            <TabsTrigger value="calendar" className="flex items-center space-x-2">
              <CalendarIcon className="w-4 h-4" />
              <span>Calendrier</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <Card className="p-8">
              <CardHeader className="text-center pb-6">
                <CardTitle className="text-2xl">Uploadez votre contenu</CardTitle>
                <CardDescription>
                  Ajoutez vos photos ou vidéos avec une description pour générer automatiquement des posts optimisés
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-purple-400 transition-colors">
                  <input
                    type="file"
                    accept="image/*,video/*"
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-lg font-semibold text-gray-700">
                      {selectedFile ? selectedFile.name : 'Cliquez pour sélectionner un fichier'}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">PNG, JPG, MP4 jusqu'à 10MB</p>
                  </label>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description du contenu</Label>
                  <Textarea
                    id="description"
                    placeholder="Décrivez ce que montre cette image/vidéo, le contexte, l'émotion que vous voulez transmettre..."
                    value={uploadDescription}
                    onChange={(e) => setUploadDescription(e.target.value)}
                    rows={4}
                  />
                </div>

                <Button 
                  onClick={handleFileUpload} 
                  disabled={isUploading || !selectedFile || !uploadDescription.trim()}
                  className="w-full h-12 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                >
                  {isUploading ? (
                    <>
                      <TrendingUp className="w-4 h-4 mr-2 animate-spin" />
                      Analyse en cours...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Analyser et générer les posts
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="posts">
            <div className="grid gap-6">
              {generatedPosts.length === 0 ? (
                <Card className="p-12 text-center">
                  <CardContent>
                    <Target className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-700 mb-2">Aucun post généré</h3>
                    <p className="text-gray-500">Uploadez du contenu pour voir vos posts générés automatiquement</p>
                  </CardContent>
                </Card>
              ) : (
                generatedPosts.map((post) => (
                  <Card key={post.id} className="overflow-hidden">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <Badge variant="outline" className="capitalize">
                            {post.platform}
                          </Badge>
                          <Badge 
                            variant={post.status === 'approved' ? 'default' : 
                                   post.status === 'rejected' ? 'destructive' : 'secondary'}
                          >
                            {post.status === 'pending' ? 'En attente' :
                             post.status === 'approved' ? 'Approuvé' : 'Rejeté'}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-500">
                          Programmé le {new Date(post.scheduled_date).toLocaleDateString('fr-FR')}
                        </div>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-4 mb-4">
                        <p className="text-gray-800 whitespace-pre-wrap">{post.post_text}</p>
                      </div>

                      {post.hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-4">
                          {post.hashtags.map((hashtag, index) => (
                            <Badge key={index} variant="secondary" className="text-blue-600">
                              #{hashtag}
                            </Badge>
                          ))}
                        </div>
                      )}

                      {post.status === 'pending' && (
                        <div className="flex space-x-3">
                          <Button
                            onClick={() => handlePostAction(post.id, 'approve')}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <Check className="w-4 h-4 mr-2" />
                            Approuver
                          </Button>
                          <Button
                            onClick={() => handlePostAction(post.id, 'reject')}
                            variant="destructive"
                          >
                            <X className="w-4 h-4 mr-2" />
                            Rejeter
                          </Button>
                          <Button variant="outline">
                            <Edit className="w-4 h-4 mr-2" />
                            Modifier
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="calendar">
            <Card className="p-8">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">Calendrier de publications</CardTitle>
                <CardDescription>
                  Visualisez vos posts programmés sur le mois
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div>
                    <Calendar
                      mode="single"
                      className="rounded-md border w-full"
                    />
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Posts du mois</h3>
                    {generatedPosts.slice(0, 5).map((post) => (
                      <div key={post.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <Badge variant="outline" className="capitalize">
                          {post.platform}
                        </Badge>
                        <div className="flex-1">
                          <p className="text-sm text-gray-600 truncate">{post.post_text}</p>
                          <p className="text-xs text-gray-400">
                            {new Date(post.scheduled_date).toLocaleDateString('fr-FR')}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
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

export default App;