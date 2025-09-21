import requests
import json

def test_single_download():
    """Test a single download URL to see what's happening"""
    
    print("🔍 TESTING SINGLE DOWNLOAD URL")
    print("=" * 50)
    
    # Load JSON to get one download URL
    with open('curl_ajax_response.json', 'r', encoding='utf-8') as f:
        audio_data = json.load(f)
    
    # Get first item
    first_key = list(audio_data.keys())[0]
    first_item = audio_data[first_key]
    
    download_url = first_item['download']
    title = first_item['title']
    expected_size = first_item['size']
    
    print(f"Testing: {title}")
    print(f"Expected size: {expected_size:,} bytes")
    print(f"URL: {download_url}")
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
    
    # First, make a HEAD request to see headers
    print("1. HEAD Request:")
    try:
        head_response = session.head(download_url, headers=headers, allow_redirects=True, timeout=10)
        print(f"   Status: {head_response.status_code}")
        print(f"   Final URL: {head_response.url}")
        print(f"   Headers:")
        for key, value in head_response.headers.items():
            print(f"     {key}: {value}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. GET Request (first 1000 bytes):")  
    try:
        # Make GET request with range header to get first 1000 bytes
        test_headers = headers.copy() 
        test_headers['Range'] = 'bytes=0-999'
        
        response = session.get(download_url, headers=test_headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Length: {response.headers.get('Content-Length', 'Not specified')}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        print(f"   Response size: {len(response.content)} bytes")
        
        if response.content:
            # Check if it's binary audio data or text/HTML
            try:
                text_content = response.content.decode('utf-8')
                print(f"   Content (text): {text_content[:200]}...")
            except UnicodeDecodeError:
                print(f"   Content appears to be binary (audio) data")
                print(f"   First 20 bytes (hex): {response.content[:20].hex()}")
        else:
            print("   No content received")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. GET Request (without range, full response headers):")
    try:
        response = session.get(download_url, headers=headers, stream=True, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        print(f"   All Response Headers:")
        for key, value in response.headers.items():
            print(f"     {key}: {value}")
        
        # Try to read first chunk
        chunk_count = 0
        total_size = 0
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                total_size += len(chunk)
                chunk_count += 1
                if chunk_count == 1:
                    print(f"   First chunk size: {len(chunk)} bytes")
                    # Check if it's text or binary
                    try:
                        chunk_text = chunk.decode('utf-8')
                        print(f"   First chunk (text): {chunk_text[:100]}...")
                    except UnicodeDecodeError:
                        print(f"   First chunk appears to be binary")
                        print(f"   First 20 bytes (hex): {chunk[:20].hex()}")
                if chunk_count >= 3:  # Only read first 3 chunks for testing
                    break
        
        print(f"   Total downloaded in test: {total_size} bytes from {chunk_count} chunks")
        
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_download()