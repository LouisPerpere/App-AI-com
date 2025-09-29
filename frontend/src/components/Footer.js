import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Main footer content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Logo & Brand */}
          <div className="col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-pink-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                Claire & Marcus
              </span>
            </div>
            <p className="text-gray-600 text-sm leading-relaxed">
              Votre assistant IA pour une présence sociale authentique et engageante. 
              Automatisez vos publications tout en gardant votre voix unique.
            </p>
          </div>

          {/* Mentions légales intégrées */}
          <div className="col-span-1">
            <h3 className="font-semibold text-gray-900 mb-4">Mentions légales</h3>
            <div className="space-y-2 text-xs text-gray-600 leading-relaxed">
              <p><strong>Éditeur :</strong> EI Fou De Vanille</p>
              <p><strong>SIRET :</strong> 952 513 661 00019</p>
              <p><strong>Adresse :</strong> 44 Rue De Lorraine, 94700 Maisons Alfort</p>
              <p><strong>RCS :</strong> Créteil</p>
              <p><strong>Responsable publication :</strong> Alexandra Perpere</p>
              <p><strong>Hébergeur :</strong> 
                <a 
                  href="https://emergentagent.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-pink-600 transition-colors ml-1"
                >
                  Emergent
                </a>
                <br />115 Rue Réaumur, 75002 Paris, France
              </p>
            </div>
          </div>

          {/* Contact Info */}
          <div className="col-span-1">
            <h3 className="font-semibold text-gray-900 mb-4">Contact</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p>
                <a 
                  href="mailto:contact@claire-marcus.com"
                  className="hover:text-pink-600 transition-colors"
                >
                  contact@claire-marcus.com
                </a>
              </p>
              <p>Responsable de la publication :<br />Alexandra Perpere</p>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200 mt-8 pt-6">
          {/* Bottom section */}
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-gray-600 text-center md:text-left">
              © {new Date().getFullYear()} Claire & Marcus - Tous droits réservés
            </div>
            
            {/* Politique de confidentialité */}
            <div className="text-xs text-gray-500 text-center md:text-right leading-relaxed">
              <p className="mb-2">
                <Link 
                  to="/politique-confidentialite" 
                  className="hover:text-pink-600 transition-colors underline"
                >
                  Politique de confidentialité
                </Link>
              </p>
              <p className="text-xs">
                Vos données personnelles sont traitées conformément au RGPD. 
                Nous ne partageons jamais vos informations avec des tiers.
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;