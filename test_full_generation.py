#!/usr/bin/env python3
"""
Test script for the complete post generation system with the new global approach
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from posts_generator import PostsGenerator

async def test_full_generation():
    """Test the complete generation system"""
    print("🧪 Testing complete post generation system...")
    
    # Initialize generator
    generator = PostsGenerator()
    
    if not generator.openai_client:
        print("❌ OpenAI client not initialized - skipping test")
        return
    
    try:
        # Test the complete generation flow
        print("🚀 Testing complete generation flow...")
        result = await generator.generate_posts_for_month(
            user_id="test_user_full",
            target_month="octobre_2025",
            num_posts=8
        )
        
        if result["success"]:
            print(f"✅ Generated {result['posts_count']} posts successfully!")
            print(f"📊 Strategy used: {result['strategy']}")
            print(f"📋 Sources used: {result['sources_used']}")
            
            # Show first few posts
            for i, post in enumerate(result["posts"][:3], 1):
                print(f"\n📝 Post {i}:")
                print(f"   Type: {post.content_type}")
                print(f"   Title: {post.title}")
                print(f"   Text: {post.text[:80]}...")
                print(f"   Scheduled: {post.scheduled_date}")
            
            return True
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_generation())
    if success:
        print("\n🎉 Full generation test completed successfully!")
        print("🚀 NEW GLOBAL APPROACH: Single ChatGPT request instead of multiple individual requests!")
    else:
        print("\n💥 Full generation test failed!")