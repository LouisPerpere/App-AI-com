import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import axios from 'axios';
import AuthPage from './Auth';
import TestAuth from './TestAuth';
import PaymentPage from './PaymentPage';
import AdminDashboard from './AdminDashboard';
import FacebookCallback from './FacebookCallback';
import PrivacyPolicy from './PrivacyPolicy';

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
import { Building, Sparkles, Crown, Upload, FileText, X, Edit, Edit2, Plus, CalendarIcon, Target, LogOut, Check, Send, Clock, ChevronLeft, ChevronRight, CreditCard, Settings, Globe, Save, Search, Users, Cog, Trash, Trash2, RefreshCw, Calendar, Image as ImageIcon, Info, Play, Eye, ChevronDown, Loader2, Share as ShareIcon, CheckCircle as CheckCircleIcon, Plus as PlusIcon, Info as InformationCircleIcon } from 'lucide-react';

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

// ContentThumbnail component avec support carrousel
const ContentThumbnail = React.memo(({ content, isSelectionMode, isSelected, onContentClick, onToggleSelection, onMoveContent }) => {
  // Token stable - récupéré une seule fois
  const stableToken = useMemo(() => {
    const token = localStorage.getItem('access_token');
    return token;
  }, []);
  
  // Check if this is a carousel item
  const isCarousel = content.type === 'carousel';
  
  // Optimisation URL des vignettes avec token stable
  const thumbnailUrl = useMemo(() => {
    let url;
    
    if (content.thumb_url) {
      url = `${content.thumb_url}?token=${stableToken}`;
    } else {
      url = null;
    }
    
    return url;
  }, [content.thumb_url, stableToken]);

  const handleClick = useCallback(() => {
    onContentClick(content);
  }, [content, onContentClick]);

  const handleToggle = useCallback((e) => {
    e.stopPropagation();
    onToggleSelection(content.id);
  }, [content.id, onToggleSelection]);

  if (isCarousel) {
    // CAROUSEL DISPLAY WITH ENHANCED STACK EFFECT
    return (
      <div 
        className={`thumbnail-container relative group transform hover:scale-105 transition-all duration-200 cursor-pointer`}
        onClick={handleClick}
      >
        <div className="relative aspect-square">
          {/* Stack layers - Enhanced and more visible */}
          <div className="absolute inset-0 bg-gray-600 rounded-xl transform translate-x-3 translate-y-3 opacity-40 shadow-lg"></div>
          <div className="absolute inset-0 bg-gray-500 rounded-xl transform translate-x-2 translate-y-2 opacity-60 shadow-lg"></div>
          <div className="absolute inset-0 bg-gray-400 rounded-xl transform translate-x-1 translate-y-1 opacity-80 shadow-lg"></div>
          
          {/* Front image */}
          <div className={`relative aspect-square bg-gray-100 rounded-xl overflow-hidden border-2 transition-colors shadow-xl ${
            isSelectionMode && isSelected
              ? 'border-pink-500 ring-2 ring-pink-200'
              : 'border-pink-200 hover:border-pink-400'
          }`}>
            <img 
              src={thumbnailUrl || '/api/placeholder.png'}
              alt={content.title || 'Carrousel'}
              className="thumbnail-image w-full h-full object-cover"
              loading="lazy"
              crossOrigin="anonymous"
              onError={(e) => {
                const fallbackUrl = '/api/placeholder.png';
                if (e.currentTarget.src !== fallbackUrl) {
                  e.currentTarget.src = fallbackUrl;
                }
              }}
            />
            
            {/* Carousel indicator badge */}
            <div className="absolute top-2 right-2 bg-pink-600 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg">
              {content.count || 1}
            </div>
            
            {/* Carousel icon */}
            <div className="absolute top-2 left-2 bg-black/50 text-white p-1 rounded-full">
              <ImageIcon className="w-3 h-3" />
            </div>
          </div>
        </div>
        
        {/* Title overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3 rounded-b-xl">
          <p className="text-xs font-medium text-white truncate">
            🎠 {content.title || 'Carrousel'}
          </p>
        </div>
        
        {/* Selection mode overlay */}
        {isSelectionMode && (
          <div className="absolute inset-0 bg-black/30 rounded-xl">
            <button
              onClick={handleToggle}
              className={`absolute top-2 right-2 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors z-10 ${
                isSelected 
                  ? 'bg-pink-600 border-pink-600' 
                  : 'bg-white/80 border-white hover:bg-white'
              }`}
            >
              {isSelected && <Check className="w-3 h-3 text-white" />}
            </button>
          </div>
        )}
      </div>
    );
  }

  // REGULAR CONTENT DISPLAY
  return (
    <div 
      className={`thumbnail-container relative group transform hover:scale-105 transition-all duration-200 cursor-pointer`}
      onClick={handleClick}
    >
      <div className={`aspect-square bg-gray-100 rounded-xl overflow-hidden border-2 transition-colors shadow-md hover:shadow-lg ${
        isSelectionMode && isSelected
          ? 'border-purple-500 ring-2 ring-purple-200'
          : 'border-purple-200 hover:border-purple-400'
      }`}>
        {content.file_type?.startsWith('image/') ? (
          <img 
            src={thumbnailUrl || '/api/placeholder.png'}
            alt={content.filename}
            className="thumbnail-image w-full h-full object-cover"
            loading="lazy"
            crossOrigin="anonymous"
            onError={(e) => {
              const fallbackUrl = content.url || '/api/placeholder.png';
              if (e.currentTarget.src !== fallbackUrl) {
                e.currentTarget.src = fallbackUrl;
              }
            }}
          />
        ) : content.file_type?.startsWith('video/') ? (
          <div className="w-full h-full bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
            <Play className="w-8 h-8 text-blue-600" />
          </div>
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
            <FileText className="w-12 h-12 text-gray-400" />
          </div>
        )}
      </div>
      
      {/* Title overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3 rounded-b-xl">
        <p className="text-xs font-medium text-white truncate">
          {content.title || content.filename}
        </p>
      </div>
      
      {/* Selection mode overlay */}
      {isSelectionMode && (
        <div className="absolute inset-0 bg-black/30 rounded-xl">
          <button
            onClick={handleToggle}
            className={`absolute top-2 right-2 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
              isSelected 
                ? 'bg-purple-600 border-purple-600' 
                : 'bg-white/80 border-white hover:bg-white'
            }`}
          >
            {isSelected && <Check className="w-3 h-3 text-white" />}
          </button>
        </div>
      )}
      
      {/* Source indicators */}
      {content.source === 'pixabay' && (
        <div className="absolute bottom-8 left-2 bg-blue-600 text-white text-xs px-2 py-1 rounded-full font-medium shadow-lg">
          Pixabay
        </div>
      )}
      
      {/* Carousel count indicator */}
      {content.type === 'carousel' && content.count > 1 && (
        <div className="absolute top-2 left-2 bg-purple-600 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg z-20" title={`Carrousel de ${content.count} images`}>
          {content.count}
        </div>
      )}
      
      {/* Used in posts indicator - green checkmark */}
      {content.used_in_posts && !isSelectionMode && (
        <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1 shadow-lg z-10" title="Utilisée dans un post">
          <Check className="w-4 h-4" />
        </div>
      )}
      
      {/* Used in posts indicator when in selection mode - moved to top-left */}
      {content.used_in_posts && isSelectionMode && (
        <div className="absolute top-2 left-2 bg-green-500 text-white rounded-full p-1 shadow-lg z-10" title="Utilisée dans un post">
          <Check className="w-3 h-3" />
        </div>
      )}
      
      {/* Move content button - appears on hover when not in selection mode */}
      {!isSelectionMode && onMoveContent && (
        <div className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onMoveContent(content);
            }}
            className="w-8 h-8 bg-orange-600 hover:bg-orange-700 text-white rounded-full flex items-center justify-center shadow-lg transition-colors"
            title="Déplacer vers un autre mois"
          >
            <Calendar className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
});

// Composant vignette de post
const PostThumbnail = ({ post, onClick, onAddImage, onModifyImage }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Non programmé';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const needsImage = post.status === 'needs_image' || !post.visual_url;
  const hasImage = !needsImage;

  const handleClick = () => {
    if (needsImage && onAddImage) {
      onAddImage(post);
    } else {
      onClick(post);
    }
  };

  return (
    <div 
      onClick={handleClick}
      className="group cursor-pointer transform hover:scale-105 transition-all duration-200"
    >
      <div className={`bg-white rounded-xl border shadow-md hover:shadow-lg overflow-hidden ${
        needsImage 
          ? 'border-orange-300 hover:border-orange-500' 
          : 'border-emerald-200 hover:border-emerald-400'
      }`}>
        {/* Image/Visual du post */}
        <div className="aspect-square bg-gradient-to-br from-emerald-100 to-blue-100 flex items-center justify-center relative">
          {post.visual_url && !needsImage ? (
            <>
              <img 
                src={post.visual_url.startsWith('http') 
                  ? post.visual_url 
                  : `${process.env.REACT_APP_BACKEND_URL}${post.visual_url}?token=${localStorage.getItem('access_token')}&t=${Date.now()}`
                } 
                alt={post.title || 'Post'}
                className="w-full h-full object-cover"
                onError={(e) => {
                  console.error('❌ Error loading post image:', post.visual_url);
                  e.target.style.display = 'none';
                  if (e.target.nextSibling) {
                    e.target.nextSibling.style.display = 'flex';
                  }
                }}
              />
              {/* Fallback en cas d'erreur de chargement */}
              <div className="hidden text-center p-4 w-full h-full items-center justify-center flex-col">
                <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Image non disponible</p>
              </div>
            </>
          ) : (
            <div className="text-center p-4">
              {needsImage ? (
                <>
                  <ImageIcon className="w-12 h-12 text-orange-500 mx-auto mb-2" />
                  <p className="text-sm text-orange-700 font-medium">Ajouter image</p>
                  <p className="text-xs text-orange-600">Cliquez pour choisir</p>
                </>
              ) : (
                <>
                  <FileText className="w-12 h-12 text-emerald-500 mx-auto mb-2" />
                  <p className="text-sm text-emerald-700 font-medium">Post IA</p>
                </>
              )}
            </div>
          )}
          
          {/* Badge plateforme */}
          <div className="absolute top-2 left-2">
            <span className="bg-emerald-500 text-white text-xs px-2 py-1 rounded-full font-medium">
              {post.platform || 'Instagram'}
            </span>
          </div>
          
          {/* Badge statut image */}
          {needsImage && (
            <div className="absolute top-2 right-2">
              <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full font-medium animate-pulse">
                ⚠️ Image requise
              </span>
            </div>
          )}
          
          {/* Boutons d'action pour posts avec images */}
          {hasImage && (
            <div className="absolute top-2 right-2 flex space-x-1">
              {/* Bouton modifier image */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onModifyImage && onModifyImage(post);
                }}
                className="w-7 h-7 bg-blue-500 hover:bg-blue-600 text-white rounded-full flex items-center justify-center transition-colors shadow-md"
                title="Modifier l'image"
              >
                <Edit2 className="w-3 h-3" />
              </button>
              
              {/* Bouton ajouter image (carrousel) */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAddImage && onAddImage(post);
                }}
                className="w-7 h-7 bg-purple-500 hover:bg-purple-600 text-white rounded-full flex items-center justify-center transition-colors shadow-md"
                title="Ajouter une image (carrousel)"
              >
                <Plus className="w-3 h-3" />
              </button>
            </div>
          )}
          
          {/* Badge date */}
          <div className="absolute bottom-2 right-2">
            <span className="bg-black/50 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">
              {formatDate(post.scheduled_date)}
            </span>
          </div>
        </div>
        
        {/* Contenu */}
        <div className="p-3">
          <h4 className="font-semibold text-gray-800 text-sm mb-1 line-clamp-1">
            {post.title || 'Post généré'}
          </h4>
          <p className="text-gray-600 text-xs line-clamp-2 mb-2">
            {post.text || 'Aucun texte disponible'}
          </p>
          
          {/* Hashtags */}
          {post.hashtags && post.hashtags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {post.hashtags.slice(0, 2).map((hashtag, idx) => (
                <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                  {hashtag.startsWith('#') ? hashtag : `#${hashtag}`}
                </span>
              ))}
              {post.hashtags.length > 2 && (
                <span className="text-xs text-gray-500">+{post.hashtags.length - 2}</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Modal d'aperçu de post
const PostPreviewModal = ({ 
  post, 
  onClose, 
  onModify, 
  onValidate, 
  isModifying, 
  modificationRequestRef  // Changé de state à ref
}) => {
  const [showModificationForm, setShowModificationForm] = useState(false);

  const formatDate = (dateString) => {
    if (!dateString) return 'Non programmé';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleModifySubmit = () => {
    const modificationValue = modificationRequestRef.current?.value || '';
    onModify(post, modificationValue);
    setShowModificationForm(false);
  };

  const handleCancel = () => {
    setShowModificationForm(false);
    if (modificationRequestRef.current) {
      modificationRequestRef.current.value = '';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto flex flex-col relative">
        {/* Overlay de modification en cours */}
        {isModifying && (
          <div className="absolute inset-0 bg-white bg-opacity-95 flex flex-col items-center justify-center z-50 rounded-2xl">
            <div className="flex flex-col items-center space-y-4">
              <div className="w-16 h-16 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin"></div>
              <div className="text-center">
                <h3 className="text-xl font-bold text-gray-800 mb-2">✨ Modification en cours</h3>
                <p className="text-gray-600 max-w-sm">
                  Notre IA travaille pour améliorer votre post selon vos instructions...
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-xl flex items-center justify-center">
              <Eye className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-800">Aperçu du post</h3>
              <p className="text-sm text-gray-600">
                {post.platform || 'Instagram'} • {formatDate(post.scheduled_date)}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isModifying}
            className="w-8 h-8 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 rounded-full flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4 text-gray-600" />
          </button>
        </div>

        {/* Contenu */}
        <div className="p-6 space-y-4 flex-1 overflow-y-auto">
          {/* Visual */}
          {post.visual_url && (
            <div className="aspect-video bg-gray-100 rounded-xl overflow-hidden">
              <img 
                src={post.visual_url.startsWith('http') 
                  ? post.visual_url 
                  : `${process.env.REACT_APP_BACKEND_URL}${post.visual_url}?token=${localStorage.getItem('access_token')}`
                } 
                alt={post.title || 'Post'}
                className="w-full h-full object-cover"
              />
            </div>
          )}

          {/* Titre */}
          {post.title && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Titre :</h4>
              <p className="text-lg font-semibold text-gray-800">{post.title}</p>
            </div>
          )}

          {/* Texte du post */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Texte du post :</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {post.text || 'Aucun texte disponible'}
              </p>
            </div>
          </div>

          {/* Hashtags */}
          {post.hashtags && post.hashtags.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Hashtags ({post.hashtags.length}) :</h4>
              <div className="flex flex-wrap gap-2">
                {post.hashtags.map((hashtag, idx) => (
                  <span key={idx} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                    {hashtag.startsWith('#') ? hashtag : `#${hashtag}`}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Formulaire de modification */}
          {showModificationForm && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-yellow-800 mb-2">
                Demande de modification :
              </h4>
              <textarea
                ref={modificationRequestRef}
                placeholder="Décrivez comment vous souhaitez modifier ce post..."
                className="w-full p-3 border border-yellow-300 rounded-lg resize-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                rows="3"
                disabled={isModifying}
              />
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-center space-x-3 p-6 border-t border-gray-200 flex-shrink-0 bg-white">
          {!showModificationForm ? (
            <>
              <button
                onClick={onValidate}
                className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
              >
                <div className="flex items-center space-x-2">
                  <Check className="w-4 h-4" />
                  <span>Valider</span>
                </div>
              </button>
              <button
                onClick={() => setShowModificationForm(true)}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
              >
                <div className="flex items-center space-x-2">
                  <Edit className="w-4 h-4" />
                  <span>Modifier</span>
                </div>
              </button>
            </>
          ) : (
            <div className="w-full">
              {/* Formulaire de modification */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-4">
                <h5 className="text-sm font-semibold text-yellow-800 mb-3">
                  ✏️ Demander une modification
                </h5>
                
                <textarea
                  ref={modificationRequestRef}
                  placeholder="Décrivez comment vous souhaitez modifier ce post..."
                  className="w-full p-3 border border-yellow-300 rounded-lg resize-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                  rows="3"
                  disabled={isModifying}
                />
              </div>

              {/* Boutons d'action - modernisés et centrés */}
              <div className="flex items-center justify-center space-x-4">
                <button
                  onClick={handleCancel}
                  disabled={isModifying}
                  className="px-6 py-3 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 rounded-xl font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-sm hover:shadow-md"
                >
                  <div className="flex items-center space-x-2">
                    <X className="w-4 h-4" />
                    <span>Annuler</span>
                  </div>
                </button>
                
                <button
                  onClick={handleModifySubmit}
                  disabled={isModifying}
                  className="px-6 py-3 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 disabled:from-gray-300 disabled:to-gray-400 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                >
                  <div className="flex items-center space-x-2">
                    {isModifying ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Envoi...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span>Envoyer</span>
                      </>
                    )}
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Composant pour afficher le texte du post de manière collapsible
const PostTextPreview = ({ postText }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  if (!postText) return null;
  
  const isLong = postText.length > 200;
  const displayText = isExpanded || !isLong ? postText : postText.substring(0, 200) + '...';
  
  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-700">Texte du post :</h4>
        {isLong && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-orange-600 hover:text-orange-700 font-medium flex items-center space-x-1"
          >
            <span>{isExpanded ? 'Réduire' : 'Voir plus'}</span>
            <ChevronDown className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
          </button>
        )}
      </div>
      <div className="bg-gray-50 rounded-lg p-3 max-h-32 overflow-y-auto">
        <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
          {displayText}
        </p>
      </div>
    </div>
  );
};

// Composant réutilisant les modules existants pour l'ajout d'images aux posts
const ImageAttachmentContent = ({ 
  activeTab, 
  onAttachImage, 
  isAttaching, 
  pendingContent, 
  pixabayResults, 
  isSearchingPixabay, 
  searchPixabay,
  handleFileSelect,
  selectedFiles,
  isUploading,
  handleBatchUpload,
  postToAttachImage,
  uploadFilesForPost,
  // Ajout des props pour l'organisation mensuelle
  getMonthlyContentData,
  collapsedMonths,
  toggleMonthCollapse,
  // Nouvelle prop pour supprimer des fichiers
  onRemoveFile
}) => {
  
  const handleLibraryImageSelect = (content) => {
    if (isAttaching) return;
    
    // Utiliser l'ID du contenu de la bibliothèque
    const imageData = {
      image_id: content.id || content._id
    };
    
    onAttachImage('library', imageData);
  };

  const handlePixabayImageSelect = (pixabayImage) => {
    if (isAttaching) return;
    
    const imageData = {
      image_url: pixabayImage.webformatURL,
      image_id: `pixabay_${pixabayImage.id}`
    };
    
    onAttachImage('pixabay', imageData);
  };

  const handleUploadForPost = async () => {
    if (isAttaching || selectedFiles.length === 0) return;
    
    // Récupérer les métadonnées du post pour les appliquer aux images
    const postTitle = postToAttachImage?.title || 'Post généré';
    const postText = postToAttachImage?.text || '';
    
    // Préparer l'upload avec les métadonnées du post
    const uploadData = await uploadFilesForPost(selectedFiles, postTitle, postText);
    
    // Utiliser les IDs des fichiers uploadés
    if (uploadData && uploadData.length > 0) {
      const imageData = {
        uploaded_file_ids: uploadData.map(item => item.id)
      };
      
      onAttachImage('upload', imageData);
    }
  };

  if (activeTab === 'library') {
    // Utiliser l'organisation mensuelle comme dans la bibliothèque principale
    const { currentAndFuture, archives } = getMonthlyContentData();
    
    return (
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-4">
          Choisir dans ma bibliothèque
        </h4>
        
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {/* Mois actuels et futurs */}
          {Object.entries(currentAndFuture)
            .sort(([, a], [, b]) => a.order - b.order)
            .map(([monthKey, monthData]) => (
              <div key={monthKey} className="border border-gray-200 rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleMonthCollapse(monthKey)}
                  className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                    <span className="font-medium text-gray-800">{monthData.label}</span>
                    <span className="text-sm text-gray-500">({monthData.content.length})</span>
                  </div>
                  <ChevronDown 
                    className={`w-4 h-4 text-gray-500 transition-transform ${
                      collapsedMonths.has(monthKey) ? 'transform rotate-180' : ''
                    }`} 
                  />
                </button>
                
                {!collapsedMonths.has(monthKey) && monthData.content.length > 0 && (
                  <div className="p-4">
                    <div className="grid grid-cols-3 gap-3">
                      {monthData.content.map((content, index) => (
                        <div
                          key={content.id || index}
                          onClick={() => handleLibraryImageSelect(content)}
                          className="group cursor-pointer transition-all duration-200 relative overflow-visible"
                        >
                          <div className="transform hover:scale-105 transition-transform duration-200">
                            <ContentThumbnail
                              content={content}
                              isSelectionMode={false}
                              isSelected={false}
                              onContentClick={() => {}}
                              onToggleSelection={() => {}}
                              onMoveContent={() => {}}
                            />
                          </div>
                          
                          {/* Badge indiquant si l'image est déjà utilisée */}
                          {content.used_in_posts && (
                            <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1 z-10">
                              <Check className="w-3 h-3" />
                            </div>
                          )}
                          
                          {/* Overlay de sélection - ajusté pour éviter débordement */}  
                          <div className="absolute inset-0 bg-orange-500 bg-opacity-0 group-hover:bg-opacity-20 transition-all rounded-xl flex items-start justify-start overflow-visible">
                            <div className="opacity-0 group-hover:opacity-100 bg-white bg-opacity-95 px-2 py-1 rounded-md font-medium text-orange-600 text-xs transition-opacity m-1 shadow-lg border border-orange-200 z-20">
                              Sélectionner
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {!collapsedMonths.has(monthKey) && monthData.content.length === 0 && (
                  <div className="p-4 text-center text-gray-500 text-sm">
                    Aucun contenu pour ce mois
                  </div>
                )}
              </div>
            ))}

          {/* Mois archives */}
          {Object.entries(archives)
            .sort(([, a], [, b]) => b.order - a.order)
            .map(([monthKey, monthData]) => (
              <div key={monthKey} className="border border-gray-200 rounded-lg overflow-hidden opacity-75">
                <button
                  onClick={() => toggleMonthCollapse(monthKey)}
                  className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                    <span className="font-medium text-gray-600">{monthData.label}</span>
                    <span className="text-sm text-gray-400">({monthData.content.length})</span>
                  </div>
                  <ChevronDown 
                    className={`w-4 h-4 text-gray-400 transition-transform ${
                      collapsedMonths.has(monthKey) ? 'transform rotate-180' : ''
                    }`} 
                  />
                </button>
                
                {!collapsedMonths.has(monthKey) && monthData.content.length > 0 && (
                  <div className="p-4">
                    <div className="grid grid-cols-3 gap-3">
                      {monthData.content.map((content, index) => (
                        <div
                          key={content.id || index}
                          onClick={() => handleLibraryImageSelect(content)}
                          className="group cursor-pointer transition-all duration-200 relative overflow-visible"
                        >
                          <div className="transform hover:scale-105 transition-transform duration-200">
                            <ContentThumbnail
                              content={content}
                              isSelectionMode={false}
                              isSelected={false}
                              onContentClick={() => {}}
                              onToggleSelection={() => {}}
                              onMoveContent={() => {}}
                            />
                          </div>
                          
                          {content.used_in_posts && (
                            <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1 z-10">
                              <Check className="w-3 h-3" />
                            </div>
                          )}
                          
                          <div className="absolute inset-0 bg-orange-500 bg-opacity-0 group-hover:bg-opacity-20 transition-all rounded-xl flex items-start justify-start overflow-visible">
                            <div className="opacity-0 group-hover:opacity-100 bg-white bg-opacity-95 px-2 py-1 rounded-md font-medium text-orange-600 text-xs transition-opacity m-1 shadow-lg border border-orange-200 z-20">
                              Sélectionner
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
        </div>
        
        {pendingContent.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <ImageIcon className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>Aucune image dans votre bibliothèque</p>
          </div>
        )}
      </div>
    );
  }

  if (activeTab === 'pixabay') {
    return (
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-4">
          Rechercher sur Pixabay
        </h4>
        
        {/* Barre de recherche corrigée */}
        <div className="mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Rechercher des images (ex: montres, horlogerie)..."
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  searchPixabay(e.target.value);
                }
              }}
            />
            <button
              onClick={() => {
                const input = document.querySelector('input[placeholder*="Rechercher des images"]');
                if (input) searchPixabay(input.value);
              }}
              disabled={isSearchingPixabay}
              className="px-4 py-3 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white rounded-lg font-medium transition-colors whitespace-nowrap"
            >
              {isSearchingPixabay ? 'Recherche...' : '🔍'}
            </button>
          </div>
        </div>

        {/* Résultats Pixabay */}
        {pixabayResults.length > 0 ? (
          <div className="grid grid-cols-3 gap-3 max-h-96 overflow-y-auto">
            {pixabayResults.map((image, index) => (
              <div
                key={image.id}
                onClick={() => handlePixabayImageSelect(image)}
                className="group cursor-pointer transform hover:scale-105 transition-all duration-200 relative"
              >
                <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden">
                  <img
                    src={image.webformatURL}
                    alt={image.tags}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
                
                {/* Overlay de sélection */}
                <div className="absolute inset-0 bg-orange-500 bg-opacity-0 group-hover:bg-opacity-20 transition-all rounded-xl flex items-start justify-start">
                  <div className="opacity-0 group-hover:opacity-100 bg-white bg-opacity-90 px-3 py-1 rounded-lg font-medium text-orange-600 text-sm transition-opacity m-2">
                    Sélectionner
                  </div>
                </div>

                {/* Badge Pixabay */}
                <div className="absolute bottom-2 left-2 bg-blue-600 text-white text-xs px-2 py-1 rounded-full font-medium">
                  Pixabay
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Search className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>Recherchez des images pour votre post</p>
          </div>
        )}
      </div>
    );
  }

  if (activeTab === 'upload') {
    return (
      <div>
        <h4 className="text-lg font-semibold text-gray-800 mb-6">
          📸 Ajouter vos propres images
        </h4>
        
        {/* Zone de drop améliorée - plus marketing */}
        <div className="relative">
          <div className="border-2 border-dashed border-orange-300 rounded-2xl p-8 text-center mb-6 bg-gradient-to-br from-orange-50 to-amber-50 hover:from-orange-100 hover:to-amber-100 transition-all duration-300">
            <input
              type="file"
              multiple
              accept="image/*,video/*"
              onChange={handleFileSelect}
              className="hidden"
              id="post-file-upload"
            />
            <label
              htmlFor="post-file-upload"
              className="cursor-pointer flex flex-col items-center"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-amber-500 rounded-full flex items-center justify-center mb-4 shadow-lg">
                <Upload className="w-8 h-8 text-white" />
              </div>
              <h5 className="text-xl font-bold text-gray-800 mb-2">
                ✨ Glissez vos fichiers ici
              </h5>
              <p className="text-gray-600 mb-2">
                ou <span className="text-orange-600 font-medium">cliquez pour parcourir</span>
              </p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span className="flex items-center">
                  <ImageIcon className="w-4 h-4 mr-1" />
                  Images
                </span>
                <span className="flex items-center">
                  <Play className="w-4 h-4 mr-1" />
                  Vidéos
                </span>
                <span className="flex items-center">
                  <Target className="w-4 h-4 mr-1" />
                  Max 10 fichiers
                </span>
              </div>
            </label>
          </div>
          
          {/* Badge indicateur si plusieurs fichiers */}
          {selectedFiles.length > 1 && (
            <div className="absolute top-4 right-4 bg-emerald-500 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg">
              🎠 Carrousel ({selectedFiles.length} images)
            </div>
          )}
        </div>

        {/* Fichiers sélectionnés */}
        {selectedFiles.length > 0 && (
          <div className="mb-6">
            <h5 className="font-medium text-gray-800 mb-3 flex items-center">
              <FileText className="w-4 h-4 mr-2" />
              {selectedFiles.length} fichier{selectedFiles.length > 1 ? 's' : ''} sélectionné{selectedFiles.length > 1 ? 's' : ''}
            </h5>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center">
                      <ImageIcon className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-700">{file.name}</span>
                      <div className="text-xs text-gray-500 flex items-center space-x-2">
                        <span>{(file.size / 1024 / 1024).toFixed(1)} MB</span>
                        {selectedFiles.length > 1 && (
                          <span className="bg-emerald-200 text-emerald-800 px-2 py-0.5 rounded-full">
                            #{index + 1}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Bouton de suppression */}
                  <button
                    onClick={() => onRemoveFile(index)}
                    className="w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors"
                    title="Supprimer ce fichier"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Bouton upload stylisé */}
        {selectedFiles.length > 0 && (
          <div className="text-center">
            <button
              onClick={handleUploadForPost}
              disabled={isUploading || isAttaching}
              className="px-8 py-4 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 disabled:from-gray-300 disabled:to-gray-400 text-white rounded-xl font-bold text-lg shadow-lg transition-all duration-300 transform hover:scale-105 disabled:transform-none"
            >
              {isUploading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Upload en cours...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Upload className="w-5 h-5" />
                  <span>
                    {selectedFiles.length === 1 
                      ? '🚀 Uploader cette image' 
                      : `🎠 Créer un carrousel (${selectedFiles.length} images)`
                    }
                  </span>
                </div>
              )}
            </button>
          </div>
        )}
      </div>
    );
  }
};

function MainApp() {
  const location = useLocation();
  
  // État pour l'authentification
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
  const [fileCustomData, setFileCustomData] = useState({}); // Store custom titles and contexts for selected files
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
  
  // Posts management states
  const [selectedPost, setSelectedPost] = useState(null);
  const [isModifyingPost, setIsModifyingPost] = useState(false);
  const [postsByMonth, setPostsByMonth] = useState({});
  const [collapsedPostMonths, setCollapsedPostMonths] = useState({});
  
  // Refs pour inputs non-contrôlés (fix clavier virtuel)
  const modificationRequestRef = useRef(null);
  const uploadTitleRefs = useRef({}); // Map des refs par index de fichier
  const uploadContextRefs = useRef({}); // Map des refs par index de fichier
  
  // Content move states
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [contentToMove, setContentToMove] = useState(null);
  const [isMovingContent, setIsMovingContent] = useState(false);
  
  // Post image attachment states
  const [showImageAttachModal, setShowImageAttachModal] = useState(false);
  const [postToAttachImage, setPostToAttachImage] = useState(null);
  const [attachImageTab, setAttachImageTab] = useState('library'); // 'library', 'pixabay', 'upload'
  const [isAttachingImage, setIsAttachingImage] = useState(false);
  const [imageAttachmentMode, setImageAttachmentMode] = useState('add'); // 'add' ou 'modify'
  
  // Pixabay integration states
  const [activeLibraryTab, setActiveLibraryTab] = useState('my-library'); // 'my-library' or 'pixabay-search'
  const [pixabayResults, setPixabayResults] = useState([]);
  const [pixabayCategories, setPixabayCategories] = useState([]);
  const [isSearchingPixabay, setIsSearchingPixabay] = useState(false);
  const [savedPixabayImages, setSavedPixabayImages] = useState(new Set()); // Track successfully saved images
  const [pixabayCurrentPage, setPixabayCurrentPage] = useState(1);
  const [pixabayTotalHits, setPixabayTotalHits] = useState(0);
  const [pixabayCurrentQuery, setPixabayCurrentQuery] = useState('');
  const [isLoadingMorePixabay, setIsLoadingMorePixabay] = useState(false);
  
  // Content pagination states
  const [contentPage, setContentPage] = useState(0);
  const [totalContentCount, setTotalContentCount] = useState(0);
  
  // Carousel upload states
  const [carouselFiles, setCarouselFiles] = useState([]);
  const [carouselTitle, setCarouselTitle] = useState('');
  const [carouselContext, setCarouselContext] = useState('');

  // Social media connections states
  const [connectedAccounts, setConnectedAccounts] = useState({
    instagram: null,
    facebook: null,
    linkedin: null
  });
  const [isConnectingAccount, setIsConnectingAccount] = useState(false);
  const [socialConnectionStatus, setSocialConnectionStatus] = useState('');

  // Auto-navigation après modification de post - Navigation vers onglet Posts
  useEffect(() => {
    const returnToPostsTab = localStorage.getItem('returnToPostsTab');
    
    if (returnToPostsTab === 'true') {
      console.log('🔄 Auto-navigation après modification de post');
      
      // Naviguer vers l'onglet Posts
      setActiveTab('posts');
      
      // Nettoyer le localStorage immédiatement pour éviter les boucles
      localStorage.removeItem('returnToPostsTab');
    }
  }, []);

  // Auto-scroll vers le post modifié - SE DÉCLENCHE QUAND LES POSTS SONT CHARGÉS
  useEffect(() => {
    const modifiedPostId = localStorage.getItem('modifiedPostId');
    
    // Vérifier que nous sommes sur l'onglet Posts et que les posts sont chargés
    if (modifiedPostId && activeTab === 'posts' && generatedPosts && generatedPosts.length > 0) {
      console.log(`🎯 Posts chargés (${generatedPosts.length}), tentative de scroll vers: ${modifiedPostId}`);
      
      // Multiple tentatives avec délais croissants
      const scrollAttempts = [500, 1000, 1500, 2500]; // Délais en ms
      let attemptIndex = 0;
      
      const attemptScroll = () => {
        console.log(`🔍 Recherche du post avec ID: ${modifiedPostId}`);
        
        // D'abord lister tous les éléments avec data-post-id pour diagnostic
        const allPostElements = document.querySelectorAll('[data-post-id]');
        console.log(`📋 Total éléments trouvés avec data-post-id: ${allPostElements.length}`);
        
        if (allPostElements.length > 0) {
          console.log('📋 IDs trouvés:', Array.from(allPostElements).map(el => el.getAttribute('data-post-id')));
        }
        
        const postElement = document.querySelector(`[data-post-id="${modifiedPostId}"]`);
        
        if (postElement) {
          console.log('✅ Post trouvé, scroll et highlight en cours...');
          
          // Scroll smooth vers le post
          postElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center',
            inline: 'nearest'
          });
          
          // Appliquer l'effet de flash highlight avec classe CSS
          postElement.classList.add('highlight-flash');
          
          // Nettoyer après l'animation
          setTimeout(() => {
            postElement.classList.remove('highlight-flash');
            localStorage.removeItem('modifiedPostId');
            console.log('🎉 Animation terminée, localStorage nettoyé');
          }, 2000);
          
          return true; // Succès
        } else {
          console.log(`⏳ Tentative ${attemptIndex + 1}: Post non trouvé avec ID: ${modifiedPostId}`);
          return false; // Échec
        }
      };
      
      // Première tentative immédiate
      if (!attemptScroll()) {
        // Tentatives avec délais croissants
        const scheduleNextAttempt = () => {
          if (attemptIndex < scrollAttempts.length) {
            setTimeout(() => {
              if (!attemptScroll()) {
                attemptIndex++;
                scheduleNextAttempt();
              } 
            }, scrollAttempts[attemptIndex]);
          } else {
            // Toutes les tentatives ont échoué, essayer un fallback
            console.log('🔄 Tentatives principales échouées, essai de fallback...');
            
            // Fallback: essayer de scroller vers le premier post visible
            setTimeout(() => {
              const anyPostElement = document.querySelector('[data-post-id]');
              if (anyPostElement) {
                console.log('📌 Fallback: Scroll vers le premier post visible');
                anyPostElement.scrollIntoView({ 
                  behavior: 'smooth', 
                  block: 'start',
                  inline: 'nearest'
                });
              }
              localStorage.removeItem('modifiedPostId');
            }, 1000);
          }
        };
        
        scheduleNextAttempt();
      }
    }
  }, [generatedPosts, activeTab]); // Dépendances : se déclenche quand les posts sont chargés ET qu'on est sur l'onglet Posts

  // Préchargement des vignettes à la connexion
  useEffect(() => {
    if (isAuthenticated) {
      console.log('🚀 Préchargement des vignettes en arrière-plan...');
      
      // Préchargement silencieux après connexion
      setTimeout(() => {
        loadPendingContent().then(() => {
          console.log('✅ Vignettes préchargées avec succès');
        }).catch(err => {
          console.log('⚠️ Erreur préchargement:', err);
        });
      }, 1000); // 1 seconde après connexion
    }
  }, [isAuthenticated]);

  // Update refs when fileCustomData changes (to preserve field values when month changes)
  useEffect(() => {
    selectedFiles.forEach((_, index) => {
      if (uploadTitleRefs.current[index] && fileCustomData[index]?.title !== undefined) {
        uploadTitleRefs.current[index].value = fileCustomData[index].title;
      }
      if (uploadContextRefs.current[index] && fileCustomData[index]?.context !== undefined) {
        uploadContextRefs.current[index].value = fileCustomData[index].context;
      }
    });
  }, [fileCustomData, selectedFiles]);
  
  // Monthly library organization states
  const [monthlyLibraryView, setMonthlyLibraryView] = useState(true); // Switch between monthly and all view
  // Initialize collapsed months - collapse all except current month (simple initialization)
  const getInitialCollapsedMonths = () => {
    const collapsed = new Set();
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth(); // 0-based
    const monthNames = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ];
    const currentMonthKey = `${monthNames[currentMonth]}_${currentYear}`;
    
    // Generate all possible month keys for 6 months + archives and collapse them except current
    for (let i = 0; i < 6; i++) {
      const targetMonth = (currentMonth + i) % 12;
      const targetYear = currentYear + Math.floor((currentMonth + i) / 12);
      const monthKey = `${monthNames[targetMonth]}_${targetYear}`;
      
      // Collapse all except current month (we'll handle important notes later)
      if (monthKey !== currentMonthKey) {
        collapsed.add(monthKey);
      }
    }
    
    // Collapse archive months
    for (let i = 1; i <= 6; i++) {
      const targetMonth = (currentMonth - i + 12) % 12;
      const targetYear = currentMonth - i < 0 ? currentYear - 1 : currentYear;
      const monthKey = `${monthNames[targetMonth]}_${targetYear}`;
      collapsed.add(monthKey);
    }
    
    return collapsed;
  };

  const [collapsedMonths, setCollapsedMonths] = useState(() => getInitialCollapsedMonths()); // Track collapsed months

  // Update collapsed states when notes change (to handle important notes)
  useEffect(() => {
    if (!Array.isArray(notes) || notes.length === 0) return;

    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth(); // 0-based
    const monthNames = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ];

    // Find sections with important notes (high priority)
    const sectionsWithImportantNotes = new Set();
    notes.forEach(note => {
      if (note.priority === 'high') {
        if (note.is_monthly_note) {
          sectionsWithImportantNotes.add('always_valid');
        } else if (note.note_month && note.note_year) {
          const noteMonthKey = `${monthNames[note.note_month - 1]}_${note.note_year}`;
          sectionsWithImportantNotes.add(noteMonthKey);
        }
      }
    });

    // Open sections with important notes
    if (sectionsWithImportantNotes.size > 0) {
      setCollapsedMonths(prev => {
        const newCollapsed = new Set(prev);
        sectionsWithImportantNotes.forEach(key => {
          newCollapsed.delete(key);
        });
        return newCollapsed;
      });
    }
  }, [notes]);

  const [selectedMonth, setSelectedMonth] = useState(null); // For new uploads
  const [uploadMode, setUploadMode] = useState('single'); // 'single' or 'carousel'
  const [isUploadingToMonth, setIsUploadingToMonth] = useState(false);
  const [isCarouselMode, setIsCarouselMode] = useState(false); // Track if we're in carousel mode
  
  // Pixabay save choice modal states
  const [showPixabaySaveModal, setShowPixabaySaveModal] = useState(false);
  const [selectedPixabayImage, setSelectedPixabayImage] = useState(null);
  const [isSavingPixabayImage, setIsSavingPixabayImage] = useState(null);
  
  // Refs pour inputs non-contrôlés (évite bug clavier mobile)
  const pixabayTitleRef = useRef(null);
  const pixabayContextRef = useRef(null);
  
  // Refs for direct DOM manipulation to avoid re-renders
  const titleInputRef = useRef(null);
  const contentInputRef = useRef(null);
  const priorityInputRef = useRef(null);
  const contextTextareaRef = useRef(null); // Ref pour éviter bug clavier virtuel
  const pixabaySearchRef = useRef(null); // Ref pour recherche Pixabay
  const isPermanentCheckboxRef = useRef(null); // Note permanente
  const targetMonthKeyRef = useRef(null); // Mois cible unifié (clé comme "octobre_2025")
  const previewTitleInputRef = useRef(null); // Pour le titre dans l'aperçu
  
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

  const loadPendingContent = async (append = false) => {
    try {
      const page = append ? contentPage + 1 : 0;
      const limit = 24; // Charge par batches de 24
      
      const response = await axios.get(`${API}/content/pending`, {
        params: { 
          limit,
          offset: page * limit 
        },
        headers: { 
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        }
      });
      
      const data = response.data;
      
      // Mettre à jour le total
      setTotalContentCount(data.total || 0);
      
      if (append) {
        // Ajouter à la liste existante
        setPendingContent(prev => [...prev, ...(data.content || [])]);
        setContentPage(page);
      } else {
        // Remplacer la liste
        setPendingContent(data.content || []);
        setContentPage(0);
      }
      
      // Update total count for display
      setTotalContentCount(data.total || 0);
      
    } catch (error) {
      console.error('Error loading pending content:', error);
    }
  };
  
  // Load content for specific months (optimized loading)
  const loadContentForMonths = useCallback(async (monthKeys) => {
    // This will be implemented to load only specific months
    console.log(`📥 Loading content for months: ${monthKeys.join(', ')}`);
    await loadPendingContent();
  }, [loadPendingContent]);

  // Fonction de tri des notes selon les spécifications périodiques
  const sortNotes = useCallback((notes) => {
    if (!Array.isArray(notes)) return [];
    
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth() + 1; // getMonth() returns 0-11, we need 1-12
    const currentYear = currentDate.getFullYear();
    
    return notes.sort((a, b) => {
      // 1. Notes "toujours valides" (mensuelles) en premier
      if (a.is_monthly_note && !b.is_monthly_note) return -1;
      if (!a.is_monthly_note && b.is_monthly_note) return 1;
      
      // 2. Entre deux notes mensuelles, trier par date de création (plus récent en premier)
      if (a.is_monthly_note && b.is_monthly_note) {
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB - dateA;
      }
      
      // 3. Entre deux notes spécifiques, trier chronologiquement par mois/année (plus proche en premier)
      if (!a.is_monthly_note && !b.is_monthly_note) {
        // Notes sans mois/année spécifiés vont à la fin
        if (!a.note_month && !a.note_year && (b.note_month || b.note_year)) return 1;
        if ((a.note_month || a.note_year) && !b.note_month && !b.note_year) return -1;
        if (!a.note_month && !a.note_year && !b.note_month && !b.note_year) {
          // Trier par date de création si aucune n'a de mois/année
          const dateA = new Date(a.created_at || 0);
          const dateB = new Date(b.created_at || 0);
          return dateB - dateA;
        }
        
        // Calculer la "distance" temporelle depuis maintenant
        const getMonthDistance = (note) => {
          if (!note.note_month || !note.note_year) return Infinity;
          
          const noteDate = new Date(note.note_year, note.note_month - 1, 1);
          const currentDateStart = new Date(currentYear, currentMonth - 1, 1);
          
          // Calcul en mois depuis maintenant
          const monthDiff = (noteDate.getFullYear() - currentDateStart.getFullYear()) * 12 + 
                           (noteDate.getMonth() - currentDateStart.getMonth());
          
          // Les dates passées ont une distance négative, les futures positive
          // On veut les plus proches en premier, donc on utilise la valeur absolue
          // mais on favorise les dates futures (distance positive plus petite)
          if (monthDiff >= 0) {
            return monthDiff; // Dates futures ou actuelles
          } else {
            return Math.abs(monthDiff) + 1000; // Dates passées (repoussées à la fin)
          }
        };
        
        const distanceA = getMonthDistance(a);
        const distanceB = getMonthDistance(b);
        
        if (distanceA !== distanceB) {
          return distanceA - distanceB; // Plus proche = distance plus petite
        }
        
        // Si même distance, trier par date de création
        const dateA = new Date(a.created_at || 0);
        const dateB = new Date(b.created_at || 0);
        return dateB - dateA;
      }
      
      // Fallback: trier par date de création
      const dateA = new Date(a.created_at || 0);
      const dateB = new Date(b.created_at || 0);
      return dateB - dateA;
    });
  }, []);

  // Monthly content organization utilities
  const getMonthlyContentData = useCallback(() => {
    if (!Array.isArray(pendingContent)) return { currentAndFuture: {}, archives: {} };
    
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth(); // 0-based (September = 8)
    
    // Generate current month and next 5 months dynamically (6 months total)
    const getCurrentAndFutureMonths = () => {
      const months = {};
      const monthNames = [
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
      ];
      
      for (let i = 0; i < 6; i++) {
        const targetMonth = (currentMonth + i) % 12;
        const targetYear = currentYear + Math.floor((currentMonth + i) / 12);
        const monthKey = `${monthNames[targetMonth]}_${targetYear}`;
        
        months[monthKey] = {
          label: `${monthNames[targetMonth].charAt(0).toUpperCase() + monthNames[targetMonth].slice(1)} ${targetYear}`,
          month: targetMonth,
          year: targetYear,
          isCurrent: i === 0,
          isFuture: i > 0,
          content: [],
          order: i
        };
      }
      return months;
    };
    
    // Generate archive months (past months)
    const getArchiveMonths = () => {
      const months = {};
      const monthNames = [
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
      ];
      
      // Generate last 6 months before current month
      for (let i = 1; i <= 6; i++) {
        const targetMonth = (currentMonth - i + 12) % 12;
        // Correct year calculation for past months
        const targetYear = currentMonth - i < 0 ? currentYear - 1 : currentYear;
        const monthKey = `${monthNames[targetMonth]}_${targetYear}`;
        
        months[monthKey] = {
          label: `${monthNames[targetMonth].charAt(0).toUpperCase() + monthNames[targetMonth].slice(1)} ${targetYear}`,
          month: targetMonth,
          year: targetYear,
          isPast: true,
          content: [],
          order: -i, // Negative for reverse chronological order
          shouldLoadThumbnails: i <= 2 || !collapsedMonths.has(monthKey) // Load thumbnails for first 2 months or when expanded
        };
      }
      return months;
    };
    
    const currentAndFuture = getCurrentAndFutureMonths();
    const archives = getArchiveMonths();
    const allMonths = { ...currentAndFuture, ...archives };
    
    // Categorize and group content by month
    const carouselGroups = {}; // Track carousel groups
    
    pendingContent.forEach(item => {
      // Check if content has explicit month attribution
      const attributedMonth = item.attributed_month;
      let targetMonth = null;
      
      if (attributedMonth && allMonths[attributedMonth]) {
        targetMonth = attributedMonth;
      } else {
        // For existing content without attribution, distribute into archive months
        const createdDate = new Date(item.created_at || item.uploaded_at);
        const itemMonth = createdDate.getMonth();
        const itemYear = createdDate.getFullYear();
        
        // Try to match with existing months or default to first archive month
        const monthNames = [
          'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
          'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
        ];
        
        const itemMonthKey = `${monthNames[itemMonth]}_${itemYear}`;
        if (allMonths[itemMonthKey]) {
          targetMonth = itemMonthKey;
        } else {
          // Default to first archive month (last month)
          const firstArchiveKey = Object.keys(archives).sort((a, b) => archives[b].order - archives[a].order)[0];
          targetMonth = firstArchiveKey;
        }
      }
      
      if (!targetMonth) return;
      
      // Handle carousel grouping
      if (item.upload_type === 'carousel' && item.carousel_id) {
        const carouselKey = `${item.carousel_id}_${targetMonth}`;
        
        if (!carouselGroups[carouselKey]) {
          carouselGroups[carouselKey] = {
            id: item.carousel_id,
            type: 'carousel',
            count: 0,
            images: [],
            title: item.common_title || item.title || 'Carrousel',
            context: item.context || '',
            created_at: item.created_at,
            upload_type: 'carousel',
            attributed_month: targetMonth,
            // Use first image for display
            thumb_url: item.thumb_url,
            source: item.source || 'upload'
          };
        }
        
        carouselGroups[carouselKey].count++;
        carouselGroups[carouselKey].images.push(item);
        
      } else {
        // Regular content (non-carousel)
        allMonths[targetMonth].content.push(item);
      }
    });
    
    // Add carousel groups as single items to their respective months
    Object.values(carouselGroups).forEach(carouselGroup => {
      const targetMonth = carouselGroup.attributed_month;
      if (allMonths[targetMonth]) {
        allMonths[targetMonth].content.push(carouselGroup);
      }
    });
    
    // Update content in respective objects
    Object.keys(currentAndFuture).forEach(key => {
      currentAndFuture[key].content = allMonths[key].content;
    });
    Object.keys(archives).forEach(key => {
      archives[key].content = allMonths[key].content;
    });
    
    return { currentAndFuture, archives };
  }, [pendingContent]);

  // Get available months for upload selector (current + 5 future months)
  const getUploadMonthOptions = useCallback(() => {
    const { currentAndFuture } = getMonthlyContentData();
    return Object.entries(currentAndFuture)
      .sort(([, a], [, b]) => a.order - b.order)
      .map(([key, info]) => ({ key, label: info.label }));
  }, [getMonthlyContentData]);

  // Get available months for notes selector (same logic as uploads but independent)
  const getNotesMonthOptions = useCallback(() => {
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth(); // 0-based
    const monthNames = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ];
    
    const options = [];
    for (let i = 0; i < 6; i++) {
      const targetMonth = (currentMonth + i) % 12;
      const targetYear = currentYear + Math.floor((currentMonth + i) / 12);
      const monthKey = `${monthNames[targetMonth]}_${targetYear}`;
      const label = `${monthNames[targetMonth].charAt(0).toUpperCase() + monthNames[targetMonth].slice(1)} ${targetYear}`;
      
      options.push({ key: monthKey, label });
    }
    
    return options;
  }, []);

  // Get default month (closest/current month)
  const getDefaultMonth = useCallback(() => {
    const options = getUploadMonthOptions();
    return options.length > 0 ? options[0].key : null;
  }, [getUploadMonthOptions]);

  // Monthly notes organization utilities - same logic as content
  const getMonthlyNotesData = useCallback(() => {
    if (!Array.isArray(notes)) return { alwaysValid: [], currentAndFuture: {}, archives: {} };
    
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth(); // 0-based (September = 8)
    
    // Generate current month and next 5 months dynamically (6 months total - same as content)
    const getCurrentAndFutureMonths = () => {
      const months = {};
      const monthNames = [
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
      ];
      
      for (let i = 0; i < 6; i++) {
        const targetMonth = (currentMonth + i) % 12;
        const targetYear = currentYear + Math.floor((currentMonth + i) / 12);
        const monthKey = `${monthNames[targetMonth]}_${targetYear}`;
        
        months[monthKey] = {
          label: `${monthNames[targetMonth].charAt(0).toUpperCase() + monthNames[targetMonth].slice(1)} ${targetYear}`,
          month: targetMonth,
          year: targetYear,
          isCurrent: i === 0,
          isFuture: i > 0,
          notes: [],
          order: i
        };
      }
      return months;
    };
    
    // Generate archive months (past months) - same as content
    const getArchiveMonths = () => {
      const months = {};
      const monthNames = [
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
      ];
      
      // Generate last 6 months before current month
      for (let i = 1; i <= 6; i++) {
        const targetMonth = (currentMonth - i + 12) % 12;
        // Correct year calculation for past months
        const targetYear = currentMonth - i < 0 ? currentYear - 1 : currentYear;
        const monthKey = `${monthNames[targetMonth]}_${targetYear}`;
        
        months[monthKey] = {
          label: `${monthNames[targetMonth].charAt(0).toUpperCase() + monthNames[targetMonth].slice(1)} ${targetYear}`,
          month: targetMonth,
          year: targetYear,
          isPast: true,
          notes: [],
          order: -i // Negative for reverse chronological order
        };
      }
      return months;
    };
    
    const currentAndFuture = getCurrentAndFutureMonths();
    const archives = getArchiveMonths();
    const allMonths = { ...currentAndFuture, ...archives };
    
    // Always valid notes (monthly notes)
    const alwaysValid = [];
    
    // Categorize notes by month
    notes.forEach(note => {
      // Always valid notes (monthly notes)
      if (note.is_monthly_note) {
        alwaysValid.push(note);
        return;
      }
      
      // Notes with specific month/year
      if (note.note_month && note.note_year) {
        const monthNames = [
          'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
          'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
        ];
        
        const noteMonthKey = `${monthNames[note.note_month - 1]}_${note.note_year}`;
        if (allMonths[noteMonthKey]) {
          allMonths[noteMonthKey].notes.push(note);
        } else {
          // If month doesn't exist in our range, add to first archive month
          const firstArchiveKey = Object.keys(archives).sort((a, b) => archives[b].order - archives[a].order)[0];
          if (firstArchiveKey) {
            allMonths[firstArchiveKey].notes.push(note);
          }
        }
      } else {
        // Notes without specific date go to current month
        const currentMonthKey = Object.keys(currentAndFuture).find(key => currentAndFuture[key].isCurrent);
        if (currentMonthKey) {
          allMonths[currentMonthKey].notes.push(note);
        }
      }
    });
    
    // Update notes in respective objects
    Object.keys(currentAndFuture).forEach(key => {
      currentAndFuture[key].notes = allMonths[key].notes;
    });
    Object.keys(archives).forEach(key => {
      archives[key].notes = allMonths[key].notes;
    });
    
    return { alwaysValid, currentAndFuture, archives };
  }, [notes]);

  // Toggle month collapse state with conditional loading
  const toggleMonthCollapse = useCallback(async (monthKey) => {
    const wasCollapsed = collapsedMonths.has(monthKey);
    
    setCollapsedMonths(prev => {
      const newSet = new Set(prev);
      if (newSet.has(monthKey)) {
        newSet.delete(monthKey);
      } else {
        newSet.add(monthKey);
      }
      return newSet;
    });
    
    // If expanding an archive month for the first time, load its content
    if (wasCollapsed) {
      const { archives } = getMonthlyContentData();
      if (archives[monthKey] && archives[monthKey].isPast) {
        console.log(`📥 Loading content for archive month: ${monthKey}`);
        // Here we would load content specifically for this month
        // For now, we'll refresh all content as the backend doesn't support month-specific loading yet
        await loadPendingContent();
      }
    }
  }, [collapsedMonths, getMonthlyContentData, loadPendingContent]);

  const loadNotes = async () => {
    try {
      const response = await axios.get(`${API}/notes`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });  
      
      const notesData = response.data.notes || response.data || [];
      // Appliquer le tri personnalisé pour les notes périodiques
      const sortedNotes = sortNotes(notesData);
      setNotes(sortedNotes);
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
  // Convert month key to month/year for backend
  const parseMonthKey = useCallback((monthKey) => {
    if (!monthKey) return { month: null, year: null };
    
    const monthNames = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ];
    
    const [monthName, year] = monthKey.split('_');
    const monthIndex = monthNames.indexOf(monthName);
    
    return {
      month: monthIndex >= 0 ? monthIndex + 1 : null, // Backend expects 1-based months
      year: year ? parseInt(year) : null
    };
  }, []);

  // Convert month/year to month key for UI
  const buildMonthKey = useCallback((month, year) => {
    if (!month || !year) return '';
    
    const monthNames = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ];
    
    const monthName = monthNames[month - 1]; // month is 1-based from backend
    return `${monthName}_${year}`;
  }, []);

  const getCurrentFormValues = useCallback(() => {
    const isMonthlyNote = isPermanentCheckboxRef.current?.checked || false;
    const monthKey = targetMonthKeyRef.current?.value || '';
    const { month, year } = parseMonthKey(monthKey);
    
    return {
      title: titleInputRef.current?.value || '',
      content: contentInputRef.current?.value || '',
      priority: priorityInputRef.current?.value || 'normal',
      is_monthly_note: isMonthlyNote,
      note_month: isMonthlyNote ? null : month,
      note_year: isMonthlyNote ? null : year
    };
  }, [parseMonthKey]);

  // Set form values in DOM
  const setFormValues = useCallback((title = '', content = '', priority = 'normal', isMonthlyNote = false, noteMonth = null, noteYear = null) => {
    if (titleInputRef.current) titleInputRef.current.value = title;
    if (contentInputRef.current) contentInputRef.current.value = content;
    if (priorityInputRef.current) {
      priorityInputRef.current.value = priority;
    }
    if (isPermanentCheckboxRef.current) {
      isPermanentCheckboxRef.current.checked = isMonthlyNote;
    }
    
    // Use the unified month selector
    if (targetMonthKeyRef.current) {
      const monthKey = buildMonthKey(noteMonth, noteYear);
      targetMonthKeyRef.current.value = monthKey;
      targetMonthKeyRef.current.disabled = isMonthlyNote;
    }
  }, [buildMonthKey]);

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
          description: formValues.title.trim(), // Le backend utilise 'description' pour le titre
          content: formValues.content.trim(),
          priority: formValues.priority,
          is_monthly_note: formValues.is_monthly_note,
          note_month: formValues.note_month,
          note_year: formValues.note_year
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data) {
          toast.success('Note modifiée avec succès ! ✏️');
          
          // Réinitialiser le formulaire
          setFormValues('', '', 'normal', false, null, null);
          setEditingNoteId(null);
          
          // Recharger les notes avec tri
          await loadNotes();
        }
      } else {
        // Mode création - POST
        const response = await axios.post(`${API}/notes`, {
          description: formValues.title.trim(), // Le backend utilise 'description' pour le titre
          content: formValues.content.trim(),
          priority: formValues.priority,
          is_monthly_note: formValues.is_monthly_note,
          note_month: formValues.note_month,
          note_year: formValues.note_year
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data) {
          toast.success('Note sauvegardée avec succès ! 📝');
          
          // Réinitialiser le formulaire
          setFormValues('', '', 'normal', false, null, null);
          setEditingNoteId(null);
          
          // Recharger les notes avec tri
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
    console.log('🖊️ Édition de la note:', note);
    
    // D'abord définir l'état d'édition
    setEditingNoteId(note.note_id);
    
    // Ensuite remplir les champs avec un délai pour s'assurer que les refs sont prêts
    setTimeout(() => {
      setFormValues(
        note.description || note.title || '', 
        note.content || '', 
        note.priority || 'normal',
        note.is_monthly_note || false,
        note.note_month || null,
        note.note_year || null
      );
      
      console.log('📝 Champs remplis avec:', {
        title: note.description || note.title,
        content: note.content,
        priority: note.priority
      });
      
      // Scroll vers le formulaire après avoir rempli les champs
      setTimeout(() => {
        const titleElement = titleInputRef.current;
        if (titleElement) {
          titleElement.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start',
            inline: 'nearest'
          });
          titleElement.focus();
          console.log('📍 Scroll vers le formulaire effectué');
        }
      }, 200);
    }, 50);
  }, [setFormValues]);

  // Annuler l'édition
  const handleCancelEdit = useCallback(() => {
    setFormValues('', '', 'normal', false, null, null);
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
      
      // Recharger les notes avec tri
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
  
  // VRAIMENT STABLE: Toggle selection mode normal (pas de transition pour l'instant)
  const toggleSelectionMode = useCallback(() => {
    setIsSelectionMode(prev => !prev);
    setSelectedContentIds(new Set()); // Reset selections
  }, []);

  // Callbacks pour les vignettes - DEBUG CHIRURGICAL
  const handleToggleSelectionRef = useRef();
  const handleContentClickRef = useRef();
  
  const handleToggleSelection = useCallback((contentId) => {
    setSelectedContentIds(prev => {
      const newSelection = new Set(prev);
      if (newSelection.has(contentId)) {
        newSelection.delete(contentId);
      } else {
        newSelection.add(contentId);
      }
      return newSelection;
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

  // Supprimer les contenus sélectionnés (optimisé avec batch delete)
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

    try {
      console.log('🚀 Starting optimized batch delete for', selectedContentIds.size, 'items');
      const startTime = Date.now();
      
      // Utiliser l'endpoint de suppression en lot optimisé
      const response = await axios.delete(`${API}/content/batch`, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: {
          content_ids: Array.from(selectedContentIds)
        }
      });

      const endTime = Date.now();
      const duration = endTime - startTime;
      
      console.log(`✅ Batch delete completed in ${duration}ms`);
      
      const { deleted_count, requested_count } = response.data;
      
      if (deleted_count === requested_count) {
        toast.success(`${deleted_count} contenu(s) supprimé(s) avec succès ! 🗑️`);
      } else {
        toast.success(`${deleted_count} sur ${requested_count} contenu(s) supprimé(s)`);
      }

      // Refresh the content list and clear selection
      setSelectedContentIds(new Set());
      setIsSelectionMode(false);
      await loadPendingContent();

    } catch (error) {
      console.error('Error in optimized batch delete:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la suppression: ${errorMessage}`);
    } finally {
      setIsDeletingContent(false);
    }
  };

  const handleContentClick = useCallback((content) => {
    if (isSelectionMode) {
      handleToggleSelection(content.id);
    } else {
      setPreviewContent(content);
      setTimeout(() => {
        if (contextTextareaRef.current) {
          contextTextareaRef.current.value = content.context || '';
        }
        if (previewTitleInputRef.current) {
          const titleValue = content.title?.trim() || '';
          previewTitleInputRef.current.value = titleValue;
        }
      }, 100);
    }
  }, [isSelectionMode, handleToggleSelection]);
  
  // DEBUG: Tracker si les callbacks changent de référence
  if (handleToggleSelectionRef.current !== handleToggleSelection) {
    console.log('🔄 handleToggleSelection callback reference changed!');
    handleToggleSelectionRef.current = handleToggleSelection;
  }
  
  if (handleContentClickRef.current !== handleContentClick) {
    console.log('🔄 handleContentClick callback reference changed!');
    handleContentClickRef.current = handleContentClick;
  }

  // VRAIMENT STABLE: Fermeture aperçu - ZÉRO dépendance
  const handleClosePreview = useCallback(() => {
    setPreviewContent(null);
    // Vider les champs après un délai pour éviter re-render cascade
    setTimeout(() => {
      if (contextTextareaRef.current) {
        contextTextareaRef.current.value = '';
      }
      if (previewTitleInputRef.current) {
        previewTitleInputRef.current.value = '';
      }
    }, 50);
  }, []); // ZÉRO dépendances = vraiment stable // ZÉRO dépendances = vraiment stable










  // Handle content title updates
  const handleContentTitleUpdate = useCallback((contentId, newTitle) => {
    // Update the title in pendingContent state
    setPendingContent(prevContent => 
      prevContent.map(content => 
        content.id === contentId 
          ? { ...content, filename: newTitle }
          : content
      )
    );
  }, []);

  // Sauvegarder le contexte d'un contenu ET le titre s'il a été modifié
  const handleSaveContext = async () => {
    if (!previewContent) return;

    // Lire la valeur directement du DOM pour contexte ET titre (même logique)
    const contextValue = contextTextareaRef.current?.value || '';
    const titleValue = previewTitleInputRef.current?.value || '';

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté');
      return;
    }

    setIsSavingContext(true);

    try {
      // 1. Sauvegarder le contexte (logique existante)
      await axios.put(`${API}/content/${previewContent.id}/context`, {
        context: contextValue.trim()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // 2. Sauvegarder le titre (MÊME LOGIQUE que le contexte)
      await axios.put(`${API}/content/${previewContent.id}/title`, {
        title: titleValue.trim()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('✅ Titre et contexte sauvegardés:', { title: titleValue.trim(), context: contextValue.trim() });

      // 3. Mettre à jour l'état local avec les nouvelles valeurs
      const updatedContent = { 
        ...previewContent, 
        title: titleValue.trim(),
        context: contextValue.trim()
      };
      setPreviewContent(updatedContent);
      
      // 4. Mettre à jour aussi dans pendingContent
      setPendingContent(prevContent => 
        prevContent.map(content => 
          content.id === previewContent.id 
            ? { ...content, title: titleValue.trim(), context: contextValue.trim() }
            : content
        )
      );

      toast.success('Contenu mis à jour avec succès !');
      
      // Fermer automatiquement la modal après sauvegarde
      setTimeout(() => {
        handleClosePreview();
      }, 1500);
      
    } catch (error) {
      console.error('❌ Erreur lors de la sauvegarde:', error);
      const errorMessage = error.response?.data?.detail || 'Erreur lors de la sauvegarde';
      toast.error(errorMessage);
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
  // Fonction pour supprimer tous les posts générés
  const handleDeleteAllPosts = async () => {
    const confirmed = window.confirm(
      "⚠️ Êtes-vous sûr de vouloir supprimer TOUS les posts générés ?\n\nCette action est irréversible et supprimera :\n- Tous les posts du calendrier\n- Tous les carrousels créés\n- Les marquages 'utilisé' sur vos images"
    );
    
    if (!confirmed) return;
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté pour supprimer les posts');
      return;
    }
    
    try {
      setIsGeneratingPosts(true); // Réutiliser l'état de loading
      
      const response = await axios.delete(`${API}/posts/generated/all`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        const deletedCount = response.data.deleted_posts || 0;
        const resetMediaCount = response.data.reset_media_flags || 0;
        
        toast.success(`✅ Suppression réussie !\n${deletedCount} posts supprimés\n${resetMediaCount} images remises à "non utilisées"`);
        
        // Recharger les posts et contenus pour refléter les changements
        setGeneratedPosts([]);
        setPostsByMonth({});
        
        // Force reload from server
        await loadGeneratedPosts();
        await loadPendingContent(); // Reload pour voir les badges verts retirés
        
        // Clear any cached state
        setSelectedPost(null);
        setShowImageAttachModal(false);
        
        console.log('✅ All posts deleted and UI refreshed');
      }
      
    } catch (error) {
      console.error('❌ Error deleting posts:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la suppression : ${errorMessage}`);
    } finally {
      setIsGeneratingPosts(false);
    }
  };

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
        
        // Organiser les posts par mois
        const postsByMonth = organizePosts(response.data.posts);
        setPostsByMonth(postsByMonth);
      }
    } catch (error) {
      console.error('Error loading generated posts:', error);
    }
  };

  // Organiser les posts par mois
  const organizePosts = (posts) => {
    const grouped = {};
    
    posts.forEach(post => {
      if (!post.scheduled_date) return;
      
      const date = new Date(post.scheduled_date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthName = date.toLocaleDateString('fr-FR', { 
        month: 'long', 
        year: 'numeric' 
      });
      
      if (!grouped[monthKey]) {
        grouped[monthKey] = {
          name: monthName,
          posts: []
        };
      }
      
      grouped[monthKey].posts.push(post);
    });
    
    // Trier les posts dans chaque mois par date
    Object.keys(grouped).forEach(monthKey => {
      grouped[monthKey].posts.sort((a, b) => 
        new Date(a.scheduled_date) - new Date(b.scheduled_date)
      );
    });
    
    return grouped;
  };

  // Fonctions de gestion des posts
  const handleValidatePost = (post) => {
    // Pour l'instant, ferme juste l'aperçu
    setSelectedPost(null);
    toast.success('Post validé ! 👍');
  };

  const handleModifyPost = async (post, modificationRequestValue) => {
    if (!modificationRequestValue?.trim()) {
      toast.error('Veuillez saisir une demande de modification');
      return;
    }

    if (!post?.id) {
      toast.error('Erreur: ID du post manquant');
      return;
    }

    setIsModifyingPost(true);
    const token = localStorage.getItem('access_token');

    if (!token) {
      toast.error('Session expirée, veuillez vous reconnecter');
      setIsModifyingPost(false);
      return;
    }

    try {
      console.log(`🔄 Modification du post ${post.id}:`, modificationRequestValue.trim());
      
      const response = await axios.put(
        `${API}/posts/${post.id}/modify`,
        { modification_request: modificationRequestValue.trim() },
        { 
          headers: { Authorization: `Bearer ${token}` },
          timeout: 30000 // 30 secondes timeout
        }
      );

      console.log('📡 Réponse du serveur:', response.data);

      if (response.data?.success) {
        console.log('✅ Modification réussie, préparation du rechargement...');
        toast.success('✅ Post modifié avec succès ! Actualisation en cours...');
        
        // Stocker l'ID du post modifié pour repositionnement sécurisé
        try {
          localStorage.setItem('modifiedPostId', post.id);
          localStorage.setItem('returnToPostsTab', 'true');
          console.log(`💾 Post ID sauvegardé pour auto-scroll: ${post.id}`);
        } catch (storageError) {
          console.warn('⚠️ Erreur localStorage, scroll automatique désactivé:', storageError);
        }
        
        // Fermer la modal et nettoyer les refs
        setSelectedPost(null);
        if (modificationRequestRef.current) {
          modificationRequestRef.current.value = '';
        }
        
        // Attendre un peu pour que l'utilisateur voie le toast, puis recharger
        console.log('⏳ Rechargement programmé dans 1.5 secondes...');
        setTimeout(() => {
          try {
            console.log('🔄 Rechargement de la page en cours...');
            window.location.reload();
          } catch (reloadError) {
            console.error('❌ Erreur lors du rechargement:', reloadError);
            // Fallback: recharger les posts manuellement
            loadGeneratedPosts();
            setActiveTab('posts');
          }
        }, 1500);
      } else {
        console.log('❌ Échec de la modification, response.data:', response.data);
        toast.error('❌ Erreur: Réponse invalide du serveur');
        setIsModifyingPost(false);
      }
      
    } catch (error) {
      console.error('❌ Erreur lors de la modification du post:', error);
      
      // Messages d'erreur spécifiques
      let errorMessage = 'Erreur lors de la modification du post';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Timeout: La requête a pris trop de temps';
      } else if (error.response?.status === 401) {
        errorMessage = 'Session expirée, veuillez vous reconnecter';
      } else if (error.response?.status === 404) {
        errorMessage = 'Post non trouvé';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
      setIsModifyingPost(false);
    }
    // Note: setIsModifyingPost(false) n'est pas appelé en cas de succès car on recharge la page
  };

  // Render des posts par mois
  const renderPostsByMonth = () => {
    const sortedMonths = Object.keys(postsByMonth).sort().reverse(); // Mois les plus récents en premier
    
    return sortedMonths.map(monthKey => {
      const monthData = postsByMonth[monthKey];
      const isCollapsed = collapsedPostMonths[monthKey];
      
      return (
        <div key={monthKey} className="space-y-4">
          {/* En-tête du mois */}
          <div 
            className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-blue-50 rounded-xl border border-emerald-200 cursor-pointer hover:bg-gradient-to-r hover:from-emerald-100 hover:to-blue-100 transition-all"
            onClick={() => setCollapsedPostMonths(prev => ({
              ...prev,
              [monthKey]: !prev[monthKey]
            }))}
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-xl flex items-center justify-center">
                <Calendar className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-800 capitalize">
                  {monthData.name}
                </h3>
                <p className="text-sm text-gray-600">
                  {monthData.posts.length} post{monthData.posts.length > 1 ? 's' : ''} programmé{monthData.posts.length > 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <ChevronDown 
              className={`w-6 h-6 text-gray-500 transition-transform duration-200 ${
                isCollapsed ? 'rotate-180' : ''
              }`} 
            />
          </div>

          {/* Posts du mois */}
          {!isCollapsed && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {monthData.posts.map((post, index) => (
                <div key={post.id || index} data-post-id={post.id}>
                  <PostThumbnail
                    key={post.id || index}
                    post={post}
                    onClick={() => setSelectedPost(post)}
                    onAddImage={handleAddImageToPost}
                    onModifyImage={handleModifyImagePost}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      );
    });
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

  // Fonctions de déplacement de contenu
  const handleMoveContent = (content) => {
    setContentToMove(content);
    setShowMoveModal(true);
  };

  // Fonction pour sélectionner des fichiers (utilisée dans ImageAttachmentContent)
  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    
    if (files.length === 0) {
      setSelectedFiles([]);
      return;
    }
    
    // Validation : max 10 fichiers pour les posts
    if (files.length > 10) {
      toast.error('Maximum 10 fichiers autorisés pour un post');
      return;
    }
    
    console.log(`📁 Selected ${files.length} files for post attachment`);
    setSelectedFiles(files);
  };

  // Fonction pour supprimer un fichier sélectionné 
  const handleRemoveSelectedFile = (indexToRemove) => {
    const newFiles = selectedFiles.filter((_, index) => index !== indexToRemove);
    setSelectedFiles(newFiles);
    console.log(`🗑️ Removed file at index ${indexToRemove}, ${newFiles.length} files remaining`);
  };

  // Fonction spécialisée pour uploader des fichiers depuis les posts
  const uploadFilesForPost = async (files, postTitle, postText) => {
    if (!files || files.length === 0) return [];
    
    console.log(`🎯 Uploading ${files.length} files for post: "${postTitle}"`);
    
    try {
      setIsUploading(true);
      
      const formData = new FormData();
      
      // Ajouter les fichiers
      files.forEach(file => {
        formData.append('files', file);
      });
      
      // Déterminer le type d'upload et les métadonnées
      const currentMonth = getDefaultMonth(); // Utiliser le mois courant
      formData.append('attributed_month', currentMonth);
      
      if (files.length > 1) {
        // Multiple fichiers = carrousel avec métadonnées partagées
        formData.append('upload_type', 'carousel');
        formData.append('common_title', postTitle);
        formData.append('common_context', postText);
        console.log(`🎠 Creating carousel with ${files.length} files for post`);
      } else {
        // Single fichier
        formData.append('upload_type', 'post_single');
      }
      
      const response = await axios.post(`${API}/content/batch-upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      console.log(`✅ Post upload response:`, response.data);
      
      // Pour un seul fichier, mettre à jour les métadonnées individuellement
      if (files.length === 1 && response.data.created && response.data.created.length > 0) {
        const createdItem = response.data.created[0];
        
        try {
          // Mettre à jour le titre
          await axios.put(`${API}/content/${createdItem.id}/title`, {
            title: postTitle
          }, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          
          // Mettre à jour le contexte
          await axios.put(`${API}/content/${createdItem.id}/context`, {
            context: postText
          }, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          });
        } catch (updateError) {
          console.warn('Failed to update post file metadata:', updateError);
        }
      }
      
      // Recharger le contenu
      await loadPendingContent();
      
      return response.data.created || [];
      
    } catch (error) {
      console.error('❌ Post upload error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de l'upload: ${errorMessage}`);
      return [];
    } finally {
      setIsUploading(false);
    }
  };

  // Fonction pour ajouter une image à un post (ouvre modal d'attachement)
  const handleAddImageToPost = (post) => {
    console.log(`🖼️ Opening image attachment modal for post: ${post.id}`);
    setPostToAttachImage(post);
    setImageAttachmentMode('add'); // Mode ajout
    setAttachImageTab('upload'); // Commencer par l'onglet upload par défaut pour ajouter
    setShowImageAttachModal(true);
  };

  // Fonction pour modifier une image d'un post (ouvre modal d'attachement)
  const handleModifyImagePost = (post) => {
    console.log(`✏️ Opening image modification modal for post: ${post.id}`);
    setPostToAttachImage(post);
    setImageAttachmentMode('modify'); // Mode modification
    setAttachImageTab('library'); // Commencer par l'onglet bibliothèque pour modifier
    setShowImageAttachModal(true);
  };

  const attachImageToPost = async (imageSource, imageData) => {
    if (!postToAttachImage) return;

    setIsAttachingImage(true);
    const token = localStorage.getItem('access_token');

    try {
      const requestBody = {
        image_source: imageSource,
        ...imageData
      };

      const response = await axios.put(
        `${API}/posts/${postToAttachImage.id}/attach-image`,
        requestBody,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success(`🖼️ ${response.data.message}`);
      
      // Forcer le rechargement du cache des images
      if (window.performance && window.performance.clearResourceTimings) {
        window.performance.clearResourceTimings();
      }
      
      // Recharger les posts
      await loadGeneratedPosts();
      
      // Fermer la modal
      setShowImageAttachModal(false);
      setPostToAttachImage(null);
      
    } catch (error) {
      console.error('Error attaching image:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de l'ajout d'image: ${errorMessage}`);
    } finally {
      setIsAttachingImage(false);
    }
  };

  const moveContentToMonth = async (targetMonth) => {
    if (!contentToMove || !targetMonth) return;

    setIsMovingContent(true);
    const token = localStorage.getItem('access_token');

    try {
      const response = await axios.put(
        `${API}/content/${contentToMove.id}/move`,
        { target_month: targetMonth },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success(`📅 ${response.data.message}`);
      
      // Recharger le contenu
      await loadPendingContent();
      
      // Fermer la modal
      setShowMoveModal(false);
      setContentToMove(null);
      
    } catch (error) {
      console.error('Error moving content:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors du déplacement: ${errorMessage}`);
    } finally {
      setIsMovingContent(false);
    }
  };

  // Social Media Connection Functions
  const loadConnectedAccounts = async () => {
    const token = localStorage.getItem('access_token');
    
    try {
      const response = await axios.get(`${API}/social/connections`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.connections) {
        setConnectedAccounts(response.data.connections);
      }
    } catch (error) {
      console.error('Error loading connected accounts:', error);
    }
  };

  const connectInstagram = async () => {
    setIsConnectingAccount(true);
    setSocialConnectionStatus('Redirection vers Instagram...');
    
    try {
      // Instagram Basic Display API requires special setup
      // For now, let's create a simulated flow for testing
      const redirectUri = `${window.location.origin}/auth/instagram/callback`;
      
      // Instead of using Facebook OAuth, let's create a simple test auth for now
      // In production, this would need proper Instagram Basic Display API setup
      
      // For testing purposes, show a message about Instagram setup
      toast.info('⚠️ Configuration Instagram en cours. Cette fonctionnalité sera bientôt disponible !');
      
      console.log('🔗 Instagram connection would redirect to:', redirectUri);
      
      // Simulate connection for demo
      setTimeout(() => {
        setConnectedAccounts(prev => ({
          ...prev,
          instagram: {
            username: 'demo_account',
            connected_at: new Date().toISOString(),
            is_active: true
          }
        }));
        
        toast.success('✅ Instagram connecté (mode démo)');
        setIsConnectingAccount(false);
        setSocialConnectionStatus('');
      }, 2000);
      
    } catch (error) {
      console.error('Error connecting Instagram:', error);
      toast.error('Erreur lors de la connexion Instagram');
      setIsConnectingAccount(false);
      setSocialConnectionStatus('');
    }
  };

  const disconnectAccount = async (platform) => {
    const token = localStorage.getItem('access_token');
    
    try {
      await axios.delete(`${API}/social/connections/${platform}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setConnectedAccounts(prev => ({
        ...prev,
        [platform]: null
      }));
      
      toast.success(`${platform} déconnecté avec succès`);
    } catch (error) {
      console.error(`Error disconnecting ${platform}:`, error);
      toast.error(`Erreur lors de la déconnexion ${platform}`);
    }
  };

  // Load connected accounts on authentication
  useEffect(() => {
    if (isAuthenticated) {
      loadConnectedAccounts();
    }
  }, [isAuthenticated]);

  // Générer la liste des mois disponibles
  const getAvailableMonths = () => {
    const months = [];
    const now = new Date();
    
    // Derniers 6 mois
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthKey = `${date.toLocaleDateString('fr-FR', { month: 'long' }).toLowerCase()}_${date.getFullYear()}`;
      const monthLabel = date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
      months.push({ key: monthKey, label: monthLabel });
    }
    
    // Prochains 6 mois
    for (let i = 1; i <= 6; i++) {
      const date = new Date(now.getFullYear(), now.getMonth() + i, 1);
      const monthKey = `${date.toLocaleDateString('fr-FR', { month: 'long' }).toLowerCase()}_${date.getFullYear()}`;
      const monthLabel = date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
      months.push({ key: monthKey, label: monthLabel });
    }
    
    return months;
  };

  // Rechercher des images sur Pixabay
  const searchPixabayImages = async (loadMore = false) => {
    const query = loadMore ? pixabayCurrentQuery : pixabaySearchRef.current?.value?.trim();
    
    if (!query) {
      toast.error('Veuillez saisir un terme de recherche');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté');
      return;
    }

    const page = loadMore ? pixabayCurrentPage + 1 : 1;
    
    if (loadMore) {
      setIsLoadingMorePixabay(true);
    } else {
      setIsSearchingPixabay(true);
    }

    try {
      const response = await axios.get(`${API}/pixabay/search`, {
        params: {
          query: query,
          page: page,
          per_page: 50,
          image_type: 'photo',
          safesearch: true
        },
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data && response.data.hits) {
        if (loadMore) {
          // Ajouter les nouveaux résultats aux existants
          setPixabayResults(prev => [...prev, ...response.data.hits]);
          setPixabayCurrentPage(page);
          toast.success(`${response.data.hits.length} images supplémentaires chargées ! 📖`);
        } else {
          // Nouvelle recherche : remplacer les résultats
          setPixabayResults(response.data.hits);
          setPixabayCurrentPage(1);
          setPixabayCurrentQuery(query);
          setPixabayTotalHits(response.data.total || 0);
          // Reset saved images state for new search
          setSavedPixabayImages(new Set());
          toast.success(`${response.data.hits.length} images trouvées sur ${response.data.total} ! 🖼️`);
        }
      } else {
        if (!loadMore) {
          setPixabayResults([]);
          setSavedPixabayImages(new Set());
          toast.info('Aucune image trouvée pour cette recherche');
        }
      }

    } catch (error) {
      console.error('Error searching Pixabay:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la recherche: ${errorMessage}`);
      if (!loadMore) {
        setPixabayResults([]);
      }
    } finally {
      setIsSearchingPixabay(false);
      setIsLoadingMorePixabay(false);
    }
  };

  // Fonction pour recherche rapide avec catégorie
  const searchPixabayCategory = async (category) => {
    if (pixabaySearchRef.current) {
      pixabaySearchRef.current.value = category;
    }
    await searchPixabayImages();
  };

  // Fonction wrapper pour le composant ImageAttachmentContent
  const searchPixabay = async (query) => {
    if (!query || !query.trim()) {
      toast.error('Veuillez saisir un terme de recherche');
      return;
    }
    
    // Mettre à jour le champ de recherche si disponible
    if (pixabaySearchRef.current) {
      pixabaySearchRef.current.value = query.trim();
    }
    
    // Réinitialiser et effectuer la recherche
    setPixabayCurrentQuery(query.trim());
    setPixabayCurrentPage(1);
    
    try {
      setIsSearchingPixabay(true);
      
      const response = await axios.get(`${API}/pixabay/search`, {
        params: { 
          query: query.trim(),
          page: 1,
          per_page: 20
        },
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      });
      
      setPixabayResults(response.data.hits || []);
      setPixabayTotalHits(response.data.total || 0);
    } catch (error) {
      console.error('Erreur recherche Pixabay:', error);
      toast.error('Erreur lors de la recherche Pixabay');
      setPixabayResults([]);
    } finally {
      setIsSearchingPixabay(false);
    }
  };

  // Open choice modal for Pixabay image save
  const savePixabayImage = (pixabayImage) => {
    console.log('🎯 Save Pixabay Image clicked:', pixabayImage.id);
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté');
      return;
    }

    setSelectedPixabayImage(pixabayImage);
    setShowPixabaySaveModal(true);
    
    // Pré-remplir les champs avec les refs (après que la modal soit rendue)
    setTimeout(() => {
      if (pixabayTitleRef.current) {
        pixabayTitleRef.current.value = ''; // Titre vide par défaut
      }
      if (pixabayContextRef.current) {
        pixabayContextRef.current.value = pixabayImage.tags || ''; // Tags en contexte par défaut
      }
    }, 100);
  };

  // Save Pixabay image to general library
  const savePixabayToLibrary = async () => {
    if (!selectedPixabayImage) return;
    
    setIsSavingPixabayImage(selectedPixabayImage.id);

    try {
      console.log('📤 Saving to general library:', `${API}/pixabay/save-image`);
      
      const customTitle = pixabayTitleRef.current?.value || selectedPixabayImage.tags;
      const customContext = pixabayContextRef.current?.value || '';
      
      const response = await axios.post(`${API}/pixabay/save-image`, {
        pixabay_id: selectedPixabayImage.id,
        image_url: selectedPixabayImage.webformatURL,
        tags: selectedPixabayImage.tags,
        custom_title: customTitle,
        custom_context: customContext,
        save_type: 'general' // Mark as general library save
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        timeout: 15000
      });

      console.log('✅ Image saved to general library:', response.data);
      toast.success('Image ajoutée au stock Pixabay ! 📚');
      
      // Mark image as saved
      setSavedPixabayImages(prev => new Set([...prev, selectedPixabayImage.id]));
      
      // Reload content
      await loadPendingContent();
      
      // Close modal and reset fields
      setShowPixabaySaveModal(false);
      setSelectedPixabayImage(null);
      if (pixabayTitleRef.current) pixabayTitleRef.current.value = '';
      if (pixabayContextRef.current) pixabayContextRef.current.value = '';

    } catch (error) {
      console.error('❌ Error saving Pixabay image:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la sauvegarde: ${errorMessage}`);
    } finally {
      setIsSavingPixabayImage(null);
    }
  };

  // Save Pixabay image to specific month
  const savePixabayToMonth = async (monthKey) => {
    if (!selectedPixabayImage) return;
    
    setIsSavingPixabayImage(selectedPixabayImage.id);

    try {
      console.log('📤 Saving to month:', monthKey, `${API}/pixabay/save-image`);
      
      const customTitle = pixabayTitleRef.current?.value || selectedPixabayImage.tags;
      const customContext = pixabayContextRef.current?.value || '';
      
      const response = await axios.post(`${API}/pixabay/save-image`, {
        pixabay_id: selectedPixabayImage.id,
        image_url: selectedPixabayImage.webformatURL,
        tags: selectedPixabayImage.tags,
        custom_title: customTitle,
        custom_context: customContext,
        save_type: 'monthly', // Mark as monthly save
        attributed_month: monthKey // Assign to specific month
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        timeout: 15000
      });

      console.log('✅ Image saved to month:', response.data);
      toast.success(`Image ajoutée à ${monthKey.replace('_', ' ')} ! 📅`);
      
      // Mark image as saved
      setSavedPixabayImages(prev => new Set([...prev, selectedPixabayImage.id]));
      
      // Reload content
      await loadPendingContent();
      
      // Close modal and reset fields
      setShowPixabaySaveModal(false);
      setSelectedPixabayImage(null);
      if (pixabayTitleRef.current) pixabayTitleRef.current.value = '';
      if (pixabayContextRef.current) pixabayContextRef.current.value = '';

    } catch (error) {
      console.error('❌ Error saving Pixabay image to month:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la sauvegarde mensuelle: ${errorMessage}`);
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
      // Fallback: chercher dans le profil business - SANS valeurs par défaut qui écrasent
      const fieldMapping = {
        'business_name_edit': businessProfile?.business_name || '',
        'business_type_edit': businessProfile?.business_type || '',
        'business_description_edit': businessProfile?.business_description || '',
        'brand_tone_edit': businessProfile?.brand_tone || 'professionnel',
        'posting_frequency_edit': businessProfile?.posting_frequency || '', // CORRIGÉ: pas de 'weekly' par défaut
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

  // Handle file custom data (titles, contexts, month, etc) during upload preview - REFS SIMPLES
  // Refs pour les champs d'upload (éviter bug clavier virtuel)
  const uploadMonthSelectors = useRef({}); // For month selection per file
  
  // Fonctions pour gérer les refs d'upload (éviter clavier virtuel)
  const getUploadTitleValue = useCallback((fileIndex) => {
    // Accès direct par sélecteur + index spécifique
    const titleInputs = document.querySelectorAll('input[placeholder="Facultatif"]');
    if (titleInputs[fileIndex]) {
      const value = titleInputs[fileIndex].value;
      console.log(`🔍 Direct DOM access [${fileIndex}]:`, value);
      
      if (value && value.trim()) {
        alert(`✅ Found title [${fileIndex}]: "${value.trim()}"`);
        return value.trim();
      } else {
        alert(`❌ Empty title [${fileIndex}]: input.value = "${value}"`);
      }
    } else {
      alert(`❌ Title input not found at index ${fileIndex}`);
    }
    
    return '';
  }, []);

  const getUploadContextValue = useCallback((fileIndex) => {
    // Méthode 1: Essai avec refs
    const element = uploadContextRefs.current[fileIndex];
    if (element && element instanceof HTMLElement && element.value) {
      const refValue = element.value.trim();
      if (refValue) {
        alert(`Debug: Upload context [${fileIndex}] = "${refValue}" (via refs)`);
        return refValue;
      }
    }
    
    // Méthode 2: Fallback DOM si refs échouent
    const textareas = document.querySelectorAll('textarea[placeholder="Facultatif"]');
    if (textareas[fileIndex] && textareas[fileIndex].value) {
      const domValue = textareas[fileIndex].value.trim();
      if (domValue) {
        alert(`Debug: Upload context [${fileIndex}] = "${domValue}" (via DOM fallback)`);
        return domValue;
      }
    }
    
    alert(`Debug: Upload context [${fileIndex}] = EMPTY! (both methods failed)`);
    return '';
  }, []);

  // Handle file custom data (titles and contexts) during upload preview - ANCIEN CODE SUPPRIMÉ
  const updateFileCustomData = useCallback((fileIndex, field, value) => {
    setFileCustomData(prev => ({
      ...prev,
      [fileIndex]: {
        ...prev[fileIndex],
        [field]: value
      }
    }));
  }, []);

  // Get file custom data
  const getFileCustomData = useCallback((fileIndex, field, defaultValue = '') => {
    return fileCustomData[fileIndex]?.[field] || defaultValue;
  }, [fileCustomData]);

  const handleBatchUpload = async () => {
    if (selectedFiles.length === 0) return;

    console.log(`🚀 Starting batch upload of ${selectedFiles.length} files`);
    
    // CAPTURER LES VALEURS IMMÉDIATEMENT avant tout re-render
    const capturedValues = [];
    for (let i = 0; i < selectedFiles.length; i++) {
      const titleInputs = document.querySelectorAll('input[placeholder="Facultatif"]');
      const contextInputs = document.querySelectorAll('textarea[placeholder="Facultatif"]');
      
      const titleValue = titleInputs[i]?.value?.trim() || '';
      const contextValue = contextInputs[i]?.value?.trim() || '';
      
      capturedValues[i] = {
        title: titleValue,
        context: contextValue
      };
    }
    
    setIsUploading(true);
    
    // Group files by month for efficient batch uploads
    const filesByMonth = {};
    
    if (isCarouselMode) {
      // CAROUSEL MODE: All files get the same metadata from the first (shared) inputs
      const sharedMonth = uploadMonthSelectors.current[0]?.value || getDefaultMonth();
      const sharedTitle = uploadTitleRefs.current[0]?.value || '';
      const sharedContext = uploadContextRefs.current[0]?.value || '';
      
      console.log(`🎠 Carousel mode: All ${selectedFiles.length} files → ${sharedMonth} with shared metadata`);
      
      filesByMonth[sharedMonth] = selectedFiles.map((file, index) => ({
        file,
        index,
        title: sharedTitle,
        context: sharedContext
      }));
      
    } else {
      // NORMAL MODE: Each file has its own metadata
      selectedFiles.forEach((file, index) => {
        const monthData = uploadMonthSelectors.current[index]?.value || getDefaultMonth();
        console.log(`📎 File ${index + 1}: ${file.name} → ${monthData}`);
        
        if (!filesByMonth[monthData]) {
          filesByMonth[monthData] = [];
        }
        
        filesByMonth[monthData].push({
          file,
          index,
          title: uploadTitleRefs.current[index]?.value || '',
          context: uploadContextRefs.current[index]?.value || ''
        });
      });
    }
    
    console.log('📁 Files grouped by month:', Object.keys(filesByMonth).map(month => `${month}: ${filesByMonth[month].length} files`));

    try {
      console.log(`📤 Starting batch upload of ${selectedFiles.length} files grouped by month`);
      
      let totalUploaded = 0;
      const allCreatedItems = [];
      
      // Upload each month group separately
      for (const [monthKey, filesData] of Object.entries(filesByMonth)) {
        console.log(`📅 Uploading ${filesData.length} files to ${monthKey}`);
        
        const formData = new FormData();
        
        // Add files to FormData
        filesData.forEach(({ file }) => {
          formData.append('files', file);
        });
        
        // Add month attribution and upload type
        formData.append('attributed_month', monthKey);
        
        if (isCarouselMode) {
          formData.append('upload_type', 'carousel');
          // Add shared metadata for carousel
          if (filesData[0]?.title) {
            formData.append('common_title', filesData[0].title);
          }
          if (filesData[0]?.context) {
            formData.append('common_context', filesData[0].context);
          }
        } else {
          formData.append('upload_type', filesData.length === 1 ? 'single' : 'batch');
        }
        
        try {
          const response = await axios.post(`${API}/content/batch-upload`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          
          console.log(`✅ Upload response for ${monthKey}:`, response.data);
          
          // Update metadata for this batch
          if (response.data.created && response.data.created.length > 0) {
            for (let i = 0; i < response.data.created.length; i++) {
              const createdItem = response.data.created[i];
              const fileData = filesData[i];
              
              allCreatedItems.push({ ...createdItem, ...fileData });
              
              try {
                // Update title if provided
                if (fileData.title) {
                  await axios.put(`${API}/content/${createdItem.id}/title`, {
                    title: fileData.title
                  }, {
                    headers: {
                      Authorization: `Bearer ${localStorage.getItem('access_token')}`
                    }
                  });
                }
                
                // Update context if provided
                if (fileData.context) {
                  await axios.put(`${API}/content/${createdItem.id}/context`, {
                    context: fileData.context
                  }, {
                    headers: {
                      Authorization: `Bearer ${localStorage.getItem('access_token')}`
                    }
                  });
                }
              } catch (updateError) {
                console.warn(`Failed to update metadata for ${createdItem.filename}:`, updateError);
              }
            }
          }
          
          totalUploaded += response.data.count || filesData.length;
          
        } catch (monthError) {
          console.error(`❌ Error uploading to ${monthKey}:`, monthError);
          toast.error(`Erreur pour ${monthKey}: ${monthError.response?.data?.detail || monthError.message}`);
        }
      }
      
      if (totalUploaded > 0) {
        const monthList = Object.keys(filesByMonth).map(key => key.replace('_', ' ')).join(', ');
        toast.success(`${totalUploaded} fichiers uploadés avec succès dans : ${monthList} !`);
      }
      
      // MAINTENANT on peut nettoyer les refs et states
      setSelectedFiles([]);
      setFileCustomData({}); // Clean up custom data
      uploadTitleRefs.current = {}; // Clean up title refs
      uploadContextRefs.current = {}; // Clean up context refs
      uploadMonthSelectors.current = {}; // Clean up month selectors
      setIsCarouselMode(false); // Exit carousel mode
      
      // Force content refresh after all metadata updates complete
      await loadPendingContent();
      
      // Fermer automatiquement la modal après sauvegarde
      setTimeout(() => {
        handleClosePreview();
      }, 1500);
    } catch (error) {
      console.error('❌ Upload error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de l'upload: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Handle monthly-specific uploads (now using selectedMonth)
  const handleMonthlyUpload = async (files, mode) => {
    if (!files.length) return;
    
    const targetMonth = selectedMonth || getDefaultMonth();
    if (!targetMonth) {
      toast.error('Veuillez sélectionner un mois de destination');
      return;
    }
    
    console.log(`🗓️ Monthly upload: ${files.length} files to ${targetMonth} (${mode})`);
    
    setIsUploadingToMonth(true);
    
    try {
      const formData = new FormData();
      
      // Add all files to FormData
      files.forEach((file, index) => {
        formData.append('files', file);
      });
      
      // Set metadata based on mode
      formData.append('attributed_month', targetMonth);
      
      if (mode === 'carousel') {
        formData.append('upload_type', 'carousel');
      } else if (mode === 'batch') {
        formData.append('upload_type', 'batch');
      } else {
        formData.append('upload_type', 'single');
      }
      
      const response = await axios.post(`${API}/content/batch-upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.data.success) {
        const monthLabel = targetMonth.replace('_', ' ');
        toast.success(`${files.length} fichier${files.length > 1 ? 's' : ''} ajouté${files.length > 1 ? 's' : ''} à ${monthLabel} ! 📅`);
        
        // Refresh content
        await loadPendingContent();
      }
      
    } catch (error) {
      console.error('❌ Monthly upload error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de l'upload mensuel: ${errorMessage}`);
    } finally {
      setIsUploadingToMonth(false);
      
      // Clear file inputs
      const uploadInput = document.getElementById('file-upload');
      const carouselInput = document.getElementById('carousel-upload');
      if (uploadInput) uploadInput.value = '';
      if (carouselInput) carouselInput.value = '';
    }
  };

  // Handle carousel upload with common title and context
  const handleCarouselUpload = async () => {
    if (!carouselFiles.length) return;
    
    const targetMonth = selectedMonth || getDefaultMonth();
    if (!targetMonth) {
      toast.error('Veuillez sélectionner un mois de destination');
      return;
    }

    if (!carouselTitle.trim()) {
      toast.error('Veuillez saisir un titre pour le carrousel');
      return;
    }

    console.log(`🎠 Carousel upload: ${carouselFiles.length} files to ${targetMonth}`);
    
    setIsUploadingToMonth(true);
    
    try {
      const formData = new FormData();
      
      // Add all carousel files
      carouselFiles.forEach((file, index) => {
        formData.append('files', file);
      });
      
      // Add common metadata for carousel
      formData.append('attributed_month', targetMonth);
      formData.append('upload_type', 'carousel');
      formData.append('common_title', carouselTitle.trim());
      formData.append('common_context', carouselContext.trim());
      
      const response = await axios.post(`${API}/content/batch-upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.data.success) {
        const monthLabel = targetMonth.replace('_', ' ');
        toast.success(`Carrousel de ${carouselFiles.length} images ajouté à ${monthLabel} ! 🎠`);
        
        // Clear carousel data
        setCarouselFiles([]);
        setCarouselTitle('');
        setCarouselContext('');
        
        // Refresh content
        await loadPendingContent();
      }
      
    } catch (error) {
      console.error('❌ Carousel upload error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de l'upload carrousel: ${errorMessage}`);
    } finally {
      setIsUploadingToMonth(false);
      
      // Clear carousel input
      const carouselInput = document.getElementById('carousel-upload');
      if (carouselInput) carouselInput.value = '';
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
                  <p className="text-purple-600 font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent text-center transition-all duration-300 hover:scale-105 -mt-1" 
                     style={{
                       animation: 'breathe 4s ease-in-out infinite'
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
                            defaultValue={businessProfile?.posting_frequency || ''}
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
                          label="Infos contact pour vos posts"
                          placeholder="Ex: 📧 contact@entreprise.com | 📞 01 23 45 67 89 | 📍 123 Rue Example, Paris | ⏰ Lun-Ven 9h-18h"
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

          <TabsContent value="bibliotheque" className="space-y-4">
            <Card className="card-gradient">
              <CardHeader className="pb-4">
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
              <CardContent className="p-4">
                {/* Sub-tabs for Library */}
                <div className="mb-4">
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

                {/* CONTENU UNIFIÉ - Plus de branche conditionnelle destructrice */}
                <div key="stable-library-container">
                  {/* Ma bibliothèque content - Toujours présent mais masqué si inactif */}
                  <div key="my-library-section" style={{ display: activeLibraryTab === 'my-library' ? 'block' : 'none' }}>
                    {/* Upload Section */}
                    <div className="mb-8">
                      <input
                        type="file"
                        multiple
                        accept="image/*,video/*"
                        onChange={(e) => {
                          console.log('📁 Upload input onChange triggered');
                          const files = Array.from(e.target.files);
                          console.log(`📁 Selected ${files.length} files for upload`);
                          
                          if (files.length === 0) {
                            console.log('📁 No files selected');
                            setSelectedFiles([]);
                            setFileCustomData({});
                            return;
                          }
                          
                          // Initialize default month for each file
                          const defaultMonth = getDefaultMonth();
                          const newFileCustomData = {};
                          
                          files.forEach((file, index) => {
                            newFileCustomData[index] = {
                              attributedMonth: defaultMonth,
                              title: '',
                              context: ''
                            };
                          });
                          
                          console.log('📁 Setting files with default months:', newFileCustomData);
                          setSelectedFiles(files);
                          setFileCustomData(newFileCustomData);
                        }}
                        className="hidden"
                        id="file-upload"
                      />
                      
                      {/* Hidden inputs for uploads */}
                      <input
                        type="file"
                        accept="image/*,video/*"
                        onChange={(e) => handleMonthlyUpload(Array.from(e.target.files), 'single')}
                        className="hidden"
                        id="monthly-upload"
                      />
                      
                      {/* Duplicate of upload input for carousel - same logic but carousel mode */}
                      <input
                        type="file"
                        multiple
                        accept="image/*"
                        onChange={(e) => {
                          console.log('🎠 Carousel input onChange triggered');
                          const files = Array.from(e.target.files);
                          console.log(`🎠 Selected ${files.length} files for carousel`);
                          
                          if (files.length === 0) {
                            console.log('🎠 No files selected');
                            setSelectedFiles([]);
                            setFileCustomData({});
                            setIsCarouselMode(false);
                            return;
                          }
                          
                          if (files.length > 10) {
                            toast.error('Maximum 10 images pour un carrousel');
                            e.target.value = '';
                            return;
                          }
                          
                          // Initialize carousel mode with shared data for all files
                          const defaultMonth = getDefaultMonth();
                          const newFileCustomData = {};
                          
                          // All files get the same data structure, but we'll only show UI for the first one
                          files.forEach((file, index) => {
                            newFileCustomData[index] = {
                              attributedMonth: defaultMonth,
                              title: '', // Will be shared across all files
                              context: '' // Will be shared across all files
                            };
                          });
                          
                          console.log('🎠 Setting carousel files with shared metadata');
                          setSelectedFiles(files);
                          setFileCustomData(newFileCustomData);
                          setIsCarouselMode(true); // Enable carousel mode
                          
                          toast.success(`✨ Carrousel de ${files.length} images créé !`);
                        }}
                        className="hidden"
                        id="carousel-upload"
                      />
                      <div className="block border-2 border-dashed border-purple-300 rounded-3xl p-8 text-center bg-gradient-to-br from-purple-50 to-pink-50">
                        <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                          <Upload className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Uploadez vos contenus 📁</h3>
                        <p className="text-gray-600 mb-4">Choisissez votre type d'upload</p>
                        
                        {/* Two integrated upload buttons - Force exact same size */}
                        <div className="flex gap-4 justify-center max-w-2xl mx-auto">
                          <label
                            htmlFor="file-upload"
                            className="w-44 h-14 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white rounded-xl cursor-pointer transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center font-medium text-base"
                            style={{ minWidth: '176px', minHeight: '56px' }}
                          >
                            <Upload className="w-5 h-5 mr-2" />
                            Upload
                          </label>
                          
                          <label
                            htmlFor="carousel-upload"
                            className="w-44 h-14 bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700 text-white rounded-xl cursor-pointer transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center font-medium text-base"
                            style={{ minWidth: '176px', minHeight: '56px' }}
                          >
                            <ImageIcon className="w-5 h-5 mr-2" />
                            Carrousel
                          </label>
                        </div>
                        
                        <p className="text-sm text-purple-600 font-medium mt-4">📱 Images • 🎬 Vidéos</p>
                      </div>

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


                          

                          
                          <div className={isCarouselMode ? "max-w-md mx-auto" : "grid grid-cols-1 md:grid-cols-2 gap-6"}>
                            {isCarouselMode ? (
                              /* CAROUSEL MODE - Show only first image with stack effect */
                              <div className="relative">
                                <h4 className="text-lg font-semibold text-gray-900 mb-4 text-center flex items-center justify-center">
                                  <ImageIcon className="w-5 h-5 mr-2 text-pink-600" />
                                  Carrousel de {selectedFiles.length} image{selectedFiles.length > 1 ? 's' : ''}
                                </h4>
                                
                                {/* Stack preview */}
                                <div className="relative mb-6">
                                  <div className="relative w-full max-w-xs mx-auto">
                                    {/* Generic stack effect - 3 layers */}
                                    <div className="absolute w-full aspect-square bg-gray-200 rounded-xl transform translate-x-2 translate-y-2 opacity-60"></div>
                                    <div className="absolute w-full aspect-square bg-gray-300 rounded-xl transform translate-x-1 translate-y-1 opacity-80"></div>
                                    
                                    {/* First image visible */}
                                    <div className="relative w-full aspect-square bg-gray-100 rounded-xl overflow-hidden border-2 border-gray-200">
                                      {selectedFiles[0]?.type.startsWith('image/') ? (
                                        <img 
                                          src={URL.createObjectURL(selectedFiles[0])} 
                                          alt="Première image du carrousel"
                                          className="w-full h-full object-cover"
                                        />
                                      ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-pink-100 to-purple-100">
                                          <FileText className="w-8 h-8 text-pink-600" />
                                        </div>
                                      )}
                                      
                                      <div className="absolute top-2 right-2 bg-pink-600 text-white text-xs px-2 py-1 rounded-full font-medium">
                                        {selectedFiles.length} photo{selectedFiles.length > 1 ? 's' : ''}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Shared metadata for all carousel images */}
                                <div className="space-y-4">
                                  {/* Shared title */}
                                  <div className="space-y-2">
                                    <label className="block text-sm font-medium text-gray-700">
                                      Titre du carrousel
                                    </label>
                                    <input
                                      ref={(el) => {
                                        uploadTitleRefs.current[0] = el;
                                      }}
                                      type="text"
                                      placeholder="Titre commun pour toutes les images"
                                      defaultValue=""
                                      className="w-full px-3 py-2 border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors text-sm"
                                      style={{
                                        fontSize: '16px',
                                        lineHeight: '1.5',
                                        WebkitAppearance: 'none',
                                        borderRadius: '8px',
                                        touchAction: 'manipulation'
                                      }}
                                    />
                                  </div>
                                  
                                  {/* Shared month selector */}
                                  <div className="space-y-2">
                                    <label className="block text-sm font-medium text-gray-700">
                                      <Calendar className="w-4 h-4 inline mr-1" />
                                      Mois de destination
                                    </label>
                                    <select
                                      ref={(el) => {
                                        uploadMonthSelectors.current[0] = el;
                                      }}
                                      defaultValue={fileCustomData[0]?.attributedMonth || getDefaultMonth()}
                                      className="w-full px-3 py-2 border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors text-sm bg-white"
                                      style={{
                                        fontSize: '16px',
                                        lineHeight: '1.5',
                                        WebkitAppearance: 'none',
                                        borderRadius: '8px',
                                        touchAction: 'manipulation',
                                        backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e")`,
                                        backgroundRepeat: 'no-repeat',
                                        backgroundPosition: 'right 0.7rem center',
                                        backgroundSize: '1.5em',
                                        paddingRight: '2.5rem'
                                      }}
                                    >
                                      {getUploadMonthOptions().map(({ key, label }) => (
                                        <option key={key} value={key}>
                                          {label}
                                        </option>
                                      ))}
                                    </select>
                                  </div>
                                  
                                  {/* Shared context */}
                                  <div className="space-y-2">
                                    <label className="block text-sm font-medium text-gray-700">
                                      Contexte du carrousel
                                    </label>
                                    <textarea
                                      ref={(el) => {
                                        uploadContextRefs.current[0] = el;
                                      }}
                                      placeholder="Description commune pour toutes les images"
                                      defaultValue=""
                                      rows={3}
                                      className="w-full px-3 py-2 border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors text-sm resize-none"
                                      style={{
                                        fontSize: '16px',
                                        lineHeight: '1.5',
                                        WebkitAppearance: 'none',
                                        borderRadius: '8px',
                                        touchAction: 'manipulation'
                                      }}
                                    />
                                  </div>
                                </div>
                              </div>
                            ) : (
                              /* NORMAL UPLOAD MODE - Show all files individually */
                              selectedFiles.map((file, index) => (
                              <div key={index} className="relative group bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                                <div className="flex flex-col space-y-3">
                                  {/* Image preview */}
                                  <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
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
                                  
                                  {/* Custom title input - NON-CONTRÔLÉ AVEC REF */}
                                  <div className="space-y-2">
                                    <label className="block text-sm font-medium text-gray-700">
                                      Titre (facultatif)
                                    </label>
                                    <input
                                      ref={(el) => {
                                        uploadTitleRefs.current[index] = el;
                                      }}
                                      type="text"
                                      placeholder="Facultatif"
                                      defaultValue={fileCustomData[index]?.title || ""}
                                      className="w-full px-3 py-2 border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors text-sm"
                                      style={{
                                        fontSize: '16px',
                                        lineHeight: '1.5',
                                        WebkitAppearance: 'none',
                                        borderRadius: '8px',
                                        touchAction: 'manipulation'
                                      }}
                                    />
                                  </div>
                                  
                                  {/* Month selector per file */}
                                  <div className="space-y-2">
                                    <label className="block text-sm font-medium text-gray-700">
                                      <Calendar className="w-4 h-4 inline mr-1" />
                                      Mois de destination
                                    </label>
                                    <select
                                      ref={(el) => {
                                        uploadMonthSelectors.current[index] = el;
                                      }}
                                      defaultValue={fileCustomData[index]?.attributedMonth || getDefaultMonth()}
                                      className="w-full px-3 py-2 border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-sm bg-white"
                                      style={{
                                        fontSize: '16px',
                                        lineHeight: '1.5',
                                        WebkitAppearance: 'none',
                                        borderRadius: '8px',
                                        touchAction: 'manipulation',
                                        backgroundImage: `url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e")`,
                                        backgroundRepeat: 'no-repeat',
                                        backgroundPosition: 'right 0.7rem center',
                                        backgroundSize: '1.5em',
                                        paddingRight: '2.5rem'
                                      }}
                                      onChange={(e) => {
                                        // Capture current values from inputs before changing month
                                        const currentTitle = uploadTitleRefs.current[index]?.value || '';
                                        const currentContext = uploadContextRefs.current[index]?.value || '';
                                        
                                        // Update the file custom data when month changes (preserve actual input values)
                                        setFileCustomData(prev => ({
                                          ...prev,
                                          [index]: {
                                            title: currentTitle,
                                            context: currentContext,
                                            attributedMonth: e.target.value
                                          }
                                        }));
                                      }}
                                    >
                                      {getUploadMonthOptions().map(({ key, label }) => (
                                        <option key={key} value={key}>
                                          {label}
                                        </option>
                                      ))}
                                    </select>
                                  </div>
                                  
                                  {/* Custom context input - NON-CONTRÔLÉ AVEC REF */}
                                  <div className="space-y-2">
                                    <label className="block text-sm font-medium text-gray-700">
                                      Description / Contexte
                                    </label>
                                    <textarea
                                      ref={(el) => {
                                        uploadContextRefs.current[index] = el;
                                      }}
                                      placeholder="Facultatif"
                                      defaultValue={fileCustomData[index]?.context || ""}
                                      rows={3}
                                      className="w-full px-3 py-2 border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors text-sm resize-none"
                                      style={{
                                        fontSize: '16px',
                                        lineHeight: '1.5',
                                        WebkitAppearance: 'none',
                                        borderRadius: '8px',
                                        touchAction: 'manipulation'
                                      }}
                                    />
                                  </div>
                                  
                                  {/* File info and remove button */}
                                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                                    <span className="text-xs text-gray-500">
                                      {Math.round(file.size / 1024)} KB
                                    </span>
                                    <button
                                      onClick={() => {
                                        setSelectedFiles(prev => prev.filter((_, i) => i !== index));
                                        // Clean up custom data for removed file
                                        setFileCustomData(prev => {
                                          const newData = { ...prev };
                                          delete newData[index];
                                          // Reindex remaining files
                                          const reindexed = {};
                                          Object.keys(newData).forEach(key => {
                                            const keyIndex = parseInt(key);
                                            if (keyIndex > index) {
                                              reindexed[keyIndex - 1] = newData[key];
                                            } else {
                                              reindexed[key] = newData[key];
                                            }
                                          });
                                          return reindexed;
                                        });
                                      }}
                                      className="flex items-center space-x-1 px-2 py-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded text-sm transition-colors"
                                      title="Supprimer ce fichier"
                                    >
                                      <X className="w-4 h-4" />
                                      <span>Supprimer</span>
                                    </button>
                                  </div>
                                </div>
                              </div>
                            )))}
                          </div>
                          
                          {/* Bouton d'upload dupliqué en bas */}
                          <div className="mt-6 text-center">
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
                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-2">
                          <Button
                            onClick={toggleSelectionMode}
                            variant={isSelectionMode ? "default" : "outline"}
                            size="sm"
                            className={`${isSelectionMode ? "bg-purple-600 text-white" : "text-purple-600 border-purple-300"} whitespace-nowrap`}
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
                            <div className="flex flex-col sm:flex-row gap-2 sm:gap-2 w-full sm:w-auto">
                              <Button
                                onClick={handleSelectAll}
                                variant="outline"
                                size="sm"
                                className="text-blue-600 border-blue-300 text-xs sm:text-sm whitespace-nowrap"
                              >
                                <span className="hidden sm:inline">
                                  {selectedContentIds.size === pendingContent.length ? 'Tout désélectionner' : 'Tout sélectionner'}
                                </span>
                                <span className="sm:hidden">
                                  {selectedContentIds.size === pendingContent.length ? 'Désélectionner' : 'Sélectionner tout'}
                                </span>
                              </Button>
                              
                              <Button
                                onClick={handleDeleteSelected}
                                disabled={selectedContentIds.size === 0 || isDeletingContent}
                                variant="outline"
                                size="sm"
                                className="text-red-600 border-red-300 hover:bg-red-50 text-xs sm:text-sm whitespace-nowrap"
                              >
                                {isDeletingContent ? (
                                  <>
                                    <div className="animate-spin rounded-full mr-1 h-3 w-3 sm:h-4 sm:w-4 border-b-2 border-red-600"></div>
                                    <span className="hidden sm:inline">Suppression...</span>
                                    <span className="sm:hidden">...</span>
                                  </>
                                ) : (
                                  <>
                                    <Trash className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                                    <span className="hidden sm:inline">Supprimer ({selectedContentIds.size})</span>
                                    <span className="sm:hidden">Suppr. ({selectedContentIds.size})</span>
                                  </>
                                )}
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* MONTHLY ORGANIZATION VIEW */}
                      <div>
                        {/* Toggle between monthly and all view */}
                        <div className="flex justify-between items-center mb-6 px-2">
                          <div className="flex items-center space-x-4">
                            <Button
                              onClick={() => setMonthlyLibraryView(!monthlyLibraryView)}
                              variant="outline"
                              size="sm"
                              className="text-purple-600 border-purple-300"
                            >
                              <Calendar className="w-4 h-4 mr-2" />
                              {monthlyLibraryView ? 'Vue liste' : 'Vue mensuelle'}
                            </Button>
                            <div className="text-sm font-medium text-gray-700">
                              <span className="text-purple-600 font-bold">{pendingContent.length}</span>
                              <span className="text-gray-500">/{totalContentCount}</span>
                              <span className="ml-2 text-gray-600">contenus</span>
                            </div>
                          </div>

                        </div>

                        {monthlyLibraryView ? (
                          /* MONTHLY SECTIONS VIEW */
                          <div className="space-y-6">
                            {(() => {
                              const { currentAndFuture, archives } = getMonthlyContentData();
                              
                              return (
                                <>
                                  {/* Current and Future Months */}
                                  {Object.entries(currentAndFuture)
                                    .sort(([, a], [, b]) => a.order - b.order)
                                    .map(([monthKey, monthInfo]) => {
                                      const isCollapsed = collapsedMonths.has(monthKey);
                                      const hasContent = monthInfo.content.length > 0;
                                      
                                      return (
                                        <div key={monthKey} className="border border-gray-200 rounded-2xl overflow-hidden">
                                          {/* Month Header */}
                                          <div 
                                            className={`flex items-center justify-between p-4 cursor-pointer transition-colors ${
                                              monthInfo.isCurrent 
                                                ? 'bg-gradient-to-r from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100' 
                                                : 'bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100'
                                            }`}
                                            onClick={() => toggleMonthCollapse(monthKey)}
                                          >
                                            <div className="flex items-center space-x-3">
                                              <div className={`w-3 h-3 rounded-full transition-transform duration-200 ${isCollapsed ? 'rotate-0' : 'rotate-90'}`}>
                                                <ChevronRight className="w-3 h-3 text-purple-600" />
                                              </div>
                                              <h3 className="text-lg font-semibold text-gray-800">
                                                {monthInfo.label}
                                                {monthInfo.isCurrent && (
                                                  <span className="ml-2 text-sm text-green-600 font-normal">(actuel)</span>
                                                )}
                                              </h3>
                                              <Badge variant="secondary" className={
                                                monthInfo.isCurrent 
                                                  ? "bg-green-100 text-green-700"
                                                  : "bg-purple-100 text-purple-700"
                                              }>
                                                {monthInfo.content.length} {monthInfo.content.length <= 1 ? 'contenu' : 'contenus'}
                                              </Badge>
                                            </div>
                                          </div>
                                          
                                          {/* Month Content */}
                                          {!isCollapsed && (
                                            <div className="p-2">
                                              {hasContent || !monthInfo.isPast ? (
                                                <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                                                  {/* Existing content */}
                                                  {monthInfo.content.map((content) => (
                                                    <ContentThumbnail
                                                      key={content.id}
                                                      content={content}
                                                      isSelectionMode={isSelectionMode}
                                                      isSelected={selectedContentIds.has(content.id)}
                                                      onContentClick={handleContentClick}
                                                      onToggleSelection={handleToggleSelection}
                                                      onMoveContent={handleMoveContent}
                                                    />
                                                  ))}
                                                </div>
                                              ) : (
                                                <div className="text-center py-8 text-gray-500">
                                                  <Calendar className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                                  <p className="text-sm">Aucun contenu pour ce mois</p>
                                                </div>
                                              )}
                                            </div>
                                          )}
                                        </div>
                                      );
                                    })}
                                  
                                  {/* Archives Section */}
                                  {Object.keys(archives).length > 0 && (
                                    <div className="border-t-2 border-gray-300 pt-6 mt-8">
                                      <h4 className="text-sm font-medium text-gray-500 mb-4 text-center">archives</h4>
                                      <div className="space-y-4">
                                        {Object.entries(archives)
                                          .sort(([, a], [, b]) => b.order - a.order) // Most recent archive first
                                          .map(([monthKey, monthInfo]) => {
                                            const isCollapsed = collapsedMonths.has(monthKey);
                                            const hasContent = monthInfo.content.length > 0;
                                            
                                            return (
                                              <div key={monthKey} className="border border-gray-200 rounded-xl overflow-hidden">
                                                <div 
                                                  className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 cursor-pointer hover:from-gray-100 hover:to-gray-150 transition-colors"
                                                  onClick={() => toggleMonthCollapse(monthKey)}
                                                >
                                                  <div className="flex items-center space-x-3">
                                                    <div className={`w-3 h-3 rounded-full transition-transform duration-200 ${isCollapsed ? 'rotate-0' : 'rotate-90'}`}>
                                                      <ChevronRight className="w-3 h-3 text-gray-600" />
                                                    </div>
                                                    <h3 className="text-md font-medium text-gray-700">
                                                      {monthInfo.label}
                                                    </h3>
                                                    <Badge variant="secondary" className="bg-gray-200 text-gray-600">
                                                      {monthInfo.content.length}
                                                    </Badge>
                                                  </div>
                                                </div>
                                                
                                                {!isCollapsed && (
                                                  <div className="p-2">
                                                    {hasContent && monthInfo.shouldLoadThumbnails ? (
                                                      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                                                        {monthInfo.content.map((content) => (
                                                          <ContentThumbnail
                                                            key={content.id}
                                                            content={content}
                                                            isSelectionMode={isSelectionMode}
                                                            isSelected={selectedContentIds.has(content.id)}
                                                            onContentClick={handleContentClick}
                                                            onToggleSelection={handleToggleSelection}
                                                            onMoveContent={handleMoveContent}
                                                          />
                                                        ))}
                                                      </div>
                                                    ) : hasContent && !monthInfo.shouldLoadThumbnails ? (
                                                      <div className="text-center py-8 text-gray-500">
                                                        <div className="animate-pulse">
                                                          <div className="w-8 h-8 bg-gray-300 rounded-full mx-auto mb-2"></div>
                                                          <p className="text-sm">Chargement des vignettes...</p>
                                                        </div>
                                                      </div>
                                                    ) : (
                                                      <div className="text-center py-8 text-gray-500">
                                                        <Calendar className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                                        <p className="text-sm">Aucun contenu pour ce mois</p>
                                                      </div>
                                                    )}
                                                  </div>
                                                )}
                                              </div>
                                            );
                                          })}
                                      </div>
                                    </div>
                                  )}
                                </>
                              );
                            })()}
                          </div>
                        ) : (
                          /* TRADITIONAL GRID VIEW */
                          <div>
                            <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                              {pendingContent.map((content) => (
                                <ContentThumbnail
                                  key={content.id}
                                  content={content}
                                  isSelectionMode={isSelectionMode}
                                  isSelected={selectedContentIds.has(content.id)}
                                  onContentClick={handleContentClick}
                                  onToggleSelection={handleToggleSelection}
                                  onMoveContent={handleMoveContent}
                                />
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Message si pas de contenu */}
                        {pendingContent.length === 0 && (
                          <div className="text-center py-12 card-glass rounded-3xl border-2 border-dashed border-purple-300">
                            <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
                              <ImageIcon className="w-12 h-12 text-white" />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-700 mb-4">Votre bibliothèque de contenus 📚</h3>
                            <p className="text-xl text-gray-500 mb-6">Uploadez vos premiers contenus pour voir votre succès exploser ! 🚀</p>

                          </div>
                        )}
                        

                        

                      </div>
                    </div>
                  </div>

                  {/* Pixabay search content - Toujours présent mais masqué si inactif */}
                  <div style={{ display: activeLibraryTab === 'pixabay-search' ? 'block' : 'none' }}>
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
                        
                        <div className="flex space-x-2 sm:space-x-3">
                          <input
                            ref={pixabaySearchRef}
                            type="text"
                            placeholder="Ex: entreprise, marketing, équipe..."
                            onKeyPress={(e) => e.key === 'Enter' && searchPixabayImages()}
                            className="flex-1 text-base border-blue-200 focus:border-blue-400 rounded-md border px-3 py-2"
                            style={{
                              fontSize: '16px',
                              lineHeight: '1.5', 
                              WebkitAppearance: 'none',
                              borderRadius: '8px',
                              touchAction: 'manipulation'
                            }}
                          />
                          <Button
                            onClick={() => {
                              console.log('🔍 Pixabay GO button clicked!');
                              console.log('Search ref:', pixabaySearchRef.current);
                              console.log('Search value:', pixabaySearchRef.current?.value);
                              searchPixabayImages();
                            }}
                            disabled={isSearchingPixabay}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-3 sm:px-6 whitespace-nowrap"
                          >
                            {isSearchingPixabay ? (
                              <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-1 sm:mr-2"></div>
                                <span className="hidden sm:inline">Recherche...</span>
                                <span className="sm:hidden">...</span>
                              </>
                            ) : (
                              <>
                                <Search className="w-4 h-4 mr-1 sm:mr-2" />
                                <span className="hidden sm:inline">Rechercher</span>
                                <span className="sm:hidden">Go</span>
                              </>
                            )}
                          </Button>
                        </div>

                        {/* Categories */}
                        <div className="mt-4">
                          <p className="text-sm text-gray-600 mb-2">Catégories populaires :</p>
                          <div className="flex flex-wrap gap-2">
                            {[
                              'entreprise', 'marketing', 'équipe', 'bureau', 
                              'technologie', 'nature', 'personnes', 'arrière-plans'
                            ].map((category) => (
                              <Button
                                key={category}
                                onClick={() => searchPixabayCategory(category)}
                                variant="ghost"
                                size="sm"
                                className="text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 border-blue-200"
                              >
                                {category}
                              </Button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Search Results */}
                    {pixabayResults.length > 0 && (
                      <div>
                        <h4 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                          <ImageIcon className="w-6 h-6 mr-2 text-blue-600" />
                          Résultats de recherche ({pixabayResults.length})
                        </h4>
                        
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
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
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      if (!savedPixabayImages.has(image.id)) {
                                        savePixabayImage(image);
                                      }
                                    }}
                                    disabled={isSavingPixabayImage === image.id || savedPixabayImages.has(image.id)}
                                    className={`opacity-0 group-hover:opacity-100 transition-opacity duration-300 cursor-pointer ${
                                      savedPixabayImages.has(image.id) 
                                        ? 'bg-green-600 hover:bg-green-700' 
                                        : 'bg-blue-600 hover:bg-blue-700'
                                    } text-white`}
                                    size="sm"
                                  >
                                    {isSavingPixabayImage === image.id ? (
                                      <>
                                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-1"></div>
                                        Ajout...
                                      </>
                                    ) : savedPixabayImages.has(image.id) ? (
                                      <>
                                        <Check className="w-4 h-4 mr-1" />
                                        Ajouté
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
                                <p className="text-xs text-gray-600 truncate" title={image.tags}>
                                  {image.tags.split(',').slice(0, 3).join(' • ')}
                                  {image.tags.split(',').length > 3 && '...'}
                                </p>
                                <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                                  <span>{image.views?.toLocaleString()} vues</span>
                                  <span>{image.downloads?.toLocaleString()} ⬇️</span>
                                </div>
                                
                                {/* Mobile-friendly button - visible on small screens */}
                                <Button
                                  onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    if (!savedPixabayImages.has(image.id)) {
                                      savePixabayImage(image);
                                    }
                                  }}
                                  disabled={isSavingPixabayImage === image.id || savedPixabayImages.has(image.id)}
                                  className={`w-full mt-2 text-xs sm:hidden text-white ${
                                    savedPixabayImages.has(image.id) 
                                      ? 'bg-green-600 hover:bg-green-700' 
                                      : 'bg-blue-600 hover:bg-blue-700'
                                  }`}
                                  size="sm"
                                >
                                  {isSavingPixabayImage === image.id ? (
                                    <>
                                      <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin mr-1"></div>
                                      Ajout...
                                    </>
                                  ) : savedPixabayImages.has(image.id) ? (
                                    <>
                                      <Check className="w-3 h-3 mr-1" />
                                      Ajouté ✓
                                    </>
                                  ) : (
                                    <>
                                      <Upload className="w-3 h-3 mr-1" />
                                      Ajouter
                                    </>
                                  )}
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                        
                        {/* Load More Button pour Pixabay */}
                        {pixabayResults.length > 0 && pixabayResults.length < pixabayTotalHits && (
                          <div className="text-center mt-8">
                            <Button
                              onClick={() => searchPixabayImages(true)}
                              disabled={isLoadingMorePixabay}
                              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3"
                            >
                              {isLoadingMorePixabay ? (
                                <>
                                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                                  Chargement...
                                </>
                              ) : (
                                <>
                                  <Search className="w-4 h-4 mr-2" />
                                  Charger plus d'images ({pixabayResults.length}/{pixabayTotalHits})
                                </>
                              )}
                            </Button>
                          </div>
                        )}

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
                </div>
                
                {/* Modal d'aperçu du contenu */}
                {previewContent && (
                  <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
                      {/* Header de la modal simplifié (sans titre) */}
                      <div className="flex items-center justify-between p-4 border-b">
                        <h3 className="text-lg font-semibold text-gray-900">
                          Aperçu du contenu
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
                                src={previewContent.source === 'pixabay' 
                                  ? previewContent.url
                                  : `${process.env.REACT_APP_BACKEND_URL}${previewContent.url}?token=${localStorage.getItem('access_token')}`
                                }
                                alt={previewContent.filename}
                                className="w-full h-auto max-h-96 object-contain rounded-lg border"
                              />
                            ) : previewContent.file_type?.startsWith('video/') ? (
                              <>
                                <video 
                                  src={previewContent.source === 'pixabay' 
                                    ? previewContent.url
                                    : `${process.env.REACT_APP_BACKEND_URL}${previewContent.url}?token=${localStorage.getItem('access_token')}`
                                  }
                                  controls
                                  preload="metadata"
                                  className="w-full h-auto max-h-96 rounded-lg border"
                                  onError={(e) => {
                                    console.error('Video loading error:', e);
                                    // Fallback: show video icon instead
                                    e.target.style.display = 'none';
                                    const fallback = e.target.nextElementSibling;
                                    if (fallback) fallback.style.display = 'flex';
                                  }}
                                />
                                <div 
                                  className="w-full h-48 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg border items-center justify-center hidden"
                                  style={{ display: 'none' }}
                                >
                                  <div className="text-center">
                                    <Play className="w-12 h-12 text-blue-600 mx-auto mb-2" />
                                    <p className="text-sm text-blue-800">Vidéo non supportée par le navigateur</p>
                                    <a 
                                      href={previewContent.source === 'pixabay' 
                                        ? previewContent.url
                                        : `${process.env.REACT_APP_BACKEND_URL}${previewContent.url}?token=${localStorage.getItem('access_token')}`
                                      }
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-blue-600 hover:text-blue-800 underline text-sm mt-2 inline-block"
                                    >
                                      Ouvrir dans un nouvel onglet
                                    </a>
                                  </div>
                                </div>
                              </>
                            ) : (
                              <div className="w-full h-48 bg-gray-100 rounded-lg border flex items-center justify-center">
                                <FileText className="w-12 h-12 text-gray-400" />
                              </div>
                            )}
                            {/* Titre toujours éditable */}
                            <div className="space-y-2">
                              <label className="block text-sm font-medium text-gray-700">
                                Titre
                              </label>
                              <input
                                ref={previewTitleInputRef}
                                type="text"
                                className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
                                disabled={isSavingContext}
                                placeholder="Facultatif"
                                style={{
                                  fontSize: '16px',
                                  lineHeight: '1.5',
                                  WebkitAppearance: 'none',
                                  borderRadius: '8px',
                                  boxShadow: 'none',
                                  WebkitBoxShadow: 'none',
                                  touchAction: 'manipulation'
                                }}
                              />
                            </div>
                            
                            {/* Informations du fichier (simplifiées) */}
                            <div className="text-sm text-gray-600 space-y-1">
                              <p><strong>Ajouté le:</strong> {
                                previewContent.uploaded_at ? new Date(previewContent.uploaded_at).toLocaleDateString('fr-FR') :
                                previewContent.created_at ? new Date(previewContent.created_at).toLocaleDateString('fr-FR') :
                                previewContent.timestamp ? new Date(previewContent.timestamp).toLocaleDateString('fr-FR') :
                                'Date inconnue'
                              }</p>
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
                                className={`flex-1 bg-purple-600 hover:bg-purple-700 text-white flex items-center gap-2 ${
                                  isSavingContext ? 'opacity-75 cursor-not-allowed' : ''
                                }`}
                              >
                                {isSavingContext ? (
                                  <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                                    Sauvegarde...
                                  </>
                                ) : (
                                  'Sauvegarder'
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

          <TabsContent value="notes" className="space-y-4">
            <Card className="card-gradient">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center space-x-3 text-xl">
                  <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center">
                    <Edit className="w-5 h-5 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    Notes et informations ✨
                  </span>
                </CardTitle>
                <CardDescription className="text-base text-gray-600">
                  Ajoutez des informations importantes pour créer des posts qui cartonnent ! 🎯
                </CardDescription>
                
                {/* Exemples d'informations à noter */}
                <div className="mt-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-blue-800 mb-2">💡 Exemples d'informations à noter :</p>
                  <div className="text-sm text-blue-700 space-y-1">
                    <div>• <strong>Événements :</strong> Fermeture exceptionnelle, participation à un salon, journées portes ouvertes</div>
                    <div>• <strong>Animations :</strong> Organisation d'un jeu, concours, promotion spéciale, nouveauté</div>
                    <div>• <strong>Promotions :</strong> Réduction 15% ce mois-ci, code promo SPECIAL20, offre fidélité</div>
                    <div>• <strong>Particularités :</strong> Savoir-faire unique, histoire de l'entreprise, valeurs importantes</div>
                    <div>• <strong>Actualités :</strong> Nouveau partenariat, certification obtenue, équipe qui grandit</div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                {/* Add New Note Section */}
                <div className="mb-6">
                  <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-4 border-2 border-indigo-200">
                    <div className="flex items-center mb-3">
                      <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center mr-3">
                        <Edit className="w-4 h-4 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900">Ajouter une nouvelle note</h3>
                    </div>
                    
                    <div className="space-y-3">
                      {/* Titre de la note avec input HTML natif */}
                      <div className="space-y-1">
                        <label htmlFor="note_title_native" className="block text-sm font-medium text-gray-700">
                          Titre de la note
                        </label>
                        <input
                          ref={titleInputRef}
                          id="note_title_native"
                          type="text"
                          onChange={handleNoteTitleChange}
                          placeholder="Ex: Nouvelle promotion, Événement spécial..."
                          className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
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
                      <div className="space-y-1">
                        <label htmlFor="note_content_native" className="block text-sm font-medium text-gray-700">
                          Contenu
                        </label>
                        <textarea
                          ref={contentInputRef}
                          id="note_content_native"
                          onChange={handleNoteContentChange}
                          placeholder="Décrivez les détails importants que vous voulez voir apparaître dans vos posts..."
                          className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
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
                            minHeight: '150px'
                          }}
                          rows={6}
                          autoComplete="off"
                          autoCorrect="on"
                          autoCapitalize="sentences"
                          spellCheck="true"
                          inputMode="text"
                          enterKeyHint="enter"
                        />
                      </div>
                      
                      {/* Priorité avec dropdown HTML natif */}
                      <div className="space-y-1">
                        <label htmlFor="note_priority_native" className="block text-sm font-medium text-gray-700">
                          Priorité
                        </label>
                        <select
                          ref={priorityInputRef}
                          id="note_priority_native"
                          onChange={handleNotePriorityChange}
                          className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
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
                      
                      {/* Nouveaux champs pour les notes périodiques */}
                      <div className="space-y-3 border-t border-gray-200 pt-3">
                        <h4 className="text-sm font-medium text-gray-700 flex items-center">
                          <Calendar className="w-4 h-4 mr-2" />
                          Planification de la note
                        </h4>
                        
                        {/* Checkbox note mensuelle */}
                        <div className="flex items-center space-x-3">
                          <input
                            ref={isPermanentCheckboxRef}
                            id="note_monthly_checkbox"
                            type="checkbox"
                            className="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500 focus:ring-2"
                            onChange={(e) => {
                              const isChecked = e.target.checked;
                              // Griser/dégriser le dropdown mois
                              if (targetMonthKeyRef.current) {
                                targetMonthKeyRef.current.disabled = isChecked;
                                if (isChecked) {
                                  targetMonthKeyRef.current.value = '';
                                }
                              }
                            }}
                          />
                          <label htmlFor="note_monthly_checkbox" className="text-sm text-gray-700">
                            Note valable tous les mois
                          </label>
                        </div>
                        
                        {/* Dropdown mois unifié (même logique que uploads) */}
                        <div className="space-y-1">
                          <label htmlFor="note_target_month_key" className="block text-sm font-medium text-gray-700">
                            Attribuer cette note à
                          </label>
                          <select
                            ref={targetMonthKeyRef}
                            id="note_target_month_key"
                            className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none disabled:bg-gray-100 disabled:text-gray-500"
                            style={{
                              fontSize: '16px',
                              lineHeight: '1.5',
                              WebkitAppearance: 'none',
                              WebkitBorderRadius: '8px',
                              borderRadius: '8px',
                              boxShadow: 'none',
                              WebkitBoxShadow: 'none',
                              touchAction: 'manipulation',
                              cursor: 'pointer'
                            }}
                          >
                            <option value="">Choisir un mois</option>
                            {getNotesMonthOptions().map(({ key, label }) => (
                              <option key={key} value={key}>
                                📅 {label}
                              </option>
                            ))}
                          </select>
                        </div>
                        
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <p className="text-xs text-blue-700">
                            💡 <strong>Note valable tous les mois :</strong> La note sera utilisée chaque mois pour la génération de contenu.<br/>
                            💡 <strong>Note spécifique :</strong> La note ne sera utilisée que pour le mois et l'année sélectionnés, puis supprimée automatiquement le 5 du mois suivant.
                          </p>
                        </div>
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
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <h3 className="text-xl font-semibold text-gray-900">📝 Mes notes ({notes.length})</h3>
                      <div className="text-sm text-gray-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
                        <span className="font-semibold">Organisation :</span> 📅 Par mois
                      </div>
                    </div>
                    
                    {/* MONTHLY NOTES ORGANIZATION - Same logic as content */}
                    <div className="space-y-6">
                      {(() => {
                        const { alwaysValid, currentAndFuture, archives } = getMonthlyNotesData();
                        
                        return (
                          <>
                            {/* Always Valid Notes (Monthly Notes) - First section */}
                            {alwaysValid.length > 0 && (
                              <div className="border border-green-200 rounded-2xl overflow-hidden">
                                <div 
                                  className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 cursor-pointer hover:from-green-100 hover:to-emerald-100 transition-colors"
                                  onClick={() => toggleMonthCollapse('always_valid')}
                                >
                                  <div className="flex items-center space-x-3">
                                    <div className={`w-3 h-3 rounded-full transition-transform duration-200 ${collapsedMonths.has('always_valid') ? 'rotate-0' : 'rotate-90'}`}>
                                      <ChevronRight className="w-3 h-3 text-green-600" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-800">
                                      🔁 Notes toujours valides
                                    </h3>
                                    <Badge variant="secondary" className="bg-green-100 text-green-700">
                                      {alwaysValid.length} note{alwaysValid.length > 1 ? 's' : ''}
                                    </Badge>
                                  </div>
                                </div>
                                
                                {!collapsedMonths.has('always_valid') && (
                                  <div className="p-4">
                                    <div className="grid gap-4">
                                      {alwaysValid.map((note, index) => (
                                        <div key={note.note_id || `always_${index}`} className="card-glass p-4 sm:p-6 rounded-2xl border border-green-200">
                                          {/* Note content - same as before */}
                                          <div className="space-y-3 sm:space-y-0 sm:flex sm:items-start sm:justify-between mb-3">
                                            <div className="flex-1 min-w-0">
                                              <div className="flex items-center space-x-2 mb-2">
                                                <div className={`w-3 h-3 rounded-full flex-shrink-0 ${
                                                  note.priority === 'high' ? 'bg-red-500' :
                                                  note.priority === 'normal' ? 'bg-yellow-500' : 'bg-green-500'
                                                }`}></div>
                                                <h4 className="font-semibold text-gray-900 truncate text-sm sm:text-base">
                                                  {note.description || note.title || 'Note sans titre'}
                                                </h4>
                                              </div>
                                              
                                              <div className="flex flex-wrap gap-1 sm:gap-2">
                                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                                  {note.priority === 'high' ? 'élevée' : 
                                                   note.priority === 'low' ? 'faible' : 'normale'}
                                                </span>
                                                <span className="text-xs text-green-700 bg-green-100 px-2 py-1 rounded-full font-medium">
                                                  🔁 Mensuelle
                                                </span>
                                              </div>
                                            </div>
                                            
                                            <div className="flex items-center justify-between sm:justify-end space-x-2 sm:ml-4">
                                              <div className="text-xs text-gray-500">
                                                {note.created_at ? new Date(note.created_at).toLocaleDateString('fr-FR', {
                                                  day: 'numeric',
                                                  month: 'short',
                                                  year: '2-digit'
                                                }) : ''}
                                              </div>
                                              
                                              <div className="flex items-center space-x-1">
                                                <Button
                                                  onClick={() => handleEditNote(note)}
                                                  variant="ghost"
                                                  size="sm"
                                                  className="p-2 h-8 w-8 text-blue-600 hover:text-blue-800 hover:bg-blue-50"
                                                  title="Modifier cette note"
                                                >
                                                  <Edit className="h-4 w-4" />
                                                </Button>
                                                
                                                <Button
                                                  onClick={() => handleDeleteNote(note.note_id)}
                                                  variant="ghost"
                                                  size="sm"
                                                  className="p-2 h-8 w-8 text-red-600 hover:text-red-800 hover:bg-red-50"
                                                  title="Supprimer cette note"
                                                >
                                                  <Trash2 className="h-4 w-4" />
                                                </Button>
                                              </div>
                                            </div>
                                          </div>
                                          
                                          {note.content && (
                                            <p className="text-gray-700 text-sm sm:text-base break-words">
                                              {note.content}
                                            </p>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                            
                            {/* Current and Future Months */}
                            {Object.entries(currentAndFuture)
                              .sort(([, a], [, b]) => a.order - b.order)
                              .map(([monthKey, monthInfo]) => {
                                const isCollapsed = collapsedMonths.has(monthKey);
                                const hasNotes = monthInfo.notes.length > 0;
                                
                                return (
                                  <div key={monthKey} className="border border-blue-200 rounded-2xl overflow-hidden">
                                    <div 
                                      className={`flex items-center justify-between p-4 cursor-pointer transition-colors ${
                                        monthInfo.isCurrent 
                                          ? 'bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100' 
                                          : 'bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100'
                                      }`}
                                      onClick={() => toggleMonthCollapse(monthKey)}
                                    >
                                      <div className="flex items-center space-x-3">
                                        <div className={`w-3 h-3 rounded-full transition-transform duration-200 ${isCollapsed ? 'rotate-0' : 'rotate-90'}`}>
                                          <ChevronRight className="w-3 h-3 text-blue-600" />
                                        </div>
                                        <h3 className="text-lg font-semibold text-gray-800">
                                          📅 {monthInfo.label}
                                          {monthInfo.isCurrent && (
                                            <span className="ml-2 text-sm text-blue-600 font-normal">(actuel)</span>
                                          )}
                                        </h3>
                                        <Badge variant="secondary" className={
                                          monthInfo.isCurrent 
                                            ? "bg-blue-100 text-blue-700"
                                            : "bg-purple-100 text-purple-700"
                                        }>
                                          {monthInfo.notes.length} note{monthInfo.notes.length > 1 ? 's' : ''}
                                        </Badge>
                                      </div>
                                    </div>
                                    
                                    {!isCollapsed && hasNotes && (
                                      <div className="p-4">
                                        <div className="grid gap-4">
                                          {monthInfo.notes.map((note, index) => (
                                            <div key={note.note_id || `${monthKey}_${index}`} className="card-glass p-4 sm:p-6 rounded-2xl border border-indigo-200">
                                              {/* Same note content structure */}
                                              <div className="space-y-3 sm:space-y-0 sm:flex sm:items-start sm:justify-between mb-3">
                                                <div className="flex-1 min-w-0">
                                                  <div className="flex items-center space-x-2 mb-2">
                                                    <div className={`w-3 h-3 rounded-full flex-shrink-0 ${
                                                      note.priority === 'high' ? 'bg-red-500' :
                                                      note.priority === 'normal' ? 'bg-yellow-500' : 'bg-green-500'
                                                    }`}></div>
                                                    <h4 className="font-semibold text-gray-900 truncate text-sm sm:text-base">
                                                      {note.description || note.title || 'Note sans titre'}
                                                    </h4>
                                                  </div>
                                                  
                                                  <div className="flex flex-wrap gap-1 sm:gap-2">
                                                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                                      {note.priority === 'high' ? 'élevée' : 
                                                       note.priority === 'low' ? 'faible' : 'normale'}
                                                    </span>
                                                    {(note.note_month && note.note_year) && (
                                                      <span className="text-xs text-blue-700 bg-blue-100 px-2 py-1 rounded-full font-medium">
                                                        📅 {['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'][note.note_month - 1]} {note.note_year}
                                                      </span>
                                                    )}
                                                  </div>
                                                </div>
                                                
                                                <div className="flex items-center justify-between sm:justify-end space-x-2 sm:ml-4">
                                                  <div className="text-xs text-gray-500">
                                                    {note.created_at ? new Date(note.created_at).toLocaleDateString('fr-FR', {
                                                      day: 'numeric',
                                                      month: 'short',
                                                      year: '2-digit'
                                                    }) : ''}
                                                  </div>
                                                  
                                                  <div className="flex items-center space-x-1">
                                                    <Button
                                                      onClick={() => handleEditNote(note)}
                                                      variant="ghost"
                                                      size="sm"
                                                      className="p-2 h-8 w-8 text-blue-600 hover:text-blue-800 hover:bg-blue-50"
                                                      title="Modifier cette note"
                                                    >
                                                      <Edit className="h-4 w-4" />
                                                    </Button>
                                                    
                                                    <Button
                                                      onClick={() => handleDeleteNote(note.note_id)}
                                                      variant="ghost"
                                                      size="sm"
                                                      className="p-2 h-8 w-8 text-red-600 hover:text-red-800 hover:bg-red-50"
                                                      title="Supprimer cette note"
                                                    >
                                                      <Trash2 className="h-4 w-4" />
                                                    </Button>
                                                  </div>
                                                </div>
                                              </div>
                                              
                                              {note.content && (
                                                <p className="text-gray-700 text-sm sm:text-base break-words">
                                                  {note.content}
                                                </p>
                                              )}
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                    
                                    {!isCollapsed && !hasNotes && (
                                      <div className="p-4 text-center py-8 text-gray-500">
                                        <Edit className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                        <p className="text-sm">Aucune note pour ce mois</p>
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                              
                            {/* Archives Section */}
                            {Object.keys(archives).length > 0 && (
                              <div className="border-t-2 border-gray-300 pt-6 mt-8">
                                <h4 className="text-sm font-medium text-gray-500 mb-4 text-center">archives</h4>
                                <div className="space-y-4">
                                  {Object.entries(archives)
                                    .sort(([, a], [, b]) => b.order - a.order) // Most recent archive first
                                    .map(([monthKey, monthInfo]) => {
                                      const isCollapsed = collapsedMonths.has(monthKey);
                                      const hasNotes = monthInfo.notes.length > 0;
                                      
                                      return (
                                        <div key={monthKey} className="border border-gray-200 rounded-xl overflow-hidden">
                                          <div 
                                            className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 cursor-pointer hover:from-gray-100 hover:to-gray-150 transition-colors"
                                            onClick={() => toggleMonthCollapse(monthKey)}
                                          >
                                            <div className="flex items-center space-x-3">
                                              <div className={`w-3 h-3 rounded-full transition-transform duration-200 ${isCollapsed ? 'rotate-0' : 'rotate-90'}`}>
                                                <ChevronRight className="w-3 h-3 text-gray-600" />
                                              </div>
                                              <h3 className="text-md font-medium text-gray-700">
                                                📅 {monthInfo.label}
                                              </h3>
                                              <Badge variant="secondary" className="bg-gray-200 text-gray-600">
                                                {monthInfo.notes.length}
                                              </Badge>
                                            </div>
                                          </div>
                                          
                                          {!isCollapsed && hasNotes && (
                                            <div className="p-3">
                                              <div className="grid gap-3">
                                                {monthInfo.notes.map((note, index) => (
                                                  <div key={note.note_id || `archive_${monthKey}_${index}`} className="card-glass p-3 sm:p-4 rounded-xl border border-gray-200">
                                                    {/* Simplified archive note display */}
                                                    <div className="flex items-start justify-between mb-2">
                                                      <div className="flex-1 min-w-0">
                                                        <div className="flex items-center space-x-2 mb-1">
                                                          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                                                            note.priority === 'high' ? 'bg-red-500' :
                                                            note.priority === 'normal' ? 'bg-yellow-500' : 'bg-green-500'
                                                          }`}></div>
                                                          <h4 className="font-medium text-gray-800 truncate text-sm">
                                                            {note.description || note.title || 'Note sans titre'}
                                                          </h4>
                                                        </div>
                                                      </div>
                                                      
                                                      <div className="flex items-center space-x-1 ml-2">
                                                        <Button
                                                          onClick={() => handleEditNote(note)}
                                                          variant="ghost"
                                                          size="sm"
                                                          className="p-1 h-6 w-6 text-blue-600 hover:text-blue-800 hover:bg-blue-50"
                                                          title="Modifier cette note"
                                                        >
                                                          <Edit className="h-3 w-3" />
                                                        </Button>
                                                        
                                                        <Button
                                                          onClick={() => handleDeleteNote(note.note_id)}
                                                          variant="ghost"
                                                          size="sm"
                                                          className="p-1 h-6 w-6 text-red-600 hover:text-red-800 hover:bg-red-50"
                                                          title="Supprimer cette note"
                                                        >
                                                          <Trash2 className="h-3 w-3" />
                                                        </Button>
                                                      </div>
                                                    </div>
                                                    
                                                    {note.content && (
                                                      <p className="text-gray-600 text-xs break-words">
                                                        {note.content}
                                                      </p>
                                                    )}
                                                  </div>
                                                ))}
                                              </div>
                                            </div>
                                          )}
                                        </div>
                                      );
                                    })}
                                </div>
                              </div>
                            )}
                          </>
                        );
                      })()}
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
                  <div className="flex flex-col sm:flex-row gap-4 items-center justify-center">
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
                    
                    {/* Bouton de suppression - affiché seulement si des posts existent */}
                    {generatedPosts.length > 0 && (
                      <Button
                        onClick={handleDeleteAllPosts}
                        disabled={isGeneratingPosts}
                        variant="outline"
                        className="px-6 py-4 text-red-600 border-red-300 hover:bg-red-50 font-medium"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Supprimer tous les posts
                      </Button>
                    )}
                  </div>
                </div>

                {/* Organisation mensuelle des posts générés */}
                {generatedPosts.length > 0 ? (
                  <div className="space-y-6">
                    {renderPostsByMonth()}
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

                {/* Modal d'aperçu de post */}
                {selectedPost && (
                  <PostPreviewModal
                    post={selectedPost}
                    onClose={() => setSelectedPost(null)}
                    onModify={handleModifyPost}
                    onValidate={handleValidatePost}
                    isModifying={isModifyingPost}
                    modificationRequestRef={modificationRequestRef}
                  />
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
                  <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-purple-500 rounded-2xl flex items-center justify-center">
                    <ShareIcon className="w-6 h-6 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                    Connexions réseaux sociaux 📱
                  </span>
                </CardTitle>
                <CardDescription className="text-lg text-gray-600">
                  Connectez vos comptes pour publier automatiquement vos posts ⚡
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                
                {/* Instagram Connection */}
                <div className="bg-white rounded-2xl p-4 sm:p-6 border border-gray-100 hover:shadow-lg transition-shadow social-connection-card">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between social-connection-content">
                    <div className="flex items-center space-x-4 flex-1 min-w-0">
                      <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-purple-500 rounded-xl flex items-center justify-center flex-shrink-0">
                        <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24" style={{aspectRatio: '1'}}>
                          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900">Instagram</h3>
                        <p className="text-sm text-gray-500 truncate">
                          {connectedAccounts.instagram ? 
                            `Connecté : @${connectedAccounts.instagram.username}` : 
                            'Publiez automatiquement sur Instagram'
                          }
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3 mt-4 sm:mt-0 social-connection-buttons">
                      {connectedAccounts.instagram ? (
                        <>
                          <div className="flex items-center justify-center space-x-2 text-green-600 px-3 py-2">
                            <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
                            <span className="text-sm font-medium">Connecté</span>
                          </div>
                          <button
                            onClick={() => disconnectAccount('instagram')}
                            className="px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors social-disconnect-button"
                          >
                            Déconnecter
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={connectInstagram}
                          disabled={isConnectingAccount}
                          className="px-6 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-lg hover:from-pink-600 hover:to-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 social-connect-button"
                        >
                          {isConnectingAccount ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin flex-shrink-0"></div>
                              <span>Connexion...</span>
                            </>
                          ) : (
                            <>
                              <PlusIcon className="w-4 h-4 flex-shrink-0" />
                              <span>Connecter</span>
                            </>
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Facebook Connection - Coming Soon */}
                <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100 opacity-75">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center flex-shrink-0">
                        <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24" style={{aspectRatio: '1'}}>
                          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900">Facebook</h3>
                        <p className="text-sm text-gray-500 truncate">Publiez sur vos pages Facebook</p>
                      </div>
                    </div>
                    
                    <div className="px-4 py-2 bg-gray-200 text-gray-500 rounded-lg cursor-not-allowed">
                      Bientôt disponible
                    </div>
                  </div>
                </div>

                {/* LinkedIn Connection - Coming Soon */}
                <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100 opacity-75">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-blue-700 rounded-xl flex items-center justify-center flex-shrink-0">
                        <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24" style={{aspectRatio: '1'}}>
                          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900">LinkedIn</h3>
                        <p className="text-sm text-gray-500 truncate">Partagez sur votre profil professionnel</p>
                      </div>
                    </div>
                    
                    <div className="px-4 py-2 bg-gray-200 text-gray-500 rounded-lg cursor-not-allowed">
                      Bientôt disponible
                    </div>
                  </div>
                </div>

                {/* Status Message */}
                {socialConnectionStatus && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800 text-center">{socialConnectionStatus}</p>
                  </div>
                )}

                {/* Instructions */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                  <h4 className="text-lg font-semibold text-purple-900 mb-3 flex items-center">
                    <InformationCircleIcon className="w-5 h-5 mr-2" />
                    Comment ça marche ?
                  </h4>
                  <div className="space-y-3 text-purple-700">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                      <p>Connectez votre compte Instagram en cliquant sur "Connecter"</p>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                      <p>Générez vos posts dans l'onglet "Posts"</p>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                      <p>Cliquez sur "Valider" pour publier automatiquement à la date programmée</p>
                    </div>
                  </div>
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
        
        {/* Modal de choix pour sauvegarder Pixabay */}
        {showPixabaySaveModal && selectedPixabayImage && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Où souhaitez-vous sauvegarder cette image ?
                </h3>
                <p className="text-sm text-gray-600">
                  Choisissez comment organiser cette image Pixabay
                </p>
              </div>
              
              {/* Preview de l'image */}
              <div className="mb-4">
                <img 
                  src={selectedPixabayImage.webformatURL} 
                  alt="Pixabay preview"
                  className="w-full h-32 object-cover rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Tags originaux: {selectedPixabayImage.tags}
                </p>
              </div>
              
              {/* Champs personnalisables */}
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Titre personnalisé
                  </label>
                  <input
                    ref={pixabayTitleRef}
                    type="text"
                    placeholder="Titre pour cette image..."
                    className="w-full p-3 border border-gray-300 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none"
                    style={{
                      fontSize: '16px',
                      lineHeight: '1.5',
                      WebkitAppearance: 'none',
                      WebkitBorderRadius: '8px',
                      borderRadius: '8px',
                      touchAction: 'manipulation'
                    }}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contexte d'utilisation
                  </label>
                  <textarea
                    ref={pixabayContextRef}
                    placeholder="Décrivez comment vous voulez utiliser cette image..."
                    rows={3}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-500 focus:outline-none resize-none"
                    style={{
                      fontSize: '16px',
                      lineHeight: '1.5',
                      WebkitAppearance: 'none',
                      WebkitBorderRadius: '8px',
                      borderRadius: '8px',
                      touchAction: 'manipulation'
                    }}
                  />
                </div>
              </div>
              
              {/* Choix de sauvegarde */}
              <div className="space-y-3 mb-6">
                <Button
                  onClick={savePixabayToLibrary}
                  disabled={isSavingPixabayImage === selectedPixabayImage.id}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                >
                  <ImageIcon className="w-4 h-4 mr-2" />
                  Ajouter au stock d'images Pixabay
                </Button>
                
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">ou</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700">Attribuer à un mois spécifique :</p>
                  {(() => {
                    const { currentAndFuture } = getMonthlyContentData();
                    return Object.entries(currentAndFuture)
                      .sort(([, a], [, b]) => a.order - b.order)
                      .map(([monthKey, monthInfo]) => (
                        <Button
                          key={monthKey}
                          onClick={() => savePixabayToMonth(monthKey)}
                          disabled={isSavingPixabayImage === selectedPixabayImage.id}
                          variant="outline"
                          className={`w-full border-purple-300 hover:bg-purple-50 ${
                            monthInfo.isCurrent 
                              ? 'text-green-600 border-green-300 hover:bg-green-50'
                              : 'text-purple-600'
                          }`}
                        >
                          <Calendar className="w-4 h-4 mr-2" />
                          {monthInfo.label}
                          {monthInfo.isCurrent && <span className="ml-1 text-xs">(actuel)</span>}
                        </Button>
                      ));
                  })()}
                </div>
              </div>
              
              {/* Boutons d'action */}
              <div className="flex space-x-3">
                <Button
                  onClick={() => {
                    // Close modal and reset fields
                    setShowPixabaySaveModal(false);
                    setSelectedPixabayImage(null);
                    if (pixabayTitleRef.current) pixabayTitleRef.current.value = '';
                    if (pixabayContextRef.current) pixabayContextRef.current.value = '';
                  }}
                  variant="outline"
                  className="flex-1"
                  disabled={isSavingPixabayImage === selectedPixabayImage.id}
                >
                  Annuler
                </Button>
              </div>
              
              {/* Loading indicator */}
              {isSavingPixabayImage === selectedPixabayImage.id && (
                <div className="mt-4 text-center">
                  <div className="inline-flex items-center text-sm text-gray-600">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mr-2"></div>
                    Sauvegarde en cours...
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Modal de déplacement de contenu */}
        {showMoveModal && contentToMove && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  📅 Déplacer vers un autre mois
                </h3>
                <p className="text-sm text-gray-600">
                  Vers quel mois souhaitez-vous déplacer ce contenu ?
                </p>
              </div>
              
              {/* Preview du contenu */}
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gray-200 rounded-lg flex-shrink-0 overflow-hidden">
                    {contentToMove.thumb_url ? (
                      <img 
                        src={`${contentToMove.thumb_url}?token=${localStorage.getItem('access_token')}`}
                        alt={contentToMove.title || 'Contenu'}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                        <FileText className="w-6 h-6 text-gray-400" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">
                      {contentToMove.title || contentToMove.filename || 'Sans titre'}
                    </p>
                    <p className="text-sm text-gray-500">
                      Actuellement dans: {contentToMove.attributed_month || 'Aucun mois'}
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Sélection du mois */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Choisir le mois de destination :
                </label>
                <div className="grid grid-cols-1 gap-2 max-h-60 overflow-y-auto">
                  {getAvailableMonths().map((month) => (
                    <button
                      key={month.key}
                      onClick={() => moveContentToMonth(month.key)}
                      disabled={isMovingContent || month.key === contentToMove.attributed_month}
                      className={`p-3 text-left rounded-lg border transition-colors ${
                        month.key === contentToMove.attributed_month
                          ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                          : 'bg-white hover:bg-orange-50 border-gray-200 hover:border-orange-300 text-gray-900'
                      }`}
                    >
                      <div className="font-medium capitalize">
                        {month.label}
                      </div>
                      {month.key === contentToMove.attributed_month && (
                        <div className="text-xs text-gray-500 mt-1">
                          Mois actuel
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Actions */}
              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowMoveModal(false);
                    setContentToMove(null);
                  }}
                  disabled={isMovingContent}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium transition-colors"
                >
                  Annuler
                </button>
              </div>
              
              {/* Loading indicator */}
              {isMovingContent && (
                <div className="mt-4 flex items-center justify-center">
                  <div className="flex items-center space-x-2 text-orange-600">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Déplacement en cours...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Modal d'attachement d'image */}
        {showImageAttachModal && postToAttachImage && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
              {/* Header avec texte du post */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl flex items-center justify-center">
                    <ImageIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-800">
                      {imageAttachmentMode === 'modify' ? 'Modifier l\'image du post' : 'Ajouter une image au post'}
                    </h3>
                    <p className="text-sm text-gray-600">"{postToAttachImage.title || 'Post généré'}"</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowImageAttachModal(false)}
                  className="w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-colors"
                >
                  <X className="w-4 h-4 text-gray-600" />
                </button>
              </div>

              {/* Zone de texte du post - collapsible */}
              <div className="border-b border-gray-100">
                <PostTextPreview postText={postToAttachImage.text} />
              </div>

              {/* Tabs */}
              <div className="flex border-b border-gray-200">
                <button
                  onClick={() => setAttachImageTab('library')}
                  className={`flex-1 px-6 py-3 font-medium text-sm transition-colors ${
                    attachImageTab === 'library'
                      ? 'border-b-2 border-orange-500 text-orange-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  📚 Ma Bibliothèque
                </button>
                <button
                  onClick={() => setAttachImageTab('pixabay')}
                  className={`flex-1 px-6 py-3 font-medium text-sm transition-colors ${
                    attachImageTab === 'pixabay'
                      ? 'border-b-2 border-orange-500 text-orange-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  🔍 Pixabay
                </button>
                <button
                  onClick={() => setAttachImageTab('upload')}
                  className={`flex-1 px-6 py-3 font-medium text-sm transition-colors ${
                    attachImageTab === 'upload'
                      ? 'border-b-2 border-orange-500 text-orange-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  📤 Upload
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6">
                <ImageAttachmentContent
                  activeTab={attachImageTab}
                  onAttachImage={attachImageToPost}
                  isAttaching={isAttachingImage}
                  // Réutiliser les états et fonctions existants
                  pendingContent={pendingContent}
                  pixabayResults={pixabayResults}
                  isSearchingPixabay={isSearchingPixabay}
                  searchPixabay={searchPixabay}
                  handleFileSelect={handleFileSelect}
                  selectedFiles={selectedFiles}
                  isUploading={isUploading}
                  handleBatchUpload={handleBatchUpload}
                  // Nouvelles props pour posts
                  postToAttachImage={postToAttachImage}
                  uploadFilesForPost={uploadFilesForPost}
                  // Props pour organisation mensuelle
                  getMonthlyContentData={getMonthlyContentData}
                  collapsedMonths={collapsedMonths}
                  toggleMonthCollapse={toggleMonthCollapse}
                  // Nouvelle prop pour supprimer des fichiers
                  onRemoveFile={handleRemoveSelectedFile}
                />
              </div>
            </div>
          </div>
        )}
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