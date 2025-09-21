import requests
import json

def test_stream_vs_download():
    """Test both stream and download URLs"""
    
    print("🔍 TESTING STREAM VS DOWNLOAD URLs")
    print("=" * 50)
    
    # Load JSON to get URLs
    with open('curl_ajax_response.json', 'r', encoding='utf-8') as f:
        audio_data = json.load(f)
    
    # Get first item
    first_key = list(audio_data.keys())[0]
    first_item = audio_data[first_key]
    
    download_url = first_item['download']
    stream_url = first_item['source']
    title = first_item['title']
    expected_size = first_item['size']
    
    print(f"Testing: {title}")
    print(f"Expected size: {expected_size:,} bytes")
    print("-" * 50)
    
    # Create session with cookies
    session = requests.Session()
    
    cookies = {
        'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
        'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
        'cf_clearance': 'I1i63KhgLPNUKKPECrRj9nP6FnBCP3ZeColxfnsFVAM-1758331351-1.2.1.1-NTTIQrqghh4ouAu95VvVnWzqrKQfgo17qpGutEcbR4BMGKto.jmFv6yYr6Kq.AFuX6OR3TcUeu_QdJJlct2TJxRcWs2QPGPWqJe_C6g7o5pVMLR0a48Dh_HPOLAW9tk0Y9qUaMt2fyROlLKoOdfUvHUsZPgmj7i53AS5r53GD9IKnbBNsCq.txAOzoY4oKqIfwXGZE3BU_XGwU6Gnj2Y6YWuuunAcVbmQOIirFC8MWg'
    }
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='sachtienganhhanoi.com')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': 'audio/mpeg,audio/*,*/*',
        'Referer': 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/',
        'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7'
    }
    
    # Test both URLs
    urls_to_test = [
        ("Download URL", download_url),
        ("Stream URL", stream_url)
    ]
    
    for url_type, url in urls_to_test:
        print(f"\n{url_type}:")
        print(f"URL: {url}")
        print("-" * 30)
        
        try:
            # HEAD request first
            head_response = session.head(url, headers=headers, allow_redirects=True, timeout=10)
            print(f"HEAD Status: {head_response.status_code}")
            print(f"HEAD Content-Type: {head_response.headers.get('Content-Type', 'Not specified')}")
            print(f"HEAD Content-Length: {head_response.headers.get('Content-Length', 'Not specified')}")
            
            # GET request for first few bytes
            range_headers = headers.copy()
            range_headers['Range'] = 'bytes=0-1023'  # First 1KB
            
            response = session.get(url, headers=range_headers, timeout=10)
            print(f"GET Status: {response.status_code}")
            print(f"GET Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            print(f"GET Content-Length: {response.headers.get('Content-Length', 'Not specified')}")
            print(f"GET Response size: {len(response.content)} bytes")
            
            if response.content:
                # Check if it's binary audio data or text/HTML
                try:
                    text_content = response.content.decode('utf-8')
                    print(f"Content (text): {text_content[:150]}...")
                    
                    # Save error content
                    with open(f'{url_type.lower().replace(" ", "_")}_error.html', 'w', encoding='utf-8') as f:
                        f.write(text_content)
                    print(f"Full error saved to {url_type.lower().replace(' ', '_')}_error.html")
                    
                except UnicodeDecodeError:
                    print(f"Content appears to be binary (audio) data - SUCCESS!")
                    print(f"First 20 bytes (hex): {response.content[:20].hex()}")
                    
                    # This looks like audio! Try to save a sample
                    with open(f'{title}_sample_{url_type.lower().replace(" ", "_")}.mp3', 'wb') as f:
                        f.write(response.content)
                    print(f"Sample saved to {title}_sample_{url_type.lower().replace(' ', '_')}.mp3")
            else:
                print("No content received")
                
        except Exception as e:
            print(f"Error: {e}")

def try_with_fresh_session():
    """Try to get a fresh session by login first"""
    print(f"\n{'='*60}")
    print("🔄 TRYING WITH FRESH LOGIN SESSION")
    print(f"{'='*60}")
    
    session = requests.Session()
    
    # Step 1: Login first to get fresh session
    print("1. Attempting fresh login...")
    
    login_url = "https://sachtienganhhanoi.com/my-account/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    # Get login page
    login_page = session.get(login_url, headers=headers)
    if login_page.status_code == 200:
        print("   ✅ Got login page")
        
        # Parse for nonce
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(login_page.text, 'html.parser')
        nonce_field = soup.find('input', {'name': 'woocommerce-login-nonce'})
        nonce_value = nonce_field['value'] if nonce_field else None
        
        if nonce_value:
            print(f"   ✅ Found nonce: {nonce_value}")
            
            # Attempt login
            login_data = {
                'username': 'dungla2011@gmail.com',
                'password': '11111111',
                'woocommerce-login-nonce': nonce_value,
                'login': 'Log in'
            }
            
            login_response = session.post(login_url, data=login_data, headers=headers, allow_redirects=True)
            print(f"   Login response status: {login_response.status_code}")
            
            # Step 2: Get fresh audio page and AJAX data
            print("\n2. Getting fresh audio page...")
            audio_url = "https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/"
            audio_page = session.get(audio_url, headers=headers)
            
            if audio_page.status_code == 200:
                print("   ✅ Got audio page with fresh session")
                
                # Extract fresh parameters
                soup = BeautifulSoup(audio_page.text, 'html.parser')
                wpcp_div = soup.find('div', {'class': lambda x: x and 'wpcp-module' in x and 'ShareoneDrive' in x})
                
                if wpcp_div:
                    fresh_token = wpcp_div.get('data-token')
                    fresh_account_id = wpcp_div.get('data-account-id')
                    fresh_drive_id = wpcp_div.get('data-drive-id')
                    
                    print(f"   Fresh token: {fresh_token}")
                    print(f"   Fresh account ID: {fresh_account_id}")
                    
                    # Step 3: Try download with fresh session
                    print("\n3. Testing download with fresh session...")
                    
                    # Build fresh download URL
                    fresh_download_url = f"https://sachtienganhhanoi.com/wp-admin/admin-ajax.php?action=shareonedrive-download&id=741A9E8166169047!s4e9bd73c97bc4957a80e8089ae699329&dl=1&account_id={fresh_account_id}&drive_id={fresh_drive_id}&listtoken={fresh_token}"
                    
                    print(f"   Fresh URL: {fresh_download_url[:100]}...")
                    
                    response = session.get(fresh_download_url, headers=headers, stream=True, timeout=10)
                    print(f"   Status: {response.status_code}")
                    print(f"   Content-Type: {response.headers.get('Content-Type')}")
                    
                    chunk_count = 0
                    total_size = 0
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            total_size += len(chunk)
                            chunk_count += 1
                            if chunk_count == 1:
                                # Check first chunk
                                try:
                                    chunk_text = chunk.decode('utf-8')
                                    print(f"   First chunk (text): {chunk_text[:100]}...")
                                except UnicodeDecodeError:
                                    print(f"   First chunk appears to be binary audio data!")
                                    print(f"   First 20 bytes (hex): {chunk[:20].hex()}")
                                    
                                    # Save sample
                                    with open('fresh_session_sample.mp3', 'wb') as f:
                                        f.write(chunk)
                                    print(f"   Sample saved to fresh_session_sample.mp3")
                            
                            if chunk_count >= 5:  # Only test first few chunks
                                break
                    
                    print(f"   Downloaded {total_size} bytes in {chunk_count} chunks")
                    
                else:
                    print("   ❌ Could not find ShareoneDrive div")
            else:
                print(f"   ❌ Failed to get audio page: {audio_page.status_code}")
        else:
            print("   ❌ Could not find nonce")
    else:
        print(f"   ❌ Failed to get login page: {login_page.status_code}")

if __name__ == "__main__":
    test_stream_vs_download()
    try_with_fresh_session()