import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { 
  TrendingUp, 
  Heart, 
  MessageCircle, 
  Share2, 
  Eye, 
  Users,
  Calendar,
  Filter,
  ArrowUpDown,
  ExternalLink,
  RefreshCw
} from 'lucide-react';
import axios from 'axios';

const getBackendURL = () => {
  if (import.meta.env?.REACT_APP_BACKEND_URL) {
    return import.meta.env.REACT_APP_BACKEND_URL;
  }
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  return 'https://claire-marcus.com';
};

const BACKEND_URL = getBackendURL();

const Analytics = () => {
  const [posts, setPosts] = useState([]);
  const [filteredPosts, setFilteredPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    loadAnalytics();
  }, [selectedPeriod]);

  useEffect(() => {
    filterAndSortPosts();
  }, [posts, selectedPlatform, sortBy, sortOrder]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No access token found');
        return;
      }

      const response = await axios.get(
        `${BACKEND_URL}/api/analytics/posts`,
        {
          params: {
            days: parseInt(selectedPeriod)
          },
          headers: {
            Authorization: `Bearer ${token}`
          },
          timeout: 30000
        }
      );

      if (response.data.success) {
        setPosts(response.data.posts || []);
        console.log(`📊 Loaded ${response.data.posts?.length || 0} posts`);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
      if (error.response?.status === 401) {
        console.error('Authentication error - please login again');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const filterAndSortPosts = () => {
    let filtered = [...posts];

    // Filter by platform
    if (selectedPlatform !== 'all') {
      filtered = filtered.filter(post => post.platform === selectedPlatform);
    }

    // Sort
    filtered.sort((a, b) => {
      let aValue, bValue;

      switch (sortBy) {
        case 'likes':
          aValue = a.likes || 0;
          bValue = b.likes || 0;
          break;
        case 'comments':
          aValue = a.comments || 0;
          bValue = b.comments || 0;
          break;
        case 'shares':
          aValue = a.shares || 0;
          bValue = b.shares || 0;
          break;
        case 'reach':
          aValue = a.reach || 0;
          bValue = b.reach || 0;
          break;
        case 'engagement':
          // Calcul du taux d'engagement
          aValue = ((a.likes || 0) + (a.comments || 0)) / Math.max(a.reach || 1, 1);
          bValue = ((b.likes || 0) + (b.comments || 0)) / Math.max(b.reach || 1, 1);
          break;
        case 'date':
        default:
          aValue = new Date(a.created_time).getTime();
          bValue = new Date(b.created_time).getTime();
          break;
      }

      if (sortOrder === 'asc') {
        return aValue - bValue;
      } else {
        return bValue - aValue;
      }
    });

    setFilteredPosts(filtered);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num?.toString() || '0';
  };

  const calculateEngagementRate = (post) => {
    const totalEngagement = (post.likes || 0) + (post.comments || 0) + (post.shares || 0);
    const reach = post.reach || post.engagement || 1;
    return ((totalEngagement / reach) * 100).toFixed(1);
  };

  // Calculate summary stats
  const totalLikes = filteredPosts.reduce((sum, post) => sum + (post.likes || 0), 0);
  const totalComments = filteredPosts.reduce((sum, post) => sum + (post.comments || 0), 0);
  const totalShares = filteredPosts.reduce((sum, post) => sum + (post.shares || 0), 0);
  const totalReach = filteredPosts.reduce((sum, post) => sum + (post.reach || 0), 0);
  const avgEngagement = filteredPosts.length > 0 
    ? (filteredPosts.reduce((sum, post) => sum + parseFloat(calculateEngagementRate(post)), 0) / filteredPosts.length).toFixed(1)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-purple-600" />
            <span>Statistiques</span>
          </h2>
          <p className="text-gray-600 mt-1">Analysez les performances de vos publications</p>
        </div>
        <Button
          onClick={loadAnalytics}
          disabled={isLoading}
          className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Actualiser
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Posts</p>
                <p className="text-2xl font-bold text-gray-900">{filteredPosts.length}</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-5 h-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Likes</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(totalLikes)}</p>
              </div>
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <Heart className="w-5 h-5 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Commentaires</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(totalComments)}</p>
              </div>
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <MessageCircle className="w-5 h-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Partages</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(totalShares)}</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Share2 className="w-5 h-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Portée</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(totalReach)}</p>
              </div>
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <Eye className="w-5 h-5 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Filtres:</span>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Réseau:</span>
              <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous</SelectItem>
                  <SelectItem value="facebook">Facebook</SelectItem>
                  <SelectItem value="instagram">Instagram</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Période:</span>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">7 derniers jours</SelectItem>
                  <SelectItem value="30">30 derniers jours</SelectItem>
                  <SelectItem value="90">3 derniers mois</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <ArrowUpDown className="w-4 h-4 text-gray-600" />
              <span className="text-sm text-gray-600">Trier par:</span>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">Date</SelectItem>
                  <SelectItem value="likes">Likes</SelectItem>
                  <SelectItem value="comments">Commentaires</SelectItem>
                  <SelectItem value="shares">Partages</SelectItem>
                  <SelectItem value="reach">Portée</SelectItem>
                  <SelectItem value="engagement">Engagement</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'asc' ? '↑ Croissant' : '↓ Décroissant'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Posts List */}
      {isLoading ? (
        <Card>
          <CardContent className="p-12 text-center">
            <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Chargement des statistiques...</p>
          </CardContent>
        </Card>
      ) : filteredPosts.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucune donnée disponible</h3>
            <p className="text-gray-600">
              {posts.length === 0 
                ? "Aucun post publié sur vos pages connectées pour la période sélectionnée."
                : "Aucun post ne correspond aux filtres sélectionnés."}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredPosts.map((post) => (
            <Card key={post.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-0">
                {/* Image */}
                {post.image_url && (
                  <div className="aspect-video bg-gray-100 relative overflow-hidden">
                    <img
                      src={post.image_url}
                      alt="Post"
                      className="w-full h-full object-cover"
                    />
                    <Badge 
                      className={`absolute top-2 left-2 ${
                        post.platform === 'facebook' 
                          ? 'bg-blue-600' 
                          : 'bg-gradient-to-r from-purple-600 to-pink-600'
                      }`}
                    >
                      {post.platform === 'facebook' ? 'Facebook' : 'Instagram'}
                    </Badge>
                  </div>
                )}

                {/* Content */}
                <div className="p-4 space-y-3">
                  {/* Date */}
                  <div className="flex items-center text-xs text-gray-500">
                    <Calendar className="w-3 h-3 mr-1" />
                    {formatDate(post.created_time)}
                  </div>

                  {/* Message */}
                  <p className="text-sm text-gray-700 line-clamp-3">
                    {post.message || 'Aucun texte'}
                  </p>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-2 pt-2 border-t">
                    <div className="flex items-center space-x-1">
                      <Heart className="w-4 h-4 text-red-500" />
                      <span className="text-sm font-medium">{formatNumber(post.likes)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <MessageCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm font-medium">{formatNumber(post.comments)}</span>
                    </div>
                    {post.platform === 'facebook' && (
                      <div className="flex items-center space-x-1">
                        <Share2 className="w-4 h-4 text-blue-500" />
                        <span className="text-sm font-medium">{formatNumber(post.shares)}</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-1">
                      <Eye className="w-4 h-4 text-purple-500" />
                      <span className="text-sm font-medium">{formatNumber(post.reach)}</span>
                    </div>
                  </div>

                  {/* Engagement Rate */}
                  <div className="flex items-center justify-between pt-2 border-t">
                    <span className="text-xs text-gray-600">Taux d'engagement</span>
                    <Badge variant="outline" className="text-purple-600 border-purple-200">
                      {calculateEngagementRate(post)}%
                    </Badge>
                  </div>

                  {/* View on Platform */}
                  {post.permalink && (
                    <a
                      href={post.permalink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center space-x-2 text-sm text-purple-600 hover:text-purple-700 transition-colors"
                    >
                      <span>Voir sur {post.platform === 'facebook' ? 'Facebook' : 'Instagram'}</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Analytics;
