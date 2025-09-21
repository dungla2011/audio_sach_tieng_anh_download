#!/usr/bin/env python3
"""
Test PTP Load Posts AJAX Action
===============================
Test the specific ptp_load_posts action found in the page analysis
"""

import requests
import json
import time
from urllib.parse import urljoin

def load_cookies():
    """Load cookies from file"""
    try:
        with open('auto_extracted_cookies.json', 'r') as f:
            cookies_data = json.load(f)
        
        cookies = {}
        if 'cookies' in cookies_data:
            cookies = cookies_data['cookies']
        elif 'all_cookies' in cookies_data:
            cookies = cookies_data['all_cookies']
        
        return cookies, cookies_data.get('nonce', '')
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return {}, ''

def test_ptp_action():
    """Test the ptp_load_posts action with various parameters"""
    
    cookies, file_nonce = load_cookies()
    
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='.sachtienganhhanoi.com')
    
    base_url = "https://sachtienganhhanoi.com"
    ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
    referer = "https://sachtienganhhanoi.com/audio_stream/"
    
    # AJAX headers
    ajax_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': referer
    }
    
    print("🧪 Testing ptp_load_posts action with various parameters...")
    
    # Test variations
    test_cases = [
        # Basic test
        {'action': 'ptp_load_posts'},
        
        # With page number
        {'action': 'ptp_load_posts', 'page': '2'},
        {'action': 'ptp_load_posts', 'paged': '2'},
        
        # With nonce
        {'action': 'ptp_load_posts', 'nonce': file_nonce},
        {'action': 'ptp_load_posts', 'security': file_nonce},
        {'action': 'ptp_load_posts', '_wpnonce': file_nonce},
        
        # With category/filter
        {'action': 'ptp_load_posts', 'category': 'audio'},
        {'action': 'ptp_load_posts', 'post_type': 'product'},
        
        # Combined parameters
        {'action': 'ptp_load_posts', 'page': '2', 'nonce': file_nonce},
        {'action': 'ptp_load_posts', 'paged': '2', 'security': file_nonce},
        
        # Offset-based pagination
        {'action': 'ptp_load_posts', 'offset': '10'},
        {'action': 'ptp_load_posts', 'offset': '20'},
        
        # Common WordPress query vars
        {'action': 'ptp_load_posts', 'posts_per_page': '10'},
        {'action': 'ptp_load_posts', 'numberposts': '10'},
    ]
    
    successful_responses = []
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n  [{i}/{len(test_cases)}] Testing: {params}")
        
        try:
            response = session.post(ajax_url, data=params, headers=ajax_headers, timeout=15)
            
            print(f"    Status: {response.status_code}")
            print(f"    Response length: {len(response.text)}")
            
            if response.status_code == 200:
                content = response.text.strip()
                print(f"    Content preview: {content[:100]}...")
                
                # Check if response is not empty or error
                if content and content != '0' and content != '-1' and len(content) > 10:
                    print(f"    ✅ SUCCESS! Got meaningful response")
                    
                    # Try to parse as JSON
                    try:
                        json_data = json.loads(content)
                        is_json = True
                        print(f"    📋 Response is valid JSON")
                    except:
                        is_json = False
                        print(f"    📄 Response is HTML/text")
                    
                    successful_responses.append({
                        'params': params,
                        'status_code': response.status_code,
                        'content_length': len(content),
                        'content': content,
                        'is_json': is_json
                    })
                else:
                    print(f"    ❌ Empty or error response: '{content}'")
            else:
                print(f"    ❌ HTTP error: {response.status_code}")
                if response.text:
                    print(f"    Error content: {response.text[:100]}")
            
        except Exception as e:
            print(f"    ❌ Exception: {e}")
        
        time.sleep(0.5)  # Be respectful
    
    return successful_responses

def analyze_responses(responses):
    """Analyze successful responses for URLs and content"""
    print(f"\n" + "="*60)
    print(f"📊 ANALYSIS OF SUCCESSFUL RESPONSES")
    print(f"="*60)
    
    if not responses:
        print("❌ No successful responses to analyze")
        return
    
    print(f"✅ Found {len(responses)} successful responses\n")
    
    for i, resp in enumerate(responses, 1):
        print(f"Response {i}:")
        print(f"  Parameters: {resp['params']}")
        print(f"  Length: {resp['content_length']} chars")
        print(f"  Is JSON: {resp['is_json']}")
        
        # Look for URLs in response
        import re
        content = resp['content']
        
        # Extract URLs
        url_pattern = r'https?://[^\s"\'<>]+'
        urls = re.findall(url_pattern, content)
        audio_urls = [url for url in urls if 'audio' in url.lower()]
        
        print(f"  URLs found: {len(urls)}")
        print(f"  Audio URLs: {len(audio_urls)}")
        
        if audio_urls:
            print(f"  Sample audio URLs:")
            for url in audio_urls[:3]:
                print(f"    {url}")
        
        # Look for product/post structure
        if resp['is_json']:
            try:
                json_data = json.loads(content)
                print(f"  JSON keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
            except:
                pass
        
        print(f"  Preview: {content[:200]}...")
        print()
    
    # Save results
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f'ptp_test_results_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'test_info': {
                'timestamp': timestamp,
                'total_tests': len(responses),
                'successful_responses': len(responses)
            },
            'responses': responses
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {filename}")

def main():
    print("🧪 PTP LOAD POSTS TESTER")
    print("="*50)
    
    responses = test_ptp_action()
    analyze_responses(responses)

if __name__ == "__main__":
    main()