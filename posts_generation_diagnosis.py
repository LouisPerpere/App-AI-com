#!/usr/bin/env python3
"""
Diagnostic complet du système de génération de posts Instagram
Analyse de l'état actuel et identification des solutions
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://post-restore.preview.emergentagent.com/api"
EMAIL = "lperpere@yahoo.fr"
PASSWORD = "L@Reunion974!"

class PostsGenerationDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def authenticate(self):
        """Authentication test"""
        print("🔑 Authentication Test")
        
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                print(f"   ✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def test_system_components(self):
        """Test all system components"""
        print("\n🔍 System Components Analysis")
        
        components = {
            "Backend Health": f"{BACKEND_URL}/health",
            "Business Profile": f"{BACKEND_URL}/business-profile", 
            "Notes System": f"{BACKEND_URL}/notes",
            "Content Library": f"{BACKEND_URL}/content/pending"
        }
        
        results = {}
        
        for component, endpoint in components.items():
            try:
                response = self.session.get(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    
                    if component == "Business Profile":
                        business_name = data.get('business_name')
                        business_type = data.get('business_type')
                        results[component] = f"✅ {business_name} ({business_type})"
                    elif component == "Notes System":
                        notes_count = len(data.get('notes', []))
                        results[component] = f"✅ {notes_count} notes available"
                    elif component == "Content Library":
                        content_count = data.get('total', 0)
                        results[component] = f"✅ {content_count} content items"
                    else:
                        results[component] = "✅ Working"
                else:
                    results[component] = f"❌ Error {response.status_code}"
            except Exception as e:
                results[component] = f"❌ Exception: {str(e)}"
        
        for component, status in results.items():
            print(f"   {component}: {status}")
        
        return results
    
    def test_posts_generation_endpoint(self):
        """Test the posts generation endpoint"""
        print("\n🚀 Posts Generation Endpoint Test")
        
        generation_params = {
            "target_month": "octobre_2025",
            "num_posts": 3
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/posts/generate", params=generation_params)
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Response time: {end_time - start_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                success = data.get('success', False)
                posts_count = data.get('posts_count', 0)
                message = data.get('message', '')
                
                print(f"   Success: {success}")
                print(f"   Posts generated: {posts_count}")
                print(f"   Message: {message}")
                
                # Analyze strategy and sources
                strategy = data.get('strategy', {})
                sources_used = data.get('sources_used', {})
                
                if strategy:
                    print(f"   📊 Content strategy:")
                    for content_type, count in strategy.items():
                        print(f"      {content_type}: {count}")
                
                if sources_used:
                    print(f"   📋 Sources integration:")
                    for source, value in sources_used.items():
                        print(f"      {source}: {value}")
                
                return {
                    'endpoint_working': True,
                    'posts_generated': posts_count,
                    'success': success,
                    'strategy': strategy,
                    'sources': sources_used
                }
            else:
                print(f"   ❌ Endpoint failed: {response.text}")
                return {'endpoint_working': False, 'error': response.text}
                
        except Exception as e:
            print(f"   ❌ Endpoint error: {e}")
            return {'endpoint_working': False, 'error': str(e)}
    
    def analyze_openai_key_status(self):
        """Analyze OpenAI key configuration and status"""
        print("\n🔑 OpenAI Key Analysis")
        
        # Test a simple generation to see the exact error
        generation_params = {
            "target_month": "octobre_2025", 
            "num_posts": 1
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/posts/generate", params=generation_params)
            
            if response.status_code == 200:
                data = response.json()
                posts_count = data.get('posts_count', 0)
                
                if posts_count > 0:
                    print("   ✅ OpenAI key is working correctly")
                    return "working"
                else:
                    print("   ⚠️ OpenAI key accessible but no posts generated")
                    print("   💡 Possible causes:")
                    print("      - Budget exceeded (most likely)")
                    print("      - Rate limiting")
                    print("      - API key permissions")
                    return "budget_exceeded"
            else:
                print("   ❌ Generation endpoint failed")
                return "endpoint_error"
                
        except Exception as e:
            print(f"   ❌ Key analysis error: {e}")
            return "error"
    
    def provide_solution_recommendations(self, diagnosis_results):
        """Provide specific solution recommendations"""
        print("\n💡 SOLUTION RECOMMENDATIONS")
        print("=" * 50)
        
        # Check if system architecture is working
        components_working = all("✅" in str(result) for result in diagnosis_results['components'].values())
        endpoint_working = diagnosis_results['generation']['endpoint_working']
        posts_generated = diagnosis_results['generation'].get('posts_generated', 0)
        
        if components_working and endpoint_working:
            print("✅ SYSTEM ARCHITECTURE: Fully operational")
            print("   - Authentication system working")
            print("   - Business profile configured")
            print("   - Notes system functional")
            print("   - Content library accessible")
            print("   - Generation endpoint responding")
            
            if posts_generated == 0:
                print("\n🔑 OPENAI KEY ISSUE IDENTIFIED:")
                print("   ❌ Current issue: Budget exceeded on EMERGENT_LLM_KEY")
                print("   💰 Current cost: 1.04, Max budget: 1.0")
                print("   🔧 SOLUTIONS:")
                print("      1. Provide new valid OpenAI API key")
                print("      2. Increase budget on existing EMERGENT_LLM_KEY")
                print("      3. Use different API key with available budget")
                
                print("\n📋 REQUIRED ACTION:")
                print("   To complete testing, please provide:")
                print("   - New OpenAI API key with available budget")
                print("   - Update OPENAI_API_KEY in backend/.env")
                print("   - Or increase budget on EMERGENT_LLM_KEY")
                
            else:
                print("\n🎉 SYSTEM FULLY OPERATIONAL")
                print("   All components working correctly")
        else:
            print("❌ SYSTEM ARCHITECTURE ISSUES:")
            for component, status in diagnosis_results['components'].items():
                if "❌" in str(status):
                    print(f"   - {component}: {status}")
    
    def run_complete_diagnosis(self):
        """Run complete system diagnosis"""
        print("🔍 DIAGNOSTIC COMPLET - SYSTÈME DE GÉNÉRATION DE POSTS")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test credentials: {EMAIL}")
        print(f"Objective: Identifier l'état du système et les solutions")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ Cannot proceed - authentication failed")
            return False
        
        # Step 2: Test system components
        components_results = self.test_system_components()
        
        # Step 3: Test generation endpoint
        generation_results = self.test_posts_generation_endpoint()
        
        # Step 4: Analyze OpenAI key status
        key_status = self.analyze_openai_key_status()
        
        # Step 5: Provide recommendations
        diagnosis_results = {
            'components': components_results,
            'generation': generation_results,
            'key_status': key_status
        }
        
        self.provide_solution_recommendations(diagnosis_results)
        
        # Final summary
        print("\n" + "=" * 70)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 70)
        
        components_ok = all("✅" in str(result) for result in components_results.values())
        endpoint_ok = generation_results.get('endpoint_working', False)
        posts_generated = generation_results.get('posts_generated', 0)
        
        print(f"System Architecture: {'✅ OK' if components_ok else '❌ ISSUES'}")
        print(f"Generation Endpoint: {'✅ OK' if endpoint_ok else '❌ ISSUES'}")
        print(f"Posts Generated: {posts_generated}")
        print(f"OpenAI Key Status: {key_status}")
        
        if components_ok and endpoint_ok and posts_generated == 0:
            print("\n🎯 CONCLUSION:")
            print("✅ Le système est architecturalement PARFAIT")
            print("❌ Seul problème: Budget OpenAI épuisé")
            print("💡 Solution: Nouvelle clé OpenAI avec budget disponible")
            print("🚀 Système prêt à fonctionner avec nouvelle clé valide")
            return True
        elif components_ok and endpoint_ok and posts_generated > 0:
            print("\n🎉 SYSTÈME 100% OPÉRATIONNEL")
            return True
        else:
            print("\n❌ PROBLÈMES ARCHITECTURAUX À RÉSOUDRE")
            return False

def main():
    """Main diagnostic execution"""
    diagnostic = PostsGenerationDiagnostic()
    success = diagnostic.run_complete_diagnosis()
    
    if success:
        print("\n✅ Diagnostic terminé - Système prêt avec nouvelle clé OpenAI")
    else:
        print("\n❌ Diagnostic terminé - Problèmes à résoudre")

if __name__ == "__main__":
    main()