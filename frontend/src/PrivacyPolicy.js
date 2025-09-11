import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Shield, ArrowLeft } from 'lucide-react';

const PrivacyPolicy = ({ onBack }) => {
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
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Politique de confidentialité</h1>
              <p className="text-gray-600">claire-marcus.com</p>
            </div>
          </div>
          
          <p className="text-sm text-gray-500">Dernière mise à jour : 11/09/2025</p>
        </div>

        <Card className="shadow-lg">
          <CardContent className="p-8 space-y-8">
            
            {/* Section 1 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">1</span>
                Responsable du traitement
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Le site claire-marcus.com est édité par :</p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p><strong>Claire & Marcus</strong></p>
                  <p>EI Fou de Vanille, Enregistrée au RCS de Créteil, SIRET 952 513 661 00019.</p>
                  <p>TVA Non Applicable, art. 293 B du CGI</p>
                  <p>Adresse : 44 Rue De Lorraine, 94700 Maisons Alfort</p>
                  <p>Email : contact@claire-marcus.com</p>
                </div>
                <p>Le responsable du traitement au sens du Règlement Général sur la Protection des Données (RGPD) est <strong>Alexandra Mara Perpere</strong>.</p>
              </div>
            </section>

            {/* Section 2 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
                Données collectées
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Nous collectons et traitons les données suivantes :</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li><strong>Données d'identification :</strong> nom, prénom, adresse e-mail, mot de passe.</li>
                  <li><strong>Données professionnelles :</strong> description de l'activité, localisation, budget publicitaire, informations de connexion aux réseaux sociaux.</li>
                  <li><strong>Contenus fournis :</strong> photos, vidéos, textes, événements, commentaires.</li>
                  <li><strong>Données techniques :</strong> adresse IP, logs de connexion, type d'appareil, statistiques d'utilisation.</li>
                  <li><strong>Données de facturation (si applicables) :</strong> coordonnées de facturation, historique des paiements.</li>
                </ul>
                <p className="bg-green-50 p-3 rounded-lg text-green-800">
                  <strong>Aucune donnée sensible</strong> (au sens de l'article 9 RGPD) n'est collectée.
                </p>
              </div>
            </section>

            {/* Section 3 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
                Finalités et bases légales
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Les données sont utilisées pour :</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li>Créer et gérer votre compte utilisateur (exécution du contrat).</li>
                  <li>Générer automatiquement vos publications et programmer leur diffusion (exécution du contrat).</li>
                  <li>Améliorer nos services et l'expérience utilisateur (intérêt légitime).</li>
                  <li>Respecter nos obligations légales (facturation, sécurité, conservation) (obligation légale).</li>
                  <li>Envoyer des communications commerciales ou newsletters (consentement, que vous pouvez retirer à tout moment).</li>
                </ul>
              </div>
            </section>

            {/* Section 4 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">4</span>
                Partage des données
              </h2>
              <div className="text-gray-700 space-y-3">
                <div className="bg-red-50 p-3 rounded-lg text-red-800 mb-3">
                  <strong>Nous ne vendons jamais vos données.</strong>
                </div>
                <p>Elles peuvent être transmises uniquement à :</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li>Nos prestataires techniques (hébergement, stockage, maintenance, outils d'analyse).</li>
                  <li>Les plateformes sociales que vous connectez (Facebook, Instagram, LinkedIn, etc.), uniquement pour publier vos contenus.</li>
                  <li>Les autorités administratives ou judiciaires, sur réquisition légale.</li>
                </ul>
              </div>
            </section>

            {/* Section 5 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">5</span>
                Transfert hors Union européenne
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Certaines données peuvent être hébergées ou traitées en dehors de l'Union européenne (par ex. Emergent, MongoDB Atlas, situés aux États-Unis).</p>
                <p>Dans ce cas, nous nous assurons que :</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li>Les prestataires bénéficient de mécanismes de conformité tels que les Clauses Contractuelles Types (CCT) de la Commission européenne.</li>
                  <li>Les transferts sont limités aux stricts besoins du service.</li>
                </ul>
              </div>
            </section>

            {/* Section 6 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">6</span>
                Durée de conservation
              </h2>
              <div className="text-gray-700">
                <ul className="list-disc pl-6 space-y-2">
                  <li><strong>Compte utilisateur :</strong> tant que vous êtes inscrit.</li>
                  <li><strong>Contenus (photos, vidéos, posts) :</strong> jusqu'à suppression par vous, ou 12 mois après la clôture du compte.</li>
                  <li><strong>Logs techniques :</strong> 12 mois.</li>
                  <li><strong>Données de facturation :</strong> 10 ans (obligation légale).</li>
                </ul>
              </div>
            </section>

            {/* Section 7 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">7</span>
                Sécurité
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Nous mettons en œuvre des mesures de sécurité adaptées :</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li>Chiffrement des communications (HTTPS).</li>
                  <li>Accès restreints et authentifiés aux données.</li>
                  <li>Sauvegardes régulières.</li>
                  <li>Jetons d'accès chiffrés pour vos réseaux sociaux.</li>
                </ul>
              </div>
            </section>

            {/* Section 8 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">8</span>
                Vos droits
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Conformément au RGPD et à la loi Informatique et Libertés, vous disposez des droits suivants :</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li>Accès à vos données.</li>
                  <li>Rectification des données inexactes.</li>
                  <li>Suppression (« droit à l'oubli »).</li>
                  <li>Limitation du traitement.</li>
                  <li>Portabilité de vos données.</li>
                  <li>Opposition au traitement de vos données pour des motifs légitimes.</li>
                  <li>Retrait du consentement à tout moment (par ex. newsletter, publicités).</li>
                </ul>
                <div className="bg-blue-50 p-4 rounded-lg mt-4">
                  <p><strong>Pour exercer vos droits :</strong> contact@claire-marcus.com</p>
                  <p>Vous pouvez également introduire une réclamation auprès de la CNIL (www.cnil.fr).</p>
                </div>
              </div>
            </section>

            {/* Section 9 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">9</span>
                Cookies et traceurs
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Notre site utilise des cookies :</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li><strong>Nécessaires</strong> (authentification, session, sécurité).</li>
                  <li><strong>Statistiques</strong> (mesure d'audience anonyme).</li>
                  <li><strong>Marketing</strong> (uniquement avec votre consentement).</li>
                </ul>
                <p>Vous pouvez gérer vos préférences directement depuis votre navigateur.</p>
              </div>
            </section>

            {/* Section 10 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">10</span>
                Hébergement
              </h2>
              <div className="text-gray-700 space-y-3">
                <p>Le site est hébergé par :</p>
                <ul className="list-disc pl-6 space-y-2">
                  <li><strong>Frontend :</strong> Emergent</li>
                  <li><strong>Backend :</strong> Emergent</li>
                  <li><strong>Base de données :</strong> MongoDB Atlas (possiblement hors UE)</li>
                </ul>
              </div>
            </section>

            {/* Section 11 */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">11</span>
                Contact
              </h2>
              <div className="text-gray-700">
                <p>Pour toute question relative à vos données personnelles :</p>
                <div className="bg-purple-50 p-4 rounded-lg mt-3">
                  <p><strong>Claire & Marcus</strong></p>
                  <p>Email : contact@claire-marcus.com</p>
                </div>
              </div>
            </section>

          </CardContent>
        </Card>
        
        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>© 2025 Claire & Marcus - Tous droits réservés</p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;