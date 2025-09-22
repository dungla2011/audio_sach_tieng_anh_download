#!/usr/bin/env python3
"""
Auto Audio Downloader for sachtienganhhanoi.com
===============================================
Automatically downloads audio files from any audio page using command line arguments.
Can process single URLs or batch process from JSON files.

Usage:
    python auto_downloader.py <audio_page_url>
    python auto_downloader.py file=<json_filename>
    
Examples:
    python auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/
    python auto_downloader.py file=ALL_AUDIO_ITEMS_5879_items.json
    
Note: Uses cookies and nonce from the working session. Update these if they expire.
"""

import sys
import os
import re
from browser_session_downloader import BrowserSessionDownloader

def load_cookies_from_curl():
    """Auto-load cookies and nonce from curl_cmd.txt (supports both Windows CMD and Bash formats)"""
    try:
        curl_file = 'curl_cmd.txt'
        if not os.path.exists(curl_file):
            return None, None, None
            
        with open(curl_file, 'r', encoding='utf-8') as f:
            curl_content = f.read()
        
        # Detect format and extract cookies
        cookies = {}
        action = None
        
        # Try Windows CMD format first: -b ^"..."^ (multiline support)
        cookie_match = re.search(r'-b\s+\^"([^"]+)"\s*\^', curl_content, re.DOTALL)
        if not cookie_match:
            # Try Bash format: -b '...' or -b "..."
            cookie_match = re.search(r"-b\s+['\"]([^'\"]+)['\"]", curl_content, re.DOTALL)
        
        if cookie_match:
            cookie_string = cookie_match.group(1)
            cookie_pairs = cookie_string.split('; ')
            
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    # Decode Windows batch URL encoding if present
                    value = value.replace('^%^', '%')
                    cookies[name] = value
        
        # Extract nonce from --data-raw parameter
        nonce = None
        nonce_match = re.search(r'_ajax_nonce=([a-f0-9]+)', curl_content)
        if nonce_match:
            nonce = nonce_match.group(1)
        
        # Extract action to determine request type
        action_match = re.search(r'action=([^&^%]+)', curl_content)
        if action_match:
            action = action_match.group(1).replace('^&', '&')
        
        return cookies, nonce, action
        
    except Exception as e:
        print(f"⚠️  Warning: Could not load from curl_cmd.txt: {e}")
        return None, None, None

def main():
    """Main function with command line argument support"""
    
    print("🎵 Auto Audio Downloader for sachtienganhhanoi.com")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("❌ Error: No input provided")
        print("\nUsage:")
        print(f"    python {os.path.basename(__file__)} <audio_page_url> [revert]")
        print(f"    python {os.path.basename(__file__)} file=<json_filename> [revert]")
        print("\nExamples:")
        print("    python auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/")
        print("    python auto_downloader.py file=ALL_AUDIO_ITEMS_5879_items.json")
        print("    python auto_downloader.py file=ALL_AUDIO_ITEMS_5879_items.json revert")
        print("\nOptions:")
        print("    revert    Download files in reverse order")
        sys.exit(1)
    
    # Parse arguments
    arguments = sys.argv[1:]
    main_argument = arguments[0]
    reverse_order = 'revert' in arguments
    
    if reverse_order:
        print("🔄 Reverse order mode enabled - downloading from last to first")
    
    # Check if it's a file parameter
    if main_argument.startswith('file='):
        json_filename = main_argument[5:]  # Remove 'file=' prefix
        process_json_file(json_filename, reverse_order)
    else:
        # Single URL mode
        audio_url = main_argument
        
        # Validate URL
        if not audio_url.startswith('https://sachtienganhhanoi.com/'):
            print(f"❌ Error: Invalid URL. Must start with 'https://sachtienganhhanoi.com/'")
            print(f"   Provided: {audio_url}")
            sys.exit(1)
        
        process_single_url(audio_url, reverse_order)

def process_json_file(json_filename, reverse_order=False):
    """Process all URLs from JSON file"""
    import json
    import time
    
    print(f"📄 Processing JSON file: {json_filename}")
    if reverse_order:
        print("🔄 Will process items in reverse order")
    
    # Check if file exists
    if not os.path.exists(json_filename):
        print(f"❌ Error: File '{json_filename}' not found")
        sys.exit(1)
    
    # Load JSON data
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} items from JSON file")
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        sys.exit(1)
    
    # Filter audio items (items with URLs that contain 'audio' or have '[AUDIO]' in title)
    audio_items = []
    for item in data:
        url = item.get('url', '')
        title = item.get('title', '')
        
        if url and ('audio' in url.lower() or '[audio]' in title.lower()):
            audio_items.append(item)
    
    print(f"🎵 Found {len(audio_items)} audio items to download")
    
    if not audio_items:
        print("❌ No audio items found in JSON file")
        sys.exit(1)
    
    # Apply reverse order if requested
    if reverse_order:
        audio_items = list(reversed(audio_items))
        print("🔄 Audio items order reversed")
    
    # Confirm before starting bulk download
    order_text = " (in reverse order)" if reverse_order else ""
    response = input(f"\n⚠️  Ready to download {len(audio_items)} audio items{order_text}. Continue? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Download cancelled by user")
        sys.exit(0)
    
    # Process each URL
    successful = 0
    failed = 0
    start_time = time.time()
    
    print(f"\n🚀 Starting bulk download of {len(audio_items)} items...")
    print("=" * 60)
    
    for i, item in enumerate(audio_items, 1):
        url = item.get('url')
        title = item.get('title', 'Unknown')
        
        print(f"\n[{i}/{len(audio_items)}] Processing: {title[:60]}...")
        print(f"URL: {url}")
        
        try:
            success = process_single_url(url, reverse_order, show_header=False)
            if success:
                successful += 1
                print("✅ Success")
            else:
                failed += 1
                print("❌ Failed")
        except Exception as e:
            failed += 1
            print(f"❌ Error: {e}")
        
        # Add delay between downloads to be respectful
        if i < len(audio_items):  # Don't delay after last item
            print("⏳ Waiting 2 seconds...")
            time.sleep(2)
    
    # Final summary
    elapsed = time.time() - start_time
    print(f"\n" + "=" * 60)
    print("📊 BULK DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Total items: {len(audio_items)}")
    print(f"⏱️  Total time: {elapsed:.1f} seconds")
    print(f"📈 Average: {elapsed/len(audio_items):.1f} seconds per item")

def process_single_url(audio_url, reverse_order=False, show_header=True):
    """Process a single URL"""
    if show_header:
        print(f"🎯 Target URL: {audio_url}")
        if reverse_order:
            print("� Reverse order mode enabled")
        print()

    # Try to auto-load cookies from curl_cmd.txt first
    auto_cookies, auto_nonce, curl_action = load_cookies_from_curl()
    
    if auto_cookies and auto_nonce:
        print(f"🔄 Auto-loaded cookies from curl_cmd.txt")
        if curl_action:
            if curl_action == 'shareonedrive-get-playlist':
                print(f"✅ Perfect! Found audio download nonce")
            else:
                print(f"⚠️  Warning: Nonce is for '{curl_action}', not 'shareonedrive-get-playlist'")
                print(f"   You need to capture audio play request, not page load request")
        
        # Filter only relevant cookies
        cookies_dict = {}
        for name, value in auto_cookies.items():
            if name.startswith(('wordpress_', 'WPCP_', 'cf_clearance')):
                cookies_dict[name] = value
        ajax_nonce = auto_nonce
    else:
        print("🔐 Using fallback cookies")
        # Fallback cookies and nonce from browser session
        cookies_dict = {
            'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
            'WPCP_UUID': '1820fbed-abf7-47e7-aab2-117f2564139c',
            'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
            'cf_clearance': 'wAUDVjAy8aWHrTWDYpBQ0GaTkMS_uj4oU5mMDn7eZQg-1758502075-1.2.1.1-7IYkUXSOtHIrM0aOs7HWp9ep7E3qm3ngzq6fFvQNXEbZcZ6W93kF7l86zdOzRWW6mEA3sGeewwOZ7lWBovmiwcUxaMbQpubsSR2J9VQQ0zKSucO08TiiLh0D8pVwhgqbB2x.1Niiep58L0H3_N8xD46VAlgnx4dpx_GZI.ErNlwXKHFzOwb.7QsxGGBZUcabfFSHK.Vov9eCgqIN7y.cCdkKiDhix1mV9VyowQ1A6WQ',
        }
        ajax_nonce = '06782abbf6'
    
    print(f"🔑 Using nonce: {ajax_nonce}")
    print(f"🍪 Loaded {len(cookies_dict)} cookies")    # Create downloader and start process
    downloader = BrowserSessionDownloader()
    
    if show_header:
        print("🚀 Starting download process...")
    
    success = downloader.download_from_url(audio_url, cookies_dict, ajax_nonce, reverse_order)
    
    if show_header:
        print()
        if success:
            print("✅ Download process completed successfully!")
            print("📁 Check the created folder(s) for your audio files.")
        else:
            print("❌ Download process failed!")
            print("\n💡 Troubleshooting:")
            print("   - Cookies or nonce may have expired")
            print("   - Target page may not have audio content")
            print("   - Network connection issues")
            print("\n🔧 To update cookies and nonce:")
            print("   1. Login to sachtienganhhanoi.com in Chrome")
            print("   2. Go to any audio page and open DevTools")
            print("   3. Find admin-ajax.php request in Network tab")
            print("   4. Copy as cURL and extract new cookies/nonce")
            print("   5. Update the cookies_dict and ajax_nonce in this script")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Download interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)