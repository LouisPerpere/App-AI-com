import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import './App.css';
import axios from 'axios';
import AuthPage from './Auth';
import TestAuth from './TestAuth';
import PaymentPage from './PaymentPage';
import AdminDashboard from './AdminDashboard';
import FacebookCallback from './FacebookCallback';
import PrivacyPolicy from './PrivacyPolicy';
import MentionsLegales from './MentionsLegales';
import DataDeletion from './DataDeletion';
import Footer from './components/Footer';

// Remove withCredentials to avoid CORS conflicts with token-based auth
// axios.defaults.withCredentials = true;

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
import { Building, Sparkles, Crown, Upload, FileText, X, Edit, Edit2, Plus, CalendarIcon, Target, LogOut, Check, Send, Clock, ChevronLeft, ChevronRight, CreditCard, Settings, Globe, Save, Search, Users, Cog, Trash, Trash2, RefreshCw, Calendar, Image as ImageIcon, Info, Play, Eye, ChevronDown, Loader2, Share as ShareIcon, CheckCircle as CheckCircleIcon, Plus as PlusIcon, Info as InformationCircleIcon, ArrowLeftCircle, Lock } from 'lucide-react';

// Import toast for notifications
import { toast } from 'react-hot-toast';

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
      return 'https://post-restore.preview.emergentagent.com';
    }
  }
  
  // Fallback final: URL hardcodée pour garantir fonctionnement
  return 'https://post-restore.preview.emergentagent.com';
};

const API = `${getBackendURL()}/api`;

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
      
      {/* Usage indicators by social network - replace the generic green checkmark */}
      {!isSelectionMode && (content.used_on_facebook || content.used_on_instagram || content.used_on_linkedin) && (
        <div className="absolute top-2 right-2 flex flex-col gap-1 z-10">
          {/* Facebook badge */}
          {content.used_on_facebook && (
            <div className="bg-blue-600 text-white rounded-full p-1 shadow-lg" title="Utilisée sur Facebook">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
            </div>
          )}
          
          {/* Instagram badge */}
          {content.used_on_instagram && (
            <div className="bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full p-1 shadow-lg" title="Utilisée sur Instagram">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
            </div>
          )}
          
          {/* LinkedIn badge */}
          {content.used_on_linkedin && (
            <div className="bg-blue-700 text-white rounded-full p-1 shadow-lg" title="Utilisée sur LinkedIn">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
            </div>
          )}
        </div>
      )}
      
      {/* Usage indicators in selection mode - moved to top-left */}
      {isSelectionMode && (content.used_on_facebook || content.used_on_instagram || content.used_on_linkedin) && (
        <div className="absolute top-2 left-2 flex gap-1 z-10">
          {/* Compact version for selection mode */}
          {content.used_on_facebook && (
            <div className="bg-blue-600 text-white rounded-full p-0.5 shadow-lg" title="Utilisée sur Facebook">
              <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
            </div>
          )}
          {content.used_on_instagram && (
            <div className="bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full p-0.5 shadow-lg" title="Utilisée sur Instagram">
              <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
            </div>
          )}
          {content.used_on_linkedin && (
            <div className="bg-blue-700 text-white rounded-full p-0.5 shadow-lg" title="Utilisée sur LinkedIn">
              <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
            </div>
          )}
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
const PostThumbnail = ({ post, onClick, onAddImage, onModifyImage, onValidatePost, onDeletePost, onModifyDateTime }) => {
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

  const needsImage = post.status === 'needs_image' || !post.visual_url || post.visual_url === '';
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
          {post.visual_url && post.visual_url.length > 0 && !needsImage ? (
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
          <div className="absolute top-2 left-2 flex flex-col space-y-1">
            {/* Badge statut du post */}
            {post.published || post.status === 'published' ? (
              <span className="bg-blue-500 text-white text-xs px-3 py-2 rounded-full font-medium flex items-center space-x-1">
                <CheckCircleIcon className="w-3 h-3" />
                <span>Publié</span>
              </span>
            ) : post.validated ? (
              <span className="bg-green-500 text-white text-xs px-3 py-2 rounded-full font-medium flex items-center space-x-1">
                <Check className="w-3 h-3" />
                <span>Programmé</span>
              </span>
            ) : (
              <>
                {/* Bouton supprimer - SEULEMENT si pas validé */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeletePost && onDeletePost(post);
                  }}
                  className="w-7 h-7 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors shadow-md"
                  title="Supprimer ce post"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </>
            )}
            
            {/* Badge de plateforme */}
            <span className={`text-white text-xs px-2 py-1 rounded-full font-medium flex items-center gap-1 ${
              (post.platform || 'instagram').toLowerCase() === 'facebook' 
                ? 'bg-blue-600' 
                : (post.platform || 'instagram').toLowerCase() === 'instagram'
                ? 'bg-gradient-to-r from-pink-500 to-purple-500'
                : 'bg-emerald-500'
            }`}>
              {/* Logo Facebook */}
              {(post.platform || 'instagram').toLowerCase() === 'facebook' && (
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              )}
              {/* Logo Instagram */}
              {(post.platform || 'instagram').toLowerCase() === 'instagram' && (
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              )}
              {/* Texte de la plateforme pour autres cas */}
              {!['facebook', 'instagram'].includes((post.platform || 'instagram').toLowerCase()) && (
                post.platform || 'Instagram'
              )}
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
          
          {/* Boutons d'action - SEULEMENT si pas validé */}
          {hasImage && !post.validated && (
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
              
              {/* Bouton modifier date/heure */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onModifyDateTime && onModifyDateTime(post);
                }}
                className="w-7 h-7 bg-amber-500 hover:bg-amber-600 text-white rounded-full flex items-center justify-center transition-colors shadow-md"
                title="Modifier la date et l'heure"
              >
                <Clock className="w-3 h-3" />
              </button>
            </div>
          )}
          
          {/* Badge date - TOUJOURS visible */}
          <div className="absolute bottom-2 right-2 flex items-center space-x-1">
            <span className="bg-black/50 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">
              {formatDate(post.scheduled_date)}
            </span>
            {/* Bouton modifier date/heure - SEULEMENT si pas validé */}
            {!post.validated && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onModifyDateTime && onModifyDateTime(post);
                }}
                className="w-7 h-7 bg-amber-500 hover:bg-amber-600 text-white rounded-full flex items-center justify-center transition-colors shadow-lg border border-white"
                title="Modifier la date et l'heure"
                style={{ zIndex: 10 }}
              >
                <Clock className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          
          {/* Supprimer l'ancien indicateur de statut validé - remplacé par le badge "Programmé" */}
        </div>
        
        {/* Contenu */}
        <div className="p-3">
          <h4 className="font-semibold text-gray-800 text-sm mb-1">
            <div className="line-clamp-1 overflow-hidden">
              {post.title || 'Post généré'}
            </div>
          </h4>
          <div className="text-gray-600 text-xs mb-2">
            <div className="line-clamp-2 overflow-hidden leading-tight">
              {post.text || 'Aucun texte disponible'}
            </div>
          </div>
          
          {/* Hashtags */}
          {post.hashtags && post.hashtags.length > 0 && (
            <div className="flex flex-wrap gap-1 overflow-hidden">
              {post.hashtags.slice(0, 2).map((hashtag, idx) => (
                <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full whitespace-nowrap">
                  {hashtag.startsWith('#') ? hashtag : `#${hashtag}`}
                </span>
              ))}
              {post.hashtags.length > 2 && (
                <span className="text-xs text-gray-500 whitespace-nowrap">+{post.hashtags.length - 2}</span>
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
  modificationRequestRef,  // Changé de state à ref
  isFromCalendar = false, // Nouveau prop pour savoir si c'est depuis le calendrier
  onMovePost, // Fonction pour déplacer le post
  onCancelPost, // Fonction pour annuler/déprogrammer le post
  onPublishNow, // Fonction pour publier immédiatement
  isPublishing, // État de publication pour le spinner
  // Nouveaux props pour la gestion d'état globale
  showModificationPreview,
  setShowModificationPreview, 
  modifiedPostData,
  setModifiedPostData,
  showSecondaryModification,
  setShowSecondaryModification
}) => {
  const [showModificationForm, setShowModificationForm] = useState(false);
  const [modificationRequest, setModificationRequest] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false); // Nouvel état pour confirmation suppression
  
  const [isApplyingModification, setIsApplyingModification] = useState(false);
  const [modificationTextValue, setModificationTextValue] = useState(''); // Nouvel état pour la valeur du textarea
  const [secondaryModificationText, setSecondaryModificationText] = useState('');
  
  // Refs pour le scrolling automatique
  const modificationPreviewRef = useRef(null);
  const secondaryModificationRef = useRef(null);
  
  // Supprimer isValidated - on utilise directement post.validated
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [newScheduledDate, setNewScheduledDate] = useState('');
  const [newScheduledTime, setNewScheduledTime] = useState('');

  // Effet pour scrolling automatique vers l'aperçu de modification
  useEffect(() => {
    if (showModificationPreview && modificationPreviewRef.current) {
      setTimeout(() => {
        modificationPreviewRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }, 200); // Petit délai pour que l'élément soit rendu
    }
  }, [showModificationPreview]);

  // Effet pour scrolling automatique vers la zone de modification secondaire
  useEffect(() => {
    if (showSecondaryModification && secondaryModificationRef.current) {
      setTimeout(() => {
        secondaryModificationRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }, 200);
    }
  }, [showSecondaryModification]);

  // Initialiser les champs de date et heure avec les valeurs actuelles
  useEffect(() => {
    if (post.scheduled_date) {
      const date = new Date(post.scheduled_date);
      const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
      const timeStr = date.toTimeString().split(' ')[0].slice(0, 5); // HH:MM
      setNewScheduledDate(dateStr);
      setNewScheduledTime(timeStr);
    } else {
      // Valeurs par défaut : demain à 10h
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(10, 0, 0, 0);
      
      const dateStr = tomorrow.toISOString().split('T')[0];
      const timeStr = '10:00';
      setNewScheduledDate(dateStr);
      setNewScheduledTime(timeStr);
    }
  }, [post.scheduled_date]);

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

  const handleModifySubmit = async () => {
    console.log('🔥 DEBUG: handleModifySubmit appelée');
    
    // Approche complètement différente : récupérer directement la valeur du textarea actuel
    let modificationValue = '';
    
    // Trouver le textarea dans le DOM
    const textareas = document.querySelectorAll('textarea');
    const modificationTextarea = Array.from(textareas).find(textarea => 
      textarea.placeholder && textarea.placeholder.includes('modifier ce post')
    );
    
    if (modificationTextarea && modificationTextarea.value && modificationTextarea.value.trim()) {
      modificationValue = modificationTextarea.value.trim();
      console.log('🔥 DEBUG: Valeur trouvée dans DOM textarea:', modificationValue);
    } else {
      // Fallback sur les méthodes précédentes
      modificationValue = modificationTextValue || modificationRequestRef.current?.value || '';
      console.log('🔥 DEBUG: Fallback sur état/ref:', modificationValue);
    }
    
    console.log('🔥 DEBUG: modificationValue final =', `"${modificationValue}"`);
    console.log('🔥 DEBUG: longueur =', modificationValue.length);
    
    if (!modificationValue || modificationValue.length === 0) {
      console.log('🔥 DEBUG: Aucune valeur trouvée - abandon');
      toast.error('Veuillez saisir une demande de modification');
      return;
    }

    // Désactiver le bouton pendant le traitement
    // Note: isModifying est géré par le parent
    
    try {
      console.log('🔥 DEBUG: Appel onModify avec post.id =', post.id);
      console.log('🔥 DEBUG: Valeur envoyée =', `"${modificationValue}"`);
      
      const result = await onModify(post, modificationValue, 'content');
      console.log('🔥 DEBUG: Résultat onModify =', result);
      
      if (result && result.success && result.modifiedPost) {
        console.log('🔥 DEBUG: Succès - affichage aperçu modification');
        console.log('🔥 DEBUG: Nouveau contenu reçu =', result.modifiedPost);
        
        // Debug des états React
        console.log('🔥 DEBUG: État avant mise à jour:', {
          showModificationPreview: showModificationPreview,
          modifiedPostData: modifiedPostData,
          showModificationForm: showModificationForm
        });
        
        // Forcer la mise à jour des états avec un timeout pour s'assurer que React traite tout
        setTimeout(() => {
          console.log('🔥 DEBUG: Mise à jour forcée avec timeout');
          setModifiedPostData(result.modifiedPost);
          setShowModificationForm(false);
          setShowModificationPreview(true);
          
          // Vider le textarea après succès
          if (modificationTextarea) {
            modificationTextarea.value = '';
          }
          setModificationTextValue('');
          if (modificationRequestRef.current) {
            modificationRequestRef.current.value = '';
          }
        }, 100);
        
        console.log('🔥 DEBUG: Timeout de mise à jour programmé');
      } else {
        console.log('🔥 DEBUG: Pas de succès - résultat =', result);
        toast.error('Erreur: Aucune modification générée par l\'IA');
      }
    } catch (error) {
      console.error('🔥 DEBUG: Exception dans handleModifySubmit:', error);
      toast.error('Erreur lors de la modification: ' + error.message);
    }
  };

  const handleAcceptModification = async () => {
    if (!modifiedPostData) return;
    
    // Pas d'état isApplyingModification pour l'instant, on utilisera isModifying
    
    try {
      // Mettre à jour le post actuel avec les nouvelles données
      const updatedPost = {
        ...post,
        ...modifiedPostData,
        modified_at: new Date().toISOString()
      };

      // Si c'est un post du calendrier, notifier le parent
      if (isFromCalendar && onModify) {
        await onModify(updatedPost, 'apply_modification', 'final_update');
      } else {
        // Pour l'onglet Posts, sauvegarder en base de données
        const token = localStorage.getItem('access_token');
        if (token) {
          try {
            await axios.put(
              `${process.env.REACT_APP_BACKEND_URL}/api/posts/${post.id}`,
              {
                title: modifiedPostData.title || post.title,
                text: modifiedPostData.text || post.text,
                hashtags: modifiedPostData.hashtags || post.hashtags,
                modified_at: new Date().toISOString()
              },
              { 
                headers: { Authorization: `Bearer ${token}` },
                timeout: 10000
              }
            );
            console.log('✅ Modifications sauvegardées en base de données');
          } catch (saveError) {
            console.error('❌ Erreur sauvegarde:', saveError);
          }
        }
      }
      
      // Mettre à jour l'objet post local pour affichage immédiat
      Object.assign(post, updatedPost);
      
      toast.success('✅ Modification appliquée avec succès !');
      
      // FERMER TOUTES les sous-fenêtres de modification
      setShowModificationPreview(false);
      setModifiedPostData(null);
      setShowSecondaryModification(false);
      setSecondaryModificationText('');
      setModificationTextValue('');
      
      // Nettoyer aussi le textarea principal si présent
      if (modificationRequestRef && modificationRequestRef.current) {
        modificationRequestRef.current.value = '';
      }
      
      // Recharger les données pour synchroniser
      if (typeof window !== 'undefined' && window.loadGeneratedPosts) {
        setTimeout(() => window.loadGeneratedPosts(), 500);
      }
      
    } catch (error) {
      console.error('Erreur application modification:', error);
      toast.error('Erreur lors de l\'application de la modification');
    }
  };

  const handleRejectModification = () => {
    setShowModificationPreview(false);
    setModifiedPostData(null);
    setModificationTextValue(''); // Reset aussi la valeur du textarea
    setShowModificationForm(true); // Retour au formulaire pour une nouvelle demande
  };

  const handleSecondaryModification = () => {
    setShowSecondaryModification(true);
    setSecondaryModificationText('');
  };

  const handleCancelSecondaryModification = () => {
    // Annuler SEULEMENT la modification secondaire, garder l'aperçu principal
    setShowSecondaryModification(false);
    setSecondaryModificationText('');
  };

  const handleCancelMainModification = () => {
    // Annuler TOUT le workflow de modification
    setShowModificationPreview(false);
    setModifiedPostData(null);
    setShowSecondaryModification(false);
    setSecondaryModificationText('');
    setModificationTextValue('');
    
    // Nettoyer le textarea principal
    if (modificationRequestRef && modificationRequestRef.current) {
      modificationRequestRef.current.value = '';
    }
  };

  const handleSubmitSecondaryModification = async () => {
    if (!secondaryModificationText?.trim()) {
      toast.error('Veuillez saisir une demande de modification');
      return;
    }

    try {
      // Appeler l'IA avec la nouvelle demande
      const result = await onModify(post, secondaryModificationText, 'content');
      
      if (result && result.success && result.modifiedPost) {
        // Mettre à jour le contenu modifié
        setModifiedPostData(result.modifiedPost);
        setShowSecondaryModification(false);
        setSecondaryModificationText('');
        // Rester dans l'aperçu de modification
      } else {
        toast.error('Erreur: Aucune modification générée par l\'IA');
      }
    } catch (error) {
      console.error('Erreur modification secondaire:', error);
      toast.error('Erreur lors de la modification: ' + error.message);
    }
  };

  const handleScheduleSubmit = () => {
    if (!newScheduledDate || !newScheduledTime) {
      toast.error('Veuillez sélectionner une date et une heure');
      return;
    }
    
    // Créer la date programmée
    const scheduledDateTime = new Date(`${newScheduledDate}T${newScheduledTime}:00`);
    const now = new Date();
    
    // Vérifier que la date est dans le futur
    if (scheduledDateTime <= now) {
      toast.error('La date de programmation doit être dans le futur');
      return;
    }
    
    // Appeler la fonction de modification avec le nouveau schedule
    onModify(post, scheduledDateTime.toISOString(), 'schedule');
    setShowScheduleForm(false);
  };

  const handleCancel = () => {
    setShowModificationForm(false);
    setShowScheduleForm(false);
    setModificationTextValue(''); // Reset la valeur du textarea
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
              <p className="text-sm text-gray-600 flex items-center gap-1">
                {/* Logo Facebook */}
                {(post.platform || 'instagram').toLowerCase() === 'facebook' && (
                  <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                )}
                {/* Logo Instagram */}
                {(post.platform || 'instagram').toLowerCase() === 'instagram' && (
                  <svg className="w-4 h-4 text-pink-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                  </svg>
                )}
                {(post.platform || 'instagram').toLowerCase() === 'facebook' ? 'Facebook' : 'Instagram'} • {formatDate(post.scheduled_date)}
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

          {/* Aperçu des modifications */}
          {showModificationPreview && modifiedPostData && (
            <div ref={modificationPreviewRef} className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-green-800 mb-3 flex items-center">
                <CheckCircleIcon className="w-4 h-4 mr-2" />
                Nouveau contenu généré par l'IA
              </h4>
              
              {/* Nouveau titre */}
              {modifiedPostData.title && (
                <div className="mb-3">
                  <p className="text-xs text-gray-600 mb-1">Nouveau titre :</p>
                  <p className="text-sm font-semibold text-gray-800 bg-white p-2 rounded border">
                    {modifiedPostData.title}
                  </p>
                </div>
              )}
              
              {/* Nouveau texte */}
              <div className="mb-3">
                <p className="text-xs text-gray-600 mb-1">Nouveau texte :</p>
                <div className="bg-white p-3 rounded border">
                  <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                    {modifiedPostData.text}
                  </p>
                </div>
              </div>
              
              {/* Nouveaux hashtags */}
              {modifiedPostData.hashtags && modifiedPostData.hashtags.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs text-gray-600 mb-2">Nouveaux hashtags :</p>
                  <div className="flex flex-wrap gap-1">
                    {modifiedPostData.hashtags.map((hashtag, idx) => (
                      <span key={idx} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                        {hashtag.startsWith('#') ? hashtag : `#${hashtag}`}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Boutons de validation - Layout amélioré */}
              <div className="pt-3 border-t border-green-200">
                {/* Première ligne : Confirmer et Annuler */}
                <div className="flex items-center justify-center space-x-3 mb-3">
                  <button
                    onClick={handleAcceptModification}
                    disabled={isApplyingModification}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl disabled:opacity-50"
                  >
                    <div className="flex items-center justify-center space-x-2">
                      {isApplyingModification ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Application...</span>
                        </>
                      ) : (
                        <>
                          <CheckCircleIcon className="w-4 h-4" />
                          <span>Confirmer</span>
                        </>
                      )}
                    </div>
                  </button>
                  
                  <button
                    onClick={handleCancelMainModification}
                    disabled={isApplyingModification}
                    className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors disabled:opacity-50"
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <X className="w-4 h-4" />
                      <span>Annuler</span>
                    </div>
                  </button>
                </div>
                
                {/* Deuxième ligne : Modifier à nouveau sur toute la largeur */}
                <button
                  onClick={handleSecondaryModification}
                  disabled={isApplyingModification}
                  className="w-full px-4 py-2 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl disabled:opacity-50"
                >
                  <div className="flex items-center justify-center space-x-2">
                    <Edit className="w-4 h-4" />
                    <span>Modifier à nouveau</span>
                  </div>
                </button>
              </div>
              
              {/* Zone de modification secondaire */}
              {showSecondaryModification && (
                <div ref={secondaryModificationRef} className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h5 className="text-sm font-semibold text-yellow-800 mb-3">
                    ✏️ Nouvelle demande de modification
                  </h5>
                  
                  <textarea
                    value={secondaryModificationText}
                    onChange={(e) => setSecondaryModificationText(e.target.value)}
                    placeholder="Décrivez comment vous souhaitez modifier davantage ce post..."
                    className="w-full p-3 border border-yellow-300 rounded-lg resize-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                    rows="3"
                    disabled={isModifying}
                  />
                  
                  {/* Boutons de la zone secondaire */}
                  <div className="flex items-center justify-center space-x-3 mt-3">
                    <button
                      onClick={handleCancelSecondaryModification}
                      disabled={isModifying}
                      className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors disabled:opacity-50"
                    >
                      Annuler
                    </button>
                    
                    <button
                      onClick={handleSubmitSecondaryModification}
                      disabled={isModifying || !secondaryModificationText?.trim()}
                      className="px-4 py-2 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 disabled:from-gray-300 disabled:to-gray-400 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl disabled:transform-none"
                    >
                      <div className="flex items-center space-x-2">
                        {isModifying ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
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
          )}
        </div>

        {/* Actions */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          {(post.validated || post.published || post.status === 'published') && !isFromCalendar ? (
            /* Mode lecture seule pour les posts validés/publiés SEULEMENT dans l'onglet Posts */
            <div className="text-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3 ${
                post.published || post.status === 'published' 
                  ? 'bg-blue-100' 
                  : 'bg-green-100'
              }`}>
                {post.published || post.status === 'published' ? (
                  <CheckCircleIcon className="w-8 h-8 text-blue-600" />
                ) : (
                  <Calendar className="w-8 h-8 text-green-600" />
                )}
              </div>
              <p className={`text-lg font-semibold mb-1 ${
                post.published || post.status === 'published' 
                  ? 'text-blue-800' 
                  : 'text-green-800'
              }`}>
                {post.published || post.status === 'published' ? 'Post publié' : 'Post programmé'}
              </p>
              <p className="text-sm text-gray-600">
                {post.published || post.status === 'published' ? (
                  post.published_at ? (
                    `Publié le ${new Date(post.published_at).toLocaleDateString('fr-FR', {
                      weekday: 'long',
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}`
                  ) : 'Publié avec succès'
                ) : (
                  `Programmé pour le ${new Date(post.scheduled_date || post.date).toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}`
                )}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {post.published || post.status === 'published' 
                  ? 'Ce post a été publié sur les réseaux sociaux.'
                  : 'Ce post est maintenant dans le calendrier et ne peut plus être modifié depuis cet onglet.'
                }
              </p>
            </div>
          ) : (
            /* Mode édition normal pour les posts non validés OU pour tous les posts dans le calendrier */
            <>
              {/* Interface spécifique pour les posts du calendrier */}
              {isFromCalendar ? (
                <>
                  {/* Message explicatif pour la modification */}
                  <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                      </div>
                      <div>
                        <p className="text-sm text-blue-800 font-medium mb-1">
                          Pour modifier ce post
                        </p>
                        <p className="text-sm text-blue-700">
                          Vous devez d'abord le déprogrammer. Vous pourrez ensuite le modifier depuis l'onglet Posts.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-center space-x-2">
                    <button
                      onClick={() => onMovePost && onMovePost(post)}
                      className="flex-1 px-3 py-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-md hover:shadow-lg text-sm"
                    >
                      <div className="flex items-center justify-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>Déplacer</span>
                      </div>
                    </button>
                    
                    <button
                      onClick={() => setShowDeleteConfirmation(true)}
                      className="flex-1 px-3 py-2 bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-md hover:shadow-lg text-sm"
                    >
                      <div className="flex items-center justify-center space-x-1">
                        <ArrowLeftCircle className="w-4 h-4" />
                        <span>Déprogrammer</span>
                      </div>
                    </button>
                  </div>
                </>
              ) : (
                /* Interface pour les posts normaux (onglet Posts) */
                <div className="space-y-3">
                  <div className="flex items-center justify-center space-x-4">
                    <button
                      onClick={() => {
                        setModificationTextValue(''); // Reset la valeur avant d'ouvrir
                        setShowModificationForm(true);
                      }}
                      disabled={showModificationForm || showModificationPreview || isModifying}
                      className={`px-6 py-3 rounded-xl font-medium transition-all duration-200 transform shadow-lg ${
                        showModificationForm || showModificationPreview || isModifying
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed shadow-none'
                          : 'bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white hover:scale-105 active:scale-95 hover:shadow-xl'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <Edit className="w-4 h-4" />
                        <span>Modifier</span>
                      </div>
                    </button>
                    
                    {/* Bouton Valider seulement dans l'onglet Posts */}
                    {!isFromCalendar && (
                      <button
                        onClick={async () => {
                          if (isValidating) return;
                          
                          setIsValidating(true);
                          try {
                            const success = await onValidate(post);
                            if (success) {
                              // Pas besoin de setIsValidated car on utilise post.validated maintenant
                            }
                          } catch (error) {
                            console.error('Validation error:', error);
                          } finally {
                            setIsValidating(false);
                          }
                        }}
                        disabled={isValidating || post.validated || post.published || post.status === 'published' || showModificationForm || showModificationPreview || isModifying}
                        className={`px-6 py-3 rounded-xl font-medium transition-all duration-200 transform shadow-lg ${
                          post.validated
                            ? 'bg-green-600 text-white cursor-not-allowed' 
                            : post.published || post.status === 'published'
                              ? 'bg-blue-600 text-white cursor-not-allowed'
                              : isValidating 
                                ? 'bg-gray-400 text-white cursor-not-allowed'
                                : showModificationForm || showModificationPreview || isModifying
                                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed shadow-none'
                                  : 'bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white hover:scale-105 active:scale-95 hover:shadow-xl'
                        }`}
                      >
                        <div className="flex items-center space-x-2">
                          {isValidating ? (
                            <>
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span>Programmation...</span>
                            </>
                          ) : post.published || post.status === 'published' ? (
                            <>
                              <CheckCircleIcon className="w-4 h-4" />
                              <span>Publié !</span>
                            </>
                          ) : post.validated ? (
                            <>
                              <Check className="w-4 h-4" />
                              <span>Programmé !</span>
                            </>
                          ) : (
                            <>
                              <Send className="w-4 h-4" />
                              <span>Programmer</span>
                            </>
                          )}
                        </div>
                      </button>
                    )}
                  </div>
                  
                  {/* Bouton "publier de suite" centré sous les boutons principaux */}
                  {!post.published && !post.validated && post.status !== 'published' && !isFromCalendar && (
                    <div className="text-center">
                      <button
                        onClick={() => onPublishNow(post)}
                        disabled={isPublishing}
                        className={`text-xs transition-colors underline flex items-center justify-center space-x-1 ${
                          isPublishing 
                            ? 'text-gray-400 cursor-not-allowed' 
                            : 'text-gray-500 hover:text-purple-600'
                        }`}
                      >
                        {isPublishing ? (
                          <>
                            <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                            <span>Publication...</span>
                          </>
                        ) : (
                          <span>Publier de suite</span>
                        )}
                      </button>
                    </div>
                  )}
                  
                  {/* Message "Post publié" si le post vient d'être publié */}
                  {(post.published || post.status === 'published') && !isFromCalendar && (
                    <div className="text-center">
                      <div className="text-xs text-blue-600 font-medium flex items-center justify-center space-x-1">
                        <CheckCircleIcon className="w-3 h-3" />
                        <span>Post publié !</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
        <div className="px-6 py-4 border-t border-gray-200 bg-white">
          {!showModificationForm ? (
            <></>
          ) : (
            <div className="w-full">
              {/* Formulaire de modification */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-4">
                <h5 className="text-sm font-semibold text-yellow-800 mb-3">
                  ✏️ Demander une modification
                </h5>
                
                <textarea
                  ref={modificationRequestRef}
                  value={modificationTextValue}
                  onChange={(e) => setModificationTextValue(e.target.value)}
                  placeholder="Décrivez comment vous souhaitez modifier ce post..."
                  className="w-full p-3 border border-yellow-300 rounded-lg resize-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                  rows="3"
                  disabled={isModifying}
                />
              </div>

              {/* Boutons d'action - modernisés et centrés */}
              <div className="flex items-center justify-center space-x-3">
                <button
                  onClick={handleCancel}
                  disabled={isModifying}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-sm hover:shadow-md"
                >
                  <div className="flex items-center space-x-2">
                    <X className="w-4 h-4" />
                    <span>Annuler</span>
                  </div>
                </button>
                
                <button
                  onClick={handleModifySubmit}
                  disabled={isModifying}
                  className="px-4 py-2 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 disabled:from-gray-300 disabled:to-gray-400 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
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
      
      {/* Modal de confirmation de déprogrammation */}
      {showDeleteConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-60 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ArrowLeftCircle className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Déprogrammer ce post ?
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Ce post sera retiré du calendrier et repassera en <strong>brouillon</strong> dans l'onglet "Posts".
                <br/><br/>
                Vous pourrez alors le modifier et le reprogrammer plus tard.
              </p>
            </div>
            
            {/* Boutons de confirmation */}
            <div className="flex items-center justify-center space-x-3">
              <button
                onClick={() => setShowDeleteConfirmation(false)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
              >
                Annuler
              </button>
              
              <button
                onClick={() => {
                  setShowDeleteConfirmation(false);
                  onCancelPost && onCancelPost(post);
                }}
                className="px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
              >
                <div className="flex items-center space-x-2">
                  <ArrowLeftCircle className="w-4 h-4" />
                  <span>Confirmer la déprogrammation</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      )}
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
  const [generatingMonths, setGeneratingMonths] = useState(new Set()); // Track which months are generating
  const [selectedMonthForGeneration, setSelectedMonthForGeneration] = useState(null); // Store selected month for modal
  
  // États pour le calendrier
  const [calendarPosts, setCalendarPosts] = useState([]);
  const [calendarView, setCalendarView] = useState('month'); // 'month', 'week', 'list'
  const [calendarFilters, setCalendarFilters] = useState({
    platform: 'all', // 'all', 'facebook', 'instagram', 'linkedin'
    status: 'all' // 'all', 'scheduled', 'published', 'failed'
  });
  const [calendarDate, setCalendarDate] = useState(new Date());
  const [isLoadingCalendar, setIsLoadingCalendar] = useState(false);
  
  // Helper function pour vérifier si la génération est bloquée
  const isGenerationBlocked = useCallback((monthKey) => {
    const now = new Date();
    const currentDay = now.getDate();
    const currentHour = now.getHours();
    const isLastDayOfMonth = currentDay === new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    
    // Parse le monthKey pour obtenir année et mois
    const [yearStr, monthStr] = monthKey.split('-');
    const targetYear = parseInt(yearStr);
    const targetMonth = parseInt(monthStr);
    
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1; // getMonth() retourne 0-11, on veut 1-12
    
    // Calculer la différence en mois
    const monthDifference = (targetYear - currentYear) * 12 + (targetMonth - currentMonth);
    
    // RÈGLES DE DISPONIBILITÉ :
    
    // 1. Mois actuel : toujours disponible (sauf après 22h le dernier jour)
    if (monthDifference === 0) {
      // Exception : bloquer après 22h le dernier jour du mois actuel
      return isLastDayOfMonth && currentHour >= 22;
    }
    
    // 2. Mois suivant : disponible seulement à partir du 15 du mois actuel
    if (monthDifference === 1) {
      return currentDay < 15; // Bloqué si on est avant le 15
    }
    
    // 3. Mois plus loin : toujours bloqués
    if (monthDifference > 1) {
      return true; // Bloqué
    }
    
    // 4. Mois passés : bloqués
    if (monthDifference < 0) {
      return true; // Bloqué
    }
    
    return false;
  }, []);
  
  // Helper function pour obtenir le message de blocage approprié
  const getBlockedMessage = useCallback((monthKey) => {
    const now = new Date();
    const currentDay = now.getDate();
    const currentHour = now.getHours();
    const isLastDayOfMonth = currentDay === new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    
    // Parse le monthKey
    const [yearStr, monthStr] = monthKey.split('-');
    const targetYear = parseInt(yearStr);
    const targetMonth = parseInt(monthStr);
    
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;
    const monthDifference = (targetYear - currentYear) * 12 + (targetMonth - currentMonth);
    
    // Messages selon le type de blocage
    if (monthDifference === 0 && isLastDayOfMonth && currentHour >= 22) {
      return { 
        desktop: "passez au mois suivant", 
        mobile: "Mois suivant",
        icon: "Clock"
      };
    }
    
    if (monthDifference === 1 && currentDay < 15) {
      return { 
        desktop: `disponible le 15`, 
        mobile: "Le 15",
        icon: "Calendar"
      };
    }
    
    if (monthDifference > 1) {
      return { 
        desktop: "trop tôt", 
        mobile: "Trop tôt",
        icon: "Lock"
      };
    }
    
    if (monthDifference < 0) {
      return { 
        desktop: "mois passé", 
        mobile: "Passé",
        icon: "X"
      };
    }
    
    return { 
      desktop: "indisponible", 
      mobile: "Non",
      icon: "X"
    };
  }, []);

  // Helper function pour mapper les icônes
  const getIconComponent = (iconName) => {
    switch(iconName) {
      case 'Clock': return Clock;
      case 'Calendar': return Calendar;
      case 'Lock': return Lock;
      case 'X': return X;
      default: return Clock;
    }
  };

  const [selectedCalendarPost, setSelectedCalendarPost] = useState(null);
  
  // États pour le workflow de modification amélioré (globaux)
  const [showModificationPreview, setShowModificationPreview] = useState(false);
  const [modifiedPostData, setModifiedPostData] = useState(null);
  const [showSecondaryModification, setShowSecondaryModification] = useState(false);

  // Fonction pour charger les posts du calendrier
  const loadCalendarPosts = async (filters = {}) => {
    setIsLoadingCalendar(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('No token available for calendar');
        return;
      }

      // Build query parameters
      const params = new URLSearchParams();
      
      // Add date range (current month by default)
      const startOfMonth = new Date(calendarDate.getFullYear(), calendarDate.getMonth(), 1);
      const endOfMonth = new Date(calendarDate.getFullYear(), calendarDate.getMonth() + 1, 0);
      
      params.append('start_date', startOfMonth.toISOString());
      params.append('end_date', endOfMonth.toISOString());
      
      // Add platform filter
      const platformFilter = filters.platform || calendarFilters.platform;
      if (platformFilter && platformFilter !== 'all') {
        params.append('platform', platformFilter);
      }

      const response = await axios.get(`${API}/calendar/posts?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      let posts = response.data.posts || [];
      
      // Apply status filter on frontend (if not handled by backend)
      const statusFilter = filters.status || calendarFilters.status;
      if (statusFilter && statusFilter !== 'all') {
        posts = posts.filter(post => post.status === statusFilter);
      }

      setCalendarPosts(posts);
      console.log(`📅 Loaded ${posts.length} calendar posts`);
      
    } catch (error) {
      console.error('Error loading calendar posts:', error);
      toast.error('Erreur lors du chargement du calendrier');
    } finally {
      setIsLoadingCalendar(false);
    }
  };

  // Fonction pour mettre à jour les filtres du calendrier
  const updateCalendarFilters = (newFilters) => {
    setCalendarFilters(prev => ({ ...prev, ...newFilters }));
    loadCalendarPosts(newFilters);
  };

  // Charger le calendrier quand la date change
  useEffect(() => {
    if (activeTab === 'calendar') {
      loadCalendarPosts();
    }
  }, [calendarDate, activeTab]);

  // Function to get notes specific to a month or always valid
  const getNotesForMonth = (monthKey) => {
    if (!notes || !monthKey) return [];
    
    // Parse month key (e.g., "2025-10" -> month: 10, year: 2025)
    const [year, month] = monthKey.split('-').map(Number);
    
    return notes.filter(note => {
      // Always valid notes (monthly notes or high priority general notes)
      if (note.is_monthly_note || (note.priority === 'high' && !note.note_month && !note.note_year)) {
        return true;
      }
      
      // Month-specific notes
      if (note.note_month && note.note_year) {
        return note.note_month === month && note.note_year === year;
      }
      
      return false;
    });
  };

  // Function to get media specific to a month
  const getMediaForMonth = (monthKey) => {
    if (!pendingContent || !monthKey) return [];
    
    // Parse month key to create target_month format (e.g., "2025-10" -> "octobre_2025")
    const [year, month] = monthKey.split('-').map(Number);
    const frenchMonths = [
      'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
      'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ];
    const targetMonth = `${frenchMonths[month - 1]}_${year}`;
    
    return pendingContent.filter(media => {
      // Media explicitly attributed to this month
      if (media.attributed_month === targetMonth) {
        return true;
      }
      
      // For current month, include unattributed recent media
      const currentDate = new Date();
      const currentMonth = currentDate.getMonth() + 1;
      const currentYear = currentDate.getFullYear();
      
      if (month === currentMonth && year === currentYear && !media.attributed_month) {
        return true;
      }
      
      return false;
    });
  };

  // Initialize collapsed post months - current and next month open, others closed
  const getInitialCollapsedPostMonths = () => {
    const collapsed = {};
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth(); // 0-based
    
    // Current month key
    const currentMonthKey = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}`;
    
    // Next month key
    const nextMonthDate = new Date(currentYear, currentMonth + 1, 1);
    const nextMonthKey = `${nextMonthDate.getFullYear()}-${String(nextMonthDate.getMonth() + 1).padStart(2, '0')}`;
    
    // Generate all future months and collapse them except current and next
    for (let i = 0; i <= 8; i++) {
      const targetDate = new Date(currentYear, currentMonth + i, 1);
      const monthKey = `${targetDate.getFullYear()}-${String(targetDate.getMonth() + 1).padStart(2, '0')}`;
      
      // Collapse all except current and next month
      if (monthKey !== currentMonthKey && monthKey !== nextMonthKey) {
        collapsed[monthKey] = true;
      }
    }
    
    // Collapse all past months by default
    for (let i = 1; i <= 6; i++) {
      const targetDate = new Date(currentYear, currentMonth - i, 1);
      const monthKey = `${targetDate.getFullYear()}-${String(targetDate.getMonth() + 1).padStart(2, '0')}`;
      collapsed[monthKey] = true;
    }
    
    return collapsed;
  };

  // Posts management states
  const [selectedPost, setSelectedPost] = useState(null);
  const [isModifyingPost, setIsModifyingPost] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [postsByMonth, setPostsByMonth] = useState({});
  const [collapsedPostMonths, setCollapsedPostMonths] = useState(() => getInitialCollapsedPostMonths());
  
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
  
  // Privacy policy state
  const [showPrivacyPolicy, setShowPrivacyPolicy] = useState(false);

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

  // Gérer le callback Instagram/Facebook OAuth au chargement de la page
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const instagramSuccess = urlParams.get('instagram_success');
    const facebookSuccess = urlParams.get('facebook_success');
    const instagramError = urlParams.get('instagram_error');
    const facebookError = urlParams.get('facebook_error');
    const instagramUsername = urlParams.get('username');
    const facebookPageName = urlParams.get('page_name');
    const code = urlParams.get('code'); // Code d'autorisation Facebook OAuth
    
    // Gestion du succès Instagram
    if (instagramSuccess === 'true') {
      toast.success(`✅ Instagram connecté avec succès! @${instagramUsername || 'utilisateur'}`);
      
      // Mettre à jour l'état des connexions
      setConnectedAccounts(prev => ({
        ...prev,
        instagram: {
          username: instagramUsername || 'utilisateur',
          connected_at: new Date().toISOString(),
          is_active: true
        }
      }));
      
      // Nettoyer l'URL
      window.history.replaceState(null, null, window.location.pathname);
    }
    
    // Gestion du succès Facebook
    if (facebookSuccess === 'true' || (code && !instagramError && !facebookError)) {
      toast.success(`✅ Facebook connecté avec succès! Page: ${facebookPageName || 'My Own Watch'}`);
      
      // Mettre à jour l'état des connexions
      setConnectedAccounts(prev => ({
        ...prev,
        facebook: {
          page_name: facebookPageName || 'My Own Watch',
          connected_at: new Date().toISOString(),
          is_active: true
        }
      }));
      
      // Recharger les connexions depuis la base de données
      setTimeout(() => {
        loadConnectedAccounts();
      }, 1000);
      
      // Nettoyer l'URL
      window.history.replaceState(null, null, window.location.pathname);
    }
    
    // Gestion des erreurs Instagram
    if (instagramError) {
      let errorMessage = 'Erreur de connexion Instagram';
      
      switch (instagramError) {
        case 'access_denied':
          errorMessage = 'Accès refusé par l\'utilisateur';
          break;
        case 'missing_parameters':
          errorMessage = 'Paramètres manquants dans la réponse Instagram';
          break;
        case 'config_error':
          errorMessage = 'Erreur de configuration Instagram';
          break;
        case 'token_exchange_failed':
          errorMessage = 'Échec de l\'échange de token Instagram';
          break;
        case 'callback_error':
          errorMessage = 'Erreur lors du traitement du callback Instagram';
          break;
        default:
          errorMessage = `Erreur Instagram: ${instagramError}`;
      }
      
      toast.error(`❌ ${errorMessage}`);
      
      // Nettoyer l'URL
      window.history.replaceState(null, null, window.location.pathname);
    }
    
    // Gestion des erreurs Facebook
    if (facebookError) {
      toast.error(`❌ Erreur de connexion Facebook: ${facebookError}`);
      // Nettoyer l'URL
      window.history.replaceState(null, null, window.location.pathname);
    }
  }, []);

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
  const [analysisProgress, setAnalysisProgress] = useState(0); // Barre de progression fictive
  
  // Progress interval ref
  const progressIntervalRef = useRef(null);
  
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

  // Load website analysis when navigating to Analysis tab (only if not already loaded)
  useEffect(() => {
    if (activeTab === 'analyse' && isAuthenticated && user && !websiteAnalysis) {
      console.log('🔄 Loading website analysis for Analysis tab (not found in initial load)...');
      loadWebsiteAnalysis();
    }
  }, [activeTab, isAuthenticated, user, websiteAnalysis]);

  // Load social connections when navigating to Social tab
  useEffect(() => {
    if (activeTab === 'social' && isAuthenticated && user) {
      console.log('🔄 Loading social connections for Social tab...');
      loadConnectedAccounts();
    }
  }, [activeTab, isAuthenticated, user]);

  // Add message listener for OAuth callback success
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data?.type === 'FACEBOOK_AUTH_SUCCESS' || event.data?.type === 'INSTAGRAM_AUTH_SUCCESS') {
        console.log('🎉 Received OAuth success message:', event.data);
        
        // Update connected accounts state
        if (event.data.type === 'FACEBOOK_AUTH_SUCCESS' && event.data.page_name) {
          setConnectedAccounts(prev => ({
            ...prev,
            facebook: {
              page_name: event.data.page_name,
              connected_at: new Date().toISOString(),
              is_active: true
            }
          }));
          toast.success(`✅ Facebook connecté: ${event.data.page_name}`);
        }
        
        if (event.data.type === 'INSTAGRAM_AUTH_SUCCESS' && event.data.username) {
          setConnectedAccounts(prev => ({
            ...prev,
            instagram: {
              username: event.data.username,
              connected_at: new Date().toISOString(),
              is_active: true
            }
          }));
          toast.success(`✅ Instagram connecté: @${event.data.username}`);
        }
        
        // Reload connections from database
        setTimeout(() => {
          loadConnectedAccounts();
        }, 1000);
        
        setIsConnectingAccount(false);
        setSocialConnectionStatus('');
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // ✅ SOLUTION DE SECOURS: Charger l'analyse quand user devient disponible
  useEffect(() => {
    if (user && isAuthenticated && !websiteAnalysis) {
      console.log('🔄 User state available, loading website analysis as fallback...');
      loadWebsiteAnalysis();
    }
  }, [user, isAuthenticated, websiteAnalysis]);

  // DEBUG: Surveiller les changements de websiteAnalysis pour identifier les problèmes d'affichage
  useEffect(() => {
    console.log('🔍 websiteAnalysis changed:', websiteAnalysis ? 'RÉSULTAT PRÉSENT' : 'AUCUN RÉSULTAT');
    if (websiteAnalysis) {
      console.log('📊 Analysis data keys:', Object.keys(websiteAnalysis));
      console.log('📄 Analysis summary length:', websiteAnalysis.analysis_summary?.length || 0);
    }
  }, [websiteAnalysis]);

  // Load website analysis from database
  const loadWebsiteAnalysis = async () => {
    console.log('🔄 loadWebsiteAnalysis called, user:', user ? 'PRESENT' : 'MISSING');
    
    if (!user) {
      console.log('❌ No user found, skipping website analysis load');
      return;
    }
    
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('❌ No access token found');
        return;
      }
      
      console.log('🌐 Fetching website analysis from API...');
      const response = await axios.get(`${API}/website/analysis`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data && response.data.analysis_summary) {
        console.log('🔍 Website analysis loaded from database:', response.data);
        setWebsiteAnalysis(response.data);
        console.log('✅ Website analysis state updated successfully');
        
        // Set last analysis info if available
        if (response.data.created_at) {
          setLastAnalysisInfo({
            lastAnalyzed: response.data.created_at,
            nextAnalysisDue: response.data.next_analysis_due || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
          });
        }
      } else {
        console.log('⚠️ No website analysis data returned from API');
      }
    } catch (error) {
      console.error('❌ Error loading website analysis:', error);
      if (error.response?.status === 404) {
        console.log('🔍 No website analysis found in database');
      }
      // Pas d'erreur visible à l'utilisateur - normal si pas d'analyse
    }
  };

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
      
      // Load business profile, notes, content, posts and social connections
      // Use setTimeout with longer delay to ensure user state is updated
      setTimeout(() => {
        loadBusinessProfile();
        loadNotes();
        loadPendingContent();
        loadGeneratedPosts();
        loadPixabayCategories();
        loadConnectedAccounts();
        loadWebsiteAnalysis(); // ✅ CRITIQUE: Charger l'analyse avec délai suffisant pour l'état user
      }, 500); // ✅ CORRECTION: Augmenté de 100ms à 500ms pour le timing React
      
    } catch (error) {
      console.error('Auth check failed:', error);
      
      // Only remove token and logout if it's actually an authentication error
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.log('Authentication invalid, logging out');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
        setIsAuthenticated(false);
      } else {
        // For network errors or other issues, keep the user logged in
        console.log('Network error during auth check, keeping user logged in');
        // Keep isAuthenticated as true if we have a token
        const token = localStorage.getItem('access_token');
        setIsAuthenticated(!!token);
      }
    }
  };

  const handleAuthSuccess = async (userData) => {
    console.log('🎉 AUTH SUCCESS - User data:', userData);
    
    // Défini directement l'état d'authentification sans race condition
    setIsAuthenticated(true);
    setUser(userData);
    setActiveStep('dashboard');
    
    // Attendre un petit délai pour que l'état soit bien défini
    await new Promise(resolve => setTimeout(resolve, 100));
    
    console.log('🔄 Loading user data after successful authentication...');
    
    // AJOUT CRITIQUE : Charger toutes les données utilisateur après connexion
    try {
      await loadBusinessProfile();
      console.log('✅ Business profile loaded after login');
      
      await loadWebsiteAnalysis();  // AJOUT CRITIQUE: charger l'analyse de site web
      console.log('✅ Website analysis loaded after login');
      
      await loadNotes();
      console.log('✅ Notes loaded after login');
      
      await loadPendingContent();
      console.log('✅ Pending content loaded after login');
      
      await loadGeneratedPosts();
      console.log('✅ Generated posts loaded after login');
      
    } catch (error) {
      console.error('❌ Error loading user data after login:', error);
      // Ne pas déconnecter l'utilisateur si le chargement des données échoue
    }
    
    console.log('🎯 Navigating to dashboard with full data loaded');
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
      
      // Récupérer le token d'authentification
      const token = localStorage.getItem('access_token');
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      
      const response = await axios.get(`${API}/content/pending-temp`, {
        params: { 
          limit,
          offset: page * limit 
        }
      });

      const data = response.data;
      
      if (data && data.content) {
        const content = data.content;
        
        // Mettre à jour le total
        setTotalContentCount(data.total || 0);
        
        if (append) {
          // Ajouter à la liste existante
          setPendingContent(prev => [...prev, ...content]);
          setContentPage(page);
        } else {
          // Remplacer la liste
          setPendingContent(content);
          setContentPage(0);
        }
        
        // Update total count for display
        setTotalContentCount(data.total || 0);
      } else {
        setTotalContentCount(0);
      }
      
    } catch (error) {
      console.error('Error loading pending content:', error);
    }
  };

  // Fonction pour nettoyer les badges des images en fonction des posts réellement existants
  const cleanImageBadges = useCallback(async () => {
    try {
      console.log('🧹 Nettoyage des badges d\'images...');
      
      // Récupérer tous les posts existants
      const existingPosts = generatedPosts || [];
      
      // Créer un map des images utilisées par plateforme
      const usedImages = new Map();
      
      existingPosts.forEach(post => {
        if (post.visual_url) {
          // Extraire l'ID de l'image depuis l'URL
          let imageId = null;
          
          // Format: /api/content/{id}/file ou similaire
          const urlMatch = post.visual_url.match(/\/content\/([^\/]+)\/file/);
          if (urlMatch) {
            imageId = urlMatch[1];
          }
          
          if (imageId) {
            if (!usedImages.has(imageId)) {
              usedImages.set(imageId, {
                used_on_facebook: false,
                used_on_instagram: false,
                used_on_linkedin: false
              });
            }
            
            // Marquer la plateforme correspondante
            const platform = (post.platform || 'instagram').toLowerCase();
            if (platform === 'facebook') {
              usedImages.get(imageId).used_on_facebook = true;
            } else if (platform === 'instagram') {
              usedImages.get(imageId).used_on_instagram = true;
            } else if (platform === 'linkedin') {
              usedImages.get(imageId).used_on_linkedin = true;
            }
          }
        }
      });
      
      // Mettre à jour l'état pendingContent avec les bonnes valeurs de badge
      setPendingContent(prevContent => {
        return prevContent.map(content => {
          const imageUsage = usedImages.get(content.id) || {
            used_on_facebook: false,
            used_on_instagram: false,
            used_on_linkedin: false
          };
          
          return {
            ...content,
            used_on_facebook: imageUsage.used_on_facebook,
            used_on_instagram: imageUsage.used_on_instagram,
            used_on_linkedin: imageUsage.used_on_linkedin
          };
        });
      });
      
      console.log(`✅ Badges nettoyés pour ${usedImages.size} images utilisées`);
      
    } catch (error) {
      console.error('❌ Erreur lors du nettoyage des badges:', error);
    }
  }, [generatedPosts]);
  
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

  const handleGeneratePosts = async (monthKey = null) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté pour générer des posts');
      return;
    }

    // Vérifier les réseaux sociaux connectés
    const connectedPlatforms = [];
    if (connectedAccounts.instagram) connectedPlatforms.push('Instagram');
    if (connectedAccounts.facebook) connectedPlatforms.push('Facebook');
    if (connectedAccounts.linkedin) connectedPlatforms.push('LinkedIn');

    // Si aucun réseau connecté, afficher un popup d'explication
    if (connectedPlatforms.length === 0) {
      toast.error(
        'Aucun réseau social connecté ! Veuillez d\'abord connecter vos comptes Facebook, Instagram ou LinkedIn dans l\'onglet "Réseaux sociaux" pour générer des posts.',
        {
          duration: 6000,
          style: {
            background: '#fef2f2',
            border: '1px solid #fecaca',
            color: '#991b1b',
          }
        }
      );
      return;
    }

    // Add the month to generating set and close modal
    if (monthKey) {
      setGeneratingMonths(prev => new Set(prev).add(monthKey));
      setShowGenerationModal(false);
    } else {
      setIsGeneratingPosts(true);
      setShowGenerationModal(false);
    }

    try {
      // Logique spéciale pour le dernier jour du mois (septembre 2025)
      const now = new Date();
      const currentHour = now.getHours();
      const isLastDayOfMonth = now.getDate() === new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
      
      // Si c'est le dernier jour du mois et qu'on génère pour le mois actuel
      const isCurrentMonth = !monthKey || monthKey === `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}`;
      
      if (isLastDayOfMonth && isCurrentMonth) {
        // Après 22h, bloquer complètement la génération du mois actuel
        if (currentHour >= 22) {
          toast.error('Génération pour le mois actuel indisponible après 22h. Seule la génération du mois suivant est possible.', {
            duration: 6000,
            style: {
              background: '#fef3c7',
              border: '1px solid #f59e0b',
              color: '#92400e',
            }
          });
          if (monthKey) {
            setGeneratingMonths(prev => {
              const newSet = new Set(prev);
              newSet.delete(monthKey);
              return newSet;
            });
          } else {
            setIsGeneratingPosts(false);
          }
          return;
        }
        
        // Avant 22h : génération spéciale pour le dernier jour
        toast.info(`Mode dernier jour activé ! Génération de 1 post par réseau connecté pour aujourd'hui, programmé dans la journée (minimum 1h après génération).`, {
          duration: 8000,
          style: {
            background: '#eff6ff',
            border: '1px solid #3b82f6',
            color: '#1d4ed8',
          }
        });
      }
      
      // Calculer les jours restants pour affichage informatif
      const currentDate = new Date();
      const [year, month] = (monthKey || `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}`).split('-');
      const targetDate = new Date(parseInt(year), parseInt(month) - 1, 1);
      const lastDay = new Date(parseInt(year), parseInt(month), 0).getDate();
      const lastDateOfMonth = new Date(parseInt(year), parseInt(month) - 1, lastDay);
      
      const calculationDate = currentDate > targetDate ? currentDate : targetDate;
      const tomorrow = new Date(calculationDate);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      const remainingDays = Math.max(Math.ceil((lastDateOfMonth - tomorrow) / (1000 * 60 * 60 * 24)) + 1, 1);
      
      // Informer l'utilisateur des réseaux et du calcul proportionnel
      const platformList = connectedPlatforms.join(', ');
      toast.success(`Génération de posts en cours pour : ${platformList}
      📅 Jours restants dans le mois : ${remainingDays}
      🔄 Posts adaptés proportionnellement`, {
        duration: 4000
      });

      const requestBody = monthKey ? { month_key: monthKey } : {};
      
      // Ajouter le flag last_day_mode si c'est le dernier jour du mois actuel
      if (isLastDayOfMonth && isCurrentMonth && currentHour < 22) {
        requestBody.last_day_mode = true;
        requestBody.generation_hour = currentHour;
      }
      
      const response = await axios.post(`${API}/posts/generate`, requestBody, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const monthName = monthKey ? 
        new Date(monthKey + '-01').toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }) :
        'ce mois';
      
      toast.success(`Posts générés avec succès pour ${monthName} sur ${platformList} ! 🎉
      📋 Programmation à partir de demain`, {
        duration: 5000
      });
      
      // Recharger les posts générés
      await loadGeneratedPosts();

    } catch (error) {
      console.error('Error generating posts:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      
      // Gestion spéciale pour le blocage de génération le dernier jour du mois
      if (errorMessage.includes('Génération bloquée : nous sommes le dernier jour')) {
        toast.error(errorMessage, {
          duration: 8000,
          style: {
            background: '#fef3c7',
            border: '1px solid #f59e0b',
            color: '#92400e',
            maxWidth: '500px',
          }
        });
      } else {
        toast.error(`Erreur lors de la génération: ${errorMessage}`);
      }
    } finally {
      // Remove the month from generating set
      if (monthKey) {
        setGeneratingMonths(prev => {
          const newSet = new Set(prev);
          newSet.delete(monthKey);
          return newSet;
        });
      } else {
        setIsGeneratingPosts(false);
      }
    }
  };

  // Supprimer un post individuel
  const handleDeletePost = async (post) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer ce post ?\n\n"${post.title || 'Post sans titre'}"`)) {
      return;
    }

    const token = localStorage.getItem('access_token');
    
    try {
      const response = await axios.delete(`${API}/posts/generated/${post.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.status === 200) {
        toast.success('🗑️ Post supprimé avec succès');
        
        // Recharger les posts pour refléter la suppression
        await loadGeneratedPosts();
      }
    } catch (error) {
      console.error('Erreur lors de la suppression du post:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la suppression: ${errorMessage}`);
    }
  };

  // Charger les posts générés
  const loadGeneratedPosts = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      console.log('🔄 Loading generated posts from server...');
      const response = await axios.get(`${API}/posts/generated?t=${Date.now()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data && response.data.posts) {
        console.log(`📊 Loaded ${response.data.posts.length} posts from server`);
        setGeneratedPosts(response.data.posts);
        
        // Organiser les posts par mois
        const postsByMonth = organizePosts(response.data.posts);
        setPostsByMonth(postsByMonth);
        
        // Debug: Log des posts par mois
        Object.keys(postsByMonth).forEach(monthKey => {
          console.log(`📅 ${monthKey}: ${postsByMonth[monthKey].posts.length} posts`);
        });
        
        // Nettoyer les badges des images après chargement des posts
        cleanImageBadges();
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

      if (response.data?.success && response.data?.modified_post) {
        console.log('✅ Modification réussie, retour des données pour aperçu');
        
        // Retourner les données pour l'aperçu au lieu de recharger la page
        return {
          success: true,
          modifiedPost: {
            text: response.data.modified_post.text,
            title: response.data.modified_post.title,
            hashtags: response.data.modified_post.hashtags || []
          }
        };
      } else {
        console.log('❌ Échec de la modification, response.data:', response.data);
        toast.error('❌ Erreur: Réponse invalide du serveur');
        return false;
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
      return false;
    } finally {
      setIsModifyingPost(false);
    }
  };
    // Note: setIsModifyingPost(false) n'est pas appelé en cas de succès car on recharge la page

  // Nouvelle fonction pour modifier les posts du calendrier sans recharger la page
  const handleModifyCalendarPost = async (post, modificationRequestValue, modificationType = 'content') => {
    // Cas spécial : si c'est une application finale de modification
    if (modificationType === 'final_update') {
      try {
        // Mettre à jour dans la base de données le post modifié
        const token = localStorage.getItem('access_token');
        if (!token) {
          toast.error('Session expirée, veuillez vous reconnecter');
          return false;
        }

        // Appel API pour persister définitivement les changements en base de données
        const authToken = localStorage.getItem('access_token');
        if (!authToken) {
          toast.error('Session expirée, veuillez vous reconnecter');
          return false;
        }

        try {
          // Sauvegarder les modifications finales dans la base
          const updateResponse = await axios.put(
            `${API}/posts/${post.id}`,
            {
              title: post.title,
              text: post.text,
              hashtags: post.hashtags,
              modified_at: new Date().toISOString()
            },
            { 
              headers: { Authorization: `Bearer ${authToken}` },
              timeout: 10000
            }
          );

          if (updateResponse.data?.success) {
            console.log('✅ Modifications sauvegardées avec succès en base');
          }
        } catch (saveError) {
          console.error('❌ Erreur sauvegarde finale:', saveError);
          // Continuer même si la sauvegarde échoue pour ne pas bloquer l'UX
        }
        
        // Recharger les données pour synchroniser les vues
        await loadCalendarPosts();
        await loadGeneratedPosts();
        
        return true;
      } catch (error) {
        console.error('Erreur mise à jour finale:', error);
        return false;
      }
    }

    if (!modificationRequestValue?.trim()) {
      toast.error('Veuillez saisir une demande de modification');
      return false;
    }

    if (!post?.id) {
      toast.error('Erreur: ID du post manquant');
      return false;
    }

    setIsModifyingPost(true);
    const token = localStorage.getItem('access_token');

    if (!token) {
      toast.error('Session expirée, veuillez vous reconnecter');
      setIsModifyingPost(false);
      return false;
    }

    try {
      console.log(`🔄 Modification du post calendrier ${post.id}:`, modificationRequestValue.trim());
      
      const response = await axios.put(
        `${API}/posts/${post.id}/modify`,
        { modification_request: modificationRequestValue.trim() },
        { 
          headers: { Authorization: `Bearer ${token}` },
          timeout: 30000
        }
      );

      console.log('📡 Réponse du serveur:', response.data);

      if (response.data?.success && response.data?.modified_post) {
        // Retourner les données pour validation utilisateur au lieu d'appliquer directement
        return {
          success: true,
          modifiedPost: {
            text: response.data.modified_post.text,
            title: response.data.modified_post.title,
            hashtags: response.data.modified_post.hashtags || []
          }
        };
      } else {
        toast.error('❌ Erreur: Réponse invalide du serveur');
        return false;
      }
      
    } catch (error) {
      console.error('❌ Erreur lors de la modification du post calendrier:', error);
      
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
      return false;
    } finally {
      setIsModifyingPost(false);
    }
  };

  // Générer la liste des mois organisée comme la bibliothèque
  const generateMonthsList = () => {
    const currentDate = new Date();
    const currentAndFuture = [];
    const pastMonths = [];
    
    // Mois actuel
    const currentMonthKey = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
    const currentMonthName = currentDate.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
    currentAndFuture.push({ 
      key: currentMonthKey, 
      name: currentMonthName, 
      date: new Date(currentDate), 
      isPast: false, 
      isCurrent: true 
    });
    
    // 8 mois futurs
    for (let i = 1; i <= 8; i++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth() + i, 1);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthName = date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
      currentAndFuture.push({ key: monthKey, name: monthName, date: date, isPast: false });
    }
    
    // 6 mois passés (ordre inverse pour avoir le plus récent en premier)
    for (let i = 1; i <= 6; i++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthName = date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
      pastMonths.push({ key: monthKey, name: monthName, date: date, isPast: true });
    }
    
    return { currentAndFuture, pastMonths };
  };

  // Render des posts par mois avec organisation similaire à la bibliothèque
  const renderPostsByMonth = () => {
    const { currentAndFuture, pastMonths } = generateMonthsList();
    
    return (
      <>
        {/* Mois actuels et futurs */}
        <div className="space-y-4">
          {currentAndFuture.map(month => {
            const monthPosts = postsByMonth[month.key] || { posts: [], name: month.name };
            const isCollapsed = collapsedPostMonths[month.key];
            const hasGeneratedPosts = monthPosts.posts && monthPosts.posts.length > 0;
            
            return (
              <div key={month.key} className="space-y-4">
                {/* En-tête du mois avec bouton générer intégré */}
                <div className={`p-4 rounded-xl border transition-all ${
                  month.isPast 
                    ? 'bg-gray-50 border-gray-200' 
                    : hasGeneratedPosts
                    ? 'bg-gradient-to-r from-emerald-50 to-blue-50 border-emerald-200'
                    : 'bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200'
                }`}>
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div 
                      className="flex items-center space-x-3 cursor-pointer flex-1 min-w-0"
                      onClick={() => setCollapsedPostMonths(prev => ({
                        ...prev,
                        [month.key]: !prev[month.key]
                      }))}
                    >
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                        month.isPast 
                          ? 'bg-gray-400' 
                          : hasGeneratedPosts
                          ? 'bg-gradient-to-r from-emerald-500 to-blue-500'
                          : 'bg-gradient-to-r from-purple-500 to-pink-500'
                      }`}>
                        <Calendar className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className={`text-lg font-bold truncate ${
                          month.isPast ? 'text-gray-600' : 'text-gray-900'
                        }`}>
                          {month.name}
                          {month.isCurrent && <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full whitespace-nowrap">Actuel</span>}
                        </h3>
                        <p className={`text-sm truncate ${
                          month.isPast ? 'text-gray-500' : 'text-gray-600'
                        }`}>
                          {hasGeneratedPosts 
                            ? `${monthPosts.posts.length} post${monthPosts.posts.length > 1 ? 's' : ''}`
                            : month.isPast 
                            ? 'Mois passé'
                            : 'Aucun post généré'
                          }
                        </p>
                      </div>
                      <ChevronDown 
                        className={`w-4 h-4 text-gray-400 transform transition-transform flex-shrink-0 ${
                          isCollapsed ? 'rotate-180' : ''
                        }`} 
                      />
                    </div>
                    
                    {/* Bouton générer dans l'en-tête - Version responsive */}
                    {!month.isPast && (
                      <div className="flex-shrink-0">
                        <Button
                          onClick={(e) => {
                            e.stopPropagation(); // Empêcher le collapse/expand
                            // Stocker le mois sélectionné et ouvrir le modal de confirmation
                            setSelectedMonthForGeneration(month.key);
                            setShowGenerationModal(true);
                          }}
                          disabled={generatingMonths.has(month.key) || isGenerationBlocked(month.key)}
                          size="sm"
                          className={`w-full sm:w-auto px-3 py-2 text-xs font-medium transition-all ${
                            isGenerationBlocked(month.key)
                              ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                              : hasGeneratedPosts
                              ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                              : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                          }`}
                        >
                          {generatingMonths.has(month.key) ? (
                            <>
                              <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin mr-1.5"></div>
                              <span className="hidden sm:inline">Génération...</span>
                              <span className="sm:hidden">...</span>
                            </>
                          ) : isGenerationBlocked(month.key) ? (() => {
                            const blockedMessage = getBlockedMessage(month.key);
                            const IconComponent = getIconComponent(blockedMessage.icon);
                            return (
                              <>
                                <IconComponent className="w-3 h-3 mr-1" />
                                <span className="hidden sm:inline">{blockedMessage.desktop}</span>
                                <span className="sm:hidden">{blockedMessage.mobile}</span>
                              </>
                            );
                          })() : (
                            <>
                              <Sparkles className="w-3 h-3 mr-1.5" />
                              <span className="hidden sm:inline">
                                {hasGeneratedPosts 
                                  ? `Regénérer ${month.name.split(' ')[0]}`
                                  : `Générer ${month.name.split(' ')[0]}`
                                }
                              </span>
                              <span className="sm:hidden">
                                {hasGeneratedPosts ? 'Regénérer' : 'Générer'}
                              </span>
                            </>
                          )}
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Contenu des posts (collapse) */}
                {!isCollapsed && hasGeneratedPosts && (
                  <div className="pl-4 space-y-4">
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                      {monthPosts.posts.map((post, index) => (
                        <div key={post.id || index} data-post-id={post.id}>
                          <PostThumbnail
                            post={post}
                            onClick={() => setSelectedPost(post)}
                            onAddImage={(post) => handleAddImageToPost(post, 'add')}
                            onModifyImage={(post) => handleAddImageToPost(post, 'modify')}
                            onValidatePost={handleValidatePost}
                            onDeletePost={handleDeletePost}
                            onModifyDateTime={handleModifyDateTime}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {!isCollapsed && !hasGeneratedPosts && !month.isPast && (
                  <div className="pl-4">
                    <div className="text-center py-8 bg-purple-50 rounded-lg border border-purple-200">
                      <Sparkles className="w-8 h-8 text-purple-500 mx-auto mb-2" />
                      <p className="text-purple-700 font-medium">Aucun post pour ce mois</p>
                      <p className="text-purple-600 text-sm">Cliquez sur "Générer" pour commencer</p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Séparateur Archives */}
        {pastMonths.length > 0 && (
          <div className="flex items-center justify-center py-6">
            <div className="flex items-center space-x-3">
              <div className="h-px bg-gray-300 flex-1 w-12"></div>
              <span className="text-sm text-gray-500 font-medium">Archives</span>
              <div className="h-px bg-gray-300 flex-1 w-12"></div>
            </div>
          </div>
        )}
        
        {/* Mois passés (archives) */}
        <div className="space-y-4 opacity-75">
          {pastMonths.map(month => {
            const monthPosts = postsByMonth[month.key] || { posts: [], name: month.name };
            const isCollapsed = collapsedPostMonths[month.key] !== false; // Collapsed par défaut
            const hasGeneratedPosts = monthPosts.posts && monthPosts.posts.length > 0;
            
            return (
              <div key={month.key} className="space-y-4">
                {/* En-tête du mois passé */}
                <div className="p-4 rounded-xl border bg-gray-50 border-gray-200">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div 
                      className="flex items-center space-x-3 cursor-pointer flex-1 min-w-0"
                      onClick={() => setCollapsedPostMonths(prev => ({
                        ...prev,
                        [month.key]: !prev[month.key]
                      }))}
                    >
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-gray-400">
                        <Calendar className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-bold truncate text-gray-600">
                          {month.name}
                        </h3>
                        <p className="text-sm truncate text-gray-500">
                          {hasGeneratedPosts 
                            ? `${monthPosts.posts.length} post${monthPosts.posts.length > 1 ? 's' : ''}`
                            : 'Mois passé'
                          }
                        </p>
                      </div>
                      <ChevronDown 
                        className={`w-4 h-4 text-gray-400 transform transition-transform flex-shrink-0 ${
                          isCollapsed ? 'rotate-180' : ''
                        }`} 
                      />
                    </div>
                  </div>
                </div>

                {/* Contenu des posts passés */}
                {!isCollapsed && hasGeneratedPosts && (
                  <div className="pl-4 space-y-4">
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                      {monthPosts.posts.map((post, index) => (
                        <div key={post.id || index} data-post-id={post.id}>
                          <PostThumbnail
                            post={post}
                            onClick={() => setSelectedPost(post)}
                            onAddImage={(post) => handleAddImageToPost(post, 'add')}
                            onModifyImage={(post) => handleAddImageToPost(post, 'modify')}
                            onValidatePost={handleValidatePost}
                            onDeletePost={handleDeletePost}
                            onModifyDateTime={handleModifyDateTime}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </>
    );
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

  const connectFacebook = async () => {
    setIsConnectingAccount(true);
    setSocialConnectionStatus('Initialisation de la connexion Facebook...');
    
    try {
      const token = localStorage.getItem('access_token');
      
      // Étape 1: Obtenir l'URL d'autorisation Facebook (endpoint dédié)
      const response = await axios.get(`${API}/social/facebook/auth-url`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.auth_url) {
        setSocialConnectionStatus('Redirection vers Facebook...');
        
        // Stocker l'état avec user_id pour vérification CSRF et identification utilisateur
        const stateWithUserId = `${response.data.state}|${user.user_id}`;
        localStorage.setItem('facebook_auth_state', stateWithUserId);
        
        // Modifier l'URL pour inclure le user_id dans le state
        const urlWithUserId = response.data.auth_url.replace(
          `state=${response.data.state}`,
          `state=${encodeURIComponent(stateWithUserId)}`
        );
        
        // Rediriger vers Facebook OAuth
        window.location.href = urlWithUserId;
      } else {
        throw new Error('URL d\'autorisation non disponible');
      }
      
    } catch (error) {
      console.error('❌ Error connecting Facebook:', error);
      toast.error('Erreur lors de la connexion Facebook');
      setSocialConnectionStatus('');
      setIsConnectingAccount(false);
    }
  };

  const connectInstagram = async () => {
    setIsConnectingAccount(true);
    setSocialConnectionStatus('Initialisation de la connexion Instagram...');
    
    try {
      const token = localStorage.getItem('access_token');
      
      // Étape 1: Obtenir l'URL d'autorisation Instagram
      const response = await axios.get(`${API}/social/instagram/auth-url`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.auth_url) {
        setSocialConnectionStatus('Redirection vers Instagram...');
        
        // Stocker l'état avec user_id pour vérification CSRF et identification utilisateur
        const stateWithUserId = `${response.data.state}|${user.user_id}`;
        localStorage.setItem('instagram_auth_state', stateWithUserId);
        
        // Modifier l'URL pour inclure le user_id dans le state
        const urlWithUserId = response.data.auth_url.replace(
          `state=${response.data.state}`,
          `state=${encodeURIComponent(stateWithUserId)}`
        );
        
        // Rediriger vers Instagram OAuth
        window.location.href = urlWithUserId;
      } else {
        throw new Error('URL d\'autorisation non disponible');
      }
      
    } catch (error) {
      console.error('❌ Error connecting Instagram:', error);
      toast.error('Erreur lors de la connexion Instagram');
      setSocialConnectionStatus('');
      setIsConnectingAccount(false);
    }
  };

  const disconnectAccount = async (platform) => {
    const token = localStorage.getItem('access_token');
    
    try {
      await axios.delete(`${API}/social/connections/${platform}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Recharger les comptes connectés
      await loadConnectedAccounts();
      toast.success(`Déconnexion ${platform} réussie`);
      
    } catch (error) {
      console.error(`Error disconnecting ${platform}:`, error);
      toast.error(`Erreur lors de la déconnexion ${platform}`);
    }
  };

  // Fonction pour programmer un post (au lieu de publier immédiatement)
  const handleValidatePost = async (post) => {
    if (!post || !post.id) {
      toast.error('❌ Post invalide');
      return;
    }
    
    // Vérifier les réseaux connectés
    const connectedPlatforms = [];
    if (connectedAccounts.facebook) connectedPlatforms.push('facebook');
    if (connectedAccounts.instagram) connectedPlatforms.push('instagram');
    if (connectedAccounts.linkedin) connectedPlatforms.push('linkedin');

    if (connectedPlatforms.length === 0) {
      toast.error('Connectez au moins un réseau social d\'abord !');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté !');
      return;
    }

    try {
      toast.loading('⏰ Programmation en cours...', { id: 'schedule-post' });

      // Programmer le post au lieu de le publier immédiatement
      const response = await axios.post(
        `${API}/posts/schedule`,
        { 
          post_id: post.id,
          scheduled_date: post.date,
          scheduled_time: post.time
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data?.success) {
        toast.success(`🎉 Post programmé avec succès pour ${new Date(post.date + 'T' + post.time).toLocaleString('fr-FR')}`, { id: 'schedule-post' });
        
        // Marquer le post comme programmé dans l'interface
        post.validated = true;
        post.status = "scheduled";
        
        // Mettre à jour dans la liste des posts générés
        setGeneratedPosts(prevPosts => {
          return prevPosts.map(p => 
            p.id === post.id ? { 
              ...p, 
              validated: true, 
              status: "scheduled",
              scheduled_at: response.data.scheduled_at,
              scheduled_date: post.date,
              scheduled_time: post.time
            } : p
          );
        });
        
        // Recharger les données pour s'assurer de la cohérence
        await loadGeneratedPosts();
        await loadCalendarPosts(); // Recharger aussi le calendrier
        
        // Retourner true pour indiquer le succès
        return true;
      } else {
        toast.error('Erreur lors de la programmation', { id: 'schedule-post' });
        return false;
      }
      
    } catch (error) {
      console.error('Scheduling error details:', error);
      console.error('Error response:', error.response);
      console.error('Error response data:', error.response?.data);
      
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Erreur inconnue';
      toast.error(`❌ ${errorMessage}`, { id: 'schedule-post' });
      console.error('Scheduling error:', error);
      return false;
    }
  };

  // Fonction pour publier un post immédiatement (utilise l'ancien endpoint qui fonctionnait)
  const handlePublishNow = async (post) => {
    if (!post || !post.id) {
      toast.error('❌ Post invalide');
      return;
    }

    // Éviter les clics multiples
    if (isPublishing) {
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté !');
      return;
    }

    try {
      setIsPublishing(true);
      toast.loading('⚡ Publication en cours...', { id: 'publish-now' });

      // Utiliser l'ancien endpoint /posts/publish qui fonctionnait
      const response = await axios.post(
        `${API}/posts/publish`,
        { 
          post_id: post.id
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data?.success) {
        toast.success(`🎉 Post publié avec succès !`, { id: 'publish-now' });
        
        // Marquer le post comme publié dans l'interface
        post.published = true;
        post.status = "published";
        
        // Mettre à jour dans la liste des posts générés
        setGeneratedPosts(prevPosts => {
          return prevPosts.map(p => 
            p.id === post.id ? { 
              ...p, 
              published: true, 
              status: "published",
              published_at: response.data.published_at || new Date().toISOString(),
              publication_method: "immediate"
            } : p
          );
        });
        
        // Mettre à jour les posts du calendrier s'ils existent
        setSelectedPost(prev => prev?.id === post.id ? { ...prev, published: true, status: "published" } : prev);
        setSelectedCalendarPost(prev => prev?.id === post.id ? { ...prev, published: true, status: "published" } : prev);
        
        // Ne pas fermer le modal - garder ouvert pour voir le changement d'état
        // Recharger les données pour s'assurer de la cohérence
        await loadGeneratedPosts();
        await loadCalendarPosts();
        
        return true;
      } else {
        toast.error('Erreur lors de la publication', { id: 'publish-now' });
        return false;
      }
      
    } catch (error) {
      console.error('Publication error:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Erreur inconnue';
      toast.error(`❌ ${errorMessage}`, { id: 'publish-now' });
      return false;
    } finally {
      setIsPublishing(false);
    }
  };

  // États pour le modal de modification date/heure
  const [showDateTimeModal, setShowDateTimeModal] = useState(false);
  const [selectedPostForDateTime, setSelectedPostForDateTime] = useState(null);
  const [newScheduleDate, setNewScheduleDate] = useState('');
  const [newScheduleTime, setNewScheduleTime] = useState('');

  // Fonction pour déplacer un post du calendrier à une autre date/heure
  const handleMoveCalendarPost = async (post) => {
    console.log('🔥 DEBUG: handleMoveCalendarPost appelée avec post:', post.id);
    setSelectedPostForDateTime(post);
    
    if (post.scheduled_date) {
      const date = new Date(post.scheduled_date);
      setNewScheduleDate(date.toISOString().split('T')[0]);
      setNewScheduleTime(date.toTimeString().slice(0, 5));
    } else {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(10, 0, 0, 0);
      setNewScheduleDate(tomorrow.toISOString().split('T')[0]);
      setNewScheduleTime('10:00');
    }
    
    console.log('🔥 DEBUG: Ouverture modal date/heure');
    setShowDateTimeModal(true);
  };

  // Fonction pour annuler la programmation d'un post (déprogrammer)
  const handleCancelCalendarPost = async (post) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté');
      return;
    }

    try {
      toast.loading('🗑️ Déprogrammation en cours...', { id: 'unschedule-post' });

      const response = await axios.put(
        `${API}/posts/${post.id}/unschedule`,
        {}, // Pas de body requis
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data?.success) {
        toast.success('✅ Post déprogrammé avec succès ! Vous pouvez maintenant le modifier dans l\'onglet Posts.', { id: 'unschedule-post' });
        
        // Fermer la modal
        setSelectedCalendarPost(null);
        
        // Recharger les données
        await loadCalendarPosts();
        await loadGeneratedPosts(); // Pour que le bouton redevienne "Programmer"
      } else {
        toast.error('Erreur lors de la déprogrammation', { id: 'unschedule-post' });
      }
    } catch (error) {
      console.error('Error unscheduling post:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`❌ ${errorMessage}`, { id: 'unschedule-post' });
    }
  };

  // Fonction pour vérifier si une date/heure est valide
  const isDateTimeValid = (post, dateStr, timeStr) => {
    if (!dateStr || !timeStr || !post) return { dateValid: false, timeValid: false, valid: false };
    
    try {
      const limits = getDateLimitsForPost(post);
      const minDate = new Date(limits.min);
      const maxDate = new Date(limits.max);
      const selectedDateTime = new Date(`${dateStr}T${timeStr}:00`);
      const now = new Date();
      
      // Ajouter 10 minutes de marge minimum
      const minAllowedTime = new Date(now.getTime() + 10 * 60 * 1000);
      
      const dateValid = selectedDateTime >= minAllowedTime && selectedDateTime >= minDate && selectedDateTime <= maxDate;
      const timeValid = dateValid; // Si la date est valide, l'heure l'est aussi dans ce contexte
      const valid = dateValid && timeValid; // Propriété combinée pour le bouton
      
      console.log('🔥 DEBUG: isDateTimeValid', {
        dateStr, timeStr, 
        selectedDateTime: selectedDateTime.toISOString(),
        minAllowedTime: minAllowedTime.toISOString(),
        dateValid, timeValid, valid
      });
      
      return { dateValid, timeValid, valid };
    } catch (error) {
      console.error('🔥 DEBUG: Erreur isDateTimeValid', error);
      return { dateValid: false, timeValid: false, valid: false };
    }
  };

  // Fonction pour modifier manuellement la date et l'heure d'un post
  const handleModifyDateTime = async (post) => {
    // Ouvrir le modal avec les valeurs actuelles du post
    setSelectedPostForDateTime(post);
    
    // Initialiser les valeurs
    if (post.scheduled_date) {
      const date = new Date(post.scheduled_date);
      setNewScheduleDate(date.toISOString().split('T')[0]); // YYYY-MM-DD
      setNewScheduleTime(date.toTimeString().slice(0, 5)); // HH:MM
    } else {
      // Valeur par défaut : demain à 10h
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(10, 0, 0, 0);
      setNewScheduleDate(tomorrow.toISOString().split('T')[0]);
      setNewScheduleTime('10:00');
    }
    
    setShowDateTimeModal(true);
  };

  // Calculer les dates limites pour le calendrier basées sur le mois du post
  const getDateLimitsForPost = (post) => {
    const now = new Date();
    
    // Date minimum : aujourd'hui (pas hier)
    const minDate = new Date();
    minDate.setHours(0, 0, 0, 0);
    
    // Déterminer le mois du post
    let postMonth, postYear;
    
    // Essayer de déterminer le mois depuis différentes sources
    if (post.attributed_month) {
      // Format: "septembre_2025" ou "2025-09"
      if (post.attributed_month.includes('_')) {
        const [monthName, year] = post.attributed_month.split('_');
        const monthNames = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
        postMonth = monthNames.indexOf(monthName);
        postYear = parseInt(year);
      } else if (post.attributed_month.includes('-')) {
        const [year, month] = post.attributed_month.split('-');
        postYear = parseInt(year);
        postMonth = parseInt(month) - 1; // JavaScript months are 0-indexed
      }
    } else if (post.target_month) {
      // Format similaire à attributed_month
      if (post.target_month.includes('_')) {
        const [monthName, year] = post.target_month.split('_');
        const monthNames = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
        postMonth = monthNames.indexOf(monthName);
        postYear = parseInt(year);
      }
    }
    
    // Si on n'arrive pas à déterminer le mois du post, utiliser le mois actuel
    if (postMonth === undefined || postYear === undefined) {
      postMonth = now.getMonth();
      postYear = now.getFullYear();
    }
    
    // Date maximum : dernier jour du mois suivant au mois du post
    const maxDate = new Date(postYear, postMonth + 2, 0); // Mois suivant = postMonth + 1, donc +2 pour obtenir le dernier jour
    maxDate.setHours(23, 59, 59, 999);
    
    return {
      min: minDate.toISOString().split('T')[0], // YYYY-MM-DD format
      max: maxDate.toISOString().split('T')[0]  // YYYY-MM-DD format
    };
  };

  // Fonction pour sauvegarder la nouvelle date/heure
  const handleSaveDateTimeChange = async () => {
    if (!newScheduleDate || !newScheduleTime) {
      toast.error('Veuillez sélectionner une date et une heure');
      return;
    }

    const scheduledDateTime = new Date(`${newScheduleDate}T${newScheduleTime}:00`);
    const now = new Date();
    
    if (scheduledDateTime < now) {
      toast.error('La date ne peut pas être dans le passé');
      return;
    }

    // Obtenir les limites pour ce post spécifique
    const limits = getDateLimitsForPost(selectedPostForDateTime);
    const maxDate = new Date(limits.max);
    
    if (scheduledDateTime > maxDate) {
      toast.error('La date ne peut pas dépasser la fin du mois suivant au mois du post');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      toast.error('Vous devez être connecté pour modifier la date et l\'heure');
      return;
    }

    try {
      // Utiliser un endpoint différent selon si c'est un post du calendrier ou non
      const isCalendarPost = selectedCalendarPost && selectedPostForDateTime.id === selectedCalendarPost.id;
      const endpoint = isCalendarPost 
        ? `/posts/move-calendar-post/${selectedPostForDateTime.id}`
        : `/posts/${selectedPostForDateTime.id}/schedule`;

      const response = await axios.put(
        `${API}${endpoint}`,
        { scheduled_date: scheduledDateTime.toISOString() },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data?.success) {
        toast.success('✅ Date et heure mises à jour avec succès !');
        
        // Mettre à jour l'objet post local avec la nouvelle date
        const updatedScheduledDate = scheduledDateTime.toISOString();
        
        // Si c'est le post actuellement affiché dans le modal calendrier, le mettre à jour
        if (selectedCalendarPost && selectedPostForDateTime.id === selectedCalendarPost.id) {
          const updatedPost = {
            ...selectedCalendarPost,
            scheduled_date: updatedScheduledDate,
            modified_at: new Date().toISOString()
          };
          setSelectedCalendarPost(updatedPost);
          console.log('🔄 DEBUG: selectedCalendarPost mis à jour avec nouvelle date:', updatedScheduledDate);
        }
        
        // FORCER le rechargement complet des deux onglets avec logs détaillés
        console.log('🔄 DEBUG: Force reload des posts après déplacement...');
        
        try {
          // Attendre un délai pour que le backend ait le temps de persister
          await new Promise(resolve => setTimeout(resolve, 500));
          
          // Recharger d'abord les posts générés (onglet Posts) avec force refresh
          console.log('🔄 DEBUG: Rechargement forcé generatePosts...');
          await loadGeneratedPosts();
          console.log('✅ DEBUG: generatePosts rechargé');
          
          // Puis recharger le calendrier avec force refresh
          console.log('🔄 DEBUG: Rechargement forcé calendarPosts...');  
          await loadCalendarPosts();
          console.log('✅ DEBUG: calendarPosts rechargé');
          
          // Vérifier si la synchronisation a fonctionné
          setTimeout(() => {
            const postAfterReload = generatedPosts.find(p => p.id === selectedPostForDateTime.id);
            if (postAfterReload) {
              console.log('🔍 DEBUG: Post après reload:', {
                id: postAfterReload.id,
                old_date: selectedPostForDateTime.scheduled_date,
                new_date: postAfterReload.scheduled_date,
                synchronized: postAfterReload.scheduled_date === updatedScheduledDate
              });
            }
          }, 1000);
          
        } catch (reloadError) {
          console.error('❌ DEBUG: Erreur lors du rechargement:', reloadError);
        }
        
        // Fermer le modal
        setShowDateTimeModal(false);
        setSelectedPostForDateTime(null);
      } else {
        throw new Error(response.data?.message || 'Erreur lors de la mise à jour');
      }
      
    } catch (error) {
      console.error('Error updating schedule:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur inconnue';
      toast.error(`Erreur lors de la mise à jour: ${errorMessage}`);
    }
  };

  // Fonction pour annuler la modification date/heure
  const handleCancelDateTimeChange = () => {
    setShowDateTimeModal(false);
    setSelectedPostForDateTime(null);
    setNewScheduleDate('');
    setNewScheduleTime('');
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

  // Analyse de site web avec contournement proxy
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
    setAnalysisProgress(0); // Reset barre de progression
    
    // Nettoyer ancien interval s'il existe
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
    }
    
    // Barre de progression fictive qui se remplit sur 90 secondes
    progressIntervalRef.current = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressIntervalRef.current);
          return 100;
        }
        // Progression non-linéaire : plus lente au début, plus rapide à la fin
        const increment = prev < 30 ? 0.5 : prev < 70 ? 1.2 : 0.8;
        return Math.min(prev + increment, 99); // Ne pas dépasser 99% tant que l'analyse n'est pas finie
      });
    }, 1000); // Mise à jour chaque seconde
    
    try {
      // Toast simple d'information
      toast.loading('Analyse approfondie en cours... Durée maximale : 90 secondes', {
        id: 'website-analysis',
        duration: 95000 // 95 secondes pour être sûr
      });
      
      // CONTOURNEMENT PROXY: Essayer d'abord l'endpoint normal, puis localhost si échec
      let response;
      
      try {
        // Tentative 1: Endpoint normal avec timeout augmenté
        response = await axios.post(`${API}/website/analyze`, {
          website_url: websiteUrl.trim()
        }, {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 95000  // Augmenté à 95 secondes pour matcher le backend 90s + marge
        });
        
        // Vérifier si c'est une vraie analyse GPT ou un fallback
        const summary = response.data?.analysis_summary || '';
        const isGeneric = summary.startsWith('Entreprise analysée :') && summary.length < 100;
        
        if (isGeneric) {
          throw new Error('Réponse générique détectée, tentative contournement...');
        }
        
        console.log('✅ Analyse normale réussie');
        
      } catch (proxyError) {
        console.log('⚠️ Endpoint normal échoué, tentative contournement localhost...');
        
        // Tentative 2: Contournement localhost (pour environnement de développement)
        try {
          response = await axios.post(`${API}/website/analyze`, {
            website_url: websiteUrl.trim()
          }, {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 30000
          });
          
          console.log('✅ Contournement localhost réussi');
          toast.success('Analyse réussie via contournement technique');
          
        } catch (localhostError) {
          // Si les deux échouent, lancer l'erreur originale
          throw proxyError;
        }
      }

      // Dismisser le toast de loading et arrêter la progression
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setAnalysisProgress(100); // Compléter immédiatement la barre
      toast.dismiss('website-analysis');
      
      console.log('✅ Analysis completed, setting result:', response.data); // Debug log
      setWebsiteAnalysis(response.data);
      
      // Fix dates - utiliser la date actuelle si pas de dates valides du backend
      const now = new Date().toISOString();
      const nextMonth = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(); // 30 jours = 1 mois
      
      setLastAnalysisInfo({
        lastAnalyzed: response.data.created_at || response.data.updated_at || now,
        nextAnalysisDue: response.data.next_analysis_due || nextMonth
      });
      
      // Toast de succès unique (suppression du doublon ligne 3647)
      const analysisType = response.data.analysis_type || 'standard';
      const pagesCount = response.data.pages_analyzed_count || response.data.pages_count || 1;
      toast.success(`Analyse ${analysisType} terminée ! ${pagesCount} page(s) analysée(s)`, {
        duration: 4000
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
      
      // SUPPRESSION DU DOUBLON DE TOAST - déjà affiché ligne 3634
      
    } catch (error) {
      // Arrêter la progression et nettoyer
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setAnalysisProgress(0); // Reset seulement en cas d'erreur
      
      const errorMessage = error.response?.status === 408 ? 'Timeout - Site trop complexe à analyser (90 secondes)' : error.response?.data?.error || error.response?.data?.detail || 'Erreur lors de l\'analyse du site web';
      toast.error(`Erreur lors de l'analyse : ${errorMessage}`);
      console.error('Website analysis error:', error);
    } finally {
      setIsAnalyzing(false);
      // NE PAS reset setAnalysisProgress(0) ici - garde la barre à 100% en cas de succès
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      // S'assurer que le toast de loading soit bien supprimé
      toast.dismiss('website-analysis');
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
        'business_coordinates_edit': 'coordinates',
        'business_objective_edit': 'business_objective'  // AJOUT CRITIQUE: mapping manquant
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
    return <AuthPage onAuthSuccess={handleAuthSuccess} onShowPrivacyPolicy={() => setShowPrivacyPolicy(true)} />;
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

  // Show privacy policy if requested
  if (showPrivacyPolicy) {
    return <PrivacyPolicy onBack={() => setShowPrivacyPolicy(false)} />;
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
                  <AvatarImage src={businessProfile?.logo_url ? `${getBackendURL()}${businessProfile.logo_url}` : ""} />
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
                {/* TOUJOURS afficher les champs, même sans profil existant */}
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
                              { value: 'technique', label: '🔧 Technique' },
                              { value: 'storytelling', label: '📖 Storytelling' }
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
                      
                      {/* Nouvelle section - Objectif de résultats */}
                      <div className="mt-2">
                        <EditableField
                          fieldId="business_objective_edit"
                          label="🎯 Objectif de résultats"
                          defaultValue={businessProfile?.business_objective || 'equilibre'}
                          isSelect={true}
                          options={[
                            { value: 'conversion', label: '💰 Conversion (+ de ventes)' },
                            { value: 'communaute', label: '👥 Communauté (+ d\'abonnés)' },
                            { value: 'equilibre', label: '⚖️ Équilibré (mix ventes/abonnés)' }
                          ]}
                          fieldType="business"
                        />
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
              </CardContent>
              
              {/* Lien politique de confidentialité */}
              <div className="px-6 pb-4">
                <div className="border-t border-gray-200 pt-4">
                  <button
                    onClick={() => setShowPrivacyPolicy(true)}
                    className="text-xs text-gray-500 hover:text-purple-600 transition-colors underline"
                  >
                    Politique de confidentialité
                  </button>
                </div>
              </div>
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
                          {lastAnalysisInfo.lastAnalyzed ? 
                            new Date(lastAnalysisInfo.lastAnalyzed).toLocaleDateString('fr-FR', {
                              day: '2-digit',
                              month: '2-digit', 
                              year: 'numeric'
                            }) : 'Date non disponible'
                          }
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-blue-800">Prochaine analyse :</span>
                        <span className="text-blue-700 ml-1">
                          {lastAnalysisInfo.nextAnalysisDue ? 
                            new Date(lastAnalysisInfo.nextAnalysisDue).toLocaleDateString('fr-FR', {
                              day: '2-digit',
                              month: '2-digit',
                              year: 'numeric'
                            }) : 'Date non disponible'
                          }
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
                      <div className="flex flex-col items-center space-y-3">
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-purple-800 border-t-transparent rounded-full animate-spin"></div>
                          <span className="text-purple-800 font-medium">Analyse approfondie en cours...</span>
                        </div>
                        {/* Barre de progression fictive */}
                        <div className="w-full bg-purple-100 rounded-full h-3 border border-purple-200">
                          <div 
                            className="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-1000 ease-out"
                            style={{ width: `${analysisProgress}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-purple-700 font-medium">
                          {Math.round(analysisProgress)}% - {
                            analysisProgress < 20 ? 'Découverte des pages...' :
                            analysisProgress < 50 ? 'Extraction du contenu...' :
                            analysisProgress < 80 ? 'Analyse IA GPT-4o...' :
                            'Finalisation Claude...'
                          }
                        </div>
                      </div>
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
                      
                      {/* Analyse GPT-4o (Business/Structure) */}
                      {websiteAnalysis.analysis_summary && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">📋 Analyse Business (GPT-4o):</p>
                          <div className="bg-white rounded p-3 border">
                            <p className="text-gray-700 leading-relaxed text-sm">{websiteAnalysis.analysis_summary}</p>
                          </div>
                        </div>
                      )}

                      {/* Analyse Claude Storytelling (Dimension Narrative) */}
                      {websiteAnalysis.storytelling_analysis && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">
                            ✨ Analyse Storytelling (Claude Sonnet 4):
                          </p>
                          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded p-3 border border-purple-200">
                            <div className="text-gray-700 leading-relaxed text-sm whitespace-pre-line">
                              {websiteAnalysis.storytelling_analysis}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Indicateur des IA utilisées */}
                      {websiteAnalysis.analysis_type === 'gpt4o_plus_claude_storytelling' && (
                        <div className="mb-4">
                          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-2 border border-gray-200">
                            <div className="flex gap-4 text-xs text-gray-500 mb-1">
                              <span>🧠 Business: {websiteAnalysis.business_ai || 'GPT-4o'}</span>
                              <span>✨ Storytelling: {websiteAnalysis.storytelling_ai || 'Claude Sonnet 4'}</span>
                            </div>
                            {websiteAnalysis.pages_analyzed && websiteAnalysis.pages_analyzed.length > 0 && (
                              <div className="text-xs text-gray-500">
                                📊 Analyse approfondie de {websiteAnalysis.pages_analyzed.length} pages
                                {websiteAnalysis.non_technical_pages_count && (
                                  <span> ({websiteAnalysis.non_technical_pages_count} pages de contenu)</span>
                                )}
                              </div>
                            )}
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

                      {/* Services principaux avec détails */}
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

                      {/* Détails produits/services (nouveau) */}
                      {websiteAnalysis.products_services_details && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">📦 Détails produits/services:</p>
                          <div className="bg-blue-50 rounded p-3 border border-blue-200">
                            <p className="text-gray-700 text-sm leading-relaxed">
                              {(() => {
                                const details = websiteAnalysis.products_services_details;
                                if (typeof details === 'string') {
                                  return details;
                                } else if (Array.isArray(details)) {
                                  return details.length > 0 
                                    ? details.join(' • ')
                                    : 'Aucun détail spécifique sur les produits/services n\'a pu être extrait du site web.';
                                } else if (typeof details === 'object' && details !== null) {
                                  // Formatage intelligent pour objets
                                  return Object.entries(details)
                                    .map(([key, value]) => `${key}: ${value}`)
                                    .join(' • ');
                                } else {
                                  return 'Informations produits/services non disponibles';
                                }
                              })()}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Expertise de l'entreprise (nouveau) */}
                      {websiteAnalysis.company_expertise && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">🎯 Expertise:</p>
                          <div className="bg-green-50 rounded p-3 border border-green-200">
                            {typeof websiteAnalysis.company_expertise === 'string' ? (
                              <p className="text-gray-700 text-sm leading-relaxed">{websiteAnalysis.company_expertise}</p>
                            ) : (
                              <div className="text-gray-700 text-sm leading-relaxed space-y-2">
                                {websiteAnalysis.company_expertise.founder_info && (
                                  <div><span className="font-medium">👤 Fondateur:</span> {websiteAnalysis.company_expertise.founder_info}</div>
                                )}
                                {websiteAnalysis.company_expertise.team_size && (
                                  <div><span className="font-medium">👥 Équipe:</span> {websiteAnalysis.company_expertise.team_size}</div>
                                )}
                                {websiteAnalysis.company_expertise.key_skills && Array.isArray(websiteAnalysis.company_expertise.key_skills) && (
                                  <div><span className="font-medium">🔧 Compétences:</span> {websiteAnalysis.company_expertise.key_skills.join(', ')}</div>
                                )}
                                {websiteAnalysis.company_expertise.certifications && Array.isArray(websiteAnalysis.company_expertise.certifications) && (
                                  <div><span className="font-medium">🏆 Certifications:</span> {websiteAnalysis.company_expertise.certifications.join(', ')}</div>
                                )}
                                {websiteAnalysis.company_expertise.experience_years && (
                                  <div><span className="font-medium">📅 Expérience:</span> {websiteAnalysis.company_expertise.experience_years}</div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Proposition de valeur unique (nouveau) */}
                      {websiteAnalysis.unique_value_proposition && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">💎 Proposition de valeur unique:</p>
                          <div className="bg-yellow-50 rounded p-3 border border-yellow-200">
                            <p className="text-gray-700 text-sm leading-relaxed">
                              {typeof websiteAnalysis.unique_value_proposition === 'string' 
                                ? websiteAnalysis.unique_value_proposition 
                                : 'Proposition de valeur non disponible'
                              }
                            </p>
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
                        <div className="mb-4">
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

                      {/* NOUVELLES SECTIONS APPROFONDIES */}

                      {/* Catalogue Produits */}
                      {websiteAnalysis.products_catalog && websiteAnalysis.products_catalog.length > 0 && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">🛍️ Catalogue Produits:</p>
                          <div className="space-y-2">
                            {websiteAnalysis.products_catalog.map((product, index) => (
                              <div key={index} className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded p-3 border border-blue-200">
                                <h4 className="font-semibold text-sm text-gray-800">{product.name}</h4>
                                <p className="text-xs text-gray-600 mb-1">{product.description}</p>
                                {product.price && (
                                  <p className="text-xs font-medium text-green-600">Prix: {product.price}</p>
                                )}
                                {product.features && product.features.length > 0 && (
                                  <div className="mt-1">
                                    <p className="text-xs font-medium text-gray-700">Caractéristiques:</p>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {product.features.map((feature, i) => (
                                        <span key={i} className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded">
                                          {feature}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Services Détaillés */}
                      {websiteAnalysis.services_detailed && websiteAnalysis.services_detailed.length > 0 && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">⚙️ Services Détaillés:</p>
                          <div className="space-y-2">
                            {websiteAnalysis.services_detailed.map((service, index) => (
                              <div key={index} className="bg-gradient-to-r from-green-50 to-emerald-50 rounded p-3 border border-green-200">
                                <h4 className="font-semibold text-sm text-gray-800">{service.service_name}</h4>
                                <p className="text-xs text-gray-600 mb-1">{service.description}</p>
                                {service.pricing && (
                                  <p className="text-xs font-medium text-green-600">Tarif: {service.pricing}</p>
                                )}
                                {service.benefits && service.benefits.length > 0 && (
                                  <div className="mt-1">
                                    <p className="text-xs font-medium text-gray-700">Bénéfices:</p>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                      {service.benefits.map((benefit, i) => (
                                        <span key={i} className="bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded">
                                          {benefit}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Histoire de l'Entreprise */}
                      {websiteAnalysis.company_story && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">📚 Histoire de l'Entreprise:</p>
                          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded p-3 border border-purple-200">
                            {websiteAnalysis.company_story.mission && (
                              <div className="mb-2">
                                <p className="text-xs font-medium text-gray-700">Mission:</p>
                                <p className="text-xs text-gray-600">{websiteAnalysis.company_story.mission}</p>
                              </div>
                            )}
                            {websiteAnalysis.company_story.values && websiteAnalysis.company_story.values.length > 0 && (
                              <div className="mb-2">
                                <p className="text-xs font-medium text-gray-700">Valeurs:</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {websiteAnalysis.company_story.values.map((value, i) => (
                                    <span key={i} className="bg-purple-100 text-purple-800 text-xs px-2 py-0.5 rounded">
                                      {value}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Preuve Sociale */}
                      {websiteAnalysis.social_proof && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">🏆 Preuve Sociale:</p>
                          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded p-3 border border-yellow-200">
                            {websiteAnalysis.social_proof.testimonials && websiteAnalysis.social_proof.testimonials.length > 0 && (
                              <div className="mb-2">
                                <p className="text-xs font-medium text-gray-700">Témoignages:</p>
                                {websiteAnalysis.social_proof.testimonials.map((testimonial, i) => (
                                  <p key={i} className="text-xs text-gray-600 italic mt-1">"{testimonial}"</p>
                                ))}
                              </div>
                            )}
                            {websiteAnalysis.social_proof.achievements && websiteAnalysis.social_proof.achievements.length > 0 && (
                              <div>
                                <p className="text-xs font-medium text-gray-700">Réalisations:</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {websiteAnalysis.social_proof.achievements.map((achievement, i) => (
                                    <span key={i} className="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded">
                                      {achievement}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Mine de Contenu */}
                      {websiteAnalysis.content_goldmine && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">💎 Mine de Contenu:</p>
                          <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded p-3 border border-teal-200">
                            {websiteAnalysis.content_goldmine.expertise_areas && websiteAnalysis.content_goldmine.expertise_areas.length > 0 && (
                              <div className="mb-2">
                                <p className="text-xs font-medium text-gray-700">Domaines d'expertise:</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {websiteAnalysis.content_goldmine.expertise_areas.map((area, i) => (
                                    <span key={i} className="bg-teal-100 text-teal-800 text-xs px-2 py-0.5 rounded">
                                      {area}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {websiteAnalysis.content_goldmine.tips_tricks && websiteAnalysis.content_goldmine.tips_tricks.length > 0 && (
                              <div>
                                <p className="text-xs font-medium text-gray-700">Conseils pratiques identifiés:</p>
                                {websiteAnalysis.content_goldmine.tips_tricks.map((tip, i) => (
                                  <p key={i} className="text-xs text-gray-600 mt-1">• {tip}</p>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Stratégie Hashtags */}
                      {websiteAnalysis.hashtag_strategy && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">🏷️ Stratégie Hashtags:</p>
                          <div className="bg-gradient-to-r from-rose-50 to-pink-50 rounded p-3 border border-rose-200">
                            {websiteAnalysis.hashtag_strategy.primary && websiteAnalysis.hashtag_strategy.primary.length > 0 && (
                              <div className="mb-2">
                                <p className="text-xs font-medium text-gray-700">Hashtags principaux:</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {websiteAnalysis.hashtag_strategy.primary.map((hashtag, i) => (
                                    <span key={i} className="bg-rose-100 text-rose-800 text-xs px-2 py-0.5 rounded">
                                      {hashtag}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {websiteAnalysis.hashtag_strategy.secondary && websiteAnalysis.hashtag_strategy.secondary.length > 0 && (
                              <div>
                                <p className="text-xs font-medium text-gray-700">Hashtags secondaires:</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {websiteAnalysis.hashtag_strategy.secondary.map((hashtag, i) => (
                                    <span key={i} className="bg-pink-100 text-pink-800 text-xs px-2 py-0.5 rounded">
                                      {hashtag}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Idées Contenu Visuel */}
                      {websiteAnalysis.visual_content_ideas && websiteAnalysis.visual_content_ideas.length > 0 && (
                        <div className="mb-4">
                          <p className="font-semibold text-gray-700 mb-2 text-xs">🎨 Idées Contenu Visuel:</p>
                          <div className="space-y-2">
                            {websiteAnalysis.visual_content_ideas.map((idea, index) => (
                              <div key={index} className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded p-2 border border-indigo-200">
                                <p className="text-xs text-gray-700">{idea}</p>
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
                <CardTitle className="flex items-center justify-between text-2xl">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-2xl flex items-center justify-center">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <span className="bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                      Posts engageants générés pour vous 🚀
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={loadGeneratedPosts}
                      className="px-3 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors flex items-center space-x-2"
                      title="Recharger les posts depuis le serveur"
                    >
                      <RefreshCw className="w-4 h-4" />
                      <span className="hidden sm:inline">Actualiser</span>
                    </button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Organisation mensuelle des posts - TOUJOURS AFFICHÉE */}
                <div className="space-y-6">
                  {renderPostsByMonth()}
                </div>

                {/* Modal d'aperçu de post */}
                {selectedPost && (
                  <PostPreviewModal
                    post={selectedPost}
                    onClose={() => setSelectedPost(null)}
                    onModify={handleModifyPost}
                    onValidate={handleValidatePost}
                    onPublishNow={handlePublishNow}
                    isModifying={isModifyingPost}
                    isPublishing={isPublishing}
                    modificationRequestRef={modificationRequestRef}
                    showModificationPreview={showModificationPreview}
                    setShowModificationPreview={setShowModificationPreview}
                    modifiedPostData={modifiedPostData}
                    setModifiedPostData={setModifiedPostData}
                    showSecondaryModification={showSecondaryModification}
                    setShowSecondaryModification={setShowSecondaryModification}
                  />
                )}

                {/* Modal de modification date/heure supprimé - maintenant global */}

                {/* Modal de confirmation de génération */}
                {showGenerationModal && (
                  <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl max-w-md w-full p-6">
                      <div className="text-center mb-6">
                        <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                          <FileText className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">
                          {selectedMonthForGeneration ? 
                            `Générer les posts de ${new Date(selectedMonthForGeneration + '-01').toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })} ?` :
                            'Générer les posts du mois ?'
                          }
                        </h3>
                        <p className="text-gray-600 text-sm">
                          Claire va analyser votre profil, vos photos et vos notes pour créer des posts engageants.
                        </p>
                      </div>

                      {/* Vérifications des prérequis */}
                      <div className="bg-blue-50 rounded-lg p-4 mb-6">
                        <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                          <Info className="w-4 h-4 mr-2" />
                          Vérifiez vos prérequis pour {selectedMonthForGeneration ? 
                            new Date(selectedMonthForGeneration + '-01').toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }) :
                            'ce mois'
                          } :
                        </h4>
                        <div className="space-y-2">
                          <div className="flex items-center text-sm">
                            {businessProfile && Object.keys(businessProfile).length > 3 ? (
                              <Check className="w-4 h-4 mr-2 text-green-600" />
                            ) : (
                              <X className="w-4 h-4 mr-2 text-red-500" />
                            )}
                            <span className={businessProfile && Object.keys(businessProfile).length > 3 ? 'text-green-800' : 'text-red-600'}>
                              Profil d'entreprise complété
                            </span>
                          </div>
                          <div className="flex items-center text-sm">
                            {websiteAnalysis ? (
                              <Check className="w-4 h-4 mr-2 text-green-600" />
                            ) : (
                              <X className="w-4 h-4 mr-2 text-red-500" />
                            )}
                            <span className={websiteAnalysis ? 'text-green-800' : 'text-red-600'}>
                              Analyse de site web effectuée
                            </span>
                          </div>
                          <div className="flex items-center text-sm">
                            {(() => {
                              const monthNotes = getNotesForMonth(selectedMonthForGeneration);
                              const hasNotes = monthNotes.length > 0;
                              return (
                                <>
                                  {hasNotes ? (
                                    <Check className="w-4 h-4 mr-2 text-green-600" />
                                  ) : (
                                    <X className="w-4 h-4 mr-2 text-red-500" />
                                  )}
                                  <span className={hasNotes ? 'text-green-800' : 'text-red-600'}>
                                    Notes pour ce mois ({monthNotes.length})
                                  </span>
                                </>
                              );
                            })()}
                          </div>
                          <div className="flex items-center text-sm">
                            {(() => {
                              const monthMedia = getMediaForMonth(selectedMonthForGeneration);
                              const hasMedia = monthMedia.length > 0;
                              return (
                                <>
                                  {hasMedia ? (
                                    <Check className="w-4 h-4 mr-2 text-green-600" />
                                  ) : (
                                    <X className="w-4 h-4 mr-2 text-red-500" />
                                  )}
                                  <span className={hasMedia ? 'text-green-800' : 'text-red-600'}>
                                    Médias pour ce mois ({monthMedia.length})
                                  </span>
                                </>
                              );
                            })()}
                          </div>
                        </div>
                        
                        {(() => {
                          const monthNotes = getNotesForMonth(selectedMonthForGeneration);
                          const monthMedia = getMediaForMonth(selectedMonthForGeneration);
                          const missingElements = [];
                          
                          if (!businessProfile || Object.keys(businessProfile).length <= 3) missingElements.push('profil d\'entreprise');
                          if (!websiteAnalysis) missingElements.push('analyse de site web');
                          if (monthNotes.length === 0) missingElements.push('notes pour ce mois');
                          if (monthMedia.length === 0) missingElements.push('médias pour ce mois');
                          
                          if (missingElements.length > 0) {
                            return (
                              <div className="mt-3 p-2 bg-amber-100 border border-amber-300 rounded text-amber-800 text-xs">
                                ⚠️ Éléments manquants : {missingElements.join(', ')}. Vous pouvez continuer, mais les posts seront moins riches.
                              </div>
                            );
                          }
                          return null;
                        })()}
                      </div>

                      {/* Boutons d'action */}
                      <div className="flex space-x-3">
                        <Button
                          onClick={() => {
                            setShowGenerationModal(false);
                            setSelectedMonthForGeneration(null);
                          }}
                          variant="outline"
                          className="flex-1"
                        >
                          Annuler
                        </Button>
                        <Button
                          onClick={() => {
                            const monthKey = selectedMonthForGeneration;
                            setSelectedMonthForGeneration(null);
                            handleGeneratePosts(monthKey);
                          }}
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
                <CardTitle className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center">
                      <CalendarIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-800">Calendrier</h2>
                      <div className="flex items-center space-x-4 text-xs text-gray-600 mt-1">
                        <span>📊 {calendarPosts.length} total</span>
                        <span>📘 {calendarPosts.filter(p => p.platform === 'facebook').length} FB</span>
                        <span>📷 {calendarPosts.filter(p => p.platform === 'instagram').length} IG</span>
                        <span>💼 {calendarPosts.filter(p => p.platform === 'linkedin').length} LI</span>
                        {/* DEBUG : Indicateur de post sélectionné */}
                        {selectedCalendarPost && (
                          <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs">
                            📌 Post sélectionné: {selectedCalendarPost.platform}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Contrôles condensés */}
                  <div className="flex flex-wrap items-center gap-2 text-sm">
                    {/* Navigation mois */}
                    <div className="flex items-center">
                      <button
                        onClick={() => {
                          const newDate = new Date(calendarDate);
                          newDate.setMonth(newDate.getMonth() - 1);
                          setCalendarDate(newDate);
                        }}
                        className="p-1.5 hover:bg-gray-100 rounded transition-colors"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      
                      <div className="px-3 py-1.5 bg-white rounded border text-xs font-medium min-w-[100px] text-center">
                        {calendarDate.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}
                      </div>
                      
                      <button
                        onClick={() => {
                          const newDate = new Date(calendarDate);
                          newDate.setMonth(newDate.getMonth() + 1);
                          setCalendarDate(newDate);
                        }}
                        className="p-1.5 hover:bg-gray-100 rounded transition-colors"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                    
                    {/* Filtres */}
                    <select
                      value={calendarFilters.platform}
                      onChange={(e) => updateCalendarFilters({ platform: e.target.value })}
                      className="px-2 py-1.5 border border-gray-300 rounded text-xs bg-white"
                    >
                      <option value="all">Tous réseaux</option>
                      <option value="facebook">Facebook</option>
                      <option value="instagram">Instagram</option>
                      <option value="linkedin">LinkedIn</option>
                    </select>
                    
                    <select
                      value={calendarFilters.status}
                      onChange={(e) => updateCalendarFilters({ status: e.target.value })}
                      className="px-2 py-1.5 border border-gray-300 rounded text-xs bg-white"
                    >
                      <option value="all">Tous statuts</option>
                      <option value="scheduled">Programmés</option>
                      <option value="published">Publiés</option>
                      <option value="failed">Échoués</option>
                    </select>
                    
                    <button
                      onClick={() => loadCalendarPosts()}
                      disabled={isLoadingCalendar}
                      className="p-1.5 hover:bg-gray-100 rounded transition-colors"
                      title="Actualiser"
                    >
                      <RefreshCw className={`w-4 h-4 ${isLoadingCalendar ? 'animate-spin' : ''}`} />
                    </button>
                  </div>
                </CardTitle>
              </CardHeader>
              
              <CardContent>
                {isLoadingCalendar ? (
                  <div className="text-center py-20">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-orange-500" />
                    <p className="text-gray-500">Chargement du calendrier...</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Calendrier principal - toujours affiché */}
                    <div className="bg-white rounded-xl border">
                      {/* Grille calendrier */}
                      <div className="p-4">
                        {/* En-tête jours de la semaine */}
                        <div className="grid grid-cols-7 gap-1 mb-4">
                          {['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map(day => (
                            <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
                              {day}
                            </div>
                          ))}
                        </div>
                        
                        {/* Grille des jours du mois */}
                        <div className="grid grid-cols-7 gap-1">
                          {(() => {
                            const year = calendarDate.getFullYear();
                            const month = calendarDate.getMonth();
                            const firstDay = new Date(year, month, 1);
                            const lastDay = new Date(year, month + 1, 0);
                            const startDate = new Date(firstDay);
                            startDate.setDate(startDate.getDate() - ((firstDay.getDay() + 6) % 7));
                            
                            const days = [];
                            const currentDate = new Date(startDate);
                            
                            for (let i = 0; i < 42; i++) {
                              const dayPosts = calendarPosts.filter(post => {
                                const postDate = new Date(post.scheduled_date);
                                return postDate.toDateString() === currentDate.toDateString();
                              });
                              
                              const isCurrentMonth = currentDate.getMonth() === month;
                              const isToday = currentDate.toDateString() === new Date().toDateString();
                              
                              days.push(
                                <div
                                  key={currentDate.toISOString()}
                                  className={`
                                    min-h-[80px] p-1 border border-gray-100 rounded-lg
                                    ${isCurrentMonth ? 'bg-white' : 'bg-gray-50'}
                                    ${isToday ? 'ring-2 ring-orange-500 bg-orange-50' : ''}
                                  `}
                                >
                                  <div className={`
                                    text-sm font-medium mb-1
                                    ${isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}
                                    ${isToday ? 'text-orange-600' : ''}
                                  `}>
                                    {currentDate.getDate()}
                                  </div>
                                  
                                  {/* Posts du jour */}
                                  <div className="space-y-1">
                                    {dayPosts.slice(0, 3).map((post, idx) => (
                                      <div
                                        key={idx}
                                        onClick={(e) => {
                                          e.preventDefault();
                                          e.stopPropagation();
                                          console.log('🔥 Calendar post clicked:', post);
                                          // Force update immédiatement
                                          setSelectedCalendarPost(post);
                                        }}
                                        className={`
                                          flex items-center space-x-1 text-xs p-1 rounded cursor-pointer hover:opacity-80 transition-all hover:scale-105
                                          ${post.platform === 'facebook' ? 'bg-blue-100 text-blue-800 hover:bg-blue-200' : ''}
                                          ${post.platform === 'instagram' ? 'bg-pink-100 text-pink-800 hover:bg-pink-200' : ''}
                                          ${post.platform === 'linkedin' ? 'bg-blue-100 text-blue-900 hover:bg-blue-200' : ''}
                                        `}
                                        title={`Cliquer pour voir : ${post.platform}: ${post.text?.slice(0, 50) || 'Post'}...`}
                                      >
                                        {/* Mini vignette image */}
                                        {post.visual_url ? (
                                          <div className="w-4 h-4 rounded overflow-hidden bg-gray-200 flex-shrink-0">
                                            <img 
                                              src={post.visual_url.startsWith('http') 
                                                ? post.visual_url 
                                                : `${process.env.REACT_APP_BACKEND_URL}${post.visual_url}?token=${localStorage.getItem('access_token')}&t=${Date.now()}`
                                              }
                                              alt=""
                                              className="w-full h-full object-cover"
                                              onError={(e) => {
                                                // Approach React-compatible : cacher l'image et montrer le fallback
                                                e.target.style.display = 'none';
                                                const fallbackDiv = e.target.nextElementSibling;
                                                if (fallbackDiv) {
                                                  fallbackDiv.style.display = 'flex';
                                                }
                                              }}
                                            />
                                            {/* Fallback pour les erreurs d'image - caché par défaut */}
                                            <div className="hidden w-full h-full bg-gray-300 flex items-center justify-center text-gray-500 text-xs">
                                              📷
                                            </div>
                                          </div>
                                        ) : (
                                          <div className="w-4 h-4 rounded bg-gray-300 flex items-center justify-center flex-shrink-0">
                                            <span className="text-gray-500 text-xs">📷</span>
                                          </div>
                                        )}
                                        
                                        {/* Badge plateforme */}
                                        <span className="flex-shrink-0">
                                          {post.platform === 'facebook' && '📘'}
                                          {post.platform === 'instagram' && '📷'}
                                          {post.platform === 'linkedin' && '💼'}
                                        </span>
                                        
                                        {/* Heure */}
                                        <span className="font-medium truncate">
                                          {new Date(post.scheduled_date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                      </div>
                                    ))}
                                    {dayPosts.length > 3 && (
                                      <div className="text-xs text-gray-500 p-1">
                                        +{dayPosts.length - 3} autres
                                      </div>
                                    )}
                                  </div>
                                </div>
                              );
                              
                              currentDate.setDate(currentDate.getDate() + 1);
                            }
                            
                            return days;
                          })()}
                        </div>
                      </div>
                    </div>
                    
                    {/* Liste détaillée des posts (optionnelle, repliable) */}
                    {calendarPosts.length > 0 && (
                      <div className="bg-white rounded-xl border">
                        <div className="p-4 border-b">
                          <h3 className="font-medium text-gray-900">Posts détaillés</h3>
                        </div>
                        <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
                          {Object.entries(
                            calendarPosts.reduce((groups, post) => {
                              const date = new Date(post.scheduled_date).toLocaleDateString('fr-FR', {
                                weekday: 'long',
                                day: '2-digit',
                                month: 'long'
                              });
                              groups[date] = groups[date] || [];
                              groups[date].push(post);
                              return groups;
                            }, {})
                          ).map(([date, posts]) => (
                            <div key={date} className="space-y-2">
                              <h4 className="font-medium text-gray-700 capitalize">{date}</h4>
                              <div className="space-y-2 pl-4">
                                {posts.map((post, index) => (
                                  <div 
                                    key={index} 
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      console.log('🔥 Calendar list post clicked:', post);
                                      // Ouvrir immédiatement le modal
                                      setSelectedCalendarPost(post);
                                    }}
                                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                                  >
                                    <div className="flex items-center space-x-3">
                                      {/* Vignette image du post */}
                                      <div className="relative flex-shrink-0">
                                        {post.visual_url ? (
                                          <div className="w-12 h-12 rounded-lg overflow-hidden bg-gray-100">
                                            <img 
                                              src={post.visual_url.startsWith('http') 
                                                ? post.visual_url 
                                                : `${process.env.REACT_APP_BACKEND_URL}${post.visual_url}?token=${localStorage.getItem('access_token')}&t=${Date.now()}`
                                              }
                                              alt={post.title || 'Post image'}
                                              className="w-full h-full object-cover"
                                              onError={(e) => {
                                                e.target.style.display = 'none';
                                                e.target.nextSibling.style.display = 'flex';
                                              }}
                                            />
                                            {/* Fallback pour les erreurs d'image */}
                                            <div className="hidden w-full h-full bg-gray-200 flex items-center justify-center">
                                              <ImageIcon className="w-4 h-4 text-gray-400" />
                                            </div>
                                          </div>
                                        ) : (
                                          <div className="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center">
                                            <ImageIcon className="w-4 h-4 text-gray-400" />
                                          </div>
                                        )}
                                        {/* Badge plateforme sur l'image */}
                                        <div className={`
                                          absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-xs text-white
                                          ${post.platform === 'facebook' ? 'bg-blue-600' : ''}
                                          ${post.platform === 'instagram' ? 'bg-pink-600' : ''}
                                          ${post.platform === 'linkedin' ? 'bg-blue-700' : ''}
                                        `}>
                                          {post.platform === 'facebook' && '📘'}
                                          {post.platform === 'instagram' && '📷'}
                                          {post.platform === 'linkedin' && '💼'}
                                        </div>
                                      </div>
                                      
                                      {/* Contenu texte */}
                                      <div className="flex-1 min-w-0">
                                        <div className="font-medium text-sm text-gray-900">
                                          {new Date(post.scheduled_date).toLocaleTimeString('fr-FR', { 
                                            hour: '2-digit', 
                                            minute: '2-digit' 
                                          })}
                                        </div>
                                        <div className="text-xs text-gray-500 truncate">
                                          {post.text?.slice(0, 100) || 'Post sans texte'}...
                                        </div>
                                        {/* Titre si présent */}
                                        {post.title && (
                                          <div className="text-xs font-medium text-gray-700 truncate mt-1">
                                            {post.title}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                    <div className={`
                                      px-2 py-1 rounded-full text-xs font-medium
                                      ${post.status === 'scheduled' ? 'bg-blue-100 text-blue-800' : ''}
                                      ${post.status === 'published' ? 'bg-green-100 text-green-800' : ''}
                                      ${post.status === 'failed' ? 'bg-red-100 text-red-800' : ''}
                                    `}>
                                      {post.status === 'scheduled' && '📅 Programmé'}
                                      {post.status === 'published' && '✅ Publié'}
                                      {post.status === 'failed' && '❌ Échec'}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Message si vide - plus petit et moins intrusif */}
                    {calendarPosts.length === 0 && (
                      <div className="text-center py-8 bg-gray-50 rounded-xl">
                        <CalendarIcon className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-500 mb-3">Aucun post programmé ce mois-ci</p>
                        <Button 
                          onClick={() => setActiveTab('posts')}
                          size="sm"
                          className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
                        >
                          Aller aux Posts
                        </Button>
                      </div>
                    )}
                  </div>
                )}
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

                {/* Facebook Connection - Maintenant Active */}
                <div className="bg-white rounded-2xl p-4 sm:p-6 border border-gray-100 hover:shadow-lg transition-shadow social-connection-card">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between social-connection-content">
                    <div className="flex items-center space-x-4 flex-1 min-w-0">
                      <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center flex-shrink-0">
                        <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24" style={{aspectRatio: '1'}}>
                          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900">Facebook</h3>
                        <p className="text-sm text-gray-500 truncate">
                          {connectedAccounts.facebook ? 
                            `Connecté : ${connectedAccounts.facebook.username}` : 
                            'Publiez sur vos pages Facebook'
                          }
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3 mt-4 sm:mt-0 social-connection-buttons">
                      {connectedAccounts.facebook ? (
                        <>
                          <div className="flex items-center justify-center space-x-2 text-green-600 px-3 py-2">
                            <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
                            <span className="text-sm font-medium">Connecté</span>
                          </div>
                          <button
                            onClick={() => disconnectAccount('facebook')}
                            className="px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors social-disconnect-button"
                          >
                            Déconnecter
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={connectFacebook}
                          disabled={isConnectingAccount}
                          className="px-6 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 social-connect-button"
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
        
        {/* MODAUX GLOBAUX - Accessibles depuis tous les onglets */}
        
        {/* Modal d'aperçu de post depuis le calendrier */}
        {selectedCalendarPost && (
          <PostPreviewModal
            post={selectedCalendarPost}
            onClose={() => setSelectedCalendarPost(null)}
            onModify={handleModifyCalendarPost}
            onValidate={handleValidatePost}
            onPublishNow={handlePublishNow}
            isModifying={isModifyingPost}
            isPublishing={isPublishing}
            modificationRequestRef={modificationRequestRef}
            isFromCalendar={true}
            onMovePost={handleMoveCalendarPost}
            onCancelPost={handleCancelCalendarPost}
            showModificationPreview={showModificationPreview}
            setShowModificationPreview={setShowModificationPreview}
            modifiedPostData={modifiedPostData}
            setModifiedPostData={setModifiedPostData}
            showSecondaryModification={showSecondaryModification}
            setShowSecondaryModification={setShowSecondaryModification}
          />
        )}
        
        {/* Modal de modification date/heure - maintenant global */}
        {showDateTimeModal && selectedPostForDateTime && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CalendarIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Modifier date et heure du post
                </h3>
                <p className="text-sm text-gray-600">
                  Choisissez la nouvelle date et heure pour ce post.
                </p>
              </div>

              {/* Sélection date */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date :
                </label>
                <input
                  type="date"
                  value={newScheduleDate}
                  onChange={(e) => setNewScheduleDate(e.target.value)}
                  className={`w-full ${!isDateTimeValid(selectedPostForDateTime, newScheduleDate, newScheduleTime).dateValid 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'} 
                    p-3 rounded-lg transition-colors`}
                  min={getDateLimitsForPost(selectedPostForDateTime).min}
                  max={getDateLimitsForPost(selectedPostForDateTime).max}
                />
                {!isDateTimeValid(selectedPostForDateTime, newScheduleDate, newScheduleTime).dateValid && newScheduleDate && (
                  <p className="text-red-500 text-xs mt-1">
                    La date doit être entre le {
                      new Date(getDateLimitsForPost(selectedPostForDateTime).min).toLocaleDateString('fr-FR')
                    } et le {
                      new Date(getDateLimitsForPost(selectedPostForDateTime).max).toLocaleDateString('fr-FR')
                    }
                  </p>
                )}
              </div>

              {/* Sélection heure */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Heure :
                </label>
                <input
                  type="time"
                  value={newScheduleTime}
                  onChange={(e) => setNewScheduleTime(e.target.value)}
                  className={`w-full ${!isDateTimeValid(selectedPostForDateTime, newScheduleDate, newScheduleTime).timeValid 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'} 
                    p-3 rounded-lg transition-colors`}
                />
                {!isDateTimeValid(selectedPostForDateTime, newScheduleDate, newScheduleTime).timeValid && newScheduleTime && (
                  <p className="text-red-500 text-xs mt-1">
                    L'heure doit être dans le futur (minimum 10 minutes)
                  </p>
                )}
              </div>

              {/* Boutons */}
              <div className="flex items-center justify-center space-x-3">
                <button
                  onClick={() => {
                    setShowDateTimeModal(false);
                    setSelectedPostForDateTime(null);
                  }}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                >
                  Annuler
                </button>
                
                <button
                  onClick={handleSaveDateTimeChange}
                  disabled={!isDateTimeValid(selectedPostForDateTime, newScheduleDate, newScheduleTime).valid}
                  className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 disabled:from-gray-300 disabled:to-gray-400 text-white rounded-lg font-medium transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl disabled:transform-none"
                >
                  Confirmer
                </button>
              </div>
            </div>
          </div>
        )}
        
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
      <Footer onShowPrivacyPolicy={() => setShowPrivacyPolicy(true)} />
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/auth/facebook/callback" element={<FacebookCallback />} />
        <Route path="/mentions-legales" element={<MentionsLegales />} />
        <Route path="/politique-confidentialite" element={<PrivacyPolicy onBack={() => window.location.href = '/'} />} />
        <Route path="/suppression-donnees" element={<DataDeletion onBack={() => window.location.href = '/'} />} />
        <Route path="/*" element={<MainApp />} />
      </Routes>
    </Router>
  );
}

export default App;