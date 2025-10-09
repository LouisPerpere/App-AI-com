import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './components/ui/card';
import { Shield, ArrowLeft, CheckCircle, AlertCircle, Trash2, Mail, Clock } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

const DataDeletion = ({ onBack }) => {
  const [searchParams] = useSearchParams();
  const confirmationCode = searchParams.get('code');
  const [showConfirmation, setShowConfirmation] = useState(false);

  useEffect(() => {
    if (confirmationCode) {
      setShowConfirmation(true);
    }
  }, [confirmationCode]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-white p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="flex items-center space-x-2 text-purple-600 hover:text-purple-700 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Retour</span>
          </button>
          
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-rose-500 rounded-2xl flex items-center justify-center">
              <Trash2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Suppression de données</h1>
              <p className="text-gray-600">claire-marcus.com</p>
            </div>
          </div>
          
          <p className="text-sm text-gray-500">Dernière mise à jour : 11/09/2025</p>
        </div>

        {/* Confirmation Card if code present */}
        {showConfirmation && confirmationCode && (
          <Card className="shadow-lg mb-6 border-green-200 bg-green-50">
            <CardContent className="p-6">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-green-900 mb-2">
                    Demande de suppression enregistrée
                  </h3>
                  <p className="text-green-800 mb-3">
                    Votre demande de suppression de données a été reçue et enregistrée avec succès.
                  </p>
                  <div className="bg-white p-3 rounded-lg border border-green-300">
                    <p className="text-sm text-gray-700 mb-1">Code de confirmation :</p>
                    <p className="font-mono text-green-700 font-bold">{confirmationCode}</p>
                  </div>
                  <p className="text-sm text-green-700 mt-3">
                    Conservez ce code pour toute référence future concernant votre demande.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <Card className="shadow-lg">
          <CardContent className="p-8 space-y-8">
            
            {/* Section 1: Introduction */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">1</span>
                À propos de la suppression de données
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>
                  Si vous avez utilisé votre compte Facebook pour vous connecter à <strong>Claire & Marcus</strong>, 
                  vous avez le droit de demander la suppression de vos données personnelles conformément au RGPD.
                </p>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm text-blue-900 font-medium mb-1">
                        Important
                      </p>
                      <p className="text-sm text-blue-800">
                        Cette page concerne uniquement les demandes de suppression initiées par Facebook. 
                        Si vous souhaitez supprimer votre compte directement, connectez-vous à votre tableau de bord 
                        et accédez aux paramètres de votre compte.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 2: Données concernées */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
                Données concernées par la suppression
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Lorsque vous demandez la suppression de vos données, nous supprimons :</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Vos informations de connexion Facebook (tokens d'accès, ID Facebook)</li>
                  <li>Vos autorisations de publication sur Facebook et Instagram</li>
                  <li>Les liens entre votre compte Facebook et votre compte Claire & Marcus</li>
                </ul>
                <div className="bg-amber-50 p-4 rounded-lg border border-amber-200 mt-4">
                  <div className="flex items-start space-x-3">
                    <Clock className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm text-amber-900 font-medium mb-1">
                        Conservation des données de compte
                      </p>
                      <p className="text-sm text-amber-800">
                        Si vous avez créé un compte Claire & Marcus avec un email et mot de passe, 
                        vos données de profil, posts et bibliothèque seront <strong>conservés</strong>. 
                        Seule la connexion Facebook sera supprimée. Pour supprimer complètement votre compte, 
                        utilisez l'option de suppression dans les paramètres de votre compte.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 3: Processus */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
                Processus de suppression
              </h2>
              <div className="text-gray-700 space-y-4">
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                      1
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Demande via Facebook</p>
                      <p className="text-sm text-gray-600">
                        Vous initiez la demande depuis les paramètres de votre compte Facebook, 
                        dans la section "Apps et sites web".
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                      2
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Réception automatique</p>
                      <p className="text-sm text-gray-600">
                        Notre système reçoit automatiquement votre demande de Facebook et génère 
                        un code de confirmation unique.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                      3
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Suppression immédiate</p>
                      <p className="text-sm text-gray-600">
                        Les données de connexion Facebook sont supprimées immédiatement et automatiquement 
                        de nos serveurs.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                      4
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Confirmation</p>
                      <p className="text-sm text-gray-600">
                        Vous recevez un code de confirmation sur cette page pour attester de la suppression.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg border border-green-200 mt-4">
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm text-green-900 font-medium mb-1">
                        Délai de traitement
                      </p>
                      <p className="text-sm text-green-800">
                        Les demandes de suppression sont traitées <strong>immédiatement et automatiquement</strong>. 
                        Aucune intervention manuelle n'est nécessaire.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 4: Contact */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">4</span>
                Besoin d'aide ?
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>
                  Si vous avez des questions concernant la suppression de vos données ou si vous rencontrez 
                  des difficultés, n'hésitez pas à nous contacter :
                </p>
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <div className="flex items-center space-x-3 mb-3">
                    <Mail className="w-5 h-5 text-purple-600" />
                    <p className="font-semibold text-gray-900">Contact</p>
                  </div>
                  <p className="text-gray-700">
                    <strong>Email :</strong>{' '}
                    <a href="mailto:contact@claire-marcus.com" className="text-purple-600 hover:text-purple-700 underline">
                      contact@claire-marcus.com
                    </a>
                  </p>
                  <p className="text-gray-700 mt-2">
                    <strong>Responsable :</strong> Alexandra Mara Perpere
                  </p>
                  <p className="text-gray-700 mt-2">
                    <strong>Entreprise :</strong> EI Fou de Vanille
                  </p>
                  <p className="text-gray-700">
                    SIRET 952 513 661 00019
                  </p>
                </div>
              </div>
            </section>

            {/* Section 5: Informations légales */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">5</span>
                Vos droits RGPD
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>
                  Conformément au Règlement Général sur la Protection des Données (RGPD), vous disposez des droits suivants :
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Droit d'accès :</strong> Obtenir une copie de vos données personnelles</li>
                  <li><strong>Droit de rectification :</strong> Corriger vos données inexactes</li>
                  <li><strong>Droit à l'effacement :</strong> Supprimer vos données (droit à l'oubli)</li>
                  <li><strong>Droit à la portabilité :</strong> Récupérer vos données dans un format structuré</li>
                  <li><strong>Droit d'opposition :</strong> Vous opposer au traitement de vos données</li>
                </ul>
                <p className="text-sm text-gray-600 mt-4">
                  Pour exercer ces droits, contactez-nous à{' '}
                  <a href="mailto:contact@claire-marcus.com" className="text-purple-600 hover:text-purple-700 underline">
                    contact@claire-marcus.com
                  </a>
                </p>
              </div>
            </section>

            {/* Footer */}
            <div className="pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-500 text-center">
                Cette page est conforme aux exigences de Facebook en matière de suppression de données.
                <br />
                Endpoint technique : <code className="bg-gray-100 px-2 py-1 rounded text-xs">
                  https://claire-marcus.com/api/social/facebook/data-deletion
                </code>
              </p>
            </div>

          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DataDeletion;
