#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for comment system functionality
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project directory to path
project_dir = Path(__file__).parent / 'smart_cabin_project'
sys.path.insert(0, str(project_dir))
sys.path.insert(0, str(project_dir.parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_cabin.settings')

import django
django.setup()

from my_cabin.views import load_guest_comments, COMMENTS_FILE, BLACKLIST_FILE

def test_comments():
    """Test the comment system"""
    print("=" * 50)
    print("Comment System Test")
    print("=" * 50)
    
    # Check if files exist
    print(f"\n1. Checking files...")
    print(f"   COMMENTS_FILE: {COMMENTS_FILE}")
    print(f"   Exists: {COMMENTS_FILE.exists()}")
    print(f"   Size: {COMMENTS_FILE.stat().st_size if COMMENTS_FILE.exists() else 'N/A'} bytes")
    
    print(f"\n   BLACKLIST_FILE: {BLACKLIST_FILE}")
    print(f"   Exists: {BLACKLIST_FILE.exists()}")
    print(f"   Size: {BLACKLIST_FILE.stat().st_size if BLACKLIST_FILE.exists() else 'N/A'} bytes")
    
    # Test loading comments
    print(f"\n2. Testing load_guest_comments()...")
    try:
        comments = load_guest_comments()
        print(f"   ✅ Successfully loaded {len(comments)} comments")
        for i, comment in enumerate(comments):
            print(f"\n   Comment {i+1}:")
            print(f"      Name: {comment.get('name', 'N/A')}")
            print(f"      Timestamp: {comment.get('timestamp', 'N/A')}")
            print(f"      Message: {comment.get('message', 'N/A')[:50]}..." if len(comment.get('message', '')) > 50 else f"      Message: {comment.get('message', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error loading comments: {e}")
        import traceback
        traceback.print_exc()
    
    # Test writing a comment
    print(f"\n3. Testing comment writing...")
    try:
        # Ensure directory exists
        COMMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Write a test comment
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        with open(COMMENTS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"【{timestamp}】來自 測試訪客：這是一個測試留言\n" + "-"*30 + "\n")
        
        print(f"   ✅ Test comment written successfully")
        
        # Reload and verify
        comments = load_guest_comments()
        print(f"   ✅ Reloaded {len(comments)} comments after writing")
        
        if comments:
            last_comment = comments[-1]
            print(f"\n   Last comment:")
            print(f"      Name: {last_comment.get('name', 'N/A')}")
            print(f"      Timestamp: {last_comment.get('timestamp', 'N/A')}")
            print(f"      Message: {last_comment.get('message', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error writing comment: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)

if __name__ == '__main__':
    test_comments()
