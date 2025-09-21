#!/usr/bin/env python3
"""
DataTables AJAX Test
===================
Test the ptp_load_posts action with proper DataTables parameters
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

def test_datatables_ajax():
    """Test DataTables AJAX request with proper parameters"""
    
    cookies, file_nonce = load_cookies()
    
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='.sachtienganhhanoi.com')
    
    ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
    referer = "https://sachtienganhhanoi.com/audio_stream/"
    
    # From the page source analysis:
    ajax_nonce = "c3b46b9ca3"
    table_id = "ptp_38232b3504e57e95_1"
    
    # AJAX headers
    ajax_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': referer
    }
    
    print("🧪 Testing DataTables AJAX request...")
    
    # Standard DataTables parameters for server-side processing
    datatables_params = {
        'action': 'ptp_load_posts',
        'table_id': table_id,
        'ajax_nonce': ajax_nonce,
        
        # DataTables standard parameters
        'draw': '1',
        'start': '0',
        'length': '10',
        
        # Search parameters
        'search[value]': '',
        'search[regex]': 'false',
        
        # Order parameters
        'order[0][column]': '0',
        'order[0][dir]': 'asc',
        
        # Column parameters
        'columns[0][data]': '0',
        'columns[0][name]': '',
        'columns[0][searchable]': 'true',
        'columns[0][orderable]': 'true',
        'columns[0][search][value]': '',
        'columns[0][search][regex]': 'false',
        
        'columns[1][data]': '1',
        'columns[1][name]': '',
        'columns[1][searchable]': 'true',
        'columns[1][orderable]': 'true',
        'columns[1][search][value]': '',
        'columns[1][search][regex]': 'false',
        
        'columns[2][data]': '2',
        'columns[2][name]': '',
        'columns[2][searchable]': 'true',
        'columns[2][orderable]': 'true',
        'columns[2][search][value]': '',
        'columns[2][search][regex]': 'false',
    }
    
    print(f"  📋 Using nonce: {ajax_nonce}")
    print(f"  📋 Using table_id: {table_id}")
    
    try:
        response = session.post(ajax_url, data=datatables_params, headers=ajax_headers, timeout=20)
        
        print(f"  Status: {response.status_code}")
        print(f"  Response length: {len(response.text)}")
        
        if response.status_code == 200:
            content = response.text.strip()
            print(f"  Content preview: {content[:200]}...")
            
            # Try to parse as JSON
            try:
                json_data = json.loads(content)
                print(f"  ✅ SUCCESS! Got valid JSON response")
                print(f"  📋 JSON keys: {list(json_data.keys())}")
                
                # Look for data in the response
                if 'data' in json_data and isinstance(json_data['data'], list):
                    print(f"  📊 Found {len(json_data['data'])} data rows")
                    
                    # Analyze first few rows
                    for i, row in enumerate(json_data['data'][:3], 1):
                        print(f"    Row {i}: {len(row)} columns")
                        if isinstance(row, list) and len(row) > 1:
                            # Look for URLs in the row data
                            for col_idx, col_data in enumerate(row):
                                if isinstance(col_data, str) and ('http' in col_data or 'audio' in col_data.lower()):
                                    print(f"      Column {col_idx}: {col_data[:100]}...")
                
                # Save the successful response
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f'datatables_success_{timestamp}.json'
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'request_params': datatables_params,
                        'response_data': json_data,
                        'timestamp': timestamp
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"  💾 Success data saved to: {filename}")
                
                return json_data
                
            except json.JSONDecodeError as e:
                print(f"  ❌ Response is not valid JSON: {e}")
                print(f"  📄 Raw response: {content}")
                
        else:
            print(f"  ❌ HTTP error: {response.status_code}")
            if response.text:
                print(f"  Error content: {response.text[:200]}...")
                
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    return None

def extract_audio_urls(json_data):
    """Extract audio page URLs from the DataTables response"""
    audio_urls = []
    
    if 'data' in json_data and isinstance(json_data['data'], list):
        for row in json_data['data']:
            if isinstance(row, list):
                for col_data in row:
                    if isinstance(col_data, str):
                        # Look for URLs in HTML content
                        import re
                        url_pattern = r'href=["\']([^"\']+)["\']'
                        urls = re.findall(url_pattern, col_data)
                        
                        for url in urls:
                            if 'audio' in url.lower() and url.startswith(('http', '/')):
                                if url.startswith('/'):
                                    url = 'https://sachtienganhhanoi.com' + url
                                audio_urls.append(url)
    
    return list(set(audio_urls))  # Remove duplicates

def main():
    print("🧪 DATATABLES AJAX TESTER")
    print("="*50)
    
    json_data = test_datatables_ajax()
    
    if json_data:
        print(f"\n📊 ANALYZING RESPONSE...")
        
        audio_urls = extract_audio_urls(json_data)
        
        if audio_urls:
            print(f"  ✅ Found {len(audio_urls)} audio URLs!")
            print(f"\n🎵 Audio URLs:")
            for i, url in enumerate(audio_urls[:10], 1):  # Show first 10
                print(f"    {i}. {url}")
            
            if len(audio_urls) > 10:
                print(f"    ... and {len(audio_urls) - 10} more")
            
            # Save URLs to file
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            urls_filename = f'discovered_audio_urls_{timestamp}.txt'
            
            with open(urls_filename, 'w', encoding='utf-8') as f:
                f.write("# Audio URLs discovered via DataTables AJAX\n")
                f.write(f"# Generated: {timestamp}\n")
                f.write(f"# Total URLs: {len(audio_urls)}\n\n")
                
                for url in audio_urls:
                    f.write(f"{url}\n")
            
            print(f"  💾 URLs saved to: {urls_filename}")
            
        else:
            print(f"  ❌ No audio URLs found in response")
    
    else:
        print(f"\n❌ No successful response received")

if __name__ == "__main__":
    main()