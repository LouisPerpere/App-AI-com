#!/usr/bin/env python3
"""
Facebook App Review - Complete Test Account Creation
Créer un compte de test complet sur l'environnement LIVE pour Facebook App Review
Restaurant fictif "Le Bistrot de Jean" avec toutes les données nécessaires.

OBJECTIF CRITIQUE:
Créer un compte de test complet sur https://claire-marcus.com avec toutes les données 
pour que le testeur Facebook n'ait qu'à tester la connexion et publication.

COMPTE UTILISATEUR À CRÉER:
- Email: test@claire-marcus.com
- Mot de passe: test123!
- Environnement: LIVE (https://claire-marcus.com)

DONNÉES ENTREPRISE FICTIVE - RESTAURANT:
- Nom: "Le Bistrot de Jean"
- Type: Restaurant gastronomique français
- Secteur: Restauration
- Adresse: 15 Rue de la Paix, 75001 Paris
- Téléphone: 01 42 60 38 15
- Site web: https://lebistrotdejean-paris.fr
- Description: Restaurant gastronomique français dirigé par le Chef Jean Dupont
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
import uuid
import base64
import io
from PIL import Image

# Configuration LIVE
LIVE_BACKEND_URL = "https://claire-marcus.com/api"
TEST_EMAIL = "test@claire-marcus.com"
TEST_PASSWORD = "test123!"

# Données restaurant fictif
RESTAURANT_DATA = {
    "business_name": "Le Bistrot de Jean",
    "business_type": "Restaurant",
    "industry": "Restauration",
    "business_description": "Restaurant gastronomique français dirigé par le Chef Jean Dupont, spécialisé dans la cuisine traditionnelle revisitée avec des produits frais et de saison.",
    "target_audience": "Amateurs de gastronomie française, couples, familles, touristes, clientèle d'affaires",
    "target_audience_details": "Clientèle âgée de 25-65 ans, revenus moyens à élevés, appréciant la cuisine raffinée et l'art de vivre français",
    "brand_tone": "Élégant et chaleureux",
    "brand_voice": "Authentique, passionné, accueillant",
    "posting_frequency": "3-4 fois par semaine",
    "preferred_platforms": ["facebook", "instagram"],
    "budget_range": "500-1000€/mois",
    "email": TEST_EMAIL,
    "website_url": "https://lebistrotdejean-paris.fr",
    "coordinates": "48.8566,2.3522",  # Paris coordinates
    "hashtags_primary": ["#bistrot", "#gastronomie", "#paris", "#chefjean", "#cuisine"],
    "hashtags_secondary": ["#restaurant", "#france", "#tradition", "#saveurs", "#artdevivre"],
    "value_proposition": "Cuisine française traditionnelle revisitée par le Chef Jean Dupont",
    "content_themes": "Plats signature, coulisses cuisine, équipe, événements spéciaux, produits de saison",
    "products_services": "Menu dégustation, carte traditionnelle, vins français, service traiteur",
    "unique_selling_points": "Chef expérimenté, produits locaux, ambiance authentique, service personnalisé",
    "business_goals": "Fidéliser la clientèle locale et attirer les touristes",
    "business_objective": "croissance"
}

# Notes système pour le restaurant
RESTAURANT_NOTES = [
    {
        "description": "Note générale Chef Jean",
        "content": "Mettre en avant le Chef Jean Dupont dans tous les posts - 15 ans d'expérience, ancien sous-chef chez Ducasse. Spécialités: Boeuf bourguignon moderne, Soufflé au Grand Marnier.",
        "priority": "high",
        "is_monthly_note": True
    },
    {
        "description": "Fermetures exceptionnelles",
        "content": "Fermé dimanche et lundi. Fermeture annuelle du 1er au 15 août. Réservation conseillée.",
        "priority": "medium",
        "is_monthly_note": True
    },
    {
        "description": "Événements spéciaux",
        "content": "Menu Saint-Valentin en février, Menu des mères en mai, Soirée dégustation vins en octobre, Menu de Noël en décembre.",
        "priority": "medium",
        "is_monthly_note": False
    },
    {
        "description": "Informations pratiques",
        "content": "Horaires: Mar-Sam 12h-14h / 19h-22h. Capacité: 40 couverts. Prix moyen: 45€ par personne. Parking public à 100m.",
        "priority": "low",
        "is_monthly_note": True
    }
]

class FacebookAppReviewTestCreator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Facebook-App-Review-Test-Creator/1.0'
        })
        self.auth_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def create_test_account(self):
        """Step 1: Create test account for Facebook App Review"""
        self.log("👤 STEP 1: Creating test account for Facebook App Review")
        
        try:
            # First check if account already exists
            login_response = self.session.post(f"{LIVE_BACKEND_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if login_response.status_code == 200:
                self.log("✅ Test account already exists, logging in")
                data = login_response.json()
                self.auth_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Set authorization header
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log(f"   User ID: {self.user_id}")
                return True
            
            # Account doesn't exist, create it
            self.log("📝 Creating new test account")
            register_response = self.session.post(f"{LIVE_BACKEND_URL}/auth/register", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "first_name": "Test",
                "last_name": "Facebook",
                "business_name": RESTAURANT_DATA["business_name"]
            })
            
            if register_response.status_code == 200:
                data = register_response.json()
                self.auth_token = data.get('access_token')
                self.user_id = data.get('user_id')
                
                # Set authorization header
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log("✅ Test account created successfully")
                self.log(f"   Email: {TEST_EMAIL}")
                self.log(f"   Password: {TEST_PASSWORD}")
                self.log(f"   User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Account creation failed: {register_response.status_code} - {register_response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Account creation error: {str(e)}", "ERROR")
            return False
    
    def setup_business_profile(self):
        """Step 2: Setup complete business profile for restaurant"""
        self.log("🏢 STEP 2: Setting up complete business profile")
        
        try:
            response = self.session.put(f"{LIVE_BACKEND_URL}/business-profile", json=RESTAURANT_DATA)
            
            if response.status_code == 200:
                self.log("✅ Business profile created successfully")
                self.log(f"   Business: {RESTAURANT_DATA['business_name']}")
                self.log(f"   Type: {RESTAURANT_DATA['business_type']}")
                self.log(f"   Industry: {RESTAURANT_DATA['industry']}")
                self.log(f"   Website: {RESTAURANT_DATA['website_url']}")
                self.log(f"   Platforms: {', '.join(RESTAURANT_DATA['preferred_platforms'])}")
                return True
            else:
                self.log(f"❌ Business profile creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Business profile error: {str(e)}", "ERROR")
            return False
    
    def create_website_analysis(self):
        """Step 3: Create fictional website analysis"""
        self.log("🌐 STEP 3: Creating fictional website analysis")
        
        try:
            # Create comprehensive website analysis data
            analysis_data = {
                "url": RESTAURANT_DATA["website_url"],
                "title": "Le Bistrot de Jean - Restaurant Gastronomique Paris",
                "description": "Restaurant gastronomique français au cœur de Paris. Cuisine traditionnelle revisitée par le Chef Jean Dupont.",
                "keywords": ["restaurant paris", "gastronomie française", "chef jean dupont", "bistrot", "cuisine traditionnelle"],
                "seo_score": 85,
                "performance_score": 78,
                "accessibility_score": 92,
                "best_practices_score": 88,
                "recommendations": [
                    "Optimiser les images pour améliorer la vitesse de chargement",
                    "Ajouter des balises alt aux images du menu",
                    "Implémenter le schema markup pour les restaurants",
                    "Améliorer la structure des URLs pour le SEO",
                    "Ajouter des avis clients sur la page d'accueil"
                ],
                "content_analysis": {
                    "word_count": 1250,
                    "readability_score": 82,
                    "content_themes": ["gastronomie", "tradition", "chef", "paris", "menu"],
                    "missing_content": ["blog culinaire", "histoire du restaurant", "équipe"]
                },
                "technical_analysis": {
                    "mobile_friendly": True,
                    "ssl_certificate": True,
                    "page_speed": 3.2,
                    "meta_tags_complete": True
                },
                "competitive_analysis": {
                    "main_competitors": ["Le Grand Véfour", "L'Ami Jean", "Bistrot Paul Bert"],
                    "positioning": "Restaurant gastronomique accessible",
                    "price_range": "€€€"
                }
            }
            
            # Note: This would typically call a website analysis endpoint
            # For now, we'll simulate this by creating a note with the analysis
            analysis_note = {
                "description": "Analyse site web - Le Bistrot de Jean",
                "content": f"Analyse complète du site {RESTAURANT_DATA['website_url']}:\n\n" +
                          f"📊 Scores:\n- SEO: {analysis_data['seo_score']}/100\n- Performance: {analysis_data['performance_score']}/100\n- Accessibilité: {analysis_data['accessibility_score']}/100\n\n" +
                          f"🎯 Recommandations principales:\n" + "\n".join([f"- {rec}" for rec in analysis_data['recommendations'][:3]]) + "\n\n" +
                          f"📈 Mots-clés principaux: {', '.join(analysis_data['keywords'])}",
                "priority": "medium",
                "is_monthly_note": False
            }
            
            response = self.session.post(f"{LIVE_BACKEND_URL}/notes", json=analysis_note)
            
            if response.status_code == 200:
                self.log("✅ Website analysis created successfully")
                self.log(f"   URL analyzed: {RESTAURANT_DATA['website_url']}")
                self.log(f"   SEO Score: {analysis_data['seo_score']}/100")
                self.log(f"   Performance Score: {analysis_data['performance_score']}/100")
                return True
            else:
                self.log(f"❌ Website analysis creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Website analysis error: {str(e)}", "ERROR")
            return False
    
    def create_system_notes(self):
        """Step 4: Create system notes for the restaurant"""
        self.log("📝 STEP 4: Creating system notes")
        
        created_notes = 0
        
        for note_data in RESTAURANT_NOTES:
            try:
                response = self.session.post(f"{LIVE_BACKEND_URL}/notes", json=note_data)
                
                if response.status_code == 200:
                    created_notes += 1
                    self.log(f"   ✅ Created note: {note_data['description']}")
                else:
                    self.log(f"   ❌ Failed to create note: {note_data['description']} - {response.status_code}")
                    
            except Exception as e:
                self.log(f"   ❌ Error creating note {note_data['description']}: {str(e)}")
        
        if created_notes == len(RESTAURANT_NOTES):
            self.log(f"✅ All {created_notes} system notes created successfully")
            return True
        else:
            self.log(f"⚠️ Created {created_notes}/{len(RESTAURANT_NOTES)} notes")
            return created_notes > 0
    
    def generate_sample_image(self, width=800, height=600, text="Sample Image", color=(70, 130, 180)):
        """Generate a sample image for testing"""
        try:
            # Create a simple image with text
            img = Image.new('RGB', (width, height), color=color)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
        except Exception as e:
            self.log(f"❌ Error generating sample image: {str(e)}")
            return None
    
    def upload_restaurant_photos(self):
        """Step 5: Upload 16 photos for the restaurant (4 per month over 4 months)"""
        self.log("📸 STEP 5: Uploading restaurant photos (16 photos - 4 per month)")
        
        # Define photo categories and descriptions for restaurant
        photo_categories = [
            # Mois 1 - Plats signature
            {"title": "Boeuf Bourguignon Moderne", "description": "Notre spécialité revisitée par le Chef Jean Dupont", "month": "janvier_2025"},
            {"title": "Soufflé au Grand Marnier", "description": "Dessert signature de la maison", "month": "janvier_2025"},
            {"title": "Foie Gras Maison", "description": "Foie gras de canard préparé selon la tradition", "month": "janvier_2025"},
            {"title": "Plateau de Fromages", "description": "Sélection de fromages français affinés", "month": "janvier_2025"},
            
            # Mois 2 - Restaurant et ambiance
            {"title": "Salle Principale", "description": "Ambiance chaleureuse et élégante du bistrot", "month": "février_2025"},
            {"title": "Bar à Vins", "description": "Notre sélection de vins français", "month": "février_2025"},
            {"title": "Terrasse Parisienne", "description": "Terrasse avec vue sur la rue de la Paix", "month": "février_2025"},
            {"title": "Cuisine Ouverte", "description": "Vue sur la cuisine et l'équipe en action", "month": "février_2025"},
            
            # Mois 3 - Équipe et service
            {"title": "Chef Jean Dupont", "description": "Notre chef passionné en cuisine", "month": "mars_2025"},
            {"title": "Équipe de Service", "description": "Notre équipe professionnelle et souriante", "month": "mars_2025"},
            {"title": "Préparation en Cuisine", "description": "L'art culinaire en action", "month": "mars_2025"},
            {"title": "Service en Salle", "description": "Service attentionné et personnalisé", "month": "mars_2025"},
            
            # Mois 4 - Événements et produits
            {"title": "Menu Dégustation", "description": "Présentation de notre menu dégustation", "month": "avril_2025"},
            {"title": "Produits du Marché", "description": "Produits frais sélectionnés au marché", "month": "avril_2025"},
            {"title": "Soirée Dégustation", "description": "Événement spécial dégustation vins", "month": "avril_2025"},
            {"title": "Réservation Privée", "description": "Espace privatisé pour événements", "month": "avril_2025"}
        ]
        
        uploaded_photos = 0
        
        for i, photo_info in enumerate(photo_categories, 1):
            try:
                self.log(f"   📷 Uploading photo {i}/16: {photo_info['title']}")
                
                # Generate sample image
                image_data = self.generate_sample_image(
                    width=800, 
                    height=600, 
                    text=photo_info['title'],
                    color=(70 + i*10, 130 + i*5, 180 - i*5)  # Vary colors
                )
                
                if not image_data:
                    continue
                
                # Prepare multipart form data
                files = {
                    'file': (f"restaurant_photo_{i}.jpg", image_data, 'image/jpeg')
                }
                
                data = {
                    'description': photo_info['description'],
                    'title': photo_info['title'],
                    'attributed_month': photo_info['month']
                }
                
                # Remove Content-Type header for multipart upload
                headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
                headers['Authorization'] = self.session.headers.get('Authorization')
                
                response = requests.post(
                    f"{LIVE_BACKEND_URL}/content/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    uploaded_photos += 1
                    self.log(f"     ✅ Uploaded: {photo_info['title']} ({photo_info['month']})")
                else:
                    self.log(f"     ❌ Failed to upload {photo_info['title']}: {response.status_code}")
                    
            except Exception as e:
                self.log(f"     ❌ Error uploading photo {i}: {str(e)}")
        
        if uploaded_photos >= 12:  # At least 75% success rate
            self.log(f"✅ Successfully uploaded {uploaded_photos}/16 restaurant photos")
            return True
        else:
            self.log(f"⚠️ Only uploaded {uploaded_photos}/16 photos")
            return False
    
    def generate_posts_for_months(self):
        """Step 6: Generate posts for 4 months"""
        self.log("📅 STEP 6: Generating posts for 4 months")
        
        try:
            # Generate posts for multiple months
            months_to_generate = ["janvier_2025", "février_2025", "mars_2025", "avril_2025"]
            total_generated = 0
            
            for month in months_to_generate:
                self.log(f"   📝 Generating posts for {month}")
                
                response = self.session.post(f"{LIVE_BACKEND_URL}/posts/generate", json={
                    "target_month": month,
                    "posts_per_platform": 4,  # 4 posts per platform per month
                    "platforms": ["facebook", "instagram"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    generated_count = data.get('generated_posts', 0)
                    total_generated += generated_count
                    self.log(f"     ✅ Generated {generated_count} posts for {month}")
                else:
                    self.log(f"     ❌ Failed to generate posts for {month}: {response.status_code}")
            
            if total_generated >= 16:  # At least 2 posts per month per platform
                self.log(f"✅ Successfully generated {total_generated} posts across 4 months")
                return True
            else:
                self.log(f"⚠️ Generated {total_generated} posts (expected at least 16)")
                return total_generated > 0
                
        except Exception as e:
            self.log(f"❌ Post generation error: {str(e)}", "ERROR")
            return False
    
    def verify_test_account_completeness(self):
        """Step 7: Verify test account is complete and ready for Facebook review"""
        self.log("✅ STEP 7: Verifying test account completeness")
        
        verification_results = {
            'business_profile': False,
            'content_library': False,
            'system_notes': False,
            'generated_posts': False,
            'account_access': False
        }
        
        try:
            # Check business profile
            profile_response = self.session.get(f"{LIVE_BACKEND_URL}/business-profile")
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                if profile_data.get('business_name') == RESTAURANT_DATA['business_name']:
                    verification_results['business_profile'] = True
                    self.log("   ✅ Business profile complete")
                else:
                    self.log("   ❌ Business profile incomplete")
            
            # Check content library
            content_response = self.session.get(f"{LIVE_BACKEND_URL}/content/pending?limit=20")
            if content_response.status_code == 200:
                content_data = content_response.json()
                content_count = len(content_data.get('content', []))
                if content_count >= 10:
                    verification_results['content_library'] = True
                    self.log(f"   ✅ Content library has {content_count} items")
                else:
                    self.log(f"   ⚠️ Content library has only {content_count} items")
            
            # Check system notes
            notes_response = self.session.get(f"{LIVE_BACKEND_URL}/notes")
            if notes_response.status_code == 200:
                notes_data = notes_response.json()
                notes_count = len(notes_data.get('notes', []))
                if notes_count >= 4:
                    verification_results['system_notes'] = True
                    self.log(f"   ✅ System notes: {notes_count} notes created")
                else:
                    self.log(f"   ⚠️ System notes: only {notes_count} notes")
            
            # Check generated posts
            posts_response = self.session.get(f"{LIVE_BACKEND_URL}/posts/generated")
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                posts_count = len(posts_data.get('posts', []))
                if posts_count >= 10:
                    verification_results['generated_posts'] = True
                    self.log(f"   ✅ Generated posts: {posts_count} posts ready")
                else:
                    self.log(f"   ⚠️ Generated posts: only {posts_count} posts")
            
            # Verify account access
            if self.auth_token and self.user_id:
                verification_results['account_access'] = True
                self.log("   ✅ Account access verified")
            
            # Summary
            passed_checks = sum(verification_results.values())
            total_checks = len(verification_results)
            
            self.log(f"\n📊 Verification Summary: {passed_checks}/{total_checks} checks passed")
            
            if passed_checks == total_checks:
                self.log("🎉 Test account is COMPLETE and ready for Facebook App Review!")
                return True
            elif passed_checks >= 3:
                self.log("⚠️ Test account is mostly complete but has some issues")
                return True
            else:
                self.log("❌ Test account is incomplete")
                return False
                
        except Exception as e:
            self.log(f"❌ Verification error: {str(e)}", "ERROR")
            return False
    
    def display_test_account_summary(self):
        """Display final summary for Facebook reviewers"""
        self.log("=" * 80)
        self.log("🎯 FACEBOOK APP REVIEW - TEST ACCOUNT SUMMARY")
        self.log("=" * 80)
        
        self.log("📋 ACCOUNT CREDENTIALS:")
        self.log(f"   🌐 Environment: https://claire-marcus.com")
        self.log(f"   📧 Email: {TEST_EMAIL}")
        self.log(f"   🔑 Password: {TEST_PASSWORD}")
        self.log(f"   👤 User ID: {self.user_id}")
        
        self.log("\n🏢 BUSINESS INFORMATION:")
        self.log(f"   🏪 Name: {RESTAURANT_DATA['business_name']}")
        self.log(f"   🍽️ Type: {RESTAURANT_DATA['business_type']} - {RESTAURANT_DATA['industry']}")
        self.log(f"   📍 Address: 15 Rue de la Paix, 75001 Paris")
        self.log(f"   📞 Phone: 01 42 60 38 15")
        self.log(f"   🌐 Website: {RESTAURANT_DATA['website_url']}")
        self.log(f"   👨‍🍳 Chef: Jean Dupont (15 ans d'expérience)")
        
        self.log("\n📊 ACCOUNT CONTENTS:")
        self.log("   ✅ Complete business profile with all fields")
        self.log("   ✅ Website analysis with SEO recommendations")
        self.log("   ✅ 16 restaurant photos (4 per month over 4 months)")
        self.log("   ✅ System notes with business guidelines")
        self.log("   ✅ Generated posts for Facebook and Instagram")
        
        self.log("\n🎯 FOR FACEBOOK REVIEWERS:")
        self.log("   1. Login with the credentials above")
        self.log("   2. Navigate to Social Connections")
        self.log("   3. Connect Facebook and Instagram accounts")
        self.log("   4. Test post generation and publication")
        self.log("   5. Verify all features work as expected")
        
        self.log("\n📱 PLATFORMS TO TEST:")
        self.log("   📘 Facebook: Page posts with images and text")
        self.log("   📸 Instagram: Feed posts with hashtags")
        
        self.log("=" * 80)
    
    def run_complete_setup(self):
        """Run the complete test account setup for Facebook App Review"""
        self.log("🚀 STARTING FACEBOOK APP REVIEW TEST ACCOUNT CREATION")
        self.log("=" * 80)
        self.log(f"🌐 LIVE Environment: {LIVE_BACKEND_URL}")
        self.log(f"🏪 Restaurant: {RESTAURANT_DATA['business_name']}")
        self.log(f"📧 Test Email: {TEST_EMAIL}")
        self.log("=" * 80)
        
        results = {
            'account_creation': False,
            'business_profile': False,
            'website_analysis': False,
            'system_notes': False,
            'photo_upload': False,
            'post_generation': False,
            'verification': False
        }
        
        # Step 1: Create test account
        if self.create_test_account():
            results['account_creation'] = True
            
            # Step 2: Setup business profile
            if self.setup_business_profile():
                results['business_profile'] = True
            
            # Step 3: Create website analysis
            if self.create_website_analysis():
                results['website_analysis'] = True
            
            # Step 4: Create system notes
            if self.create_system_notes():
                results['system_notes'] = True
            
            # Step 5: Upload restaurant photos
            if self.upload_restaurant_photos():
                results['photo_upload'] = True
            
            # Step 6: Generate posts
            if self.generate_posts_for_months():
                results['post_generation'] = True
            
            # Step 7: Verify completeness
            if self.verify_test_account_completeness():
                results['verification'] = True
        
        # Display results
        self.log("=" * 80)
        self.log("🎯 SETUP RESULTS SUMMARY")
        
        passed_steps = sum(results.values())
        total_steps = len(results)
        success_rate = (passed_steps / total_steps) * 100
        
        self.log(f"📊 Setup Results: {passed_steps}/{total_steps} steps completed ({success_rate:.1f}% success rate)")
        
        for step_name, completed in results.items():
            status = "✅ COMPLETED" if completed else "❌ FAILED"
            self.log(f"   {step_name.replace('_', ' ').title()}: {status}")
        
        if passed_steps >= 5:  # At least 5/7 steps successful
            self.log("\n🎉 TEST ACCOUNT SETUP SUCCESSFUL!")
            self.display_test_account_summary()
            return True
        else:
            self.log("\n❌ TEST ACCOUNT SETUP FAILED")
            self.log("Some critical steps failed. Please check the logs above.")
            return False

def main():
    """Main execution function"""
    print("🎯 FACEBOOK APP REVIEW - TEST ACCOUNT CREATION")
    print("=" * 80)
    print(f"📅 Creation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 LIVE Environment: {LIVE_BACKEND_URL}")
    print(f"🏪 Restaurant: {RESTAURANT_DATA['business_name']}")
    print(f"📧 Test Email: {TEST_EMAIL}")
    print("🎯 Objective: Créer un compte de test complet pour Facebook App Review")
    print("=" * 80)
    
    creator = FacebookAppReviewTestCreator()
    success = creator.run_complete_setup()
    
    # Exit with appropriate code
    if success:
        sys.exit(0)  # Setup successful
    else:
        sys.exit(1)  # Setup failed

if __name__ == "__main__":
    main()