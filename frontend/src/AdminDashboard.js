import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Label } from './components/ui/label';
import { Alert, AlertDescription } from './components/ui/alert';
import { 
  Users, DollarSign, TrendingUp, Crown, UserCheck, UserX, 
  Percent, Gift, Eye, Trash2, Plus, Search, Filter,
  Calendar, Mail, Settings, BarChart3, PieChart
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = ({ user, onLogout }) => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);
  const [promoCodes, setPromoCodes] = useState([]);
  const [payments, setPayments] = useState([]);
  const [referrals, setReferrals] = useState([]);
  const [revenueAnalytics, setRevenueAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Form states
  const [promoForm, setPromoForm] = useState({
    code: '',
    discount_type: 'percentage',
    discount_value: 0,
    max_uses: null,
    expires_at: null
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load all admin data
      const [
        statsRes,
        usersRes, 
        plansRes,
        promoRes,
        paymentsRes,
        referralsRes,
        revenueRes
      ] = await Promise.all([
        axios.get(`${API}/admin/stats`),
        axios.get(`${API}/admin/users`),
        axios.get(`${API}/admin/subscription-plans`),
        axios.get(`${API}/admin/promo-codes`),
        axios.get(`${API}/admin/payments`),
        axios.get(`${API}/admin/referrals`),
        axios.get(`${API}/admin/analytics/revenue?period=month`)
      ]);

      setStats(statsRes.data);
      setUsers(usersRes.data);
      setSubscriptionPlans(plansRes.data);
      setPromoCodes(promoRes.data);
      setPayments(paymentsRes.data);
      setReferrals(referralsRes.data);
      setRevenueAnalytics(revenueRes.data);

    } catch (error) {
      console.error('Error loading admin data:', error);
      if (error.response?.status === 403) {
        toast.error('Accès administrateur requis');
      } else {
        toast.error('Erreur lors du chargement des données');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePromoCode = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/admin/promo-codes`, promoForm);
      toast.success('Code promo créé avec succès');
      setPromoForm({
        code: '',
        discount_type: 'percentage',
        discount_value: 0,
        max_uses: null,
        expires_at: null
      });
      loadDashboardData();
    } catch (error) {
      console.error('Error creating promo code:', error);
      toast.error('Erreur lors de la création du code promo');
    }
  };

  const handleUpdateUserSubscription = async (userId, status, plan = null) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/subscription`, {
        subscription_status: status,
        subscription_plan: plan,
        subscription_ends_at: status === 'active' ? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) : null
      });
      toast.success('Abonnement mis à jour');
      loadDashboardData();
    } catch (error) {
      console.error('Error updating subscription:', error);
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/users/${userId}`);
      toast.success('Utilisateur supprimé');
      loadDashboardData();
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = searchTerm === '' || 
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (user.business_name && user.business_name.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesStatus = statusFilter === '' || user.subscription_status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-8 h-8 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-gray-600">Chargement du dashboard admin...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Admin Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-red-600 to-purple-600 rounded-xl flex items-center justify-center">
                <Crown className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">PostCraft Admin</h1>
                <p className="text-sm text-gray-600">Dashboard administrateur</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-red-100 text-red-800">
                Admin: {user.first_name} {user.last_name}
              </Badge>
              <Button variant="outline" onClick={onLogout}>
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="overview" className="space-y-8">
          <TabsList className="grid w-full grid-cols-6 h-12">
            <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
            <TabsTrigger value="users">Utilisateurs</TabsTrigger>
            <TabsTrigger value="subscriptions">Abonnements</TabsTrigger>
            <TabsTrigger value="promo">Codes Promo</TabsTrigger>
            <TabsTrigger value="payments">Paiements</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Utilisateurs Total</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    +{stats?.new_users_this_month || 0} ce mois
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Abonnements Actifs</CardTitle>
                  <UserCheck className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.active_subscriptions || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    {stats?.trial_users || 0} en essai
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">MRR</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatCurrency(stats?.mrr || 0)}</div>
                  <p className="text-xs text-muted-foreground">
                    Churn: {stats?.churn_rate?.toFixed(1) || 0}%
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Posts Générés</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.posts_generated_today || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    {stats?.posts_generated_this_month || 0} ce mois
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Actions Rapides</CardTitle>
                  <CardDescription>Gestion rapide des utilisateurs</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button className="w-full" onClick={() => loadDashboardData()}>
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Actualiser les données
                  </Button>
                  <Button variant="outline" className="w-full">
                    <Mail className="w-4 h-4 mr-2" />
                    Envoyer newsletter
                  </Button>
                  <Button variant="outline" className="w-full">
                    <Gift className="w-4 h-4 mr-2" />
                    Campagne promo
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Revenus Récents</CardTitle>
                  <CardDescription>Derniers paiements reçus</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {payments.slice(0, 5).map((payment) => (
                      <div key={payment.id} className="flex items-center justify-between">
                        <div className="text-sm">
                          <p className="font-medium">{formatCurrency(payment.amount)}</p>
                          <p className="text-gray-500">{payment.subscription_plan}</p>
                        </div>
                        <Badge variant={payment.status === 'succeeded' ? 'default' : 'destructive'}>
                          {payment.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            <div className="space-y-6">
              {/* Filters */}
              <Card>
                <CardHeader>
                  <CardTitle>Gestion des Utilisateurs</CardTitle>
                  <CardDescription>
                    {filteredUsers.length} utilisateur{filteredUsers.length > 1 ? 's' : ''}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex space-x-4 mb-6">
                    <div className="flex-1">
                      <Input
                        placeholder="Rechercher par nom, email, entreprise..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full"
                      />
                    </div>
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Filtrer par statut" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">Tous les statuts</SelectItem>
                        <SelectItem value="trial">Essai</SelectItem>
                        <SelectItem value="active">Actif</SelectItem>
                        <SelectItem value="expired">Expiré</SelectItem>
                        <SelectItem value="cancelled">Annulé</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Users Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-4">Utilisateur</th>
                          <th className="text-left p-4">Entreprise</th>
                          <th className="text-left p-4">Statut</th>
                          <th className="text-left p-4">Plan</th>
                          <th className="text-left p-4">Posts</th>
                          <th className="text-left p-4">Inscription</th>
                          <th className="text-left p-4">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredUsers.map((user) => (
                          <tr key={user.id} className="border-b hover:bg-gray-50">
                            <td className="p-4">
                              <div>
                                <p className="font-medium">{user.first_name} {user.last_name}</p>
                                <p className="text-sm text-gray-500">{user.email}</p>
                              </div>
                            </td>
                            <td className="p-4">
                              <p className="text-sm">{user.business_name || 'Non défini'}</p>
                            </td>
                            <td className="p-4">
                              <Badge variant={
                                user.subscription_status === 'active' ? 'default' :
                                user.subscription_status === 'trial' ? 'secondary' :
                                'destructive'
                              }>
                                {user.subscription_status}
                              </Badge>
                            </td>
                            <td className="p-4">
                              <p className="text-sm capitalize">{user.subscription_plan}</p>
                            </td>
                            <td className="p-4">
                              <p className="text-sm">{user.total_posts_generated || 0}</p>
                            </td>
                            <td className="p-4">
                              <p className="text-sm">{formatDate(user.created_at)}</p>
                            </td>
                            <td className="p-4">
                              <div className="flex space-x-2">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setSelectedUser(user)}
                                >
                                  <Eye className="w-4 h-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleDeleteUser(user.id)}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Promo Codes Tab */}
          <TabsContent value="promo">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Create Promo Code */}
              <Card>
                <CardHeader>
                  <CardTitle>Créer un Code Promo</CardTitle>
                  <CardDescription>Nouveau code de réduction</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleCreatePromoCode} className="space-y-4">
                    <div>
                      <Label htmlFor="promo-code">Code</Label>
                      <Input
                        id="promo-code"
                        placeholder="WELCOME2024"
                        value={promoForm.code}
                        onChange={(e) => setPromoForm({...promoForm, code: e.target.value.toUpperCase()})}
                        required
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Type de réduction</Label>
                        <Select 
                          value={promoForm.discount_type}
                          onValueChange={(value) => setPromoForm({...promoForm, discount_type: value})}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="percentage">Pourcentage</SelectItem>
                            <SelectItem value="fixed">Montant fixe</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label>Valeur</Label>
                        <Input
                          type="number"
                          placeholder={promoForm.discount_type === 'percentage' ? '20' : '10'}
                          value={promoForm.discount_value}
                          onChange={(e) => setPromoForm({...promoForm, discount_value: parseFloat(e.target.value)})}
                          required
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label>Utilisations maximales (optionnel)</Label>
                      <Input
                        type="number"
                        placeholder="100"
                        value={promoForm.max_uses || ''}
                        onChange={(e) => setPromoForm({...promoForm, max_uses: e.target.value ? parseInt(e.target.value) : null})}
                      />
                    </div>
                    
                    <div>
                      <Label>Date d'expiration (optionnel)</Label>
                      <Input
                        type="datetime-local"
                        value={promoForm.expires_at || ''}
                        onChange={(e) => setPromoForm({...promoForm, expires_at: e.target.value || null})}
                      />
                    </div>
                    
                    <Button type="submit" className="w-full">
                      <Plus className="w-4 h-4 mr-2" />
                      Créer le code promo
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Active Promo Codes */}
              <Card>
                <CardHeader>
                  <CardTitle>Codes Promo Actifs</CardTitle>
                  <CardDescription>{promoCodes.length} codes créés</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {promoCodes.map((promo) => (
                      <div key={promo.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <code className="font-mono font-bold text-purple-600">{promo.code}</code>
                          <Badge variant={promo.active ? 'default' : 'secondary'}>
                            {promo.active ? 'Actif' : 'Inactif'}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>
                            <span className="font-medium">Réduction:</span>{' '}
                            {promo.discount_type === 'percentage' 
                              ? `${promo.discount_value}%` 
                              : `${formatCurrency(promo.discount_value)}`
                            }
                          </p>
                          <p>
                            <span className="font-medium">Utilisé:</span> {promo.used_count}
                            {promo.max_uses && ` / ${promo.max_uses}`}
                          </p>
                          {promo.expires_at && (
                            <p>
                              <span className="font-medium">Expire:</span> {formatDate(promo.expires_at)}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Other tabs would be implemented similarly */}
          <TabsContent value="subscriptions">
            <Card>
              <CardHeader>
                <CardTitle>Plans d'Abonnement</CardTitle>
                <CardDescription>Gestion des plans de pricing</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {subscriptionPlans.map((plan) => (
                    <Card key={plan.id} className="border-2">
                      <CardHeader>
                        <CardTitle className="text-lg">{plan.name}</CardTitle>
                        <div className="space-y-1">
                          <p className="text-2xl font-bold">{formatCurrency(plan.price_monthly)}<span className="text-sm font-normal">/mois</span></p>
                          <p className="text-lg text-gray-600">{formatCurrency(plan.price_yearly)}<span className="text-sm">/an</span></p>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2 text-sm">
                          {plan.features.map((feature, index) => (
                            <li key={index} className="flex items-start">
                              <Check className="w-4 h-4 text-green-600 mt-0.5 mr-2 flex-shrink-0" />
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="payments">
            <Card>
              <CardHeader>
                <CardTitle>Historique des Paiements</CardTitle>
                <CardDescription>{payments.length} transactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-4">Date</th>
                        <th className="text-left p-4">Utilisateur</th>
                        <th className="text-left p-4">Montant</th>
                        <th className="text-left p-4">Plan</th>
                        <th className="text-left p-4">Période</th>
                        <th className="text-left p-4">Statut</th>
                      </tr>
                    </thead>
                    <tbody>
                      {payments.slice(0, 20).map((payment) => (
                        <tr key={payment.id} className="border-b hover:bg-gray-50">
                          <td className="p-4">{formatDate(payment.created_at)}</td>
                          <td className="p-4">{payment.user_id.slice(0, 8)}...</td>
                          <td className="p-4 font-medium">{formatCurrency(payment.amount)}</td>
                          <td className="p-4">{payment.subscription_plan}</td>
                          <td className="p-4">{payment.billing_period}</td>
                          <td className="p-4">
                            <Badge variant={payment.status === 'succeeded' ? 'default' : 'destructive'}>
                              {payment.status}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Revenus du Mois</CardTitle>
                  <CardDescription>Performance financière</CardDescription>
                </CardHeader>
                <CardContent>
                  {revenueAnalytics && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-600">
                            {formatCurrency(revenueAnalytics.total_revenue)}
                          </p>
                          <p className="text-sm text-gray-600">Revenus total</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600">
                            {revenueAnalytics.total_transactions}
                          </p>
                          <p className="text-sm text-gray-600">Transactions</p>
                        </div>
                      </div>
                      <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                        <p className="text-gray-500">Graphique des revenus (à implémenter)</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Métriques SaaS</CardTitle>
                  <CardDescription>Indicateurs clés</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span>Taux de conversion</span>
                      <span className="font-bold">
                        {stats ? ((stats.active_subscriptions / stats.total_users) * 100).toFixed(1) : 0}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Churn rate</span>
                      <span className="font-bold text-red-600">
                        {stats?.churn_rate?.toFixed(1) || 0}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>ARPU moyen</span>
                      <span className="font-bold">
                        {stats && stats.active_subscriptions > 0 
                          ? formatCurrency(stats.mrr / stats.active_subscriptions)
                          : formatCurrency(0)
                        }
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Utilisateurs actifs</span>
                      <span className="font-bold text-green-600">
                        {stats?.active_subscriptions || 0}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* User Detail Modal */}
      {selectedUser && (
        <Dialog open={!!selectedUser} onOpenChange={() => setSelectedUser(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Détails Utilisateur</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Nom complet</Label>
                  <p className="font-medium">{selectedUser.first_name} {selectedUser.last_name}</p>
                </div>
                <div>
                  <Label>Email</Label>
                  <p className="font-medium">{selectedUser.email}</p>
                </div>
                <div>
                  <Label>Entreprise</Label>
                  <p className="font-medium">{selectedUser.business_name || 'Non défini'}</p>
                </div>
                <div>
                  <Label>Posts générés</Label>
                  <p className="font-medium">{selectedUser.total_posts_generated || 0}</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>Actions d'administration</Label>
                <div className="flex space-x-2">
                  <Button
                    onClick={() => handleUpdateUserSubscription(selectedUser.id, 'active', 'pro')}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Activer Pro
                  </Button>
                  <Button
                    onClick={() => handleUpdateUserSubscription(selectedUser.id, 'trial')}
                    variant="outline"
                  >
                    Remettre en essai
                  </Button>
                  <Button
                    onClick={() => handleUpdateUserSubscription(selectedUser.id, 'expired')}
                    variant="destructive"
                  >
                    Expirer
                  </Button>
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default AdminDashboard;