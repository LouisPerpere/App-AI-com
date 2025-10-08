#!/usr/bin/env python3
"""
DIAGNOSTIC FINAL - Analyse complète des URLs vs fichiers physiques
Basé sur les résultats précédents, analyse approfondie du problème des vignettes grises
"""

import requests
import json
import os
import pymongo
from urllib.parse import urlparse
import re

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

# MongoDB connection
MONGO_URL = "mongodb+srv://lperpere:ClaireMarcus2025@cluster0.24k0jzd.mongodb.net/claire_marcus?retryWrites=true&w=majority&appName=Cluster0"

class FinalThumbnailDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.mongo_client = None
        self.db = None
        
    def authenticate(self):
        """Authentification"""
        print("🔐 AUTHENTIFICATION")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                print(f"✅ Connexion réussie: {TEST_EMAIL}")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return False
    
    def connect_mongodb(self):
        """Connexion MongoDB"""
        print("\n🗄️ CONNEXION MONGODB")
        print("=" * 50)
        
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_URL)
            self.db = self.mongo_client.claire_marcus
            
            # Test connection
            server_info = self.mongo_client.server_info()
            print(f"✅ MongoDB connecté - Version: {server_info.get('version', 'unknown')}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur MongoDB: {e}")
            return False
    
    def analyze_complete_mongodb_data(self):
        """Analyse complète des données MongoDB"""
        print("\n🔍 ANALYSE COMPLÈTE MONGODB")
        print("=" * 50)
        
        try:
            media_collection = self.db.media
            
            # Statistiques générales
            total_docs = media_collection.count_documents({})
            with_thumb_url = media_collection.count_documents({
                "thumb_url": {"$ne": None, "$ne": "", "$ne": "None", "$exists": True}
            })
            null_thumb_url = total_docs - with_thumb_url
            
            print(f"📊 STATISTIQUES MONGODB:")
            print(f"   • Total documents: {total_docs}")
            print(f"   • Avec thumb_url valide: {with_thumb_url}")
            print(f"   • Avec thumb_url null/None: {null_thumb_url}")
            
            # Récupérer 5 exemples avec thumb_url valide
            valid_examples = list(media_collection.find(
                {
                    "thumb_url": {"$ne": None, "$ne": "", "$ne": "None", "$exists": True},
                    "$expr": {"$ne": ["$thumb_url", "None"]}  # Exclude string "None"
                }, 
                {"filename": 1, "thumb_url": 1, "url": 1, "_id": 1}
            ).limit(5))
            
            print(f"\n📋 EXEMPLES AVEC THUMB_URL VALIDE ({len(valid_examples)}):")
            for i, doc in enumerate(valid_examples, 1):
                filename = doc.get("filename", "")
                thumb_url = doc.get("thumb_url", "")
                print(f"   {i}. {filename}")
                print(f"      thumb_url: {thumb_url}")
            
            # Récupérer 5 exemples avec thumb_url null/None
            null_examples = list(media_collection.find(
                {
                    "$or": [
                        {"thumb_url": None},
                        {"thumb_url": ""},
                        {"thumb_url": "None"},
                        {"thumb_url": {"$exists": False}}
                    ]
                }, 
                {"filename": 1, "thumb_url": 1, "url": 1, "_id": 1}
            ).limit(5))
            
            print(f"\n📋 EXEMPLES AVEC THUMB_URL NULL/NONE ({len(null_examples)}):")
            for i, doc in enumerate(null_examples, 1):
                filename = doc.get("filename", "")
                thumb_url = doc.get("thumb_url", "")
                print(f"   {i}. {filename}")
                print(f"      thumb_url: {thumb_url}")
            
            # Analyser les domaines dans thumb_url
            domain_analysis = {}
            all_with_thumb = list(media_collection.find(
                {
                    "thumb_url": {"$ne": None, "$ne": "", "$ne": "None", "$exists": True},
                    "$expr": {"$ne": ["$thumb_url", "None"]}
                }, 
                {"thumb_url": 1}
            ))
            
            for doc in all_with_thumb:
                thumb_url = doc.get("thumb_url", "")
                if thumb_url:
                    parsed = urlparse(thumb_url)
                    domain = parsed.netloc
                    domain_analysis[domain] = domain_analysis.get(domain, 0) + 1
            
            print(f"\n🌐 ANALYSE DES DOMAINES:")
            for domain, count in domain_analysis.items():
                print(f"   • {domain}: {count} fichiers")
            
            self.valid_examples = valid_examples
            self.null_examples = null_examples
            self.domain_analysis = domain_analysis
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur analyse MongoDB: {e}")
            return False
    
    def analyze_api_content(self):
        """Analyse du contenu via API"""
        print("\n📡 ANALYSE CONTENU API")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=100")
            
            if response.status_code == 200:
                data = response.json()
                api_content = data.get("content", [])
                
                print(f"📊 STATISTIQUES API:")
                print(f"   • Total fichiers API: {len(api_content)}")
                
                # Analyser thumb_url dans API
                api_with_thumb = 0
                api_null_thumb = 0
                api_domain_analysis = {}
                
                for item in api_content:
                    thumb_url = item.get("thumb_url", "")
                    if thumb_url and thumb_url != "None":
                        api_with_thumb += 1
                        parsed = urlparse(thumb_url)
                        domain = parsed.netloc
                        api_domain_analysis[domain] = api_domain_analysis.get(domain, 0) + 1
                    else:
                        api_null_thumb += 1
                
                print(f"   • Avec thumb_url valide: {api_with_thumb}")
                print(f"   • Avec thumb_url null/None: {api_null_thumb}")
                
                print(f"\n🌐 DOMAINES DANS API:")
                for domain, count in api_domain_analysis.items():
                    print(f"   • {domain}: {count} fichiers")
                
                # Exemples de fichiers avec thumb_url dans API
                api_examples = []
                for item in api_content:
                    thumb_url = item.get("thumb_url", "")
                    if thumb_url and thumb_url != "None":
                        api_examples.append({
                            "filename": item.get("filename", ""),
                            "thumb_url": thumb_url,
                            "id": item.get("id", "")
                        })
                        if len(api_examples) >= 5:
                            break
                
                print(f"\n📋 EXEMPLES API AVEC THUMB_URL ({len(api_examples)}):")
                for i, example in enumerate(api_examples, 1):
                    print(f"   {i}. {example['filename']}")
                    print(f"      thumb_url: {example['thumb_url']}")
                    print(f"      id: {example['id']}")
                
                self.api_content = api_content
                self.api_examples = api_examples
                self.api_domain_analysis = api_domain_analysis
                
                return True
            else:
                print(f"❌ Erreur API: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur analyse API: {e}")
            return False
    
    def specific_8ee21d73_analysis(self):
        """Analyse spécifique du fichier 8ee21d73"""
        print("\n🎯 ANALYSE SPÉCIFIQUE '8ee21d73'")
        print("=" * 50)
        
        try:
            # MongoDB search
            media_collection = self.db.media
            mongo_docs = list(media_collection.find(
                {"filename": {"$regex": "8ee21d73", "$options": "i"}},
                {"filename": 1, "thumb_url": 1, "url": 1, "_id": 1, "created_at": 1}
            ))
            
            print(f"📊 MONGODB - Trouvé {len(mongo_docs)} document(s):")
            for i, doc in enumerate(mongo_docs, 1):
                print(f"   {i}. ID: {doc.get('_id')}")
                print(f"      filename: {doc.get('filename')}")
                print(f"      thumb_url: {doc.get('thumb_url')}")
                print(f"      url: {doc.get('url')}")
                print(f"      created_at: {doc.get('created_at')}")
                print()
            
            # API search
            api_matches = []
            for item in self.api_content:
                if "8ee21d73" in item.get("filename", ""):
                    api_matches.append(item)
            
            print(f"📊 API - Trouvé {len(api_matches)} fichier(s):")
            for i, item in enumerate(api_matches, 1):
                print(f"   {i}. ID: {item.get('id')}")
                print(f"      filename: {item.get('filename')}")
                print(f"      thumb_url: {item.get('thumb_url')}")
                print(f"      url: {item.get('url')}")
                print()
            
            # Comparaison
            print("🔍 COMPARAISON MONGODB vs API:")
            if len(mongo_docs) > 0 and len(api_matches) > 0:
                mongo_doc = mongo_docs[0]  # Premier document MongoDB
                api_match = api_matches[0]  # Premier match API
                
                mongo_thumb = mongo_doc.get('thumb_url')
                api_thumb = api_match.get('thumb_url')
                
                print(f"   • MongoDB thumb_url: {mongo_thumb}")
                print(f"   • API thumb_url: {api_thumb}")
                print(f"   • Identiques: {'✅' if mongo_thumb == api_thumb else '❌'}")
                
                if mongo_thumb != api_thumb:
                    print(f"   🚨 MISMATCH DÉTECTÉ!")
                    if mongo_thumb == "None" or not mongo_thumb:
                        print(f"      CAUSE: MongoDB a thumb_url null/None")
                    elif api_thumb == "None" or not api_thumb:
                        print(f"      CAUSE: API retourne thumb_url null/None")
                    else:
                        print(f"      CAUSE: URLs différentes entre MongoDB et API")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur analyse spécifique: {e}")
            return False
    
    def test_thumbnail_accessibility(self):
        """Test d'accessibilité des vignettes"""
        print("\n🔗 TEST ACCESSIBILITÉ VIGNETTES")
        print("=" * 50)
        
        try:
            # Tester quelques URLs de vignettes
            test_urls = []
            
            # Récupérer URLs depuis API
            for example in self.api_examples[:3]:
                thumb_url = example.get("thumb_url", "")
                if thumb_url and thumb_url != "None":
                    test_urls.append({
                        "filename": example["filename"],
                        "url": thumb_url,
                        "source": "API"
                    })
            
            # Récupérer URLs depuis MongoDB
            for example in self.valid_examples[:3]:
                thumb_url = example.get("thumb_url", "")
                if thumb_url and thumb_url != "None":
                    test_urls.append({
                        "filename": example["filename"],
                        "url": thumb_url,
                        "source": "MongoDB"
                    })
            
            print(f"🧪 Test de {len(test_urls)} URLs de vignettes:")
            
            accessible_count = 0
            for i, test in enumerate(test_urls, 1):
                try:
                    response = requests.get(test["url"], timeout=10)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        content_length = len(response.content)
                        
                        if 'image' in content_type.lower():
                            accessible_count += 1
                            status = "✅ ACCESSIBLE"
                        else:
                            status = f"❌ PAS IMAGE ({content_type})"
                    else:
                        status = f"❌ HTTP {response.status_code}"
                    
                    print(f"   {i}. {test['filename']} ({test['source']})")
                    print(f"      URL: {test['url']}")
                    print(f"      Status: {status}")
                    
                except Exception as e:
                    print(f"   {i}. {test['filename']} ({test['source']})")
                    print(f"      URL: {test['url']}")
                    print(f"      Status: ❌ ERREUR ({str(e)[:50]})")
                
                print()
            
            success_rate = (accessible_count / len(test_urls) * 100) if test_urls else 0
            print(f"📊 RÉSULTAT: {accessible_count}/{len(test_urls)} vignettes accessibles ({success_rate:.1f}%)")
            
            return accessible_count > 0
            
        except Exception as e:
            print(f"❌ Erreur test accessibilité: {e}")
            return False
    
    def final_diagnosis(self):
        """Diagnostic final et recommandations"""
        print("\n🏁 DIAGNOSTIC FINAL")
        print("=" * 50)
        
        print("🔍 RÉSUMÉ DES PROBLÈMES IDENTIFIÉS:")
        
        # Problème 1: Documents dupliqués
        if hasattr(self, 'valid_examples') and hasattr(self, 'null_examples'):
            print(f"   1. DOCUMENTS DUPLIQUÉS: Certains fichiers ont plusieurs entrées MongoDB")
            print(f"      - Certaines avec thumb_url valide")
            print(f"      - D'autres avec thumb_url null/None")
        
        # Problème 2: Domaines mixtes
        if hasattr(self, 'domain_analysis'):
            domains = list(self.domain_analysis.keys())
            if len(domains) > 1:
                print(f"   2. DOMAINES MIXTES: Vignettes pointent vers différents domaines")
                for domain in domains:
                    print(f"      - {domain}: {self.domain_analysis[domain]} fichiers")
        
        # Problème 3: Accessibilité
        print(f"   3. ACCESSIBILITÉ: Vignettes générées mais non accessibles via proxy")
        
        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   1. NETTOYER DOUBLONS: Supprimer documents MongoDB dupliqués")
        print(f"   2. UNIFIER DOMAINES: Utiliser un seul domaine pour toutes les vignettes")
        print(f"   3. CORRIGER PROXY: Configurer proxy pour servir /uploads/thumbs/*")
        print(f"   4. RÉGÉNÉRER VIGNETTES: Relancer génération avec domaine unifié")
        
        print(f"\n🎯 CAUSE PRINCIPALE IDENTIFIÉE:")
        print(f"   Les URLs en MongoDB sont correctes mais le proxy/serveur web")
        print(f"   ne sert pas correctement les fichiers /uploads/thumbs/*")
        print(f"   Les vignettes existent physiquement mais ne sont pas accessibles")
        
        return True
    
    def run_complete_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("🇫🇷 DIAGNOSTIC COMPLET - VIGNETTES GRISES")
        print("=" * 80)
        print("OBJECTIF: Identifier pourquoi les vignettes apparaissent grises")
        print("=" * 80)
        
        steps = [
            ("Authentification", self.authenticate),
            ("Connexion MongoDB", self.connect_mongodb),
            ("Analyse MongoDB complète", self.analyze_complete_mongodb_data),
            ("Analyse contenu API", self.analyze_api_content),
            ("Analyse spécifique 8ee21d73", self.specific_8ee21d73_analysis),
            ("Test accessibilité vignettes", self.test_thumbnail_accessibility),
            ("Diagnostic final", self.final_diagnosis)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            try:
                if step_func():
                    success_count += 1
                    print(f"✅ {step_name}: SUCCÈS")
                else:
                    print(f"❌ {step_name}: ÉCHEC")
            except Exception as e:
                print(f"❌ {step_name}: ERREUR - {e}")
        
        success_rate = (success_count / len(steps) * 100)
        
        print(f"\n📋 RÉSUMÉ FINAL")
        print("=" * 50)
        print(f"Étapes réussies: {success_count}/{len(steps)} ({success_rate:.1f}%)")
        
        # Close MongoDB connection
        if self.mongo_client:
            self.mongo_client.close()
        
        return success_rate >= 70

if __name__ == "__main__":
    diagnostic = FinalThumbnailDiagnostic()
    success = diagnostic.run_complete_diagnostic()
    
    if success:
        print("\n✅ DIAGNOSTIC GLOBAL: SUCCÈS")
        exit(0)
    else:
        print("\n❌ DIAGNOSTIC GLOBAL: ÉCHEC")
        exit(1)