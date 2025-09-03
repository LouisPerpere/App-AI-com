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
import { Building, Sparkles, Crown, Upload, FileText, X, Edit, CalendarIcon, Target, LogOut, Check, Send, Clock, ChevronLeft, ChevronRight, CreditCard, Settings, Globe, Save, Search, Users, Cog, Trash, RefreshCw, Calendar, Image as ImageIcon, Info } from 'lucide-react';

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

  // Debug pour voir les URLs des vignettes
  console.log('🖼️ Content thumbnail:', {
    id: content.id,
    filename: content.filename,
    file_type: content.file_type,
    thumb_url: content.thumb_url,
    url: content.url,
    full_content: content
  });

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
            src={content.thumb_url || content.url}
            alt={content.filename}
            className="w-full h-full object-cover"
            loading="lazy"
            onError={(e) => {
              console.log('❌ Image failed to load:', content.thumb_url || content.url);
              // Fallback hierarchy: thumb_url -> url -> placeholder
              if (content.url && e.currentTarget.src !== content.url) {
                e.currentTarget.src = content.url;
              } else {
                // Show error placeholder
                e.currentTarget.style.display = 'none';
                const placeholder = e.currentTarget.parentElement.querySelector('.error-placeholder');
                if (placeholder) placeholder.style.display = 'flex';
              }
            }}
            onLoad={() => {
              console.log('✅ Image loaded successfully:', content.thumb_url || content.url);
            }}
          />
        ) : content.file_type?.startsWith('video/') ? (
          <div className="relative w-full h-full">
            {content.thumb_url ? (
              <img 
                src={content.thumb_url}
                alt={content.filename}
                className="w-full h-full object-cover"
                loading="lazy"
                onError={(e) => {
                  // Fallback to video icon if thumbnail fails
                  e.currentTarget.style.display = 'none';
                  e.currentTarget.parentElement.querySelector('.video-icon').style.display = 'flex';
                }}
              />
            ) : (
              <div className="video-icon w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-indigo-100">
                <div className="text-center">
                  <FileText className="w-8 h-8 text-blue-600 mx-auto mb-1" />
                  <span className="text-xs text-blue-800">VIDEO</span>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100">
            <FileText className="w-6 h-6 text-purple-600" />
          </div>
        )}
        
        {/* Error placeholder (hidden by default) */}
        <div className="error-placeholder w-full h-full items-center justify-center bg-gradient-to-br from-red-100 to-pink-100" style={{ display: 'none' }}>
          <div className="text-center">
            <X className="w-8 h-8 text-red-600 mx-auto mb-1" />
            <span className="text-xs text-red-800">ERREUR</span>
          </div>
        </div>
        
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

function MainApp() {
  const location = useLocation();
  
  // State management
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeStep, setActiveStep] = useState('onboarding');
  const [businessProfile, setBusinessProfile] = useState(null);
  const [activeTab, setActiveTab] = useState('entreprise');
  const [pendingContent, setPendingContent] = useState([]);
  const [notes, setNotes] = useState([]);
  const [showPaymentPage, setShowPaymentPage] = useState(false);
  
  // Form states
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSavingBusinessInfo, setIsSavingBusinessInfo] = useState(false);
  const [isSavingMarketingInfo, setIsSavingMarketingInfo] = useState(false);
  
  // Note form states - using refs to prevent re-renders that close virtual keyboard
  const [isSavingNote, setIsSavingNote] = useState(false);
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [isDeletingNote, setIsDeletingNote] = useState(null);
  
  // Content library states
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [selectedContentIds, setSelectedContentIds] = useState(new Set());
  const [isDeletingContent, setIsDeletingContent] = useState(false);
  const [previewContent, setPreviewContent] = useState(null);
  const [isSavingContext, setIsSavingContext] = useState(false);
  
  // Posts generation states
  const [showGenerationModal, setShowGenerationModal] = useState(false);
  const [isGeneratingPosts, setIsGeneratingPosts] = useState(false);
  const [generatedPosts, setGeneratedPosts] = useState([]);
  
  // Pixabay integration states
  const [activeLibraryTab, setActiveLibraryTab] = useState('my-library'); // 'my-library' or 'pixabay-search'
  const [pixabayResults, setPixabayResults] = useState([]);
  const [pixabayCategories, setPixabayCategories] = useState([]);
  const [isSearchingPixabay, setIsSearchingPixabay] = useState(false);
  const [isSavingPixabayImage, setIsSavingPixabayImage] = useState(null);
  
  // Refs for direct DOM manipulation to avoid re-renders
  const titleInputRef = useRef(null);
  const contentInputRef = useRef(null);
  const priorityInputRef = useRef(null);
  const contextTextareaRef = useRef(null); // Ref pour éviter bug clavier virtuel
  const pixabaySearchRef = useRef(null); // Ref pour recherche Pixabay
  
  // Website analysis states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [websiteAnalysis, setWebsiteAnalysis] = useState(null);
  const [lastAnalysisInfo, setLastAnalysisInfo] = useState(null);
  const [persistedUrl, setPersistedUrl] = useState('');
  
  // Field editing states (verrouillage/déverrouillage)
  const [editingFields, setEditingFields] = useState({});
  const [fieldValues, setFieldValues] = useState({});

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

  // Initialize priority select to default value
  useEffect(() => {
    if (priorityInputRef.current && !editingNoteId) {
      priorityInputRef.current.value = 'normal';
    }
  }, [editingNoteId]);
  // S'assurer que l'URL est bien pré-remplie quand l'analyse existe ou qu'on change d'onglet
  useEffect(() => {
    const urlToUse = websiteAnalysis?.website_url || persistedUrl;
    if (urlToUse) {
      setTimeout(() => {
        const urlInput = document.getElementById('website_analysis_url_native');
        if (urlInput && !urlInput.value) {
          urlInput.value = urlToUse;
          console.log(`✅ URL restaurée: ${urlToUse}`);
        }
      }, 200);
    }
  }, [websiteAnalysis, persistedUrl, activeTab]); // Ajouter activeTab pour déclencher quand on change d'onglet

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      setIsAuthenticated(false);
      return;
    }

    // Set axios header before making request
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

    try {
      const response = await axios.get(`${API}/auth/me`, {
        timeout: 15000,
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setUser(response.data);
      setIsAuthenticated(true);
      setActiveStep('dashboard');
      
      // Load business profile, notes, content and posts
      loadBusinessProfile();
      loadNotes();
      loadPendingContent();
      loadGeneratedPosts();
      loadPixabayCategories();
      
    } catch (error) {
      console.error('Auth check failed:', error);
      
      // Only remove token if it's actually invalid
      if (error.response?.status === 401 || error.response?.status === 403) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
      }
      
      setIsAuthenticated(false);
    }
  };

  const handleAuthSuccess = async () => {
    setActiveStep('dashboard');
    await checkAuth();
  };

  const loadBusinessProfile = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    try {
      const response = await axios.get(`${API}/business-profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBusinessProfile(response.data);
      
      // Charger aussi l'analyse de site web existante
      await loadExistingAnalysis();
      
      setActiveStep('dashboard');
    } catch (error) {
      console.log('Business profile fetch error:', error.response?.status);
      
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        setIsAuthenticated(false);
        setUser(null);
        setActiveStep('login');
      } else if (error.response?.status === 404) {
        setActiveStep('dashboard');
      } else {
        setActiveStep('dashboard');
      }
    }
  };

  const loadPendingContent = async () => {
    try {
      const response = await axios.get(`${API}/content/pending`, {
        params: { limit: 24 },
        headers: { 
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        }
      });
      
      const data = response.data;
      setPendingContent(data.content || []);
      
    } catch (error) {
      console.error('Error loading pending content:', error);
    }
  };

  const loadNotes = async () => {
    try {
      const response = await axios.get(`${API}/notes`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });  
      
      const notesData = response.data.notes || response.data || [];
      setNotes(notesData);
    } catch (error) {
      console.error('Error loading notes:', error);
      setNotes([]);
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

  const handleSaveBusinessInfo = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    setIsSavingBusinessInfo(true);
    
    try {
      // Récupérer les valeurs des champs
      const businessName = document.getElementById('business_name_edit')?.value;
      const businessType = document.getElementById('business_type_edit')?.value;
      const businessDescription = document.getElementById('business_description_edit')?.value;
      const brandTone = document.getElementById('brand_tone_edit')?.value;
      
      // Récupérer la valeur du rythme de publications (select)
      const postingFrequency = document.getElementById('posting_frequency_edit')?.value;

      const updateData = {
        business_name: businessName,
        business_type: businessType,
        business_description: businessDescription,
        brand_tone: brandTone,
        posting_frequency: postingFrequency
      };

      const response = await axios.put(`${API}/business-profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        toast.success('Informations sauvegardées avec succès !');
        // Recharger le profil pour mettre à jour l'affichage
        await loadBusinessProfile();
      } else {
        toast.error('Erreur lors de la sauvegarde');
      }
    } catch (error) {
      console.error('Save business info error:', error);
      toast.error('Erreur lors de la sauvegarde des informations');
    } finally {
      setIsSavingBusinessInfo(false);
    }
  };

  const handleSaveMarketingInfo = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    setIsSavingMarketingInfo(true);
    
    try {
      // Récupérer les valeurs des champs marketing
      const email = document.getElementById('business_email_edit')?.value;
      const websiteUrl = document.getElementById('business_website_edit')?.value;
      const targetAudience = document.getElementById('target_audience_edit')?.value;

      const updateData = {
        email: email,
        website_url: websiteUrl,
        target_audience: targetAudience
      };

      const response = await axios.put(`${API}/business-profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        toast.success('Informations marketing sauvegardées avec succès !');
        // Recharger le profil pour mettre à jour l'affichage
        await loadBusinessProfile();
      } else {
        toast.error('Erreur lors de la sauvegarde');
      }
    } catch (error) {
      console.error('Save marketing info error:', error);
      toast.error('Erreur lors de la sauvegarde des informations marketing');
    } finally {
      setIsSavingMarketingInfo(false);
    }
  };

  // Auto-sauvegarde silencieuse (sans toast de confirmation)
  const handleAutoSave = async (fieldType = 'business') => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      let updateData = {};
      
      if (fieldType === 'business') {
        // Récupérer tous les champs business
        const businessName = document.getElementById('business_name_edit')?.value;
        const businessType = document.getElementById('business_type_edit')?.value;
        const businessDescription = document.getElementById('business_description_edit')?.value;
        const brandTone = document.getElementById('brand_tone_edit')?.value;
        const postingFrequency = document.getElementById('posting_frequency_edit')?.value;
        
        updateData = {
          business_name: businessName,
          business_type: businessType,
          business_description: businessDescription,
          brand_tone: brandTone,
          posting_frequency: postingFrequency
        };
      } else if (fieldType === 'marketing') {
        // Récupérer tous les champs marketing
        const email = document.getElementById('business_email_edit')?.value;
        const websiteUrl = document.getElementById('business_website_edit')?.value;
        const targetAudience = document.getElementById('target_audience_edit')?.value;
        const coordinates = document.getElementById('business_coordinates_edit')?.value;
        
        updateData = {
          email: email,
          website_url: websiteUrl,
          target_audience: targetAudience,
          coordinates: coordinates
        };
      }

      await axios.put(`${API}/business-profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Auto-sauvegarde silencieuse - pas de toast de confirmation
      console.log('Auto-sauvegarde réussie:', fieldType);
      
    } catch (error) {
      console.error('Auto-save error:', error);
      // En cas d'erreur, on peut afficher un toast discret
      toast.error('Erreur auto-sauvegarde');
    }
  };

  // Modified handlers to prevent re-renders - using direct DOM access
  const handleNoteTitleChange = useCallback((e) => {
    // Don't use setState to avoid re-renders that close keyboard
    // Value will be read directly from DOM when needed
  }, []);

  const handleNoteContentChange = useCallback((e) => {
    // Don't use setState to avoid re-renders that close keyboard
    // Value will be read directly from DOM when needed
  }, []);

  const handleNotePriorityChange = useCallback((e) => {
    // Pas de setState pour éviter re-render qui vide les autres champs
    // La valeur sera lue directement du DOM
  }, []);

  // Get current form values from DOM
  const getCurrentFormValues = useCallback(() => {
    return {
      title: titleInputRef.current?.value || '',
      content: contentInputRef.current?.value || '',
      priority: priorityInputRef.current?.value || 'normal'
    };
  }, []);

  // Set form values in DOM
  const setFormValues = useCallback((title = '', content = '', priority = 'normal') => {
    if (titleInputRef.current) titleInputRef.current.value = title;
    if (contentInputRef.current) contentInputRef.current.value = content;
    if (priorityInputRef.current) {
      priorityInputRef.current.value = priority;
    }
  }, []);

  // Sauvegarder une note
  const handleSaveNote = async () => {
    // Get values directly from DOM to avoid state issues
    const formValues = getCurrentFormValues();
    
    // Validation des champs
    if (!formValues.title.trim()) {
      toast.error('Veuillez saisir un titre pour la note');
      titleInputRef.current?.focus();
      return;
    }
    
    if (!formValues.content.trim()) {
      toast.error('Veuillez saisir le contenu de la note');
      contentInputRef.current?.focus();
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté pour sauvegarder une note');
      return;
    }

    setIsSavingNote(true);
    
    try {
      if (editingNoteId) {
        // Mode édition - PUT
        const response = await axios.put(`${API}/notes/${editingNoteId}`, {
          title: formValues.title.trim(),
          content: formValues.content.trim(),
          priority: formValues.priority
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data) {
          toast.success('Note modifiée avec succès ! ✏️');
          
          // Réinitialiser le formulaire
          setFormValues('', '', 'normal');
          setEditingNoteId(null);
          
          // Recharger les notes
          await loadNotes();
        }
      } else {
        // Mode création - POST
        const response = await axios.post(`${API}/notes`, {
          title: formValues.title.trim(),
          content: formValues.content.trim(),
          priority: formValues.priority
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data) {
          toast.success('Note sauvegardée avec succès ! 📝');
          
          // Réinitialiser le formulaire
          setFormValues('', '', 'normal');
          setEditingNoteId(null);
          
          // Recharger les notes
          await loadNotes();
        }
      }
      
    } catch (error) {
      console.error('Error saving note:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la sauvegarde: ${errorMessage}`);
    } finally {
      setIsSavingNote(false);
    }
  };

  // Éditer une note existante
  const handleEditNote = useCallback((note) => {
    setFormValues(
      note.description || note.title || '', 
      note.content || '', 
      note.priority || 'normal'
    );
    setEditingNoteId(note.note_id);
    
    // Scroll vers le formulaire
    setTimeout(() => {
      titleInputRef.current?.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
      titleInputRef.current?.focus();
    }, 100);
  }, [setFormValues]);

  // Annuler l'édition
  const handleCancelEdit = useCallback(() => {
    setFormValues('', '', 'normal');
    setEditingNoteId(null);
  }, [setFormValues]);

  // Supprimer une note
  const handleDeleteNote = async (noteId) => {
    if (!noteId) {
      toast.error('ID de note manquant');
      return;
    }
    
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) {
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté pour supprimer une note');
      return;
    }

    setIsDeletingNote(noteId);
    
    try {
      await axios.delete(`${API}/notes/${noteId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Note supprimée avec succès ! 🗑️');
      
      // Recharger les notes
      await loadNotes();
      
    } catch (error) {
      console.error('Error deleting note:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la suppression: ${errorMessage}`);
    } finally {
      setIsDeletingNote(null);
    }
  };

  // Fonctions pour la bibliothèque de contenus
  
  // Basculer le mode sélection
  const toggleSelectionMode = useCallback(() => {
    setIsSelectionMode(!isSelectionMode);
    setSelectedContentIds(new Set()); // Reset selections
  }, [isSelectionMode]);

  // Gérer la sélection d'un contenu
  const handleToggleSelection = useCallback((contentId) => {
    setSelectedContentIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(contentId)) {
        newSet.delete(contentId);
      } else {
        newSet.add(contentId);
      }
      return newSet;
    });
  }, []);

  // Sélectionner tout / Désélectionner tout
  const handleSelectAll = useCallback(() => {
    if (selectedContentIds.size === pendingContent.length) {
      // Tout désélectionner
      setSelectedContentIds(new Set());
    } else {
      // Tout sélectionner
      setSelectedContentIds(new Set(pendingContent.map(content => content.id)));
    }
  }, [selectedContentIds.size, pendingContent]);

  // Supprimer les contenus sélectionnés
  const handleDeleteSelected = async () => {
    if (selectedContentIds.size === 0) {
      toast.error('Aucun contenu sélectionné');
      return;
    }

    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer ${selectedContentIds.size} contenu(s) ?`)) {
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté');
      return;
    }

    setIsDeletingContent(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      // Supprimer chaque contenu sélectionné
      for (const contentId of selectedContentIds) {
        try {
          await axios.delete(`${API}/content/${contentId}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          successCount++;
        } catch (error) {
          console.error(`Error deleting content ${contentId}:`, error);
          errorCount++;
        }
      }

      // Messages de retour
      if (successCount > 0) {
        toast.success(`${successCount} contenu(s) supprimé(s) avec succès ! 🗑️`);
      }
      if (errorCount > 0) {
        toast.error(`Erreur lors de la suppression de ${errorCount} contenu(s)`);
      }

      // Reset et rechargement
      setSelectedContentIds(new Set());
      setIsSelectionMode(false);
      await loadPendingContent();

    } catch (error) {
      console.error('Error in batch delete:', error);
      toast.error('Erreur lors de la suppression en masse');
    } finally {
      setIsDeletingContent(false);
    }
  };

  // Ouvrir l'aperçu d'un contenu
  const handleContentClick = useCallback((content) => {
    if (isSelectionMode) {
      handleToggleSelection(content.id);
    } else {
      setPreviewContent(content);
      // Charger le contexte existant directement dans la textarea après un court délai
      setTimeout(() => {
        if (contextTextareaRef.current) {
          contextTextareaRef.current.value = content.context || '';
        }
      }, 100);
    }
  }, [isSelectionMode, handleToggleSelection]);

  // Fermer l'aperçu
  const handleClosePreview = useCallback(() => {
    setPreviewContent(null);
    // Vider la textarea
    if (contextTextareaRef.current) {
      contextTextareaRef.current.value = '';
    }
  }, []);

  // Sauvegarder le contexte d'un contenu
  const handleSaveContext = async () => {
    if (!previewContent) return;

    // Lire la valeur directement du DOM
    const contextValue = contextTextareaRef.current?.value || '';

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté');
      return;
    }

    setIsSavingContext(true);

    try {
      await axios.put(`${API}/content/${previewContent.id}/context`, {
        context: contextValue.trim()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Contexte sauvegardé ! 💾');
      
      // Mettre à jour le contenu local avec le nouveau contexte
      const updatedContent = { ...previewContent, context: contextValue.trim() };
      setPreviewContent(updatedContent);
      
      // Remettre le texte dans la textarea après sauvegarde pour qu'il reste visible
      if (contextTextareaRef.current) {
        contextTextareaRef.current.value = contextValue.trim();
      }
      
      // Recharger la liste pour persister les changements
      await loadPendingContent();
      
      // Fermer automatiquement la modal après 1 seconde
      setTimeout(() => {
        handleClosePreview();
      }, 1000);

    } catch (error) {
      console.error('Error saving context:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la sauvegarde: ${errorMessage}`);
    } finally {
      setIsSavingContext(false);
    }
  };

  // Fonctions pour la génération de posts
  
  // Ouvrir la modal de génération
  const handleOpenGenerationModal = useCallback(() => {
    setShowGenerationModal(true);
  }, []);

  // Fermer la modal de génération
  const handleCloseGenerationModal = useCallback(() => {
    setShowGenerationModal(false);
  }, []);

  // Lancer la génération manuelle des posts
  const handleGeneratePosts = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté pour générer des posts');
      return;
    }

    setIsGeneratingPosts(true);
    setShowGenerationModal(false);

    try {
      const response = await axios.post(`${API}/posts/generate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Posts générés avec succès ! 🎉');
      
      // Recharger les posts générés
      await loadGeneratedPosts();

    } catch (error) {
      console.error('Error generating posts:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la génération: ${errorMessage}`);
    } finally {
      setIsGeneratingPosts(false);
    }
  };

  // Charger les posts générés
  const loadGeneratedPosts = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await axios.get(`${API}/posts/generated`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data && response.data.posts) {
        setGeneratedPosts(response.data.posts);
      }
    } catch (error) {
      console.error('Error loading generated posts:', error);
    }
  };

  // Fonctions Pixabay
  
  // Charger les catégories Pixabay
  const loadPixabayCategories = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await axios.get(`${API}/pixabay/categories`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data && response.data.categories) {
        setPixabayCategories(response.data.categories);
      }
    } catch (error) {
      console.error('Error loading Pixabay categories:', error);
    }
  };

  // Rechercher des images sur Pixabay
  const searchPixabayImages = async () => {
    if (!pixabayQuery.trim()) {
      toast.error('Veuillez saisir un terme de recherche');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté');
      return;
    }

    setIsSearchingPixabay(true);

    try {
      const response = await axios.get(`${API}/pixabay/search`, {
        params: {
          query: pixabayQuery.trim(),
          per_page: 20,
          image_type: 'photo',
          safesearch: true
        },
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data && response.data.hits) {
        setPixabayResults(response.data.hits);
        toast.success(`${response.data.hits.length} images trouvées ! 🖼️`);
      } else {
        setPixabayResults([]);
        toast.info('Aucune image trouvée pour cette recherche');
      }

    } catch (error) {
      console.error('Error searching Pixabay:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la recherche: ${errorMessage}`);
      setPixabayResults([]);
    } finally {
      setIsSearchingPixabay(false);
    }
  };

  // Sauvegarder une image Pixabay dans la bibliothèque
  const savePixabayImage = async (pixabayImage) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté');
      return;
    }

    setIsSavingPixabayImage(pixabayImage.id);

    try {
      await axios.post(`${API}/pixabay/save-image`, {
        pixabay_id: pixabayImage.id,
        image_url: pixabayImage.webformatURL,
        tags: pixabayImage.tags
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Image ajoutée à votre bibliothèque ! 📚');
      
      // Recharger le contenu pour voir la nouvelle image
      await loadPendingContent();

    } catch (error) {
      console.error('Error saving Pixabay image:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la sauvegarde: ${errorMessage}`);
    } finally {
      setIsSavingPixabayImage(null);
    }
  };

  // Analyse de site web
  const handleAnalyzeWebsite = async () => {
    const websiteUrl = document.getElementById('website_analysis_url_native')?.value;
    
    if (!websiteUrl || !websiteUrl.trim()) {
      toast.error('Veuillez saisir une URL de site web');
      return;
    }

    // Validation basique de l'URL
    try {
      new URL(websiteUrl);
    } catch {
      toast.error('Veuillez saisir une URL valide (ex: https://exemple.com)');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté pour analyser un site web');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const response = await axios.post(`${API}/website/analyze`, {
        website_url: websiteUrl.trim()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setWebsiteAnalysis(response.data);
      setLastAnalysisInfo({
        lastAnalyzed: response.data.created_at,
        nextAnalysisDue: response.data.next_analysis_due
      });
      
      // Persister l'URL et s'assurer qu'elle reste dans le champ
      const trimmedUrl = websiteUrl.trim();
      setPersistedUrl(trimmedUrl);
      setTimeout(() => {
        const urlInput = document.getElementById('website_analysis_url_native');
        if (urlInput) {
          urlInput.value = trimmedUrl;
        }
      }, 100);
      
      toast.success(`Analyse terminée ! ${response.data.pages_count || 1} page(s) analysée(s)`);
      
    } catch (error) {
      console.error('Website analysis error:', error);
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Erreur lors de l\'analyse du site web';
      toast.error(errorMessage);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Charger l'analyse de site web existante
  const loadExistingAnalysis = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await axios.get(`${API}/website/analysis`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data && response.data.analysis) {
        const analysis = response.data.analysis;
        setWebsiteAnalysis(analysis);
        setLastAnalysisInfo({
          lastAnalyzed: analysis.created_at || analysis.last_analyzed,
          nextAnalysisDue: analysis.next_analysis_due
        });
        
        // Persister l'URL et pré-remplir le champ
        if (analysis.website_url) {
          setPersistedUrl(analysis.website_url);
          setTimeout(() => {
            const urlInput = document.getElementById('website_analysis_url_native');
            if (urlInput) {
              urlInput.value = analysis.website_url;
              console.log(`✅ URL pré-remplie: ${analysis.website_url}`);
            }
          }, 100);
        }
      }
    } catch (error) {
      console.error('Error loading existing analysis:', error);
    }
  };

  // Fonction pour déterminer si une nouvelle analyse est nécessaire
  const needsNewAnalysis = () => {
    if (!lastAnalysisInfo?.nextAnalysisDue) return true;
    const nextDue = new Date(lastAnalysisInfo.nextAnalysisDue);
    const now = new Date();
    return now > nextDue;
  };

  // Fonctions pour le système d'édition verrouillé/déverrouillé
  const startEditing = (fieldName) => {
    // Récupérer la valeur actuelle visible dans l'interface
    const element = document.getElementById(fieldName);
    let currentValue = '';
    
    if (element) {
      currentValue = element.value || element.textContent || '';
    } else {
      // Fallback: chercher dans le profil business
      const fieldMapping = {
        'business_name_edit': businessProfile?.business_name || '',
        'business_type_edit': businessProfile?.business_type || '',
        'business_description_edit': businessProfile?.business_description || '',
        'brand_tone_edit': businessProfile?.brand_tone || 'professionnel',
        'posting_frequency_edit': businessProfile?.posting_frequency || 'weekly',
        'business_email_edit': businessProfile?.email || '',
        'business_website_edit': businessProfile?.website_url || '',
        'target_audience_edit': businessProfile?.target_audience || '',
        'business_coordinates_edit': businessProfile?.coordinates || ''
      };
      currentValue = fieldMapping[fieldName] || '';
    }
    
    setFieldValues(prev => ({ ...prev, [fieldName]: currentValue }));
    setEditingFields(prev => ({ ...prev, [fieldName]: true }));
  };

  const cancelEditing = (fieldName) => {
    setEditingFields(prev => ({ ...prev, [fieldName]: false }));
    // Restaurer la valeur originale
    const originalValue = fieldValues[fieldName] || '';
    const element = document.getElementById(fieldName);
    if (element) {
      element.value = originalValue;
    }
  };

  const confirmEditing = async (fieldName, fieldType = 'business') => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      let updateData = {};
      const newValue = document.getElementById(fieldName)?.value || '';
      
      // Mappage des noms de champs vers les clés API
      const fieldMapping = {
        'business_name_edit': 'business_name',
        'business_type_edit': 'business_type', 
        'business_description_edit': 'business_description',
        'brand_tone_edit': 'brand_tone',
        'posting_frequency_edit': 'posting_frequency',
        'business_email_edit': 'email',
        'business_website_edit': 'website_url',
        'target_audience_edit': 'target_audience',
        'business_coordinates_edit': 'coordinates'
      };

      const apiField = fieldMapping[fieldName] || fieldName;
      updateData[apiField] = newValue;

      await axios.put(`${API}/business-profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setEditingFields(prev => ({ ...prev, [fieldName]: false }));
      setFieldValues(prev => ({ ...prev, [fieldName]: newValue }));
      
      toast.success('✅ Champ sauvegardé !');
      
    } catch (error) {
      console.error('Save field error:', error);
      toast.error('Erreur lors de la sauvegarde');
    }
  };

  // Composant EditableField pour les champs verrouillés/déverrouillés
  const EditableField = ({ 
    fieldId, 
    label, 
    type = 'text', 
    placeholder = '', 
    defaultValue = '', 
    isTextarea = false,
    isSelect = false,
    options = [],
    fieldType = 'business' 
  }) => {
    const isEditing = editingFields[fieldId];
    // Utiliser la valeur courante du DOM ou la valeur par défaut
    const getCurrentValue = () => {
      const element = document.getElementById(fieldId);
      if (element) {
        return element.value || element.textContent || defaultValue;
      }
      return fieldValues[fieldId] !== undefined ? fieldValues[fieldId] : defaultValue;
    };
    const displayValue = getCurrentValue();

    if (isEditing) {
      return (
        <div className="space-y-2">
          <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700">
            {label}
          </label>
          <div className="flex items-start gap-3">
            <div className="flex-1 min-w-0">
              {isSelect ? (
                <select
                  id={fieldId}
                  defaultValue={displayValue}
                  className="w-full p-2 border-2 border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  style={{
                    fontSize: '16px',
                    lineHeight: '1.5',
                    WebkitAppearance: 'none',
                    touchAction: 'manipulation'
                  }}
                >
                  {options.map((option, index) => (
                    <option key={index} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : isTextarea ? (
                <textarea
                  id={fieldId}
                  defaultValue={displayValue}
                  placeholder={placeholder}
                  className="w-full p-2 border-2 border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
                  style={{
                    fontSize: '16px',
                    lineHeight: '1.5',
                    WebkitAppearance: 'none',
                    touchAction: 'manipulation',
                    minHeight: '100px'
                  }}
                  rows={4}
                />
              ) : (
                <input
                  id={fieldId}
                  type={type}
                  defaultValue={displayValue}
                  placeholder={placeholder}
                  className="w-full p-2 border-2 border-blue-500 rounded-lg bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  style={{
                    fontSize: '16px',
                    lineHeight: '1.5',
                    WebkitAppearance: 'none',
                    touchAction: 'manipulation'
                  }}
                />
              )}
            </div>
            
            {/* Boutons confirmer/annuler à droite */}
            <div className="flex flex-col gap-1.5 flex-shrink-0">
              <button
                onClick={() => confirmEditing(fieldId, fieldType)}
                className="group w-8 h-8 bg-gradient-to-br from-emerald-500 via-green-500 to-teal-500 hover:from-emerald-600 hover:via-green-600 hover:to-teal-600 text-white rounded-xl flex items-center justify-center transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-emerald-500/50 transform hover:scale-110 hover:rotate-12 relative overflow-hidden"
                title="Confirmer"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <Check className="w-4 h-4 relative z-10 transition-all duration-300 group-hover:scale-110" />
                <div className="absolute inset-0 rounded-xl bg-emerald-400/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
              <button
                onClick={() => cancelEditing(fieldId)}
                className="group w-8 h-8 bg-gradient-to-br from-red-500 via-pink-500 to-rose-500 hover:from-red-600 hover:via-pink-600 hover:to-rose-600 text-white rounded-xl flex items-center justify-center transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-red-500/50 transform hover:scale-110 hover:-rotate-12 relative overflow-hidden"
                title="Annuler"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <X className="w-4 h-4 relative z-10 transition-all duration-300 group-hover:scale-110" />
                <div className="absolute inset-0 rounded-xl bg-red-400/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
            </div>
          </div>
        </div>
      );
    }

    // Mode verrouillé (lecture seule)
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
        <div className="flex items-center gap-3">
          <div className="flex-1 min-w-0">
            <div className="w-full p-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-700 min-h-[40px] flex items-center text-sm">
              {(() => {
                if (!displayValue) {
                  return <span className="text-gray-400 italic text-xs">{placeholder || 'Non renseigné'}</span>;
                }
                
                // Si c'est un select, trouver le libellé correspondant à la valeur
                if (isSelect && options.length > 0) {
                  const matchingOption = options.find(option => option.value === displayValue);
                  return matchingOption ? matchingOption.label : displayValue;
                }
                
                // Sinon, afficher la valeur directement
                return displayValue;
              })()}
            </div>
          </div>
          
          {/* Bouton stylo ultra-moderne à droite du champ */}
          <button
            onClick={() => startEditing(fieldId)}
            className="group flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white rounded-xl flex items-center justify-center transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-purple-500/50 transform hover:scale-110 hover:rotate-12 relative overflow-hidden"
            title="Modifier"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <Edit className="w-4 h-4 relative z-10 transition-all duration-300 group-hover:scale-110" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full opacity-75 group-hover:opacity-100 transition-opacity duration-300"></div>
          </button>
        </div>
      </div>
    );
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
      loadPendingContent();
    } catch (error) {
      toast.error('Erreur lors de l\'upload');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

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

  const Dashboard = () => (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-cyan-50 to-emerald-50 relative overflow-hidden">
        {/* Fond animé moderne */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-br from-emerald-400/10 to-teal-400/10 rounded-full blur-2xl animate-pulse" style={{animationDelay: '4s'}}></div>
        </div>
      {/* Header moderne avec glassmorphism */}
      <div className="relative z-10 backdrop-blur-xl bg-white/80 border-0 border-b border-white/20 shadow-lg shadow-purple-500/10">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 py-2">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center space-x-3 min-w-0 flex-1">
              <div className="relative">
                <Avatar className="w-12 h-12 sm:w-14 sm:h-14 ring-4 ring-gradient-to-r ring-purple-400/30 flex-shrink-0 shadow-lg shadow-purple-500/25 transition-all duration-300 hover:scale-105">
                  <AvatarImage src={businessProfile?.logo_url ? `${BACKEND_URL}${businessProfile.logo_url}` : ""} />
                  <AvatarFallback className="bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 text-white text-base sm:text-lg font-bold">
                    <div className="logo-cm text-white transform transition-transform duration-300 hover:rotate-12">
                      <span className="logo-c">C</span>
                      <span className="logo-m">M</span>
                    </div>
                  </AvatarFallback>
                </Avatar>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full animate-ping"></div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full"></div>
              </div>
              <div className="min-w-0 flex-1">
                <h1 className="text-lg sm:text-2xl font-extrabold bg-gradient-to-r from-slate-800 via-purple-700 to-pink-600 bg-clip-text text-transparent drop-shadow-sm">
                  Claire et Marcus
                </h1>
                <p className="text-xs sm:text-sm text-slate-800 font-semibold truncate -mt-1">
                  {businessProfile?.business_name || 'Mon entreprise'}
                </p>
                <div className="text-xs -mt-1">
                  <p className="text-purple-600 font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    Claire rédige, Marcus programme.
                  </p>
                  <p className="text-purple-600 font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent transform transition-all duration-300 hover:scale-105 -mt-1" 
                     style={{
                       animation: 'breathe 3s ease-in-out infinite'
                     }}>
                    Vous respirez.
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center flex-shrink-0">
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="group relative overflow-hidden text-slate-600 hover:text-white p-2 rounded-full transition-all duration-300 hover:shadow-lg hover:shadow-red-500/25 hover:scale-110"
                title="Déconnexion"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-red-500 to-pink-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full"></div>
                <LogOut className="w-4 h-4 relative z-10 transition-transform duration-300 group-hover:rotate-12" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-2 sm:px-3 py-2">
        <Tabs 
          value={activeTab} 
          onValueChange={setActiveTab} 
          className="space-y-8"
        >
          <div className="overflow-x-auto">
            <TabsList className="w-full bg-white/70 backdrop-blur-xl p-3 rounded-2xl border-0 shadow-xl shadow-purple-500/10 min-h-[80px]">
              <div className="grid grid-cols-4 lg:grid-cols-8 gap-2 h-full">
              <TabsTrigger value="entreprise" className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:scale-105 data-[state=active]:scale-105 data-[state=active]:shadow-lg data-[state=active]:shadow-blue-500/25 bg-gradient-to-br from-blue-50 to-purple-50 data-[state=active]:from-blue-500 data-[state=active]:to-purple-500 border-0 px-3 py-3">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 opacity-0 group-data-[state=active]:opacity-100 transition-opacity duration-300 rounded-lg"></div>
                <div className="relative z-10 flex items-center justify-center text-slate-700 group-data-[state=active]:text-white transition-colors duration-300">
                  <span className="font-bold text-xs">Entreprise</span>
                </div>
              </TabsTrigger>
              <TabsTrigger value="analyse" className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:scale-105 data-[state=active]:scale-105 data-[state=active]:shadow-lg data-[state=active]:shadow-purple-500/25 bg-gradient-to-br from-purple-50 to-pink-50 data-[state=active]:from-purple-500 data-[state=active]:to-pink-500 border-0 px-3 py-3">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-0 group-data-[state=active]:opacity-100 transition-opacity duration-300 rounded-lg"></div>
                <div className="relative z-10 flex items-center justify-center text-slate-700 group-data-[state=active]:text-white transition-colors duration-300">
                  <span className="font-bold text-xs">Analyse</span>
                </div>
              </TabsTrigger>
                <TabsTrigger value="bibliotheque" className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:scale-105 data-[state=active]:scale-105 data-[state=active]:shadow-lg data-[state=active]:shadow-emerald-500/25 bg-gradient-to-br from-emerald-50 to-teal-50 data-[state=active]:from-emerald-500 data-[state=active]:to-teal-500 border-0 px-3 py-3">
                  <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-teal-600 opacity-0 group-data-[state=active]:opacity-100 transition-opacity duration-300 rounded-lg"></div>
                  <div className="relative z-10 flex items-center justify-center text-slate-700 group-data-[state=active]:text-white transition-colors duration-300">
                    <span className="font-bold text-xs">Bibliothèque</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="notes" className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:scale-105 data-[state=active]:scale-105 data-[state=active]:shadow-lg data-[state=active]:shadow-cyan-500/25 bg-gradient-to-br from-cyan-50 to-blue-50 data-[state=active]:from-cyan-500 data-[state=active]:to-blue-500 border-0 px-3 py-3">
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-blue-600 opacity-0 group-data-[state=active]:opacity-100 transition-opacity duration-300 rounded-lg"></div>
                  <div className="relative z-10 flex items-center justify-center text-slate-700 group-data-[state=active]:text-white transition-colors duration-300">
                    <span className="font-bold text-xs">Notes</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="posts" className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:scale-105 data-[state=active]:scale-105 data-[state=active]:shadow-lg data-[state=active]:shadow-orange-500/25 bg-gradient-to-br from-orange-50 to-red-50 data-[state=active]:from-orange-500 data-[state=active]:to-red-500 border-0 px-3 py-3">
                  <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-red-600 opacity-0 group-data-[state=active]:opacity-100 transition-opacity duration-300 rounded-lg"></div>
                  <div className="relative z-10 flex items-center justify-center text-slate-700 group-data-[state=active]:text-white transition-colors duration-300">
                    <span className="font-bold text-xs">Posts</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="calendar" className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:scale-105 data-[state=active]:scale-105 data-[state=active]:shadow-lg data-[state=active]:shadow-indigo-500/25 bg-gradient-to-br from-indigo-50 to-violet-50 data-[state=active]:from-indigo-500 data-[state=active]:to-violet-500 border-0 px-3 py-3">
                  <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-violet-600 opacity-0 group-data-[state=active]:opacity-100 transition-opacity duration-300 rounded-lg"></div>
                  <div className="relative z-10 flex items-center justify-center text-slate-700 group-data-[state=active]:text-white transition-colors duration-300">
                    <span className="font-bold text-xs">Calendrier</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="social" className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:scale-105 data-[state=active]:scale-105 data-[state=active]:shadow-lg data-[state=active]:shadow-rose-500/25 bg-gradient-to-br from-rose-50 to-pink-50 data-[state=active]:from-rose-500 data-[state=active]:to-pink-500 border-0 px-3 py-3">
                  <div className="absolute inset-0 bg-gradient-to-r from-rose-600 to-pink-600 opacity-0 group-data-[state=active]:opacity-100 transition-opacity duration-300 rounded-lg"></div>
                  <div className="relative z-10 flex items-center justify-center text-slate-700 group-data-[state=active]:text-white transition-colors duration-300">
                    <span className="font-bold text-xs">Social</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger value="reglages" className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:scale-105 data-[state=active]:scale-105 data-[state=active]:shadow-lg data-[state=active]:shadow-slate-500/25 bg-gradient-to-br from-slate-50 to-gray-50 data-[state=active]:from-slate-500 data-[state=active]:to-gray-500 border-0 px-3 py-3">
                  <div className="absolute inset-0 bg-gradient-to-r from-slate-600 to-gray-600 opacity-0 group-data-[state=active]:opacity-100 transition-opacity duration-300 rounded-lg"></div>
                  <div className="relative z-10 flex items-center justify-center text-slate-700 group-data-[state=active]:text-white transition-colors duration-300">
                    <span className="font-bold text-xs">Réglages</span>
                  </div>
                </TabsTrigger>
              </div>
            </TabsList>
          </div>

          <TabsContent value="entreprise" className="space-y-3">
            <Card className="relative backdrop-blur-xl bg-white/70 border-0 shadow-2xl shadow-purple-500/10 rounded-2xl overflow-hidden group hover:shadow-3xl hover:shadow-purple-500/20 transition-all duration-500 hover:scale-[1.02]">
              {/* Bordure animée */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/20 via-pink-500/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm"></div>
              <div className="relative z-10">
                <CardHeader className="pb-3 px-4 pt-4">
                  <CardTitle className="flex items-center space-x-3 text-xl">
                    <div className="relative">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/40 hover:rotate-12">
                        <Building className="w-5 h-5 text-white" />
                      </div>
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full animate-pulse"></div>
                    </div>
                    <div className="flex flex-col">
                      <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent font-extrabold">
                        Profil d'entreprise
                      </span>
                      <span className="text-2xl filter drop-shadow-sm">✨</span>
                    </div>
                  </CardTitle>
                  <CardDescription className="text-sm text-slate-600 bg-gradient-to-r from-slate-600 to-slate-700 bg-clip-text text-transparent font-medium">
                    Cliquez sur le stylo ✏️ pour modifier, puis validez ✅ ou annulez ❌
                  </CardDescription>
                </CardHeader>
              <CardContent className="px-3 pb-3">
                {businessProfile ? (
                  <div className="space-y-3">
                    <div className="relative backdrop-blur-sm bg-gradient-to-br from-blue-100/60 via-purple-100/40 to-pink-100/60 rounded-xl p-4 border border-blue-200/30 shadow-lg shadow-blue-500/10 group hover:shadow-xl hover:shadow-purple-500/20 transition-all duration-300">
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-400/5 to-purple-400/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      <div className="relative z-10">
                        <h3 className="text-base font-bold bg-gradient-to-r from-blue-700 to-purple-700 bg-clip-text text-transparent mb-3 flex items-center">
                          <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mr-2 flex items-center justify-center">
                            <div className="w-2 h-2 bg-white rounded-full"></div>
                          </div>
                          Informations de l'entreprise
                        </h3>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-2">
                        <div className="min-w-0">
                          <EditableField
                            fieldId="business_name_edit"
                            label="Nom de l'entreprise"
                            type="text"
                            placeholder="Nom de votre entreprise"
                            defaultValue={businessProfile?.business_name || ''}
                            fieldType="business"
                          />
                        </div>
                        <div className="min-w-0">
                          <EditableField
                            fieldId="business_type_edit"
                            label="Type d'entreprise"
                            type="text"
                            placeholder="Ex: restaurant, commerce, service..."
                            defaultValue={businessProfile?.business_type || ''}
                            fieldType="business"
                          />
                        </div>
                      </div>
                      <div className="mt-2">
                        <EditableField
                          fieldId="business_description_edit"
                          label="Description de l'activité"
                          placeholder="Décrivez votre activité, vos services ou produits..."
                          defaultValue={businessProfile?.business_description || ''}
                          isTextarea={true}
                          fieldType="business"
                        />
                      </div>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 mt-2">
                        <div className="min-w-0">
                          <EditableField
                            fieldId="brand_tone_edit"
                            label="Ton de marque"
                            defaultValue={businessProfile?.brand_tone || 'professionnel'}
                            isSelect={true}
                            options={[
                              { value: 'professionnel', label: '👔 Professionnel' },
                              { value: 'luxe', label: '💎 Luxe' },
                              { value: 'simple', label: '🎯 Simple' },
                              { value: 'humouristique', label: '😄 Humoristique' },
                              { value: 'proximite', label: '🤝 Proximité' },
                              { value: 'amical', label: '😊 Amical' },
                              { value: 'moderne', label: '⚡ Moderne' },
                              { value: 'traditionnel', label: '🏛️ Traditionnel' },
                              { value: 'creatif', label: '🎨 Créatif' },
                              { value: 'technique', label: '🔧 Technique' }
                            ]}
                            fieldType="business"
                          />
                        </div>
                        <div className="min-w-0">
                          <EditableField
                            fieldId="posting_frequency_edit"
                            label="Rythme de publications"
                            defaultValue={businessProfile?.posting_frequency || 'weekly'}
                            isSelect={true}
                            options={[
                              { value: 'daily', label: '📅 Quotidien (7 posts/semaine)' },
                              { value: '3x_week', label: '🔥 3x/semaine (3 posts/semaine)' },
                              { value: 'weekly', label: '📋 Hebdomadaire (1 post/semaine)' },
                              { value: 'bi_weekly', label: '📆 Bi-hebdomadaire (2 posts/semaine)' }
                            ]}
                            fieldType="business"
                          />
                        </div>
                      </div>
                    </div>
                    
                    {/* Section Contact et Marketing */}
                    <div className="relative backdrop-blur-sm bg-gradient-to-br from-purple-100/60 via-pink-100/40 to-rose-100/60 rounded-xl p-4 border border-purple-200/30 shadow-lg shadow-purple-500/10 group hover:shadow-xl hover:shadow-pink-500/20 transition-all duration-300">
                      <div className="absolute inset-0 bg-gradient-to-r from-purple-400/5 to-pink-400/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      <div className="relative z-10">
                        <h3 className="text-base font-bold bg-gradient-to-r from-purple-700 to-pink-700 bg-clip-text text-transparent mb-3 flex items-center">
                          <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mr-2 flex items-center justify-center">
                            <div className="w-2 h-2 bg-white rounded-full"></div>
                          </div>
                          Contact et Marketing
                        </h3>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-2">
                        <div className="min-w-0">
                          <EditableField
                            fieldId="business_email_edit"
                            label="Email professionnel"
                            type="email"
                            placeholder="contact@votre-entreprise.com"
                            defaultValue={businessProfile?.email || ''}
                            fieldType="marketing"
                          />
                        </div>
                        <div className="min-w-0">
                          <EditableField
                            fieldId="business_website_edit"
                            label="Site web"
                            type="url"
                            placeholder="https://votre-site.com"
                            defaultValue={businessProfile?.website_url || ''}
                            fieldType="marketing"
                          />
                        </div>
                      </div>
                      <div className="mt-2">
                        <EditableField
                          fieldId="target_audience_edit"
                          label="Audience cible"
                          placeholder="Décrivez votre audience cible (âge, centres d'intérêt, localisation...)"
                          defaultValue={businessProfile?.target_audience || ''}
                          isTextarea={true}
                          fieldType="marketing"
                        />
                      </div>
                      <div className="mt-2">
                        <EditableField
                          fieldId="business_coordinates_edit"
                          label="Coordonnées"
                          placeholder="Adresse, téléphone, horaires d'ouverture..."
                          defaultValue={businessProfile?.coordinates || ''}
                          isTextarea={true}
                          fieldType="marketing"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
                ) : (
                  <div className="text-center py-12 card-glass rounded-2xl">
                    <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Building className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-700 mb-2">Créez votre profil d'entreprise 🏢</h3>
                    <p className="text-gray-500">Configurez votre profil pour des posts sur mesure ! 🚀</p>
                  </div>
                )}
              </CardContent>
            </div>
            </Card>
          </TabsContent>

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
                {/* Champ URL du site avec input HTML natif */}
                <div className="space-y-2">
                  <label htmlFor="website_analysis_url_native" className="block text-sm font-medium text-gray-700">
                    URL de votre site web
                  </label>
                  <input
                    id="website_analysis_url_native"
                    type="url"
                    placeholder="https://votre-site.com"
                    className="w-full p-4 border border-gray-300 rounded-lg bg-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none"
                    style={{
                      fontSize: '16px',
                      lineHeight: '1.5',
                      WebkitAppearance: 'none',
                      WebkitBorderRadius: '8px',
                      borderRadius: '8px',
                      boxShadow: 'none',
                      WebkitBoxShadow: 'none',
                      touchAction: 'manipulation',
                      userSelect: 'text',
                      WebkitUserSelect: 'text'
                    }}
                    autoComplete="url"
                    autoCorrect="off"
                    autoCapitalize="off"
                    spellCheck="false"
                    inputMode="url"
                    enterKeyHint="go"
                  />
                </div>

                {/* Informations sur l'analyse existante */}
                {lastAnalysisInfo && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <div>
                        <span className="font-medium text-blue-800">Dernière analyse :</span>
                        <span className="text-blue-700 ml-1">
                          {new Date(lastAnalysisInfo.lastAnalyzed).toLocaleDateString('fr-FR', {
                            day: '2-digit',
                            month: '2-digit', 
                            year: 'numeric'
                          })}
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-blue-800">Prochaine analyse :</span>
                        <span className="text-blue-700 ml-1">
                          {new Date(lastAnalysisInfo.nextAnalysisDue).toLocaleDateString('fr-FR', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric'
                          })}
                        </span>
                        {needsNewAnalysis() && (
                          <span className="ml-2 px-2 py-0.5 bg-orange-100 text-orange-800 text-xs rounded-full">
                            Analyse recommandée
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Bouton d'analyse unique et intelligent */}
                <div className="flex gap-3">
                  <Button
                    type="button"
                    onClick={handleAnalyzeWebsite}
                    disabled={isAnalyzing}
                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-6 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isAnalyzing ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Analyse en cours...</span>
                      </>
                    ) : (  
                      <>
                        {lastAnalysisInfo ? <RefreshCw className="w-4 h-4" /> : <Search className="w-4 h-4" />}
                        <span>
                          {lastAnalysisInfo 
                            ? (needsNewAnalysis() ? 'Nouvelle analyse recommandée' : 'Relancer l\'analyse') 
                            : 'Analyser le site'
                          }
                        </span>
                      </>
                    )}
                  </Button>
                </div>

                {/* Affichage des résultats ou message par défaut */}
                {websiteAnalysis ? (
                  <div className="space-y-3">
                    <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                      <h3 className="text-base font-bold text-green-800 mb-3 flex items-center">
                        <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center mr-2 flex-shrink-0">
                          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        Analyse approfondie terminée ! 
                      </h3>
                      
                      {/* Informations sur l'analyse */}
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs mb-4">
                        <div className="min-w-0">
                          <p className="font-semibold text-gray-700 mb-1">Site analysé:</p>
                          <p className="text-gray-600 break-all text-xs">{websiteAnalysis.website_url}</p>
                        </div>
                        <div>
                          <p className="font-semibold text-gray-700 mb-1">Pages analysées:</p>
                          <p className="text-gray-600">{websiteAnalysis.pages_count || 1} page(s)</p>
                        </div>
                        {websiteAnalysis.brand_tone && (
                          <div>
                            <p className="font-semibold text-gray-700 mb-1">Ton de marque:</p>
                            <p className="text-gray-600 capitalize">{websiteAnalysis.brand_tone}</p>
                          </div>
                        )}
                      </div>

                      {/* Pages analysées */}
                      {websiteAnalysis.pages_analyzed && websiteAnalysis.pages_analyzed.length > 0 && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">📄 Pages analysées:</p>
                          <div className="space-y-1">
                            {websiteAnalysis.pages_analyzed.map((page, index) => (
                              <div key={index} className="flex items-center justify-between bg-white rounded p-2 border text-xs">
                                <div className="flex-1 min-w-0 mr-2">
                                  <p className="font-medium text-gray-900 truncate text-xs">
                                    {page.title || 'Page sans titre'}
                                  </p>
                                  <p className="text-gray-600 truncate text-xs">{page.url}</p>
                                </div>
                                <div className="flex-shrink-0">
                                  {page.status === 'analyzed' ? (
                                    <span className="inline-flex px-1.5 py-0.5 text-xs font-semibold bg-green-100 text-green-800 rounded">
                                      ✓
                                    </span>
                                  ) : (
                                    <span className="inline-flex px-1.5 py-0.5 text-xs font-semibold bg-red-100 text-red-800 rounded">
                                      ✗
                                    </span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Résumé de l'analyse */}
                      {websiteAnalysis.analysis_summary && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">📋 Résumé de l'analyse:</p>
                          <div className="bg-white rounded p-3 border">
                            <p className="text-gray-700 leading-relaxed text-sm">{websiteAnalysis.analysis_summary}</p>
                          </div>
                        </div>
                      )}

                      {/* Audience cible */}
                      {websiteAnalysis.target_audience && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">🎯 Audience cible:</p>
                          <div className="bg-white rounded p-3 border">
                            <p className="text-gray-700 text-sm leading-relaxed">{websiteAnalysis.target_audience}</p>
                          </div>
                        </div>
                      )}

                      {/* Services principaux */}
                      {websiteAnalysis.main_services && websiteAnalysis.main_services.length > 0 && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">🛠️ Services principaux:</p>
                          <div className="grid grid-cols-1 gap-1">
                            {websiteAnalysis.main_services.map((service, index) => (
                              <div key={index} className="bg-white rounded p-2 border">
                                <p className="text-xs text-gray-700">{service}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Sujets clés */}
                      {websiteAnalysis.key_topics && websiteAnalysis.key_topics.length > 0 && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">🔑 Sujets clés:</p>
                          <div className="flex flex-wrap gap-1">
                            {websiteAnalysis.key_topics.map((topic, index) => (
                              <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                                {topic}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Suggestions de contenu */}
                      {websiteAnalysis.content_suggestions && websiteAnalysis.content_suggestions.length > 0 && (
                        <div>
                          <p className="font-semibold text-gray-700 mb-2 text-xs">💡 Suggestions de contenu:</p>
                          <div className="space-y-1">
                            {websiteAnalysis.content_suggestions.map((suggestion, index) => (
                              <div key={index} className="bg-white rounded p-2 border-l-2 border-l-yellow-400">
                                <p className="text-xs text-gray-700">{suggestion}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-500">
                    <Search className="w-8 h-8 mx-auto mb-3 text-gray-400" />
                    <p className="text-base mb-2">Aucune analyse disponible</p>
                    <p className="text-xs">Entrez l'URL de votre site web et cliquez sur "Analyser le site"</p>
                    <p className="text-xs text-gray-400 mt-1">Analyse multi-pages : Accueil + pages importantes</p>
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
                {/* Sub-tabs for Library */}
                <div className="mb-6">
                  <div className="flex space-x-2 bg-gray-100 p-1 rounded-lg">
                    <Button
                      onClick={() => setActiveLibraryTab('my-library')}
                      variant={activeLibraryTab === 'my-library' ? 'default' : 'ghost'}
                      className={`flex-1 ${
                        activeLibraryTab === 'my-library'
                          ? 'bg-white shadow-sm text-purple-600'
                          : 'text-gray-600 hover:text-purple-600'
                      }`}
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Ma bibliothèque
                    </Button>
                    <Button
                      onClick={() => setActiveLibraryTab('pixabay-search')}
                      variant={activeLibraryTab === 'pixabay-search' ? 'default' : 'ghost'}
                      className={`flex-1 ${
                        activeLibraryTab === 'pixabay-search'
                          ? 'bg-white shadow-sm text-purple-600'
                          : 'text-gray-600 hover:text-purple-600'
                      }`}
                    >
                      <Search className="w-4 h-4 mr-2" />
                      <span className="hidden sm:inline">Rechercher des images</span>
                      <span className="sm:hidden">Rechercher</span>
                    </Button>
                  </div>
                </div>

                {/* Ma bibliothèque content */}
                {activeLibraryTab === 'my-library' && (
                  <div>
                    {/* Upload Section */}
                    <div className="mb-8">
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

                    {/* Content Gallery - Always visible */}
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-xl font-semibold text-gray-900 flex items-center">
                          <ImageIcon className="w-6 h-6 mr-2 text-purple-600" />
                          Vos contenus ({pendingContent.length})
                        </h4>
                        
                        {/* Boutons de contrôle */}
                        <div className="flex items-center space-x-2">
                          <Button
                            onClick={toggleSelectionMode}
                            variant={isSelectionMode ? "default" : "outline"}
                            size="sm"
                            className={isSelectionMode ? "bg-purple-600 text-white" : "text-purple-600 border-purple-300"}
                          >
                            {isSelectionMode ? (
                              <>
                                <X className="w-4 h-4 mr-1" />
                                Annuler
                              </>
                            ) : (
                              <>
                                <Check className="w-4 h-4 mr-1" />
                                Sélectionner
                              </>
                            )}
                          </Button>
                          
                          {isSelectionMode && (
                            <>
                              <Button
                                onClick={handleSelectAll}
                                variant="outline"
                                size="sm"
                                className="text-blue-600 border-blue-300"
                              >
                                {selectedContentIds.size === pendingContent.length ? 'Tout désélectionner' : 'Tout sélectionner'}
                              </Button>
                              
                              <Button
                                onClick={handleDeleteSelected}
                                disabled={selectedContentIds.size === 0 || isDeletingContent}
                                variant="outline"
                                size="sm"
                                className="text-red-600 border-red-300 hover:bg-red-50"
                              >
                                {isDeletingContent ? (
                                  <>
                                    <div className="animate-spin rounded-full mr-1 h-4 w-4 border-b-2 border-red-600"></div>
                                    Suppression...
                                  </>
                                ) : (
                                  <>
                                    <Trash className="w-4 h-4 mr-1" />
                                    Supprimer ({selectedContentIds.size})
                                  </>
                                )}
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                      
                      {pendingContent.length > 0 ? (
                        <>
                          <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-5 gap-3 mb-6">
                            {pendingContent.map((content) => (
                              <ContentThumbnail
                                key={content.id}
                                content={content}
                                isSelectionMode={isSelectionMode}
                                isSelected={selectedContentIds.has(content.id)}
                                onContentClick={handleContentClick}
                                onToggleSelection={handleToggleSelection}
                              />
                            ))}
                          </div>
                          <div className="text-center">
                            <Button
                              onClick={loadPendingContent}
                              variant="outline"
                              className="text-purple-600 border-purple-300 hover:bg-purple-50"
                            >
                              <ChevronRight className="w-4 h-4 mr-2 rotate-90" />
                              Recharger le contenu
                            </Button>
                          </div>
                        </>
                      ) : (
                        <div className="text-center py-12 card-glass rounded-3xl border-2 border-dashed border-purple-300">
                          <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                            <ImageIcon className="w-12 h-12 text-white" />
                          </div>
                          <h3 className="text-2xl font-bold text-gray-700 mb-4">Votre bibliothèque de contenus 📚</h3>
                          <p className="text-xl text-gray-500 mb-6">Uploadez vos premiers contenus pour voir votre succès exploser ! 🚀</p>
                          <Button
                            onClick={loadPendingContent}
                            variant="outline"
                            className="text-purple-600 border-purple-300 hover:bg-purple-50"
                          >
                            <ChevronRight className="w-4 h-4 mr-2 rotate-90" />
                            Charger le contenu existant
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Pixabay search content */}
                {activeLibraryTab === 'pixabay-search' && (
                  <div>
                    {/* Search Section */}
                    <div className="mb-8">
                      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl p-6 border-2 border-blue-200">
                        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                          <Search className="w-6 h-6 mr-2 text-blue-600" />
                          Rechercher des images gratuites
                        </h3>
                        <p className="text-gray-600 mb-4">
                          Trouvez des millions d'images gratuites et libres de droits pour vos contenus ! 🖼️
                        </p>
                        
                        <div className="flex space-x-3">
                          <Input
                            type="text"
                            placeholder="Ex: business, marketing, équipe..."
                            value={pixabayQuery}
                            onChange={(e) => setPixabayQuery(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && searchPixabayImages()}
                            className="flex-1 text-base border-blue-200 focus:border-blue-400"
                            style={{ fontSize: '16px', WebkitAppearance: 'none' }}
                          />
                          <Button
                            onClick={searchPixabayImages}
                            disabled={isSearchingPixabay || !pixabayQuery.trim()}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-6"
                          >
                            {isSearchingPixabay ? (
                              <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                                Recherche...
                              </>
                            ) : (
                              <>
                                <Search className="w-4 h-4 mr-2" />
                                Rechercher
                              </>
                            )}
                          </Button>
                        </div>

                        {/* Categories */}
                        {pixabayCategories.length > 0 && (
                          <div className="mt-4">
                            <p className="text-sm text-gray-600 mb-2">Catégories populaires :</p>
                            <div className="flex flex-wrap gap-2">
                              {pixabayCategories.slice(0, 8).map((category) => (
                                <Button
                                  key={category}
                                  onClick={() => {
                                    setPixabayQuery(category);
                                    searchPixabayImages();
                                  }}
                                  variant="ghost"
                                  size="sm"
                                  className="text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 border-blue-200"
                                >
                                  {category}
                                </Button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Search Results */}
                    {pixabayResults.length > 0 && (
                      <div>
                        <h4 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                          <ImageIcon className="w-6 h-6 mr-2 text-blue-600" />
                          Résultats de recherche ({pixabayResults.length})
                        </h4>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                          {pixabayResults.map((image) => (
                            <div key={image.id} className="group relative">
                              <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden border-2 border-gray-200 group-hover:border-blue-300 transition-all duration-300">
                                <img 
                                  src={image.webformatURL} 
                                  alt={image.tags}
                                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                />
                                
                                {/* Overlay with actions */}
                                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-300 flex items-center justify-center">
                                  <Button
                                    onClick={() => savePixabayImage(image)}
                                    disabled={isSavingPixabayImage === image.id}
                                    className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-blue-600 hover:bg-blue-700 text-white"
                                    size="sm"
                                  >
                                    {isSavingPixabayImage === image.id ? (
                                      <>
                                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-1"></div>
                                        Ajout...
                                      </>
                                    ) : (
                                      <>
                                        <Upload className="w-4 h-4 mr-1" />
                                        Ajouter
                                      </>
                                    )}
                                  </Button>
                                </div>
                              </div>
                              
                              {/* Image info */}
                              <div className="mt-2">
                                <p className="text-xs text-gray-600 truncate">{image.tags}</p>
                                <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                                  <span>{image.views} vues</span>
                                  <span>{image.downloads} téléchargements</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Empty state for Pixabay search */}
                    {pixabayResults.length === 0 && !isSearchingPixabay && (
                      <div className="text-center py-12 card-glass rounded-3xl border-2 border-dashed border-blue-300">
                        <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                          <Search className="w-12 h-12 text-white" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-700 mb-4">Recherchez des images gratuites ! 🔍</h3>
                        <p className="text-xl text-gray-500 mb-6">Utilisez la barre de recherche ci-dessus pour trouver des images parfaites</p>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Modal d'aperçu du contenu */}
                {previewContent && (
                  <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
                      {/* Header de la modal */}
                      <div className="flex items-center justify-between p-4 border-b">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {previewContent.filename}
                        </h3>
                        <Button
                          onClick={handleClosePreview}
                          variant="ghost"
                          size="sm"
                          className="text-gray-500 hover:text-gray-700"
                        >
                          <X className="w-5 h-5" />
                        </Button>
                      </div>
                      
                      {/* Contenu de la modal */}
                      <div className="flex-1 overflow-auto p-4">
                        <div className="grid md:grid-cols-2 gap-6">
                          {/* Aperçu du média */}
                          <div className="space-y-4">
                            {previewContent.file_type?.startsWith('image/') ? (
                              <img 
                                src={previewContent.url}
                                alt={previewContent.filename}
                                className="w-full h-auto max-h-96 object-contain rounded-lg border"
                              />
                            ) : previewContent.file_type?.startsWith('video/') ? (
                              <video 
                                src={previewContent.url}
                                controls
                                className="w-full h-auto max-h-96 rounded-lg border"
                              />
                            ) : (
                              <div className="w-full h-48 bg-gray-100 rounded-lg border flex items-center justify-center">
                                <FileText className="w-12 h-12 text-gray-400" />
                              </div>
                            )}
                            
                            {/* Informations du fichier */}
                            <div className="text-sm text-gray-600 space-y-1">
                              <p><strong>Type:</strong> {previewContent.file_type}</p>
                              <p><strong>Taille:</strong> {previewContent.file_size ? `${Math.round(previewContent.file_size / 1024)} KB` : 'N/A'}</p>
                              <p><strong>Ajouté le:</strong> {previewContent.uploaded_at ? new Date(previewContent.uploaded_at).toLocaleDateString('fr-FR') : 'N/A'}</p>
                            </div>
                          </div>
                          
                          {/* Zone d'édition du contexte */}
                          <div className="space-y-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Contexte et description 📝
                              </label>
                              <textarea
                                ref={contextTextareaRef}
                                placeholder="Ajoutez une description, du contexte, des mots-clés pour utiliser cette image dans vos posts..."
                                className="w-full h-48 p-3 border border-gray-300 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none resize-none"
                                style={{
                                  fontSize: '16px', // Pour éviter le zoom sur mobile
                                  WebkitAppearance: 'none',
                                  WebkitBorderRadius: '8px',
                                  borderRadius: '8px',
                                  boxShadow: 'none',
                                  WebkitBoxShadow: 'none',
                                  touchAction: 'manipulation',
                                  userSelect: 'text',
                                  WebkitUserSelect: 'text'
                                }}
                                onChange={() => {}} // Handler vide pour éviter re-renders
                              />
                            </div>
                            
                            {/* Boutons d'action */}
                            <div className="flex space-x-3">
                              <Button
                                onClick={handleSaveContext}
                                disabled={isSavingContext}
                                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
                              >
                                {isSavingContext ? (
                                  <>
                                    <div className="animate-spin rounded-full mr-2 h-4 w-4 border-b-2 border-white"></div>
                                    Sauvegarde...
                                  </>
                                ) : (
                                  <>
                                    <Save className="w-4 h-4 mr-2" />
                                    Sauvegarder
                                  </>
                                )}
                              </Button>
                              
                              <Button
                                onClick={handleClosePreview}
                                variant="outline"
                                className="flex-1"
                              >
                                Fermer
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
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
                    
                    <div className="space-y-4">
                      {/* Titre de la note avec input HTML natif */}
                      <div className="space-y-2">
                        <label htmlFor="note_title_native" className="block text-sm font-medium text-gray-700">
                          Titre de la note
                        </label>
                        <input
                          ref={titleInputRef}
                          id="note_title_native"
                          type="text"
                          onChange={handleNoteTitleChange}
                          placeholder="Ex: Nouvelle promotion, Événement spécial..."
                          className="w-full p-4 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation',
                            userSelect: 'text',
                            WebkitUserSelect: 'text'
                          }}
                          autoComplete="off"
                          autoCorrect="off"
                          autoCapitalize="off"
                          spellCheck="false"
                          inputMode="text"
                          enterKeyHint="next"
                        />
                      </div>
                      
                      {/* Contenu de la note avec textarea HTML native */}
                      <div className="space-y-2">
                        <label htmlFor="note_content_native" className="block text-sm font-medium text-gray-700">
                          Contenu
                        </label>
                        <textarea
                          ref={contentInputRef}
                          id="note_content_native"
                          onChange={handleNoteContentChange}
                          placeholder="Décrivez les détails importants que vous voulez voir apparaître dans vos posts..."
                          className="w-full p-4 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation',
                            userSelect: 'text',
                            WebkitUserSelect: 'text',
                            minHeight: '120px'
                          }}
                          rows={5}
                          autoComplete="off"
                          autoCorrect="on"
                          autoCapitalize="sentences"
                          spellCheck="true"
                          inputMode="text"
                          enterKeyHint="enter"
                        />
                      </div>
                      
                      {/* Priorité avec dropdown HTML natif */}
                      <div className="space-y-2">
                        <label htmlFor="note_priority_native" className="block text-sm font-medium text-gray-700">
                          Priorité
                        </label>
                        <select
                          ref={priorityInputRef}
                          id="note_priority_native"
                          onChange={handleNotePriorityChange}
                          className="w-full p-4 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.5',
                            WebkitAppearance: 'none',
                            WebkitBorderRadius: '8px',
                            borderRadius: '8px',
                            boxShadow: 'none',
                            WebkitBoxShadow: 'none',
                            touchAction: 'manipulation',
                            cursor: 'pointer',
                            userSelect: 'text',
                            WebkitUserSelect: 'text'
                          }}
                        >
                          <option value="low">🟢 Priorité faible</option>
                          <option value="normal" selected>🟡 Priorité normale</option>
                          <option value="high">🔴 Priorité élevée</option>
                        </select>
                      </div>
                      
                      {editingNoteId && (
                        <Button
                          type="button"
                          onClick={handleCancelEdit}
                          variant="outline"
                          className="w-full mt-4 border-gray-300 text-gray-600 hover:bg-gray-50"
                        >
                          Annuler l'édition
                        </Button>
                      )}
                      
                      <Button
                        type="button"
                        onClick={handleSaveNote}
                        disabled={isSavingNote}
                        className="btn-gradient-primary w-full mt-6"
                      >
                        {isSavingNote ? (
                          <>
                            <div className="animate-spin rounded-full mr-2 h-4 w-4 border-b-2 border-white"></div>
                            Enregistrement...
                          </>
                        ) : (
                          <>
                            <Edit className="w-4 h-4 mr-2" />
                            {editingNoteId ? 'Modifier cette note' : 'Ajouter cette note'}
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Display saved notes */}
                {notes.length > 0 ? (
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">📝 Mes notes ({notes.length})</h3>
                    <div className="grid gap-4">
                      {notes.map((note, index) => (
                        <div key={note.note_id || index} className="card-glass p-6 rounded-2xl border border-indigo-200">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center space-x-3 flex-1">
                              <div className={`w-3 h-3 rounded-full ${
                                note.priority === 'high' ? 'bg-red-500' :
                                note.priority === 'normal' ? 'bg-yellow-500' : 'bg-green-500'
                              }`}></div>
                              <h4 className="font-semibold text-gray-900 flex-1">
                                {note.description || note.title || 'Note sans titre'}
                              </h4>
                              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                {note.priority === 'high' ? 'élevée' : 
                                 note.priority === 'low' ? 'faible' : 'normale'}
                              </span>
                            </div>
                            
                            <div className="flex items-center space-x-2 ml-4">
                              <div className="text-xs text-gray-500 mr-2">
                                {note.created_at ? new Date(note.created_at).toLocaleDateString('fr-FR', {
                                  day: 'numeric',
                                  month: 'short',
                                  year: 'numeric'
                                }) : ''}
                              </div>
                              
                              {/* Bouton éditer */}
                              <Button
                                onClick={() => handleEditNote(note)}
                                variant="ghost"
                                size="sm"
                                className="p-2 h-8 w-8 text-blue-600 hover:text-blue-800 hover:bg-blue-50"
                                title="Modifier cette note"
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              
                              {/* Bouton supprimer */}
                              <Button
                                onClick={() => handleDeleteNote(note.note_id)}
                                disabled={isDeletingNote === note.note_id}
                                variant="ghost"
                                size="sm"
                                className="p-2 h-8 w-8 text-red-600 hover:text-red-800 hover:bg-red-50"
                                title="Supprimer cette note"
                              >
                                {isDeletingNote === note.note_id ? (
                                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                                ) : (
                                  <Trash className="w-4 h-4" />
                                )}
                              </Button>
                            </div>
                          </div>
                          <p className="text-gray-700 leading-relaxed">
                            {note.content}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 card-glass rounded-3xl border-2 border-dashed border-indigo-300">
                    <div className="w-24 h-24 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                      <Edit className="w-12 h-12 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-700 mb-4">Vos notes apparaîtront ici 📝</h3>
                    <p className="text-xl text-gray-500">Ajoutez votre première note pour commencer ! ✍️</p>
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
                {/* Bouton de génération manuelle */}
                <div className="mb-8 text-center">
                  <Button
                    onClick={handleOpenGenerationModal}
                    disabled={isGeneratingPosts}
                    className="btn-gradient-primary px-8 py-4 text-lg font-semibold"
                  >
                    {isGeneratingPosts ? (
                      <>
                        <div className="animate-spin rounded-full mr-3 h-5 w-5 border-b-2 border-white"></div>
                        Génération en cours...
                      </>
                    ) : (
                      <>
                        <FileText className="w-5 h-5 mr-3" />
                        Générer les posts du mois
                      </>
                    )}
                  </Button>
                </div>

                {/* Liste des posts générés */}
                {generatedPosts.length > 0 ? (
                  <div className="space-y-6">
                    <h4 className="text-xl font-semibold text-gray-900 mb-4">
                      📊 Posts générés ({generatedPosts.length})
                    </h4>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                      {generatedPosts.map((post, index) => (
                        <div key={post.id || index} className="card-glass p-6 rounded-2xl border border-emerald-200">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center space-x-2">
                              <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
                              <span className="text-sm font-medium text-emerald-700">
                                {post.platform || 'Multi-plateformes'}
                              </span>
                            </div>
                            <div className="text-xs text-gray-500">
                              {post.scheduled_date ? new Date(post.scheduled_date).toLocaleDateString('fr-FR') : 'Programmé'}
                            </div>
                          </div>
                          
                          <div className="space-y-3">
                            <p className="text-gray-800 text-sm leading-relaxed line-clamp-4">
                              {post.content}
                            </p>
                            
                            {post.hashtags && post.hashtags.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {post.hashtags.slice(0, 3).map((hashtag, idx) => (
                                  <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                    #{hashtag}
                                  </span>
                                ))}
                                {post.hashtags.length > 3 && (
                                  <span className="text-xs text-gray-500">+{post.hashtags.length - 3}</span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-20 card-glass rounded-3xl">
                    <div className="w-24 h-24 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                      <FileText className="w-12 h-12 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-700 mb-4">Centre de gestion des posts 📊</h3>
                    <p className="text-xl text-gray-500 mb-6">Vos posts générés apparaîtront ici ! 🎪</p>
                    <p className="text-sm text-gray-400">Cliquez sur "Générer les posts du mois" pour commencer</p>
                  </div>
                )}

                {/* Modal de confirmation de génération */}
                {showGenerationModal && (
                  <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl max-w-md w-full p-6">
                      <div className="text-center mb-6">
                        <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                          <FileText className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">
                          Générer les posts du mois ?
                        </h3>
                        <p className="text-gray-600 text-sm">
                          Claire va analyser votre profil, vos photos et vos notes pour créer des posts engageants.
                        </p>
                      </div>

                      {/* Rappel d'uploader du contenu */}
                      <div className="bg-blue-50 rounded-lg p-4 mb-6">
                        <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
                          <Info className="w-4 h-4 mr-2" />
                          Avant de générer, assurez-vous d'avoir :
                        </h4>
                        <ul className="text-sm text-blue-800 space-y-1">
                          <li className="flex items-center">
                            <Check className="w-4 h-4 mr-2" />
                            Uploadé vos photos/vidéos dans "Bibliothèque"
                          </li>
                          <li className="flex items-center">
                            <Check className="w-4 h-4 mr-2" />
                            Ajouté des notes avec vos idées dans "Notes"
                          </li>
                          <li className="flex items-center">
                            <Check className="w-4 h-4 mr-2" />
                            Complété votre profil dans "Entreprise"
                          </li>
                        </ul>
                      </div>

                      {/* Boutons d'action */}
                      <div className="flex space-x-3">
                        <Button
                          onClick={handleCloseGenerationModal}
                          variant="outline"
                          className="flex-1"
                        >
                          Annuler
                        </Button>
                        <Button
                          onClick={handleGeneratePosts}
                          className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white"
                        >
                          <FileText className="w-4 h-4 mr-2" />
                          Générer maintenant
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
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
                <div className="text-center py-20 card-glass rounded-3xl">
                  <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-teal-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                    <Target className="w-12 h-12 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">Réseaux sociaux 🌐</h3>
                  <p className="text-xl text-gray-500">Connectez vos comptes pour publier automatiquement ! 📱</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reglages" className="space-y-8">
            <Card className="card-gradient">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-2xl">
                  <div className="w-10 h-10 bg-gradient-to-r from-gray-500 to-gray-600 rounded-2xl flex items-center justify-center">
                    <Settings className="w-6 h-6 text-white" />
                  </div>
                  <span>Réglages</span>
                </CardTitle>
                <CardDescription>
                  Gérez votre profil, abonnement et paramètres de compte
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-white rounded-2xl p-6 border border-gray-100">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                      <Crown className="w-4 h-4 text-purple-600" />
                    </div>
                    Abonnement actuel
                  </h3>
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100">
                    <div>
                      <div className="font-semibold text-gray-900">Période d'essai</div>
                      <div className="text-sm text-gray-600">1 mois gratuit</div>
                    </div>
                    <Badge className="badge-info">Actif</Badge>
                  </div>
                  <Button 
                    className="mt-4 btn-gradient-primary w-full"
                    onClick={() => setShowPaymentPage(true)}
                  >
                    <CreditCard className="w-4 h-4 mr-2" />
                    Voir les abonnements
                  </Button>
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
      <Dashboard />
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