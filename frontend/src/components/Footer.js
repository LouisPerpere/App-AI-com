import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Footer = ({ onShowPrivacyPolicy }) => {
  const [isLegalOpen, setIsLegalOpen] = useState(false);

  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Accordéon Mentions Légales Discret */}
        <div className="max-w-2xl mx-auto">
          <button
            onClick={() => setIsLegalOpen(!isLegalOpen)}
            className="w-full flex items-center justify-center space-x-2 text-xs text-gray-400 hover:text-gray-600 transition-colors py-3 rounded-lg hover:bg-gray-50"
          >
            <span>Mentions légales</span>
            <svg 
              className={`w-3 h-3 transition-transform duration-200 ${isLegalOpen ? 'rotate-180' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {isLegalOpen && (
            <div className="mt-3 p-4 bg-gray-50 border rounded-lg text-xs text-gray-500 leading-relaxed">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <div><strong>EI Fou De Vanille</strong></div>
                  <div>SIRET 952 513 661 00019</div>
                  <div>44 Rue De Lorraine</div>
                  <div>94700 Maisons Alfort • RCS Créteil</div>
                </div>
                <div className="space-y-1">
                  <div>Responsable : Alexandra Mara Perpere</div>
                  <div>
                    <a href="mailto:contact@claire-marcus.com" className="text-gray-600 hover:text-gray-700 underline">
                      contact@claire-marcus.com
                    </a>
                  </div>
                  <div>
                    Hébergement : <a href="https://emergentagent.com" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-700 underline">Emergent</a>
                  </div>
                </div>
              </div>
              <div className="text-center mt-4 pt-3 border-t border-gray-300 text-xs text-gray-500">
                © {new Date().getFullYear()} Claire & Marcus • TVA Non Applicable, art. 293 B du CGI • RGPD
              </div>
            </div>
          )}
        </div>
      </div>
    </footer>
  );
};

export default Footer;