#!/usr/bin/env python3
"""
Debug script to check wpcp-container structure on a page
"""

import requests
from bs4 import BeautifulSoup

def check_page_structure(url):
    """Check the structure of wpcp-container on a page"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Login first
    login_url = "https://sachtienganhhanoi.com/my-account/"
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', {'class': 'woocommerce-form-login'})
    nonce_input = form.find('input', {'name': 'woocommerce-login-nonce'})
    nonce = nonce_input.get('value')
    
    login_data = {
        'username': 'dungla2011@gmail.com',
        'password': '11111111',
        'woocommerce-login-nonce': nonce,
        '_wp_http_referer': '/my-account/',
        'login': 'Log in'
    }
    session.post(login_url, data=login_data)
    
    # Now check the target page
    print(f"🔍 Checking page: {url}")
    response = session.get(url)
    
    if response.status_code != 200:
        print(f"❌ Failed to access page: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for any wpcp related divs
    wpcp_divs = soup.find_all('div', {'class': lambda x: x and 'wpcp' in x})
    
    if wpcp_divs:
        print(f"✅ Found {len(wpcp_divs)} wpcp-related divs:")
        for i, div in enumerate(wpcp_divs, 1):
            print(f"\n--- Div {i} ---")
            print(f"Class: {div.get('class')}")
            print(f"ID: {div.get('id')}")
            
            # Check all data attributes
            data_attrs = {k: v for k, v in div.attrs.items() if k.startswith('data-')}
            if data_attrs:
                print("Data attributes:")
                for key, value in data_attrs.items():
                    print(f"  {key}: {value}")
            else:
                print("No data attributes found")
            
            # Show first 200 chars of content
            content = div.get_text(strip=True)[:200]
            if content:
                print(f"Content preview: {content}...")
    else:
        print("❌ No wpcp-related divs found")
        
        # Let's check for any div with data-token
        token_divs = soup.find_all('div', {'data-token': True})
        if token_divs:
            print(f"✅ Found {len(token_divs)} divs with data-token:")
            for i, div in enumerate(token_divs, 1):
                print(f"\n--- Token Div {i} ---")
                print(f"Class: {div.get('class')}")
                print(f"ID: {div.get('id')}")
                data_attrs = {k: v for k, v in div.attrs.items() if k.startswith('data-')}
                for key, value in data_attrs.items():
                    print(f"  {key}: {value}")
        else:
            print("❌ No divs with data-token found either")
            
            # Let's look for any ShareOneDrive related content
            print("\n🔍 Looking for ShareOneDrive related content...")
            if 'shareonedrive' in response.text.lower():
                print("✅ Found ShareOneDrive references in page")
                # Extract script tags that might contain the data
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'shareonedrive' in script.string.lower():
                        print("Found ShareOneDrive in script:")
                        print(script.string[:500] + "..." if len(script.string) > 500 else script.string)
            else:
                print("❌ No ShareOneDrive references found")

if __name__ == "__main__":
    url = "https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/"
    check_page_structure(url)