#!/usr/bin/env python3
"""
Test direct OpenAI API key functionality
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_openai_key():
    """Test if OpenAI API key is working"""
    print("🔑 Testing OpenAI API Key...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("   ❌ No OpenAI API key found in environment")
        return False
        
    print(f"   API Key: {api_key[:20]}...{api_key[-10:]}")
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un assistant utile."},
                {"role": "user", "content": "Dis simplement 'Bonjour' en JSON: {\"message\": \"Bonjour\"}"}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        response_text = response.choices[0].message.content
        print(f"   ✅ OpenAI API Response: {response_text}")
        
        if response_text and "Bonjour" in response_text:
            print("   ✅ OpenAI API key is working correctly!")
            return True
        else:
            print("   ❌ OpenAI API returned unexpected response")
            return False
            
    except Exception as e:
        print(f"   ❌ OpenAI API Error: {str(e)}")
        
        # Check specific error types
        if "401" in str(e) or "Unauthorized" in str(e):
            print("   💡 Error type: Invalid API key")
        elif "429" in str(e) or "quota" in str(e).lower():
            print("   💡 Error type: Rate limit or quota exceeded")
        elif "budget" in str(e).lower():
            print("   💡 Error type: Budget limit exceeded")
        
        return False

if __name__ == "__main__":
    success = test_openai_key()
    exit(0 if success else 1)