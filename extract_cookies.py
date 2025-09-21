#!/usr/bin/env python3
"""
Cookie Extractor for sachtienganhhanoi.com
===========================================
Help extract fresh cookies and nonce from browser session.
"""

import re
import json

def extract_cookies_from_curl():
    """
    Interactive tool to extract cookies from Chrome's "Copy as cURL" command
    """
    print("🍪 COOKIE EXTRACTOR FOR sachtienganhhanoi.com")
    print("=" * 60)
    print()
    print("📋 Instructions:")
    print("1. Login to sachtienganhhanoi.com in Chrome")
    print("2. Go to any audio page (e.g., Now I Know 2)")
    print("3. Open DevTools (F12) → Network tab")
    print("4. Look for 'admin-ajax.php' request")
    print("5. Right-click → Copy → Copy as cURL")
    print("6. Paste the cURL command below")
    print()
    print("⚠️  Note: Paste the ENTIRE cURL command (may be very long)")
    print()
    
    # Get cURL command from user
    print("📝 Paste your cURL command here:")
    print("(Press Enter twice when done)")
    curl_lines = []
    while True:
        line = input()
        if line.strip() == "" and curl_lines:
            break
        curl_lines.append(line)
    
    curl_command = " ".join(curl_lines)
    
    if not curl_command.strip():
        print("❌ No cURL command provided!")
        return None
    
    print()
    print("🔍 Analyzing cURL command...")
    
    # Extract cookies
    cookies = {}
    cookie_matches = re.findall(r'-H [\'"]cookie: ([^\'"]+)[\'"]', curl_command)
    
    if cookie_matches:
        cookie_string = cookie_matches[0]
        # Split cookies
        for cookie_pair in cookie_string.split(';'):
            if '=' in cookie_pair:
                name, value = cookie_pair.strip().split('=', 1)
                cookies[name] = value
    
    # Extract nonce from data
    nonce = None
    data_matches = re.findall(r'--data-raw [\'"]([^\'"]+)[\'"]', curl_command)
    if data_matches:
        data_string = data_matches[0]
        nonce_match = re.search(r'_ajax_nonce=([a-f0-9]+)', data_string)
        if nonce_match:
            nonce = nonce_match.group(1)
    
    # Extract other parameters
    token_match = re.search(r'listoken=([a-f0-9]+)', curl_command)
    token = token_match.group(1) if token_match else None
    
    account_match = re.search(r'account_id=([a-f0-9]+)', curl_command)
    account_id = account_match.group(1) if account_match else None
    
    drive_match = re.search(r'drive_id=([A-F0-9]+)', curl_command)
    drive_id = drive_match.group(1) if drive_match else None
    
    print(f"✅ Extracted {len(cookies)} cookies")
    print(f"✅ Nonce: {nonce if nonce else '❌ Not found'}")
    print(f"✅ Token: {token if token else '❌ Not found'}")
    print(f"✅ Account ID: {account_id if account_id else '❌ Not found'}")
    print(f"✅ Drive ID: {drive_id if drive_id else '❌ Not found'}")
    
    # Generate Python code
    if cookies and nonce:
        print()
        print("🐍 PYTHON CODE TO UPDATE:")
        print("=" * 40)
        
        print("# Update cookies_dict in your script:")
        print("cookies_dict = {")
        for name, value in cookies.items():
            if name.startswith(('wordpress_', 'WPCP_', 'cf_clearance')):
                print(f"    '{name}': '{value}',")
        print("}")
        print()
        print(f"# Update nonce:")
        print(f"ajax_nonce = '{nonce}'")
        print()
        
        # Save to file
        extracted_data = {
            'cookies': cookies,
            'nonce': nonce,
            'token': token,
            'account_id': account_id,
            'drive_id': drive_id,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        with open('extracted_cookies.json', 'w') as f:
            json.dump(extracted_data, f, indent=2)
        
        print("💾 Full data saved to 'extracted_cookies.json'")
        
        return extracted_data
    else:
        print("❌ Failed to extract required cookies or nonce")
        print("💡 Make sure you copied the complete cURL command from an AJAX request")
        return None

def update_auto_downloader_script(extracted_data):
    """Update the auto_downloader script with new cookies and nonce"""
    if not extracted_data:
        return False
    
    script_path = "01-ok-auto_downloader.py"
    
    try:
        # Read current script
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Update cookies
        new_cookies = {}
        for name, value in extracted_data['cookies'].items():
            if name.startswith(('wordpress_', 'WPCP_', 'cf_clearance')):
                new_cookies[name] = value
        
        cookies_code = "    cookies_dict = {\n"
        for name, value in new_cookies.items():
            cookies_code += f"        '{name}': '{value}',\n"
        cookies_code += "    }"
        
        # Replace cookies section
        cookies_pattern = r'cookies_dict = \{[^}]+\}'
        script_content = re.sub(cookies_pattern, cookies_code.strip(), script_content, flags=re.DOTALL)
        
        # Replace nonce
        nonce_pattern = r"ajax_nonce = '[a-f0-9]+'"
        script_content = re.sub(nonce_pattern, f"ajax_nonce = '{extracted_data['nonce']}'", script_content)
        
        # Write back
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ Updated {script_path} with new cookies and nonce!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update script: {e}")
        return False

if __name__ == "__main__":
    try:
        extracted_data = extract_cookies_from_curl()
        
        if extracted_data:
            print()
            update_choice = input("🔄 Update auto_downloader script automatically? (y/n): ").strip().lower()
            if update_choice == 'y':
                update_auto_downloader_script(extracted_data)
            
            print()
            print("🎉 Cookie extraction complete!")
            print("📁 Files generated:")
            print("   - extracted_cookies.json (backup of all data)")
            if update_choice == 'y':
                print("   - 01-ok-auto_downloader.py (updated with new cookies)")
        else:
            print("💥 Cookie extraction failed!")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Extraction cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()