#!/usr/bin/env python3
"""
Page Source Analyzer
===================
Download and analyze the audio_stream page source to find real AJAX patterns
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os

def load_cookies_from_file():
    """Load cookies from the auto_extracted_cookies.json file"""
    try:
        with open('auto_extracted_cookies.json', 'r') as f:
            cookies_data = json.load(f)
        
        cookies = {}
        if 'cookies' in cookies_data:
            cookies = cookies_data['cookies']
        elif 'all_cookies' in cookies_data:
            cookies = cookies_data['all_cookies']
        
        return cookies
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return {}

def analyze_page_source():
    """Download and analyze the page source"""
    url = "https://sachtienganhhanoi.com/audio_stream/"
    
    # Setup session with cookies
    session = requests.Session()
    cookies = load_cookies_from_file()
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='.sachtienganhhanoi.com')
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print(f"📥 Downloading page: {url}")
    response = session.get(url)
    
    if response.status_code != 200:
        print(f"❌ Failed to download page: {response.status_code}")
        return
    
    print(f"✅ Page downloaded: {len(response.text)} characters")
    
    # Save raw HTML
    with open('audio_stream_page_source.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("💾 Raw HTML saved to: audio_stream_page_source.html")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for pagination elements
    print("\n🔍 Looking for pagination elements...")
    pagination_elements = []
    
    # Common pagination classes
    paging_selectors = [
        '.pagination', '.page-numbers', '.nav-links', '.paging',
        '.wp-pagenavi', '.page-nav', '.posts-navigation'
    ]
    
    for selector in paging_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"  ✅ Found {selector}: {len(elements)} elements")
            for elem in elements:
                pagination_elements.append({
                    'selector': selector,
                    'html': str(elem)[:200] + "..." if len(str(elem)) > 200 else str(elem),
                    'links': [a.get('href') for a in elem.find_all('a', href=True)]
                })
    
    # Look for audio/product links
    print("\n🎵 Looking for audio/product links...")
    audio_links = []
    
    all_links = soup.find_all('a', href=True)
    for link in all_links:
        href = link.get('href')
        text = link.get_text().strip()
        
        if 'audio' in href.lower() or 'audio' in text.lower():
            audio_links.append({
                'url': href,
                'text': text,
                'class': link.get('class', [])
            })
    
    print(f"  ✅ Found {len(audio_links)} audio-related links")
    
    # Look for JavaScript that might contain AJAX patterns
    print("\n📜 Analyzing JavaScript for AJAX patterns...")
    script_tags = soup.find_all('script')
    
    ajax_patterns_found = []
    for script in script_tags:
        if script.string:
            content = script.string
            
            # Look for specific patterns
            patterns = [
                (r'action["\']:\s*["\']([^"\']+)', 'AJAX Action'),
                (r'wp\.ajax\.post\s*\(\s*["\']([^"\']+)', 'WP AJAX Post'),
                (r'jQuery\.post[^(]*\([^,]*["\']([^"\']*admin-ajax[^"\']*)', 'jQuery Post to admin-ajax'),
                (r'load_more[^"\']*["\']:\s*["\']([^"\']+)', 'Load More Action'),
                (r'infinite[^"\']*["\']:\s*["\']([^"\']+)', 'Infinite Scroll Action'),
            ]
            
            for pattern, desc in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    ajax_patterns_found.extend([(match, desc) for match in matches])
    
    # Remove duplicates
    ajax_patterns_found = list(set(ajax_patterns_found))
    
    print(f"  ✅ Found {len(ajax_patterns_found)} potential AJAX patterns:")
    for pattern, desc in ajax_patterns_found:
        print(f"    - {desc}: {pattern}")
    
    # Look for data attributes that might indicate AJAX
    print("\n🔗 Looking for data attributes...")
    all_elements = soup.find_all(True)
    
    ajax_data_attrs = []
    for elem in all_elements:
        if hasattr(elem, 'attrs') and elem.attrs:
            data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            if data_attrs and any('ajax' in k.lower() or 'load' in k.lower() or 'action' in k.lower() for k in data_attrs.keys()):
                ajax_data_attrs.append({
                    'tag': elem.name,
                    'class': elem.get('class', []),
                    'id': elem.get('id', ''),
                    'data_attrs': data_attrs
                })
    
    print(f"  ✅ Found {len(ajax_data_attrs)} elements with AJAX-related data attributes")
    
    # Compile results
    analysis_results = {
        'page_info': {
            'url': url,
            'status_code': response.status_code,
            'content_length': len(response.text),
            'title': soup.find('title').get_text() if soup.find('title') else 'No title'
        },
        'pagination_elements': pagination_elements,
        'audio_links': audio_links[:20],  # Limit to first 20
        'ajax_patterns': [{'pattern': p, 'description': d} for p, d in ajax_patterns_found],
        'ajax_data_elements': ajax_data_attrs
    }
    
    # Save analysis
    with open('page_source_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: page_source_analysis.json")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    print(f"Audio links found: {len(audio_links)}")
    print(f"Pagination elements: {len(pagination_elements)}")
    print(f"AJAX patterns: {len(ajax_patterns_found)}")
    print(f"Data-attribute elements: {len(ajax_data_attrs)}")
    
    if audio_links:
        print(f"\n🎵 Sample audio links:")
        for i, link in enumerate(audio_links[:5], 1):
            print(f"  {i}. {link['text'][:50]}...")
            print(f"     {link['url']}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_page_source()