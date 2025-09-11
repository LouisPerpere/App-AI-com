#!/usr/bin/env python3
"""
URGENT DATABASE INVESTIGATION: Compare user data between preview and production databases
for lperpere@yahoo.fr to determine which database contains the actual user data.

Testing both environments:
- Preview: https://claire-marcus-pwa-1.preview.emergentagent.com/api
- Production: https://claire-marcus-pwa-1.emergent.host/api

Focus: Determine which database has the user's actual data and why claire-marcus.com shows different user ID.
"""

import requests
import json
import sys
from datetime import datetime

class DatabaseInvestigationTester:
    def __init__(self):
        self.preview_base_url = "https://claire-marcus-pwa-1.preview.emergentagent.com/api"
        self.production_base_url = "https://claire-marcus-pwa-1.emergent.host/api"
        self.email = "lperpere@yahoo.fr"
        self.password = "L@Reunion974!"
        
        # Store authentication tokens for both environments
        self.preview_token = None
        self.production_token = None
        self.preview_user_id = None
        self.production_user_id = None
        
        # Store investigation results
        self.investigation_results = {
            "preview": {},
            "production": {},
            "comparison": {},
            "conclusion": ""
        }
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate_environment(self, base_url, env_name):
        """Authenticate with specific environment and return token + user_id"""
        try:
            self.log(f"🔐 Authenticating with {env_name} environment: {base_url}")
            
            auth_data = {
                "email": self.email,
                "password": self.password
            }
            
            response = requests.post(
                f"{base_url}/auth/login-robust",
                json=auth_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user_id = data.get("user_id")
                email = data.get("email")
                
                self.log(f"✅ {env_name} Authentication successful")
                self.log(f"   User ID: {user_id}")
                self.log(f"   Email: {email}")
                
                return token, user_id
            else:
                self.log(f"❌ {env_name} Authentication failed: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return None, None
                
        except Exception as e:
            self.log(f"❌ {env_name} Authentication error: {str(e)}", "ERROR")
            return None, None
    
    def get_user_data(self, base_url, token, env_name):
        """Get comprehensive user data from environment"""
        if not token:
            return {}
            
        headers = {"Authorization": f"Bearer {token}"}
        user_data = {}
        
        try:
            # 1. Get user profile
            self.log(f"📋 Getting user profile from {env_name}")
            response = requests.get(f"{base_url}/auth/me", headers=headers, timeout=30)
            if response.status_code == 200:
                user_data["profile"] = response.json()
                self.log(f"   ✅ User profile retrieved")
            else:
                self.log(f"   ❌ User profile failed: {response.status_code}")
                user_data["profile"] = None
            
            # 2. Get business profile
            self.log(f"🏢 Getting business profile from {env_name}")
            response = requests.get(f"{base_url}/business-profile", headers=headers, timeout=30)
            if response.status_code == 200:
                business_data = response.json()
                user_data["business_profile"] = business_data
                
                # Count populated fields
                populated_fields = sum(1 for v in business_data.values() if v not in [None, "", []])
                self.log(f"   ✅ Business profile retrieved ({populated_fields} populated fields)")
                
                # Check for "My Own Watch" data
                business_name = business_data.get("business_name", "")
                if "My Own Watch" in str(business_name):
                    self.log(f"   🎯 FOUND 'My Own Watch' business data!")
                    user_data["has_my_own_watch"] = True
                else:
                    user_data["has_my_own_watch"] = False
                    
            else:
                self.log(f"   ❌ Business profile failed: {response.status_code}")
                user_data["business_profile"] = None
                user_data["has_my_own_watch"] = False
            
            # 3. Get content library
            self.log(f"📚 Getting content library from {env_name}")
            response = requests.get(f"{base_url}/content/pending?limit=50", headers=headers, timeout=30)
            if response.status_code == 200:
                content_data = response.json()
                user_data["content"] = content_data
                content_count = content_data.get("total", 0)
                self.log(f"   ✅ Content library retrieved ({content_count} items)")
                
                # Check for 19 content items as mentioned by user
                if content_count == 19:
                    self.log(f"   🎯 FOUND exactly 19 content items as reported by user!")
                    user_data["has_19_content_items"] = True
                else:
                    user_data["has_19_content_items"] = False
                    
            else:
                self.log(f"   ❌ Content library failed: {response.status_code}")
                user_data["content"] = None
                user_data["has_19_content_items"] = False
            
            # 4. Get notes
            self.log(f"📝 Getting notes from {env_name}")
            response = requests.get(f"{base_url}/notes", headers=headers, timeout=30)
            if response.status_code == 200:
                notes_data = response.json()
                user_data["notes"] = notes_data
                notes_count = len(notes_data.get("notes", []))
                self.log(f"   ✅ Notes retrieved ({notes_count} notes)")
                
                # Check for 2 notes as mentioned by user
                if notes_count == 2:
                    self.log(f"   🎯 FOUND exactly 2 notes as reported by user!")
                    user_data["has_2_notes"] = True
                else:
                    user_data["has_2_notes"] = False
                    
            else:
                self.log(f"   ❌ Notes failed: {response.status_code}")
                user_data["notes"] = None
                user_data["has_2_notes"] = False
            
            # 5. Get generated posts
            self.log(f"📄 Getting generated posts from {env_name}")
            response = requests.get(f"{base_url}/posts/generated", headers=headers, timeout=30)
            if response.status_code == 200:
                posts_data = response.json()
                user_data["posts"] = posts_data
                posts_count = posts_data.get("count", 0)
                self.log(f"   ✅ Generated posts retrieved ({posts_count} posts)")
                
                # Check for 4 posts as mentioned by user
                if posts_count == 4:
                    self.log(f"   🎯 FOUND exactly 4 posts as reported by user!")
                    user_data["has_4_posts"] = True
                else:
                    user_data["has_4_posts"] = False
                    
            else:
                self.log(f"   ❌ Generated posts failed: {response.status_code}")
                user_data["posts"] = None
                user_data["has_4_posts"] = False
                
        except Exception as e:
            self.log(f"❌ Error getting user data from {env_name}: {str(e)}", "ERROR")
            
        return user_data
    
    def analyze_data_completeness(self, user_data, env_name):
        """Analyze which environment has the most complete user data"""
        score = 0
        details = []
        
        # Check for "My Own Watch" business data (high priority)
        if user_data.get("has_my_own_watch", False):
            score += 10
            details.append("✅ Has 'My Own Watch' business data")
        else:
            details.append("❌ Missing 'My Own Watch' business data")
        
        # Check for 19 content items (high priority)
        if user_data.get("has_19_content_items", False):
            score += 8
            details.append("✅ Has exactly 19 content items")
        else:
            content_count = 0
            if user_data.get("content"):
                content_count = user_data["content"].get("total", 0)
            details.append(f"❌ Has {content_count} content items (expected 19)")
        
        # Check for 2 notes (medium priority)
        if user_data.get("has_2_notes", False):
            score += 5
            details.append("✅ Has exactly 2 notes")
        else:
            notes_count = 0
            if user_data.get("notes"):
                notes_count = len(user_data["notes"].get("notes", []))
            details.append(f"❌ Has {notes_count} notes (expected 2)")
        
        # Check for 4 posts (medium priority)
        if user_data.get("has_4_posts", False):
            score += 5
            details.append("✅ Has exactly 4 posts")
        else:
            posts_count = 0
            if user_data.get("posts"):
                posts_count = user_data["posts"].get("count", 0)
            details.append(f"❌ Has {posts_count} posts (expected 4)")
        
        # Check business profile completeness
        if user_data.get("business_profile"):
            populated_fields = sum(1 for v in user_data["business_profile"].values() if v not in [None, "", []])
            if populated_fields >= 10:
                score += 3
                details.append(f"✅ Business profile well populated ({populated_fields} fields)")
            else:
                details.append(f"⚠️ Business profile partially populated ({populated_fields} fields)")
        
        self.log(f"📊 {env_name} Data Completeness Score: {score}/31")
        for detail in details:
            self.log(f"   {detail}")
            
        return score, details
    
    def run_investigation(self):
        """Run complete database investigation"""
        self.log("🚀 STARTING URGENT DATABASE INVESTIGATION")
        self.log("=" * 80)
        
        # Step 1: Authenticate with both environments
        self.log("STEP 1: Authentication Testing")
        self.log("-" * 40)
        
        self.preview_token, self.preview_user_id = self.authenticate_environment(
            self.preview_base_url, "PREVIEW"
        )
        
        self.production_token, self.production_user_id = self.authenticate_environment(
            self.production_base_url, "PRODUCTION"
        )
        
        # Step 2: Compare User IDs
        self.log("\nSTEP 2: User ID Comparison")
        self.log("-" * 40)
        
        if self.preview_user_id and self.production_user_id:
            if self.preview_user_id == self.production_user_id:
                self.log("✅ User IDs MATCH between environments")
                self.log(f"   Consistent User ID: {self.preview_user_id}")
            else:
                self.log("❌ User IDs DIFFER between environments")
                self.log(f"   Preview User ID:    {self.preview_user_id}")
                self.log(f"   Production User ID: {self.production_user_id}")
                self.log("   🚨 THIS INDICATES SEPARATE DATABASES!")
        
        # Step 3: Get comprehensive data from both environments
        self.log("\nSTEP 3: Data Retrieval and Analysis")
        self.log("-" * 40)
        
        if self.preview_token:
            self.log("\n🔍 ANALYZING PREVIEW ENVIRONMENT DATA:")
            self.investigation_results["preview"] = self.get_user_data(
                self.preview_base_url, self.preview_token, "PREVIEW"
            )
        
        if self.production_token:
            self.log("\n🔍 ANALYZING PRODUCTION ENVIRONMENT DATA:")
            self.investigation_results["production"] = self.get_user_data(
                self.production_base_url, self.production_token, "PRODUCTION"
            )
        
        # Step 4: Compare data completeness
        self.log("\nSTEP 4: Data Completeness Analysis")
        self.log("-" * 40)
        
        preview_score = 0
        production_score = 0
        
        if self.investigation_results["preview"]:
            preview_score, preview_details = self.analyze_data_completeness(
                self.investigation_results["preview"], "PREVIEW"
            )
        
        if self.investigation_results["production"]:
            production_score, production_details = self.analyze_data_completeness(
                self.investigation_results["production"], "PRODUCTION"
            )
        
        # Step 5: Final conclusion
        self.log("\nSTEP 5: INVESTIGATION CONCLUSION")
        self.log("=" * 80)
        
        if preview_score > production_score:
            winner = "PREVIEW"
            winner_score = preview_score
            winner_url = self.preview_base_url
            winner_user_id = self.preview_user_id
        elif production_score > preview_score:
            winner = "PRODUCTION"
            winner_score = production_score
            winner_url = self.production_base_url
            winner_user_id = self.production_user_id
        else:
            winner = "TIE"
            winner_score = preview_score
        
        if winner != "TIE":
            self.log(f"🎯 CONCLUSION: {winner} database contains the user's actual data")
            self.log(f"   Environment: {winner}")
            self.log(f"   URL: {winner_url}")
            self.log(f"   User ID: {winner_user_id}")
            self.log(f"   Completeness Score: {winner_score}/31")
            
            if winner == "PREVIEW":
                self.log("🚨 CRITICAL FINDING: Preview database has the actual user data!")
                self.log("   This means claire-marcus.com production is connected to WRONG database")
                self.log("   RECOMMENDATION: Update production to use preview database connection")
            else:
                self.log("✅ Production database has the correct user data")
                self.log("   Preview database appears to be outdated or test data")
        else:
            self.log("⚠️ INCONCLUSIVE: Both databases have similar data completeness")
            self.log("   Manual investigation required to determine correct database")
        
        # Step 6: MongoDB connection details investigation
        self.log("\nSTEP 6: MongoDB Connection Investigation")
        self.log("-" * 40)
        
        self.log("🔍 Checking diagnostic endpoints for database connection details...")
        
        # Check preview diagnostic
        try:
            response = requests.get(f"{self.preview_base_url}/diag", timeout=30)
            if response.status_code == 200:
                diag_data = response.json()
                self.log("📊 PREVIEW Database Connection:")
                self.log(f"   Connected: {diag_data.get('database_connected', 'Unknown')}")
                self.log(f"   Database: {diag_data.get('database_name', 'Unknown')}")
                self.log(f"   Mongo URL: {diag_data.get('mongo_url_prefix', 'Unknown')}")
        except Exception as e:
            self.log(f"❌ Preview diagnostic failed: {str(e)}")
        
        # Check production diagnostic
        try:
            response = requests.get(f"{self.production_base_url}/diag", timeout=30)
            if response.status_code == 200:
                diag_data = response.json()
                self.log("📊 PRODUCTION Database Connection:")
                self.log(f"   Connected: {diag_data.get('database_connected', 'Unknown')}")
                self.log(f"   Database: {diag_data.get('database_name', 'Unknown')}")
                self.log(f"   Mongo URL: {diag_data.get('mongo_url_prefix', 'Unknown')}")
        except Exception as e:
            self.log(f"❌ Production diagnostic failed: {str(e)}")
        
        self.log("\n" + "=" * 80)
        self.log("🏁 DATABASE INVESTIGATION COMPLETED")
        self.log("=" * 80)
        
        return {
            "preview_user_id": self.preview_user_id,
            "production_user_id": self.production_user_id,
            "preview_score": preview_score,
            "production_score": production_score,
            "winner": winner,
            "investigation_results": self.investigation_results
        }

def main():
    """Main function to run the database investigation"""
    print("🚨 URGENT DATABASE INVESTIGATION FOR lperpere@yahoo.fr")
    print("Comparing Preview vs Production databases to find actual user data")
    print("=" * 80)
    
    tester = DatabaseInvestigationTester()
    results = tester.run_investigation()
    
    # Return appropriate exit code
    if results["winner"] in ["PREVIEW", "PRODUCTION"]:
        print(f"\n✅ Investigation completed successfully - {results['winner']} has the actual data")
        return 0
    else:
        print(f"\n⚠️ Investigation inconclusive - manual review required")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)