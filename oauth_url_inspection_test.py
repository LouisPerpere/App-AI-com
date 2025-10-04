#!/usr/bin/env python3
"""
OAuth URL Inspection Test - Detailed URL Analysis
Inspects the actual generated OAuth URLs to verify all parameters

Credentials: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import urllib.parse
from datetime import datetime

# Configuration
BACKEND_URL = "https://claire-marcus-app-1.preview.emergentagent.com/api"
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class URLInspector:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def authenticate(self):
        """Authenticate with test credentials"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login-robust", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def inspect_url(self, platform, auth_url):
        """Inspect and display URL details"""
        print(f"\n🔍 {platform.upper()} OAUTH URL INSPECTION")
        print("=" * 60)
        
        # Parse URL
        parsed = urllib.parse.urlparse(auth_url)
        params = urllib.parse.parse_qs(parsed.query)
        
        # Convert single-item lists to strings for display
        display_params = {}
        for key, value in params.items():
            if isinstance(value, list) and len(value) == 1:
                display_params[key] = value[0]
            else:
                display_params[key] = value
        
        print(f"Base URL: {parsed.scheme}://{parsed.netloc}{parsed.path}")
        print(f"Full URL: {auth_url}")
        print("\nParameters:")
        
        # Display parameters in organized way
        critical_params = ['client_id', 'config_id', 'redirect_uri', 'response_type', 'scope']
        
        for param in critical_params:
            if param in display_params:
                value = display_params[param]
                print(f"  {param}: {value}")
        
        # Display other parameters
        other_params = {k: v for k, v in display_params.items() if k not in critical_params}
        if other_params:
            print("\nOther Parameters:")
            for key, value in other_params.items():
                print(f"  {key}: {value}")
        
        return display_params
    
    def run_inspection(self):
        """Run URL inspection for both platforms"""
        print("🎯 OAUTH URL DETAILED INSPECTION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        if not self.authenticate():
            return False
        
        # Get Facebook URL
        try:
            fb_response = self.session.get(f"{BACKEND_URL}/social/facebook/auth-url")
            if fb_response.status_code == 200:
                fb_data = fb_response.json()
                fb_url = fb_data.get('auth_url', '')
                fb_params = self.inspect_url("Facebook", fb_url)
            else:
                print(f"❌ Failed to get Facebook URL: {fb_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Facebook URL error: {e}")
            return False
        
        # Get Instagram URL
        try:
            ig_response = self.session.get(f"{BACKEND_URL}/social/instagram/auth-url")
            if ig_response.status_code == 200:
                ig_data = ig_response.json()
                ig_url = ig_data.get('auth_url', '')
                ig_params = self.inspect_url("Instagram", ig_url)
            else:
                print(f"❌ Failed to get Instagram URL: {ig_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Instagram URL error: {e}")
            return False
        
        # Comparison
        print(f"\n🔄 CONFIGURATION COMPARISON")
        print("=" * 60)
        
        comparison_params = ['client_id', 'config_id', 'redirect_uri']
        
        for param in comparison_params:
            fb_value = fb_params.get(param, 'N/A')
            ig_value = ig_params.get(param, 'N/A')
            
            if param == 'client_id':
                match_status = "✅ MATCH" if fb_value == ig_value else "❌ MISMATCH"
                print(f"{param}:")
                print(f"  Facebook:  {fb_value}")
                print(f"  Instagram: {ig_value}")
                print(f"  Status: {match_status} (should match)")
            elif param == 'config_id':
                match_status = "✅ DIFFERENT" if fb_value != ig_value else "❌ SAME"
                print(f"{param}:")
                print(f"  Facebook:  {fb_value}")
                print(f"  Instagram: {ig_value}")
                print(f"  Status: {match_status} (should be different)")
            else:
                print(f"{param}:")
                print(f"  Facebook:  {fb_value}")
                print(f"  Instagram: {ig_value}")
            print()
        
        print("🎉 URL INSPECTION COMPLETED SUCCESSFULLY")
        return True

def main():
    inspector = URLInspector()
    inspector.run_inspection()

if __name__ == "__main__":
    main()