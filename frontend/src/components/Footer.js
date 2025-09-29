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

          {/* Quick Links */}
          <div className="col-span-1">
            <h3 className="font-semibold text-gray-900 mb-4">Liens utiles</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link 
                  to="/mentions-legales" 
                  className="text-gray-600 hover:text-pink-600 transition-colors"
                >
                  Mentions légales
                </Link>
              </li>
              <li>
                <Link 
                  to="/politique-confidentialite" 
                  className="text-gray-600 hover:text-pink-600 transition-colors"
                >
                  Politique de confidentialité
                </Link>
              </li>
              <li>
                <a 
                  href="mailto:contact@claire-marcus.com"
                  className="text-gray-600 hover:text-pink-600 transition-colors"
                >
                  Contact
                </a>
              </li>
            </ul>
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
            
            {/* Legal info */}
            <div className="text-xs text-gray-500 text-center md:text-right leading-relaxed">
              <p className="mb-1">
                Édité par l'EI Fou De Vanille - SIRET 952 513 661 00019
              </p>
              <p className="mb-1">
                44 Rue De Lorraine, 94700 Maisons Alfort - RCS Créteil
              </p>
              <p>
                Hébergé sur{' '}
                <a 
                  href="https://emergentagent.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-pink-600 transition-colors"
                >
                  Emergent
                </a>
                {' '}(115 Rue Réaumur, 75002 Paris, France)
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;