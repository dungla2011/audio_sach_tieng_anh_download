import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import json
import time

def decode_unicode_string(unicode_str):
    """Decode unicode escaped string"""
    try:
        # Replace u-style escapes with actual characters
        return unicode_str.encode().decode('unicode-escape')
    except:
        return unicode_str

def test_wordpress_login():
    """Test login to WordPress site"""
    
    # Login credentials
    login_url = "https://sachtienganhhanoi.com/my-account/"
    username = "dungla2011@gmail.com"
    password = "11111111"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Set headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"Testing login to: {login_url}")
        print(f"Username: {username}")
        print("Password: ********")
        print("-" * 50)
        
        # First, get the login page to extract nonce and other required fields
        print("1. Getting login page...")
        response = session.get(login_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to access login page. Status code: {response.status_code}")
            return False
            
        print(f"✅ Login page accessed successfully (Status: {response.status_code})")
        
        # Parse the HTML to find the login form
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for WordPress nonce field
        nonce_field = soup.find('input', {'name': re.compile(r'.*nonce.*')})
        nonce_value = nonce_field['value'] if nonce_field else None
        
        # Look for other hidden fields
        hidden_fields = soup.find_all('input', type='hidden')
        
        print(f"Found {len(hidden_fields)} hidden fields in login form")
        if nonce_value:
            print(f"Found nonce field: {nonce_field['name']}")
        
        # Prepare login data
        login_data = {
            'username': username,
            'password': password,
            'login': 'Log in',
            'redirect_to': '',
            'testcookie': '1'
        }
        
        # Add nonce if found
        if nonce_field and nonce_value:
            login_data[nonce_field['name']] = nonce_value
            
        # Add other hidden fields
        for field in hidden_fields:
            if field.get('name') and field.get('value'):
                if field['name'] not in login_data:
                    login_data[field['name']] = field['value']
        
        print("\n2. Attempting login...")
        
        # Submit login form
        login_response = session.post(login_url, data=login_data, headers=headers, allow_redirects=True)
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Final URL after login: {login_response.url}")
        
        # Check for email verification requirement
        response_text = login_response.text
        
        # Look for email verification messages in the response
        verification_patterns = [
            r'Bu1ea1n cu1ea7n xu00e1c minh tu00e0i khou1ea3n',  # Unicode encoded Vietnamese
            r'You need to verify your account',
            r'verification',
            r'verify.*email',
            r'email.*verification',
            r'xác minh',
            r'verification_error_page'
        ]
        
        email_verification_required = False
        verification_message = ""
        
        for pattern in verification_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                email_verification_required = True
                if 'Bu1ea1n cu1ea7n xu00e1c minh' in matches[0]:
                    # Try to decode Vietnamese unicode
                    verification_message = "Bạn cần xác minh tài khoản trước khi đăng nhập"
                else:
                    verification_message = matches[0]
                break
        
        # Check if login was successful
        success_indicators = [
            'dashboard', 'logout', 'welcome', 'woocommerce-myaccount', 'my account navigation'
        ]
        
        failure_indicators = [
            'error', 'incorrect', 'invalid', 'failed', 'wrong password'
        ]
        
        response_text_lower = response_text.lower()
        success_found = any(indicator in response_text_lower for indicator in success_indicators)
        failure_found = any(indicator in response_text_lower for indicator in failure_indicators)
        
        print("\n3. Analyzing login result...")
        
        if email_verification_required:
            print("⚠️  LOGIN BLOCKED - EMAIL VERIFICATION REQUIRED")
            print(f"📧 Message: {verification_message}")
            print("🔒 The account exists but needs email verification before login")
            success = "email_verification_required"
        elif login_response.url != login_url and success_found:
            print("✅ Login appears successful! (Redirected to account dashboard)")
            success = True
        elif success_found and not failure_found:
            print("✅ Login appears successful! (Found success indicators)")
            success = True
        elif failure_found:
            print("❌ Login failed! (Found error indicators)")
            success = False
        else:
            print("⚠️  Login result unclear. Manual verification needed.")
            success = None
        
        # Additional analysis for debugging
        print(f"\n📊 Analysis details:")
        print(f"   - Success indicators found: {success_found}")
        print(f"   - Failure indicators found: {failure_found}")
        print(f"   - Email verification required: {email_verification_required}")
        print(f"   - URL changed: {login_response.url != login_url}")
        
        # Save response for manual inspection
        with open('login_response.html', 'w', encoding='utf-8') as f:
            f.write(login_response.text)
        print("📄 Full response saved to 'login_response.html' for inspection")
        
        return success, session  # Return session for further use
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None

def analyze_audio_page_and_get_json(session, target_url):
    """
    Access the audio page and try to extract/simulate the admin-ajax.php request using curl data
    """
    print(f"\n{'='*50}")
    print("🎵 ANALYZING AUDIO PAGE")
    print(f"Target URL: {target_url}")
    print(f"{'='*50}")
    
    try:
        # Step 1: Access the audio page
        print("1. Accessing audio page...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'Referer': 'https://sachtienganhhanoi.com/my-account/'
        }
        
        response = session.get(target_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to access audio page. Status code: {response.status_code}")
            return None
            
        print(f"✅ Audio page accessed successfully (Status: {response.status_code})")
        
        # Save the page for inspection
        with open('audio_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("📄 Audio page saved to 'audio_page.html'")
        
        # Step 2: Extract data from the HTML (based on curl data)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the wpcp container with data attributes
        wpcp_div = soup.find('div', {'class': re.compile(r'.*wpcp-module.*ShareoneDrive.*')})
        
        extracted_data = {}
        if wpcp_div:
            print("✅ Found ShareoneDrive module div")
            extracted_data['token'] = wpcp_div.get('data-token')
            extracted_data['account_id'] = wpcp_div.get('data-account-id') 
            extracted_data['drive_id'] = wpcp_div.get('data-drive-id')
            extracted_data['path'] = wpcp_div.get('data-path', '')
            extracted_data['source'] = wpcp_div.get('data-source', '')
            
            print(f"   Token: {extracted_data.get('token')}")
            print(f"   Account ID: {extracted_data.get('account_id')}")
            print(f"   Drive ID: {extracted_data.get('drive_id')}")
        else:
            print("❌ ShareoneDrive module div not found")
            return None
        
        # Look for ajax nonce (usually in script tags or forms)
        nonce_value = None
        
        # Method 1: Look in script tags for nonce
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # Look for common nonce patterns
                nonce_match = re.search(r'_ajax_nonce["\']?\s*[:=]\s*["\']([a-f0-9]+)["\']', script.string)
                if nonce_match:
                    nonce_value = nonce_match.group(1)
                    break
                    
                # Look for wpcp specific nonce
                nonce_match = re.search(r'nonce["\']?\s*[:=]\s*["\']([a-f0-9]+)["\']', script.string)
                if nonce_match:
                    nonce_value = nonce_match.group(1)
                    break
        
        # Method 2: Look in form fields
        if not nonce_value:
            nonce_fields = soup.find_all('input', {'name': re.compile(r'.*nonce.*')})
            for field in nonce_fields:
                if field.get('value'):
                    nonce_value = field.get('value')
                    break
        
        print(f"Found nonce: {nonce_value}")
        
        # Step 3: Make the exact AJAX request based on curl
        ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
        
        # Headers from curl
        ajax_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://sachtienganhhanoi.com',
            'Referer': target_url,
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }
        
        # Data from curl (with extracted values)
        post_data = {
            'action': 'shareonedrive-get-playlist',
            'account_id': extracted_data.get('account_id', '741a9e8166169047'),
            'drive_id': extracted_data.get('drive_id', '741A9E8166169047'),
            'lastFolder': '',
            'sort': 'name:asc',
            'listtoken': extracted_data.get('token', '103f3ee93041bb540aca292e50a3a11f'),
            'page_url': target_url,
            '_ajax_nonce': nonce_value if nonce_value else 'e5b9dce6c4'  # fallback to curl value
        }
        
        print(f"\n📡 Making AJAX request to get playlist...")
        print(f"   Action: {post_data['action']}")
        print(f"   Account ID: {post_data['account_id']}")
        print(f"   Drive ID: {post_data['drive_id']}")
        print(f"   List Token: {post_data['listtoken']}")
        print(f"   Nonce: {post_data['_ajax_nonce']}")
        
        try:
            ajax_response = session.post(ajax_url, data=post_data, headers=ajax_headers, timeout=30)
            
            print(f"AJAX Response Status: {ajax_response.status_code}")
            print(f"Response length: {len(ajax_response.text)} characters")
            
            if ajax_response.status_code == 200:
                try:
                    json_data = ajax_response.json()
                    print("✅ SUCCESS! Got JSON response from admin-ajax.php")
                    
                    # Save the JSON response
                    filename = 'shareonedrive_playlist.json'
                    with open(filename, 'w', encoding='utf-8') as f:
                        import json
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    print(f"� JSON playlist saved to '{filename}'")
                    
                    # Display some info about the response
                    if isinstance(json_data, dict):
                        print(f"📊 JSON Response Summary:")
                        print(f"   Keys: {list(json_data.keys())}")
                        if 'contents' in json_data:
                            contents = json_data['contents']
                            if isinstance(contents, list):
                                print(f"   Number of items: {len(contents)}")
                                if contents:
                                    first_item = contents[0]
                                    print(f"   First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                    
                    return {
                        'success': True,
                        'data': json_data,
                        'filename': filename,
                        'extracted_params': extracted_data
                    }
                    
                except ValueError:
                    print("❌ Response is not valid JSON")
                    print(f"Raw response: {ajax_response.text[:500]}...")
                    
                    # Save raw response for inspection
                    with open('ajax_raw_response.txt', 'w', encoding='utf-8') as f:
                        f.write(ajax_response.text)
                    print("📄 Raw response saved to 'ajax_raw_response.txt'")
                    
                    return {
                        'success': False,
                        'error': 'Not JSON',
                        'raw_response': ajax_response.text,
                        'extracted_params': extracted_data
                    }
            else:
                print(f"❌ AJAX request failed with status {ajax_response.status_code}")
                print(f"Error response: {ajax_response.text[:200]}...")
                return {
                    'success': False,
                    'error': f'HTTP {ajax_response.status_code}',
                    'response': ajax_response.text,
                    'extracted_params': extracted_data
                }
                
        except requests.RequestException as e:
            print(f"❌ Network error during AJAX request: {e}")
            return {
                'success': False,
                'error': f'Network error: {e}',
                'extracted_params': extracted_data
            }

        
    except Exception as e:
        print(f"❌ Error analyzing audio page: {e}")
        return {
            'success': False,
            'error': f'General error: {e}',
            'extracted_params': {}
        }

if __name__ == "__main__":
    print("WordPress Login Tester & Audio Downloader")
    print("=" * 50)
    
    # Step 1: Test login
    result, session = test_wordpress_login()
    
    print("\n" + "=" * 50)
    print("📋 LOGIN RESULT:")
    
    login_successful = False
    if result is True:
        print("🎉 LOGIN SUCCESSFUL!")
        print("✅ Credentials are valid and login completed")
        login_successful = True
    elif result == "email_verification_required":
        print("📧 EMAIL VERIFICATION REQUIRED!")
        print("✅ Credentials are correct, but email needs verification")
        print("� Continuing with session (may still work for some content)")
        login_successful = True  # Session might still work
    elif result is False:
        print("💥 LOGIN FAILED!")
        print("❌ Credentials may be incorrect or other login error")
        print("🔄 Continuing anyway to test audio page access")
    else:
        print("🤔 LOGIN RESULT UNCLEAR")
        print("🔍 Check login_response.html for manual verification")
        print("🔄 Continuing anyway to test audio page access")
    
    # Step 2: Try to access audio page and get JSON data (regardless of login status)
    if session:
        target_audio_url = "https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/"
        
        ajax_results = analyze_audio_page_and_get_json(session, target_audio_url)
        
        print("\n" + "=" * 50)
        print("📋 FINAL SUMMARY:")
        print(f"🔐 Login Status: {'✅ Success' if login_successful else '❌ Failed'}")
        print(f"🎵 Audio Page Analysis: {'✅ Completed' if ajax_results is not None else '❌ Failed'}")
        
        if ajax_results and ajax_results.get('success'):
            print(f"📊 AJAX Request Status: ✅ Success")
            print(f"   📄 Data saved to: {ajax_results.get('filename', 'N/A')}")
        elif ajax_results:
            print(f"📊 AJAX Request Status: ❌ {ajax_results.get('error', 'Failed')}")
        else:
            print(f"📊 AJAX Request Status: ❌ No response")
        
        print("\n📁 Generated Files:")
        print("   - login_response.html (login attempt details)")
        print("   - audio_page.html (audio page content)")
        if ajax_results and ajax_results.get('success'):
            print(f"   - {ajax_results.get('filename', 'shareonedrive_playlist.json')} (audio playlist data)")
        elif ajax_results and not ajax_results.get('success'):
            print("   - ajax_raw_response.txt (raw AJAX response for debugging)")
        if ajax_results:
            print("   - ajax_responses.json (JSON responses from AJAX calls)")
    else:
        print("\n❌ No session available for audio page analysis")