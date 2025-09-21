import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

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
        
        return success
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("WordPress Login Tester - Enhanced Edition")
    print("=" * 50)
    
    result = test_wordpress_login()
    
    print("\n" + "=" * 50)
    print("📋 FINAL RESULT:")
    if result is True:
        print("🎉 LOGIN SUCCESSFUL!")
        print("✅ Credentials are valid and login completed")
    elif result == "email_verification_required":
        print("📧 EMAIL VERIFICATION REQUIRED!")
        print("✅ Credentials are correct, but email needs verification")
        print("📝 Check email inbox/spam for verification link")
    elif result is False:
        print("💥 LOGIN FAILED!")
        print("❌ Credentials may be incorrect or other login error")
    else:
        print("🤔 LOGIN RESULT UNCLEAR")
        print("🔍 Check login_response.html for manual verification")