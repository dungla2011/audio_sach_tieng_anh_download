import requests
from bs4 import BeautifulSoup
import re
import json

def test_ajax_with_curl_cookies():
    """
    Test AJAX request using the exact cookies and parameters from curl
    """
    print("🔧 TESTING AJAX WITH CURL COOKIES")
    print("=" * 50)
    
    # Create session
    session = requests.Session()
    
    # Set cookies from curl (these are logged-in cookies)
    cookies = {
        'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
        'WPCP_UUID': '1820fbed-abf7-47e7-aab2-117f2564139c',
        'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
        'sbjs_migrations': '1418474375998%3D1',
        'sbjs_current_add': 'fd%3D2025-09-20%2000%3A55%3A55%7C%7C%7Cep%3Dhttps%3A%2F%2Fsachtienganhhanoi.com%2Fcart%2F%7C%7C%7Crf%3D%28none%29',
        'sbjs_first_add': 'fd%3D2025-09-20%2000%3A55%3A55%7C%7C%7Cep%3Dhttps%3A%2F%2Fsachtienganhhanoi.com%2Fcart%2F%7C%7C%7Crf%3D%28none%29',
        'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
        'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
        'sbjs_udata': 'vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F140.0.0.0%20Safari%2F537.36',
        'sbjs_session': 'pgs%3D15%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fsachtienganhhanoi.com%2Faudio-now-i-know-2-student-book-audio-cd%2F',
        'cf_clearance': 'I1i63KhgLPNUKKPECrRj9nP6FnBCP3ZeColxfnsFVAM-1758331351-1.2.1.1-NTTIQrqghh4ouAu95VvVnWzqrKQfgo17qpGutEcbR4BMGKto.jmFv6yYr6Kq.AFuX6OR3TcUeu_QdJJlct2TJxRcWs2QPGPWqJe_C6g7o5pVMLR0a48Dh_HPOLAW9tk0Y9qUaMt2fyROlLKoOdfUvHUsZPgmj7i53AS5r53GD9IKnbBNsCq.txAOzoY4oKqIfwXGZE3BU_XGwU6Gnj2Y6YWuuunAcVbmQOIirFC8MWg'
    }
    
    # Set all cookies to session
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='sachtienganhhanoi.com')
    
    # Headers exactly from curl
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://sachtienganhhanoi.com',
        'priority': 'u=1, i',
        'referer': 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # Data exactly from curl
    data = {
        'action': 'shareonedrive-get-playlist',
        'account_id': '741a9e8166169047',
        'drive_id': '741A9E8166169047',
        'lastFolder': '',
        'sort': 'name:asc',
        'listtoken': '103f3ee93041bb540aca292e50a3a11f',
        'page_url': 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/',
        '_ajax_nonce': 'e5b9dce6c4'
    }
    
    print("📡 Making AJAX request with exact curl parameters...")
    print(f"   Action: {data['action']}")
    print(f"   Account ID: {data['account_id']}")
    print(f"   Drive ID: {data['drive_id']}")
    print(f"   List Token: {data['listtoken']}")
    print(f"   Nonce: {data['_ajax_nonce']}")
    print(f"   Cookies: {len(cookies)} cookies set")
    
    try:
        response = session.post(
            'https://sachtienganhhanoi.com/wp-admin/admin-ajax.php',
            headers=headers,
            data=data,
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Length: {len(response.text)} characters")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if len(response.text) > 0:
            print(f"\n📄 Raw Response (First 500 chars):")
            print("-" * 50)
            print(response.text[:500])
            print("-" * 50)
            
            # Try to parse as JSON
            try:
                json_data = response.json()
                print("\n✅ SUCCESS! Valid JSON response received")
                
                # Save JSON response
                with open('curl_ajax_response.json', 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                print("📄 JSON saved to 'curl_ajax_response.json'")
                
                # Analyze JSON structure
                print(f"\n📊 JSON Analysis:")
                if isinstance(json_data, dict):
                    print(f"   Type: Dictionary")
                    print(f"   Keys: {list(json_data.keys())}")
                    
                    if 'contents' in json_data:
                        contents = json_data['contents']
                        if isinstance(contents, list):
                            print(f"   Contents: {len(contents)} items")
                            if contents:
                                print(f"   First item: {list(contents[0].keys()) if isinstance(contents[0], dict) else 'Not a dict'}")
                elif isinstance(json_data, list):
                    print(f"   Type: List")
                    print(f"   Length: {len(json_data)}")
                else:
                    print(f"   Type: {type(json_data)}")
                    print(f"   Value: {str(json_data)[:100]}")
                    
                return json_data
                
            except ValueError:
                print("\n❌ Response is not valid JSON")
                
                # Save raw response for inspection
                with open('curl_ajax_raw_response.txt', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("📄 Raw response saved to 'curl_ajax_raw_response.txt'")
                
                return response.text
        else:
            print("\n❌ Empty response received")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None

def try_different_parameters():
    """
    Try the AJAX request with different parameter combinations
    """
    print(f"\n{'='*50}")
    print("🔧 TRYING DIFFERENT PARAMETER COMBINATIONS")
    print(f"{'='*50}")
    
    # Base session with cookies
    session = requests.Session()
    
    cookies = {
        'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
        'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
        'cf_clearance': 'I1i63KhgLPNUKKPECrRj9nP6FnBCP3ZeColxfnsFVAM-1758331351-1.2.1.1-NTTIQrqghh4ouAu95VvVnWzqrKQfgo17qpGutEcbR4BMGKto.jmFv6yYr6Kq.AFuX6OR3TcUeu_QdJJlct2TJxRcWs2QPGPWqJe_C6g7o5pVMLR0a48Dh_HPOLAW9tk0Y9qUaMt2fyROlLKoOdfUvHUsZPgmj7i53AS5r53GD9IKnbBNsCq.txAOzoY4oKqIfwXGZE3BU_XGwU6Gnj2Y6YWuuunAcVbmQOIirFC8MWg'
    }
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='sachtienganhhanoi.com')
    
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Different parameter combinations to try
    test_cases = [
        {
            'name': 'Original curl parameters',
            'data': {
                'action': 'shareonedrive-get-playlist',
                'account_id': '741a9e8166169047',
                'drive_id': '741A9E8166169047',
                'lastFolder': '',
                'sort': 'name:asc',
                'listtoken': '103f3ee93041bb540aca292e50a3a11f',
                'page_url': 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/',
                '_ajax_nonce': 'e5b9dce6c4'
            }
        },
        {
            'name': 'Without nonce',
            'data': {
                'action': 'shareonedrive-get-playlist',
                'account_id': '741a9e8166169047',
                'drive_id': '741A9E8166169047',
                'lastFolder': '',
                'sort': 'name:asc',
                'listtoken': '103f3ee93041bb540aca292e50a3a11f',
                'page_url': 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/'
            }
        },
        {
            'name': 'Minimal parameters',
            'data': {
                'action': 'shareonedrive-get-playlist',
                'account_id': '741a9e8166169047',
                'drive_id': '741A9E8166169047',
                'listtoken': '103f3ee93041bb540aca292e50a3a11f'
            }
        },
        {
            'name': 'Alternative action name',
            'data': {
                'action': 'shareonedrive_get_playlist',  # underscore instead of dash
                'account_id': '741a9e8166169047',
                'drive_id': '741A9E8166169047',
                'listtoken': '103f3ee93041bb540aca292e50a3a11f',
                '_ajax_nonce': 'e5b9dce6c4'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 30)
        
        try:
            response = session.post(
                'https://sachtienganhhanoi.com/wp-admin/admin-ajax.php',
                headers=headers,
                data=test_case['data'],
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Length: {len(response.text)} chars")
            
            if len(response.text) > 0:
                print(f"   Preview: {response.text[:100]}...")
                
                # Try parsing as JSON
                try:
                    json_data = response.json()
                    print(f"   ✅ Valid JSON! Saving as test_{i}.json")
                    with open(f'test_{i}.json', 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                except:
                    print(f"   ❌ Not JSON, saving as test_{i}.txt")
                    with open(f'test_{i}.txt', 'w', encoding='utf-8') as f:
                        f.write(response.text)
            else:
                print(f"   ❌ Empty response")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 ADVANCED AJAX TESTING WITH CURL DATA")
    print("=" * 50)
    
    # Test 1: Exact curl replication
    result = test_ajax_with_curl_cookies()
    
    # Test 2: Try different parameter combinations
    try_different_parameters()
    
    print(f"\n{'='*50}")
    print("🏁 TESTING COMPLETE")
    print("📁 Check generated files for results:")
    print("   - curl_ajax_response.json (if successful)")
    print("   - curl_ajax_raw_response.txt (raw response)")
    print("   - test_*.json / test_*.txt (parameter variation tests)")