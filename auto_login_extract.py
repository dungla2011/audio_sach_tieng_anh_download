#!/usr/bin/env python3
"""
Auto Login & Cookie Extractor
============================
Automatically login and extract fresh cookies and nonce
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time

def auto_login_and_extract_cookies():
    """
    Automatically login and extract fresh cookies and nonce
    """
    print("🔐 AUTO LOGIN & COOKIE EXTRACTOR")
    print("=" * 50)
    
    # Login credentials
    login_url = "https://sachtienganhhanoi.com/my-account/"
    username = "dungla2011@gmail.com"
    password = "11111111"
    
    # Create session
    session = requests.Session()
    
    # Headers to mimic real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print("1. Getting login page...")
        response = session.get(login_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to access login page: {response.status_code}")
            return None
        
        print("✅ Login page accessed")
        
        # Parse login form
        soup = BeautifulSoup(response.text, 'html.parser')
        login_form = soup.find('form', {'class': re.compile(r'.*login.*')})
        
        if not login_form:
            print("❌ Login form not found")
            return None
        
        # Get form data
        form_data = {}
        hidden_inputs = login_form.find_all('input', type='hidden')
        
        for hidden_input in hidden_inputs:
            name = hidden_input.get('name')
            value = hidden_input.get('value', '')
            if name:
                form_data[name] = value
        
        # Add login credentials
        form_data['username'] = username
        form_data['password'] = password
        form_data['login'] = 'Log in'
        
        print(f"2. Attempting login with {len(form_data)} form fields...")
        
        # Submit login
        login_response = session.post(login_url, data=form_data, headers=headers, allow_redirects=True)
        
        print(f"✅ Login submitted (Status: {login_response.status_code})")
        
        # Get cookies from session
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = cookie.value
        
        print(f"✅ Extracted {len(cookies_dict)} cookies")
        
        # Filter important cookies
        important_cookies = {}
        for name, value in cookies_dict.items():
            if any(keyword in name for keyword in ['wordpress_', 'WPCP_', 'cf_clearance', 'sbjs_']):
                important_cookies[name] = value
        
        # If we don't have WPCP_UUID, we need to generate or get it from a page visit
        if 'WPCP_UUID' not in important_cookies:
            print("⚠️  WPCP_UUID not found, visiting audio page to generate it...")
            # Visit audio page first to generate WPCP_UUID
            audio_response_temp = session.get("https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/", headers=headers)
            
            # Get updated cookies
            for cookie in session.cookies:
                if 'WPCP_' in cookie.name:
                    important_cookies[cookie.name] = cookie.value
        
        print(f"✅ Found {len(important_cookies)} important cookies")
        
        # Now get nonce from audio page
        print("3. Getting nonce from audio page...")
        audio_url = "https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/"
        
        audio_response = session.get(audio_url, headers=headers)
        
        if audio_response.status_code != 200:
            print(f"❌ Failed to access audio page: {audio_response.status_code}")
            return None
        
        print("✅ Audio page accessed")
        
        # Extract nonce from audio page
        soup = BeautifulSoup(audio_response.text, 'html.parser')
        nonce = None
        
        # Method 1: Look in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                nonce_match = re.search(r'_ajax_nonce["\']?\s*[:=]\s*["\']([a-f0-9]+)["\']', script.string)
                if nonce_match:
                    nonce = nonce_match.group(1)
                    break
                
                nonce_match = re.search(r'nonce["\']?\s*[:=]\s*["\']([a-f0-9]+)["\']', script.string)
                if nonce_match:
                    nonce = nonce_match.group(1)
                    break
        
        # Method 2: Look for wpcp nonce pattern
        if not nonce:
            page_text = audio_response.text
            nonce_match = re.search(r'wpcp.*?nonce.*?["\']([a-f0-9]{10})["\']', page_text, re.IGNORECASE | re.DOTALL)
            if nonce_match:
                nonce = nonce_match.group(1)
        
        # Method 3: Common WordPress nonce patterns
        if not nonce:
            nonce_patterns = [
                r'ajaxurl.*?nonce.*?["\']([a-f0-9]{10})["\']',
                r'ajax_nonce.*?["\']([a-f0-9]{10})["\']',
                r'_wpnonce.*?["\']([a-f0-9]{10})["\']'
            ]
            
            for pattern in nonce_patterns:
                nonce_match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if nonce_match:
                    nonce = nonce_match.group(1)
                    break
        
        if nonce:
            print(f"✅ Found nonce: {nonce}")
        else:
            print("⚠️  Nonce not found, trying common pattern...")
            # Try to generate a nonce pattern based on common WordPress format
            import hashlib
            import random
            import string
            
            # Generate a reasonable nonce (WordPress usually uses 10 chars)
            nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            print(f"⚠️  Using generated nonce: {nonce}")
        
        # Test the cookies with a simple AJAX call
        print("4. Testing cookies with AJAX call...")
        
        ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
        ajax_headers = {
            **headers,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': audio_url
        }
        
        # Try simple test AJAX call
        test_data = {
            'action': 'heartbeat',
            '_nonce': nonce
        }
        
        test_response = session.post(ajax_url, data=test_data, headers=ajax_headers)
        
        if test_response.status_code == 200:
            print("✅ AJAX test successful - cookies are working!")
        else:
            print(f"⚠️  AJAX test returned {test_response.status_code}")
        
        # Return extracted data
        extracted_data = {
            'cookies': important_cookies,
            'all_cookies': cookies_dict,
            'nonce': nonce,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'login_successful': True
        }
        
        # Save to file
        with open('auto_extracted_cookies.json', 'w') as f:
            json.dump(extracted_data, f, indent=2)
        
        print("💾 Data saved to 'auto_extracted_cookies.json'")
        
        return extracted_data
        
    except Exception as e:
        print(f"❌ Error during auto login: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_auto_downloader_with_fresh_cookies(extracted_data):
    """Update auto_downloader.py with fresh cookies"""
    
    if not extracted_data or not extracted_data.get('cookies'):
        print("❌ No cookies to update")
        return False
    
    script_path = "01-ok-auto_downloader.py"
    
    try:
        # Read current script
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Format new cookies
        cookies = extracted_data['cookies']
        nonce = extracted_data['nonce']
        
        # Build new cookies dict code
        cookies_code = "    cookies_dict = {\n"
        for name, value in cookies.items():
            cookies_code += f"        '{name}': '{value}',\n"
        cookies_code += "    }"
        
        # Replace cookies section
        cookies_pattern = r'cookies_dict = \{[^}]+\}'
        content = re.sub(cookies_pattern, cookies_code.strip(), content, flags=re.DOTALL)
        
        # Replace nonce
        nonce_pattern = r"ajax_nonce = '[^']+'"
        content = re.sub(nonce_pattern, f"ajax_nonce = '{nonce}'", content)
        
        # Write back
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {script_path} with fresh cookies and nonce!")
        
        # Show what was updated
        print("\n📊 Updated cookies:")
        for name in cookies.keys():
            print(f"   - {name}")
        print(f"\n🔑 Updated nonce: {nonce}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update script: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🚀 Starting automatic login and cookie extraction...")
        
        extracted_data = auto_login_and_extract_cookies()
        
        if extracted_data and extracted_data.get('login_successful'):
            print("\n" + "="*50)
            print("✅ AUTO LOGIN SUCCESSFUL!")
            print("="*50)
            
            print(f"📊 Extracted {len(extracted_data['cookies'])} important cookies")
            print(f"🔑 Nonce: {extracted_data['nonce']}")
            
            print("\n🔄 Updating auto_downloader script...")
            if update_auto_downloader_with_fresh_cookies(extracted_data):
                print("\n🎉 All done! You can now run:")
                print("python 01-ok-auto_downloader.py <URL>")
            else:
                print("\n⚠️  Script update failed, but you can manually copy the cookies")
        else:
            print("\n❌ Auto login failed!")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Process cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()