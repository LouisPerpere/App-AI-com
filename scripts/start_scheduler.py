#!/usr/bin/env python3
"""
SocialGénie Scheduler Starter
Starts the background scheduler for automatic post generation and notifications
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.scheduler import main_scheduler

if __name__ == "__main__":
    print("🚀 Starting SocialGénie Scheduler...")
    print("📅 Features:")
    print("   • Automatic post generation")
    print("   • Content upload reminders")
    print("   • Email notifications")
    print("   • Periodic scheduling")
    print()
    
    try:
        asyncio.run(main_scheduler())
    except KeyboardInterrupt:
        print("\n⏹️  Scheduler stopped by user")
    except Exception as e:
        print(f"\n❌ Scheduler error: {e}")
        sys.exit(1)