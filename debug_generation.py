#!/usr/bin/env python3
"""
Debug script to identify the exact error location
"""

import asyncio
import sys
import os
import traceback
sys.path.append('/app/backend')

from posts_generator import PostsGenerator

async def debug_generation():
    """Debug the generation system step by step"""
    print("🔍 Debugging post generation system...")
    
    # Initialize generator
    generator = PostsGenerator()
    
    if not generator.openai_client:
        print("❌ OpenAI client not initialized - skipping test")
        return
    
    try:
        user_id = "debug_user"
        target_month = "octobre_2025"
        num_posts = 5
        
        print("📊 Step 1: Gathering source data...")
        source_data = generator._gather_source_data(user_id, target_month)
        print(f"   Business profile: {source_data.get('business_profile') is not None}")
        print(f"   Website analysis: {source_data.get('website_analysis') is not None}")
        print(f"   Always valid notes: {len(source_data.get('always_valid_notes', []))}")
        print(f"   Month notes: {len(source_data.get('month_notes', []))}")
        
        print("🖼️ Step 2: Collecting available content...")
        available_content = generator._collect_available_content(user_id, target_month)
        print(f"   Month content: {len(available_content.get('month_content', []))}")
        print(f"   Older content: {len(available_content.get('older_content', []))}")
        
        print("🎯 Step 3: Determining content strategy...")
        content_strategy = generator._determine_content_strategy(source_data, num_posts)
        print(f"   Strategy: {content_strategy}")
        
        print("✨ Step 4: Testing new global generation...")
        generated_posts = await generator._generate_posts_with_strategy(
            source_data, available_content, content_strategy, num_posts, user_id
        )
        print(f"   Generated posts: {len(generated_posts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed at: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_generation())
    if success:
        print("\n🎉 Debug completed successfully!")
    else:
        print("\n💥 Debug failed!")