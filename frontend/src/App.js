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
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { 
  Upload, Calendar as CalendarIcon, Check, X, Edit, Sparkles, Target, TrendingUp, 
  ChevronLeft, ChevronRight, Clock, Send, Image as ImageIcon, FileText, Building
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeStep, setActiveStep] = useState('onboarding');
  const [businessProfile, setBusinessProfile] = useState(null);
  const [generatedPosts, setGeneratedPosts] = useState([]);
  const [pendingContent, setPendingContent] = useState([]);
  const [notes, setNotes] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isGeneratingPosts, setIsGeneratingPosts] = useState(false);
  const [currentPostIndex, setCurrentPostIndex] = useState(0);

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

  // Note form state
  const [noteForm, setNoteForm] = useState({
    title: '',
    content: '',
    priority: 'normal'
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
        loadPendingContent(response.data[0].id);
        loadNotes(response.data[0].id);
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

  const loadPendingContent = async (businessId) => {
    try {
      const response = await axios.get(`${API}/content/${businessId}/pending-description`);
      setPendingContent(response.data);
    } catch (error) {
      console.error('Error loading pending content:', error);
    }
  };

  const loadNotes = async (businessId) => {
    try {
      const response = await axios.get(`${API}/notes/${businessId}`);  
      setNotes(response.data);
    } catch (error) {
      console.error('Error loading notes:', error);
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
      const response = await axios.post(`${API}/business-profile/${businessProfile.id}/logo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setBusinessProfile({...businessProfile, logo_url: response.data.logo_url});
      toast.success('Logo mis à jour !');
    } catch (error) {
      console.error('Error uploading logo:', error);
      toast.error('Erreur lors de l\'upload du logo');
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
      await axios.post(`${API}/upload-content-batch/${businessProfile.id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast.success(`${selectedFiles.length} fichiers uploadés avec succès !`);
      setSelectedFiles([]);
      loadPendingContent(businessProfile.id);
    } catch (error) {
      console.error('Error uploading files:', error);
      toast.error('Erreur lors de l\'upload des fichiers');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAddDescription = async (contentId, description) => {
    try {
      const formData = new FormData();
      formData.append('description', description);
      
      await axios.put(`${API}/content/${contentId}/describe`, formData);
      toast.success('Description ajoutée !');
      loadPendingContent(businessProfile.id);
    } catch (error) {
      console.error('Error adding description:', error);
      toast.error('Erreur lors de l\'ajout de la description');
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/notes/${businessProfile.id}`, noteForm);
      setNoteForm({ title: '', content: '', priority: 'normal' });
      loadNotes(businessProfile.id);
      toast.success('Note ajoutée !');
    } catch (error) {
      console.error('Error adding note:', error);
      toast.error('Erreur lors de l\'ajout de la note');
    }
  };

  const handleGeneratePosts = async () => {
    setIsGeneratingPosts(true);
    try {
      const response = await axios.post(`${API}/generate-posts/${businessProfile.id}`);
      toast.success(`${response.data.total_posts} posts générés avec succès !`);
      loadGeneratedPosts(businessProfile.id);
      loadPendingContent(businessProfile.id);
    } catch (error) {
      console.error('Error generating posts:', error);
      toast.error('Erreur lors de la génération des posts');
    } finally {
      setIsGeneratingPosts(false);
    }
  };

  const handlePostAction = async (postId, action) => {
    try {
      await axios.put(`${API}/post/${postId}/${action}`);
      const actionText = action === 'approve' ? 'approuvé' : 
                        action === 'reject' ? 'rejeté' : 
                        action === 'validate-and-schedule' ? 'validé et programmé' : action;
      toast.success(`Post ${actionText} avec succès !`);
      loadGeneratedPosts(businessProfile.id);
    } catch (error) {
      console.error(`Error ${action} post:`, error);
      toast.error(`Erreur lors de l'${action} du post`);
    }
  };

  const handleScheduleUpdate = async (postId, newDate, newTime) => {
    try {
      await axios.put(`${API}/post/${postId}/schedule`, {
        scheduled_date: newDate,
        scheduled_time: newTime
      });
      toast.success('Programmation mise à jour !');
      loadGeneratedPosts(businessProfile.id);
    } catch (error) {
      console.error('Error updating schedule:', error);
      toast.error('Erreur lors de la mise à jour');
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

  const PostCarousel = ({ posts }) => {
    const currentPost = posts[currentPostIndex];
    const nextPost = posts[currentPostIndex + 1];

    if (!currentPost) return null;

    return (
      <div className="relative bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="flex">
          {/* Current Post */}
          <div className="w-full lg:w-3/4 p-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <Badge variant="outline" className="capitalize font-medium">
                  {currentPost.platform}
                </Badge>
                <Badge 
                  variant={currentPost.status === 'approved' ? 'default' : 
                         currentPost.status === 'rejected' ? 'destructive' : 'secondary'}
                >
                  {currentPost.status === 'pending' ? 'En attente' :
                   currentPost.status === 'approved' ? 'Approuvé' : 
                   currentPost.status === 'scheduled' ? 'Programmé' : 'Rejeté'}
                </Badge>
                {currentPost.auto_generated && (
                  <Badge variant="outline" className="bg-purple-50 text-purple-700">
                    Auto-généré
                  </Badge>
                )}
              </div>
              <div className="text-sm text-gray-500">
                {currentPostIndex + 1} / {posts.length}
              </div>
            </div>

            {/* Post Content */}
            <div className="bg-gray-50 rounded-xl p-6 mb-6">
              <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {currentPost.post_text}
              </p>
            </div>

            {/* Hashtags */}
            {currentPost.hashtags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-6">
                {currentPost.hashtags.map((hashtag, index) => (
                  <Badge key={index} variant="secondary" className="text-blue-600 bg-blue-50">
                    #{hashtag}
                  </Badge>
                ))}
              </div>
            )}

            {/* Scheduling */}
            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <div className="flex items-center space-x-4">
                <Clock className="w-5 h-5 text-blue-600" />
                <div className="flex-1">
                  <Label className="text-sm font-medium text-blue-900">Programmation</Label>
                  <div className="flex items-center space-x-3 mt-1">
                    <Input
                      type="date"
                      value={currentPost.scheduled_date.split('T')[0]}
                      onChange={(e) => handleScheduleUpdate(currentPost.id, e.target.value, currentPost.scheduled_time)}
                      className="w-auto text-sm"
                    />
                    <Input
                      type="time"
                      value={currentPost.scheduled_time}
                      onChange={(e) => handleScheduleUpdate(currentPost.id, currentPost.scheduled_date.split('T')[0], e.target.value)}
                      className="w-auto text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-center">
              <Button
                onClick={() => handlePostAction(currentPost.id, 'validate-and-schedule')}
                disabled={currentPost.status === 'scheduled'}
                className="w-full max-w-md h-12 bg-green-600 hover:bg-green-700 text-white font-semibold"
              >
                <Send className="w-4 h-4 mr-2" />
                {currentPost.status === 'scheduled' ? 'Déjà programmé' : 'Valider et programmer'}
              </Button>
            </div>

            {/* Secondary Actions */}
            {currentPost.status === 'pending' && (
              <div className="flex justify-center space-x-3 mt-4">
                <Button
                  onClick={() => handlePostAction(currentPost.id, 'approve')}
                  variant="outline"
                  className="border-green-600 text-green-600 hover:bg-green-50"
                >
                  <Check className="w-4 h-4 mr-2" />
                  Approuver
                </Button>
                <Button
                  onClick={() => handlePostAction(currentPost.id, 'reject')}
                  variant="outline"
                  className="border-red-600 text-red-600 hover:bg-red-50"
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
          </div>

          {/* Next Post Preview */}
          {nextPost && (
            <div className="w-1/4 bg-gray-50 p-4 border-l">
              <div className="text-xs text-gray-500 mb-2">Suivant</div>
              <Badge variant="outline" className="text-xs mb-2">
                {nextPost.platform}
              </Badge>
              <p className="text-xs text-gray-700 line-clamp-4">
                {nextPost.post_text}
              </p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPostIndex(Math.max(0, currentPostIndex - 1))}
            disabled={currentPostIndex === 0}
            className="rounded-full w-8 h-8 p-0"
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
        </div>
        <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPostIndex(Math.min(posts.length - 1, currentPostIndex + 1))}
            disabled={currentPostIndex === posts.length - 1}
            className="rounded-full w-8 h-8 p-0"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    );
  };

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
                <h1 className="text-2xl font-bold text-gray-900">SocialGénie</h1>
                <p className="text-sm text-gray-600">{businessProfile?.business_name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                {generatedPosts.filter(p => p.status === 'pending').length} posts en attente
              </Badge>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => e.target.files[0] && handleLogoUpload(e.target.files[0])}
                className="hidden"
                id="logo-upload"
              />
              <label htmlFor="logo-upload">
                <Button variant="outline" size="sm" className="cursor-pointer">
                  <ImageIcon className="w-4 h-4 mr-2" />
                  Logo
                </Button>
              </label>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="upload" className="space-y-8">
          <TabsList className="grid w-full grid-cols-4 h-12">
            <TabsTrigger value="upload" className="flex items-center space-x-2">
              <Upload className="w-4 h-4" />
              <span>Upload</span>
            </TabsTrigger>
            <TabsTrigger value="posts" className="flex items-center space-x-2">
              <Target className="w-4 h-4" />
              <span>Posts ({generatedPosts.length})</span>
            </TabsTrigger>
            <TabsTrigger value="notes" className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Notes ({notes.length})</span>
            </TabsTrigger>
            <TabsTrigger value="calendar" className="flex items-center space-x-2">
              <CalendarIcon className="w-4 h-4" />
              <span>Calendrier</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Batch Upload */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Upload className="w-5 h-5" />
                    <span>Upload en lot</span>
                  </CardTitle>
                  <CardDescription>
                    Sélectionnez plusieurs fichiers à la fois
                  </CardDescription>
                </CardHeader>  
                <CardContent className="space-y-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-purple-400 transition-colors">
                    <input
                      type="file"
                      accept="image/*,video/*"
                      multiple
                      onChange={(e) => setSelectedFiles(Array.from(e.target.files))}
                      className="hidden"
                      id="batch-upload"
                    />
                    <label htmlFor="batch-upload" className="cursor-pointer">
                      <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <p className="font-medium text-gray-700">
                        {selectedFiles.length > 0 ? `${selectedFiles.length} fichiers sélectionnés` : 'Cliquez pour sélectionner'}
                      </p>
                      <p className="text-sm text-gray-500">PNG, JPG, MP4</p>
                    </label>
                  </div>

                  <Button 
                    onClick={handleBatchUpload} 
                    disabled={isUploading || selectedFiles.length === 0}
                    className="w-full"
                  >
                    {isUploading ? (
                      <>
                        <TrendingUp className="w-4 h-4 mr-2 animate-spin" />
                        Upload en cours...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Uploader {selectedFiles.length} fichiers
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Pending Descriptions */}
              <Card>
                <CardHeader>
                  <CardTitle>Contenu à décrire ({pendingContent.length})</CardTitle>
                  <CardDescription>
                    Ajoutez des descriptions à vos fichiers uploadés
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {pendingContent.map((content) => (
                      <div key={content.id} className="border rounded-lg p-4">
                        <div className="flex items-start space-x-3">
                          <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden">
                            <img 
                              src={`${BACKEND_URL}${content.file_path}`}
                              alt="Content"
                              className="w-full h-full object-cover"
                            />
                          </div>
                          <div className="flex-1">
                            <Textarea
                              placeholder="Décrivez ce contenu..."
                              className="mb-2"
                              onBlur={(e) => {
                                if (e.target.value.trim()) {
                                  handleAddDescription(content.id, e.target.value);
                                }
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                    {pendingContent.length === 0 && (
                      <p className="text-gray-500 text-center py-8">
                        Aucun contenu en attente de description
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Generate Posts Button */}
            <div className="mt-8 text-center">
              <Button 
                onClick={handleGeneratePosts}
                disabled={isGeneratingPosts}
                size="lg"
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              >
                {isGeneratingPosts ? (
                  <>
                    <TrendingUp className="w-5 h-5 mr-2 animate-spin" />
                    Génération en cours...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Générer les posts IA
                  </>
                )}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="posts">
            {generatedPosts.length === 0 ? (
              <Card className="p-12 text-center">
                <CardContent>
                  <Target className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">Aucun post généré</h3>
                  <p className="text-gray-500">Uploadez du contenu et générez vos posts pour commencer</p>
                </CardContent>
              </Card>
            ) : (
              <PostCarousel posts={generatedPosts} />
            )}
          </TabsContent>

          <TabsContent value="notes">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Add Note */}
              <Card>
                <CardHeader>
                  <CardTitle>Ajouter une note</CardTitle>
                  <CardDescription>
                    Informations importantes à inclure dans les posts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleAddNote} className="space-y-4">
                    <div>
                      <Label htmlFor="note_title">Titre</Label>
                      <Input
                        id="note_title"
                        placeholder="Ex: Fermeture exceptionnelle"
                        value={noteForm.title}
                        onChange={(e) => setNoteForm({...noteForm, title: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="note_content">Contenu</Label>
                      <Textarea
                        id="note_content"
                        placeholder="Ex: Le restaurant sera fermé le 8 mai pour travaux"
                        value={noteForm.content}
                        onChange={(e) => setNoteForm({...noteForm, content: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="note_priority">Priorité</Label>
                      <Select 
                        value={noteForm.priority}
                        onValueChange={(value) => setNoteForm({...noteForm, priority: value})}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="high">Haute</SelectItem>
                          <SelectItem value="normal">Normale</SelectItem>
                          <SelectItem value="low">Faible</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button type="submit" className="w-full">
                      <FileText className="w-4 h-4 mr-2" />
                      Ajouter la note
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Notes List */}
              <Card>
                <CardHeader>
                  <CardTitle>Notes actives ({notes.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {notes.map((note) => (
                      <div key={note.id} className="border rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">{note.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">{note.content}</p>
                          </div>
                          <Badge 
                            variant={note.priority === 'high' ? 'destructive' : 
                                   note.priority === 'normal' ? 'secondary' : 'outline'}
                            className="text-xs"
                          >
                            {note.priority === 'high' ? 'Haute' : 
                             note.priority === 'normal' ? 'Normale' : 'Faible'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                    {notes.length === 0 && (
                      <p className="text-gray-500 text-center py-8">
                        Aucune note active
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
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
                    <h3 className="text-lg font-semibold">Posts programmés</h3>
                    {generatedPosts.filter(p => p.status === 'scheduled').slice(0, 5).map((post) => (
                      <div key={post.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <Badge variant="outline" className="capitalize">
                          {post.platform}
                        </Badge>
                        <div className="flex-1">
                          <p className="text-sm text-gray-600 truncate">{post.post_text}</p>
                          <p className="text-xs text-gray-400">
                            {new Date(post.scheduled_date).toLocaleDateString('fr-FR')} à {post.scheduled_time}
                          </p>
                        </div>
                      </div>
                    ))}
                    {generatedPosts.filter(p => p.status === 'scheduled').length === 0 && (
                      <p className="text-gray-500 text-center py-8">
                        Aucun post programmé
                      </p>
                    )}
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