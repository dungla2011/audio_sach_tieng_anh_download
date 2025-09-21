#!/usr/bin/env python3
"""
Test Bulk Downloader - Process first few items for testing
==========================================================
"""

import json
import subprocess
import sys
import os

def test_download():
    """Test download with first 5 items"""
    json_file = "ALL_AUDIO_ITEMS_5879_items.json"
    downloader_script = "01-ok-auto_downloader.py"
    
    # Check files exist
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    if not os.path.exists(downloader_script):
        print(f"❌ Downloader script not found: {downloader_script}")
        return
    
    # Load items
    with open(json_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    print(f"📂 Loaded {len(items)} total items")
    print("🧪 Testing with first 5 items...")
    
    # Test first 5 items
    for i, item in enumerate(items[:5], 1):
        url = item.get('url', '')
        title = item.get('title', 'Unknown Title')
        
        print(f"\n[{i}/5] {title}")
        print(f"URL: {url}")
        
        if not url:
            print("⚠️  No URL found, skipping...")
            continue
        
        try:
            # Run downloader
            cmd = [sys.executable, downloader_script, url]
            print(f"🚀 Running: python {downloader_script} \"{url}\"")
            
            result = subprocess.run(cmd, timeout=180)  # 3 minute timeout
            
            if result.returncode == 0:
                print("✅ SUCCESS")
            else:
                print(f"❌ FAILED (code {result.returncode})")
                
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n🏁 Test completed!")
    print(f"💡 If tests look good, run: python bulk_download_all.py")

if __name__ == "__main__":
    test_download()