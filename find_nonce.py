#!/usr/bin/env python3
"""
Find nonce in page content
"""

import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

# Login
login_url = 'https://sachtienganhhanoi.com/my-account/'
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'html.parser')
form = soup.find('form', {'class': 'woocommerce-form-login'})
nonce = form.find('input', {'name': 'woocommerce-login-nonce'}).get('value')

login_data = {
    'username': 'dungla2011@gmail.com',
    'password': '11111111', 
    'woocommerce-login-nonce': nonce,
    '_wp_http_referer': '/my-account/',
    'login': 'Log in'
}
session.post(login_url, data=login_data)

# Get audio page
url = 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/'
response = session.get(url)

print("🔍 Looking for nonce patterns in page...")

# Look for various nonce patterns
patterns = [
    r'wpcp_ajax_nonce["\']?\s*:\s*["\']([^"\']+)["\']',
    r'nonce["\']?\s*:\s*["\']([^"\']+)["\']',
    r'_ajax_nonce["\']?\s*:\s*["\']([^"\']+)["\']',
    r'security["\']?\s*:\s*["\']([^"\']+)["\']',
    r'wpAjaxUrl[^}]*nonce["\']?\s*:\s*["\']([^"\']+)["\']'
]

found_nonces = []

for pattern in patterns:
    matches = re.findall(pattern, response.text, re.IGNORECASE)
    if matches:
        print(f"✅ Pattern '{pattern}' found: {matches}")
        found_nonces.extend(matches)

if not found_nonces:
    print("❌ No nonce patterns found")
    
    # Look for any JavaScript variables that might contain nonce
    js_vars = re.findall(r'var\s+(\w*nonce\w*)\s*=\s*["\']([^"\']+)["\']', response.text, re.IGNORECASE)
    if js_vars:
        print(f"Found JS nonce variables: {js_vars}")
    
    # Look for data attributes with nonce
    nonce_attrs = re.findall(r'data-[^=]*nonce[^=]*=["\']([^"\']+)["\']', response.text, re.IGNORECASE)
    if nonce_attrs:
        print(f"Found data-nonce attributes: {nonce_attrs}")
        
    # Check if wpcp_ajax_object exists
    if 'wpcp_ajax_object' in response.text:
        print("✅ Found wpcp_ajax_object in page")
        # Extract the entire object
        ajax_obj_match = re.search(r'wpcp_ajax_object\s*=\s*(\{[^}]+\})', response.text)
        if ajax_obj_match:
            print(f"AJAX object: {ajax_obj_match.group(1)}")
    else:
        print("❌ No wpcp_ajax_object found")

# Try the login nonce we already have
print(f"\n🔧 Testing login nonce: {nonce}")

ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
ajax_data = {
    'action': 'shareonedrive-get-playlist',
    'token': '103f3ee93041bb540aca292e50a3a11f',
    'account_id': '741a9e8166169047',
    'drive_id': '741A9E8166169047',
    'nonce': nonce
}

response = session.post(ajax_url, data=ajax_data)
print(f"Response status: {response.status_code}")
print(f"Response length: {len(response.text)}")
if response.text and len(response.text) < 200:
    print(f"Response: {response.text}")
elif response.text:
    print(f"Response preview: {response.text[:100]}...")