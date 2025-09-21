#!/usr/bin/env python3
"""
Test AJAX call for Now I Know 5 modules
"""

import requests
from bs4 import BeautifulSoup
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest'
})

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

# Test Now I Know 5 modules
modules = [
    {
        'name': 'Module 1',
        'token': 'db957f0be40e5ed57c39ad47a3a700ad',
        'account_id': 'f0e9cfd79dbff848',
        'drive_id': 'drive'
    },
    {
        'name': 'Module 2', 
        'token': 'a883507d4b7835ee64fe93d085210bac',
        'account_id': '741a9e8166169047',
        'drive_id': '741A9E8166169047'
    }
]

ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"

for module in modules:
    print(f"\n=== Testing {module['name']} ===")
    
    ajax_data = {
        'action': 'shareonedrive-get-playlist',
        'token': module['token'],
        'account_id': module['account_id'],
        'drive_id': module['drive_id']
    }
    
    print(f"Request data: {ajax_data}")
    
    response = session.post(ajax_url, data=ajax_data)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Response length: {len(response.text)}")
    
    if response.text:
        if len(response.text) < 200:
            print(f"Response: {response.text}")
        else:
            print(f"Response preview: {response.text[:200]}...")
            
        try:
            data = response.json()
            if isinstance(data, dict) and 'files' in data:
                print(f"✅ Success! Found {len(data['files'])} files")
            else:
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        except:
            print("Failed to parse as JSON")
    else:
        print("Empty response")