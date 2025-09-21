#!/usr/bin/env python3
"""
Debug the response structure from module 2
"""

from browser_session_downloader import BrowserSessionDownloader
import json

# Test with working module 2 data
cookies_dict = {
    'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
    'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
    'cf_clearance': 'I1i63KhgLPNUKKPECrRj9nP6FnBCP3ZeColxfnsFVAM-1758331351-1.2.1.1-NTTIQrqghh4ouAu95VvVnWzqrKQfgo17qpGutEcbR4BMGKto.jmFv6yYr6Kq.AFuX6OR3TcUeu_QdJJlct2TJxRcWs2QPGPWqJe_C6g7o5pVMLR0a48Dh_HPOLAW9tk0Y9qUaMt2fyROlLKoOdfUvHUsZPgmj7i53AS5r53GD9IKnbBNsCq.txAOzoY4oKqIfwXGZE3BU_XGwU6Gnj2Y6YWuuunAcVbmQOIirFC8MWg'
}

ajax_nonce = 'e5b9dce6c4'
page_url = "https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/"

downloader = BrowserSessionDownloader()
downloader.set_browser_cookies(cookies_dict)

# Test with module 2 data (the working one)
module_data = {
    'token': '103f3ee93041bb540aca292e50a3a11f',
    'account_id': '741a9e8166169047',
    'drive_id': '741A9E8166169047',
    'module_number': 2
}

print("🔍 Testing Module 2 AJAX call...")

# Make direct AJAX call
ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
ajax_data = {
    'action': 'shareonedrive-get-playlist',
    'account_id': module_data['account_id'],
    'drive_id': module_data['drive_id'],
    'lastFolder': '',
    'sort': 'name:asc',
    'listtoken': module_data['token'],
    'page_url': page_url,
    '_ajax_nonce': ajax_nonce
}

ajax_headers = {
    'origin': 'https://sachtienganhhanoi.com',
    'referer': page_url,
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin'
}

response = downloader.session.post(ajax_url, data=ajax_data, headers=ajax_headers)

print(f"Status: {response.status_code}")
print(f"Length: {len(response.text)}")

# Parse JSON and save to file for analysis
try:
    data = response.json()
    
    # Save full response
    with open('debug_module2_response.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ JSON saved to debug_module2_response.json")
    
    # Analyze structure
    print(f"\nStructure Analysis:")
    print(f"Type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Keys: {len(data)} items")
        
        # Look at first few items
        for i, (key, value) in enumerate(list(data.items())[:3]):
            print(f"\nItem {i+1}: {key}")
            if isinstance(value, dict):
                print(f"  Value keys: {list(value.keys())}")
                # Check for download URLs
                if 'downloadUrl' in value:
                    print(f"  Has downloadUrl: {value['downloadUrl'][:100]}...")
                else:
                    print(f"  No downloadUrl found")
                    # Look for other URL fields
                    url_fields = [k for k, v in value.items() if isinstance(v, str) and 'http' in v]
                    if url_fields:
                        print(f"  URL fields found: {url_fields}")
                        for field in url_fields:
                            print(f"    {field}: {value[field][:100]}...")
            else:
                print(f"  Value type: {type(value)}")
                print(f"  Value: {str(value)[:100]}...")

except Exception as e:
    print(f"❌ Error: {e}")
    
    # Save raw response for debugging
    with open('debug_module2_raw.txt', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Raw response saved to debug_module2_raw.txt")