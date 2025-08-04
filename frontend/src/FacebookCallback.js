import React, { useEffect } from 'react';

const FacebookCallback = () => {
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const error = urlParams.get('error');

    if (error) {
      // Envoyer l'erreur à la fenêtre parent
      if (window.opener) {
        window.opener.postMessage({
          type: 'FACEBOOK_AUTH_ERROR',
          error: error
        }, window.location.origin);
        window.close();
      }
      return;
    }

    if (code && state) {
      // Échanger le code pour un token
      const exchangeToken = async () => {
        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social/facebook/callback`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({ code, state })
          });

          const data = await response.json();

          if (response.ok) {
            // Succès - envoyer le message à la fenêtre parent
            if (window.opener) {
              window.opener.postMessage({
                type: 'FACEBOOK_AUTH_SUCCESS',
                data: data
              }, window.location.origin);
              window.close();
            }
          } else {
            throw new Error(data.detail || 'Erreur lors de l\'authentification');
          }
        } catch (error) {
          console.error('Token exchange error:', error);
          if (window.opener) {
            window.opener.postMessage({
              type: 'FACEBOOK_AUTH_ERROR',
              error: error.message
            }, window.location.origin);
            window.close();
          }
        }
      };

      exchangeToken();
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto">
          <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        </div>
        <h1 className="text-xl font-semibold text-gray-900">Connexion Facebook en cours...</h1>
        <p className="text-gray-600">Veuillez patienter pendant que nous finalisons la connexion.</p>
      </div>
    </div>
  );
};

export default FacebookCallback;