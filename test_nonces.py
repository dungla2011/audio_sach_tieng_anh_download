#!/usr/bin/env python3
"""
Test different nonces
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
login_nonce = form.find('input', {'name': 'woocommerce-login-nonce'}).get('value')

login_data = {
    'username': 'dungla2011@gmail.com',
    'password': '11111111', 
    'woocommerce-login-nonce': login_nonce,
    '_wp_http_referer': '/my-account/',
    'login': 'Log in'
}
session.post(login_url, data=login_data)

# Get audio page and extract nonces
url = 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/'
response = session.get(url)

# Find all nonces
nonces = re.findall(r'nonce["\']?\s*:\s*["\']([^"\']+)["\']', response.text, re.IGNORECASE)
print(f"Found {len(nonces)} nonces: {nonces[:5]}...")

# Test parameters for module 2 (the working one from 3.py)
ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
test_params = {
    'action': 'shareonedrive-get-playlist',
    'token': '103f3ee93041bb540aca292e50a3a11f',
    'account_id': '741a9e8166169047',
    'drive_id': '741A9E8166169047'
}

# Test each nonce
for i, nonce in enumerate(nonces[:3]):  # Test first 3 nonces
    print(f"\n🔧 Testing nonce {i+1}: {nonce}")
    
    test_data = test_params.copy()
    test_data['nonce'] = nonce
    
    response = session.post(ajax_url, data=test_data)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Length: {len(response.text)}")
    
    if response.text:
        if 'files' in response.text or len(response.text) > 1000:
            print("✅ Success! This looks like the playlist data")
            break
        elif len(response.text) < 100:
            print(f"Response: {response.text}")
        else:
            print(f"Preview: {response.text[:100]}...")

# Also test without nonce
print(f"\n🔧 Testing without nonce:")
response = session.post(ajax_url, data=test_params)
print(f"Status: {response.status_code}")
print(f"Length: {len(response.text)}")
print(f"Response: {response.text[:100] if response.text else 'Empty'}")