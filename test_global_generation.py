#!/usr/bin/env python3
"""
Test script for the new global post generation approach
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from posts_generator import PostsGenerator

async def test_global_generation():
    """Test the new global generation approach"""
    print("🧪 Testing new global post generation approach...")
    
    # Initialize generator
    generator = PostsGenerator()
    
    if not generator.openai_client:
        print("❌ OpenAI client not initialized - skipping test")
        return
    
    # Mock data for testing
    source_data = {
        "business_profile": {
            "business_name": "Test Business",
            "business_type": "service",
            "business_description": "A test business for development",
            "target_audience": "Young professionals"
        },
        "always_valid_notes": [
            {"title": "Brand Voice", "content": "Always use friendly and professional tone"},
            {"title": "Key Values", "content": "Quality, innovation, customer satisfaction"}
        ],
        "month_notes": [
            {"title": "October Focus", "content": "Highlight autumn services and seasonal offers"}
        ]
    }
    
    available_content = {
        "month_content": [],
        "older_content": []
    }
    
    strategy = {
        "product": 2,
        "value": 2,
        "backstage": 1
    }
    
    try:
        # Test the new global generation
        print("🚀 Testing global generation with 5 posts...")
        posts = await generator._generate_posts_with_strategy(
            source_data=source_data,
            available_content=available_content,
            strategy=strategy,
            num_posts=5,
            user_id="test_user"
        )
        
        print(f"✅ Generated {len(posts)} posts successfully!")
        
        # Display results
        for i, post in enumerate(posts, 1):
            print(f"\n📝 Post {i}:")
            print(f"   Type: {post.content_type}")
            print(f"   Title: {post.title}")
            print(f"   Text: {post.text[:100]}...")
            print(f"   Hashtags: {len(post.hashtags)} hashtags")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_global_generation())
    if success:
        print("\n🎉 Global generation test completed successfully!")
    else:
        print("\n💥 Global generation test failed!")