import React from 'react';
import { ArrowLeft, Scale, Mail, MapPin, Building2, Phone } from 'lucide-react';
import { Link } from 'react-router-dom';

const MentionsLegales = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-4 mb-4">
            <Link 
              to="/" 
              className="inline-flex items-center text-gray-600 hover:text-pink-600 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour à l'accueil
            </Link>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Scale className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Mentions légales</h1>
              <p className="text-gray-600">Informations légales obligatoires</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-sm p-8 space-y-8">
          
          {/* Identification de l'éditeur */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
              <Building2 className="w-6 h-6 mr-3 text-pink-600" />
              Identification de l'éditeur
            </h2>
            
            <div className="bg-pink-50 border border-pink-200 rounded-xl p-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Société</h3>
                  <div className="space-y-2 text-gray-700">
                    <p><strong>Dénomination sociale :</strong> EI Fou De Vanille</p>
                    <p><strong>Forme juridique :</strong> Entreprise Individuelle</p>
                    <p><strong>SIRET :</strong> 952 513 661 00019</p>
                    <p><strong>RCS :</strong> Créteil</p>
                    <p><strong>TVA :</strong> Non Applicable, art. 293 B du CGI</p>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Adresse</h3>
                  <div className="space-y-2 text-gray-700">
                    <div className="flex items-start space-x-2">
                      <MapPin className="w-4 h-4 text-pink-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <p>44 Rue De Lorraine</p>
                        <p>94700 Maisons Alfort</p>
                        <p>France</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Responsable de la publication */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
              <Mail className="w-6 h-6 mr-3 text-pink-600" />
              Responsable de la publication
            </h2>
            
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
              <div className="space-y-3">
                <p><strong>Directrice de la publication :</strong> Alexandra Perpere</p>
                <p>
                  <strong>Contact :</strong>{' '}
                  <a 
                    href="mailto:contact@claire-marcus.com"
                    className="text-pink-600 hover:text-pink-700 transition-colors"
                  >
                    contact@claire-marcus.com
                  </a>
                </p>
              </div>
            </div>
          </section>

          {/* Hébergement */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
              <Building2 className="w-6 h-6 mr-3 text-pink-600" />
              Hébergement
            </h2>
            
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <div className="space-y-3">
                <p><strong>Hébergeur :</strong> Emergent</p>
                <p><strong>Adresse :</strong> 115 Rue Réaumur, 75002 Paris, France</p>
                <p>
                  <strong>Site web :</strong>{' '}
                  <a 
                    href="https://emergentagent.com" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    emergentagent.com
                  </a>
                </p>
              </div>
            </div>
          </section>

          {/* Propriété intellectuelle */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              Propriété intellectuelle
            </h2>
            
            <div className="prose prose-gray max-w-none">
              <p>
                L'ensemble des contenus présents sur le site Claire & Marcus, incluant notamment les textes, 
                images, graphiques, logos, vidéos, icônes et éléments sonores, ainsi que leur mise en forme 
                sont la propriété exclusive de l'EI Fou De Vanille ou de ses partenaires, à l'exception des 
                marques, logos ou contenus appartenant à d'autres sociétés partenaires ou auteurs.
              </p>
              
              <p>
                Toute reproduction, représentation, modification, publication, adaptation de tout ou partie 
                des éléments du site, quel que soit le moyen ou le procédé utilisé, est interdite, sauf 
                autorisation écrite préalable de l'EI Fou De Vanille.
              </p>
            </div>
          </section>

          {/* Protection des données */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              Protection des données personnelles
            </h2>
            
            <div className="prose prose-gray max-w-none">
              <p>
                Les données personnelles collectées sur ce site font l'objet d'un traitement informatique 
                destiné à la gestion de votre compte utilisateur et à l'amélioration de nos services.
              </p>
              
              <p>
                Conformément à la loi « informatique et libertés » du 6 janvier 1978 modifiée et au 
                Règlement Général sur la Protection des Données (RGPD), vous bénéficiez d'un droit d'accès, 
                de rectification, de portabilité et d'effacement de vos données ou encore de limitation 
                du traitement.
              </p>
              
              <p>
                Vous pouvez exercer ces droits en nous contactant à l'adresse{' '}
                <a 
                  href="mailto:contact@claire-marcus.com"
                  className="text-pink-600 hover:text-pink-700 transition-colors"
                >
                  contact@claire-marcus.com
                </a>
                .
              </p>
              
              <p>
                Pour plus d'informations, consultez notre{' '}
                <Link 
                  to="/politique-confidentialite"
                  className="text-pink-600 hover:text-pink-700 transition-colors"
                >
                  Politique de confidentialité
                </Link>
                .
              </p>
            </div>
          </section>

          {/* Limitation de responsabilité */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              Limitation de responsabilité
            </h2>
            
            <div className="prose prose-gray max-w-none">
              <p>
                L'EI Fou De Vanille ne pourra être tenue responsable des dommages directs et indirects 
                causés au matériel de l'utilisateur, lors de l'accès au site Claire & Marcus, et résultant 
                soit de l'utilisation d'un matériel ne répondant pas aux spécifications indiquées, soit 
                de l'apparition d'un bug ou d'une incompatibilité.
              </p>
              
              <p>
                L'EI Fou De Vanille ne pourra également être tenue responsable des dommages indirects 
                (tels par exemple qu'une perte de marché ou perte d'une chance) consécutifs à l'utilisation 
                du site.
              </p>
            </div>
          </section>

          {/* Droit applicable */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              Droit applicable
            </h2>
            
            <div className="prose prose-gray max-w-none">
              <p>
                Tant le présent site que les modalités et conditions de son utilisation sont régies par 
                le droit français, quel que soit le lieu d'utilisation. En cas de contestation éventuelle, 
                et après l'échec de toute tentative de recherche d'une solution amiable, les tribunaux 
                français seront seuls compétents pour connaître de ce litige.
              </p>
            </div>
          </section>

          {/* Date de mise à jour */}
          <section className="border-t border-gray-200 pt-6">
            <p className="text-sm text-gray-500 text-center">
              Dernière mise à jour : {new Date().toLocaleDateString('fr-FR', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default MentionsLegales;