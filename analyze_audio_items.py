#!/usr/bin/env python3
"""
Analyze Audio Items JSON
=======================
Analyze the content of ALL_AUDIO_ITEMS_5879_items.json
"""

import json
import re
from collections import Counter

def analyze_json():
    """Analyze the JSON file content"""
    json_file = "ALL_AUDIO_ITEMS_5879_items.json"
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        print("📊 AUDIO ITEMS ANALYSIS")
        print("="*50)
        print(f"📂 Total items: {len(items)}")
        
        # Analyze titles
        print(f"\n📝 Title Analysis:")
        title_keywords = Counter()
        audio_count = 0
        video_count = 0
        
        # Analyze URLs
        url_patterns = Counter()
        
        for item in items:
            title = item.get('title', '').lower()
            url = item.get('url', '')
            
            # Count audio vs video
            if '[audio]' in title:
                audio_count += 1
            if '[video]' in title:
                video_count += 1
            
            # Extract keywords from titles
            words = re.findall(r'\b[a-z]+\b', title.replace('[audio]', '').replace('[video]', ''))
            for word in words:
                if len(word) > 3:  # Skip short words
                    title_keywords[word] += 1
            
            # Analyze URL patterns
            if 'audio-' in url:
                url_patterns['audio-*'] += 1
            elif 'video-' in url:
                url_patterns['video-*'] += 1
            else:
                url_patterns['other'] += 1
        
        print(f"  🎵 Audio items: {audio_count}")
        print(f"  📹 Video items: {video_count}")
        print(f"  ❓ Other items: {len(items) - audio_count - video_count}")
        
        print(f"\n🔗 URL Patterns:")
        for pattern, count in url_patterns.most_common(10):
            print(f"  {pattern}: {count}")
        
        print(f"\n🏷️  Most Common Keywords:")
        for keyword, count in title_keywords.most_common(15):
            print(f"  {keyword}: {count}")
        
        # Show sample URLs
        print(f"\n📋 Sample URLs (first 10):")
        for i, item in enumerate(items[:10], 1):
            title = item.get('title', 'No title')[:50]
            url = item.get('url', 'No URL')
            print(f"  {i:2d}. {title}...")
            print(f"      {url}")
        
        print(f"\n🎯 READY FOR BULK DOWNLOAD!")
        print(f"Use: python test_bulk_download.py (test first 5)")
        print(f"Use: python bulk_download_all.py (download all {len(items)})")
        
    except Exception as e:
        print(f"❌ Error analyzing JSON: {e}")

if __name__ == "__main__":
    analyze_json()