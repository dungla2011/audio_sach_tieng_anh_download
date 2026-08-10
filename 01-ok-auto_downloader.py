#!/usr/bin/env python3
"""
Auto Audio Downloader for sachtienganhhanoi.com
===============================================
Automatically downloads audio files from any audio page using command line arguments.
Can process single URLs or batch process from JSON files.

Usage:
    python 01-ok-auto_downloader.py <audio_page_url>
    python 01-ok-auto_downloader.py file=<json_filename>
    
Examples:
    python 01-ok-auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/
    python 01-ok-auto_downloader.py file=ALL.json
    
Note: Uses cookies and nonce from the working session. Update these if they expire.
"""

import sys
import os
import re
from browser_session_downloader import BrowserSessionDownloader

# Override built-in print in this module to prefix a timestamp (Y-m-d H:i:s)
import datetime as _datetime
import builtins as _builtins
_orig_print = _builtins.print
def print(*args, **kwargs):
    """Module-local print replacement that prefixes a timestamp to each line."""
    sep = kwargs.pop('sep', ' ')
    end = kwargs.pop('end', '\n')
    try:
        ts = _datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = sep.join(str(a) for a in args)
        _orig_print(f"{ts} {message}", end=end)
    except Exception:
        # Fallback to original print if anything goes wrong
        _orig_print(*args, sep=sep, end=end, **kwargs)

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

        # Extract playlist identifiers so we can call admin-ajax.php directly,
        # bypassing the page HTML GET (which Cloudflare may block for scripts).
        manual_wpcp = None
        if action == 'shareonedrive-get-playlist':
            account_id_match = re.search(r'account_id=([^&^"]+)', curl_content)
            drive_id_match = re.search(r'drive_id=([^&^"]+)', curl_content)
            listtoken_match = re.search(r'listtoken=([^&^"]+)', curl_content)
            if account_id_match and drive_id_match and listtoken_match:
                manual_wpcp = {
                    'token': listtoken_match.group(1),
                    'account_id': account_id_match.group(1),
                    'drive_id': drive_id_match.group(1),
                }

        # Extract all -H headers verbatim (excluding content-length), so the replayed
        # request matches the real browser request as closely as possible. Cloudflare
        # blocks requests missing browser-fingerprint headers like sec-ch-ua.
        headers = {}
        for m in re.finditer(r"-H\s+'([^:']+):\s*([^']*)'", curl_content):
            name = m.group(1).strip().lower()
            if name not in ('content-length',):
                headers[name] = m.group(2).strip()
        if not headers:
            for m in re.finditer(r'-H\s+\^"([^:]+):\s*([^\^]*)\^"', curl_content):
                name = m.group(1).strip().lower()
                if name not in ('content-length',):
                    headers[name] = m.group(2).strip()

        return cookies, nonce, action, manual_wpcp, headers

    except Exception as e:
        print(f"⚠️  Warning: Could not load from curl_cmd.txt: {e}")
        return None, None, None, None, None

def main():
    """Main function with command line argument support"""
    
    print("🎵 Auto Audio Downloader for sachtienganhhanoi.com")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("❌ Error: No input provided")
        print("\nUsage:")
        print(f"    python {os.path.basename(__file__)} <URL_or_file> [options...]")
        print("\nExamples:")
        print("    python 01-ok-auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/")
        print("    python 01-ok-auto_downloader.py file=ALL.json")
        print("    python 01-ok-auto_downloader.py file=ALL.json revert")
        print("    python 01-ok-auto_downloader.py file=ALL.json skip=2000")
        print("    python 01-ok-auto_downloader.py revert skip=1000 file=ALL.json")
        print("    python 01-ok-auto_downloader.py skip=500 file=ALL.json revert")
        print("\nOptions (can be in any order):")
        print("    revert      Download files in reverse order")
        print("    skip=N      Skip first N items (useful for resuming)")
        print("    threads=N   Number of parallel download threads (default: 10)")
        sys.exit(1)

    # Parse arguments flexibly
    arguments = sys.argv[1:]

    # Find main argument (URL or file=)
    main_argument = None
    reverse_order = False
    skip_count = 0
    text_filter = None
    max_workers = 10

    for arg in arguments:
        if arg.startswith('https://') or arg.startswith('file='):
            main_argument = arg
        elif arg == 'revert':
            reverse_order = True
        elif arg.startswith('skip='):
            try:
                skip_count = int(arg[5:])  # Remove 'skip=' prefix (5 chars)
            except ValueError:
                print(f"❌ Error: Invalid skip value. Must be a number. Got: {arg}")
                sys.exit(1)
        elif arg.startswith('threads='):
            try:
                max_workers = int(arg[8:])
                if max_workers < 1:
                    raise ValueError
            except ValueError:
                print(f"❌ Error: Invalid threads value. Must be a positive number. Got: {arg}")
                sys.exit(1)
        elif arg.startswith('text='):
            text_filter = arg[5:].strip('"')
        else:
            print(f"❌ Error: Unknown argument: {arg}")
            sys.exit(1)

    if not main_argument:
        print("❌ Error: No URL or file specified")
        sys.exit(1)
    
    # Show parsed options
    if skip_count > 0:
        print(f"🚀 Skip mode enabled - skip first {skip_count} items")
    if reverse_order:
        print("🔄 Reverse order mode enabled - downloading from last to first")
    if text_filter:
        print(f"🔍 Text filter enabled: '{text_filter}'")
    print(f"🧵 Parallel download threads: {max_workers}")

    # Check if it's a file parameter
    if main_argument.startswith('file='):
        json_filename = main_argument[5:]  # Remove 'file=' prefix
        process_json_file(json_filename, reverse_order, skip_count, text_filter, max_workers)
    else:
        # Single URL mode
        audio_url = main_argument

        # Validate URL
        if not audio_url.startswith('https://sachtienganhhanoi.com/'):
            print(f"❌ Error: Invalid URL. Must start with 'https://sachtienganhhanoi.com/'")
            print(f"   Provided: {audio_url}")
            sys.exit(1)

        process_single_url(audio_url, reverse_order, max_workers=max_workers)

def process_json_file(json_filename, reverse_order=False, skip_count=0, text_filter=None, max_workers=10):
    """Process all URLs from JSON file, with optional text filter"""
    import json
    import time

    print(f"📄 Processing JSON file: {json_filename}")
    if reverse_order:
        print("🔄 Will process items in reverse order")
    if text_filter:
        print(f"🔍 Will filter items by text: '{text_filter}'")

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

    print(f"🎵 Found {len(audio_items)} audio items to download (before text filter)")

    # Apply text filter if specified
    if text_filter:
        keywords = [w.strip().lower() for w in text_filter.split() if w.strip()]
        def title_matches(title):
            t = title.lower()
            return all(word in t for word in keywords)
        filtered_items = [item for item in audio_items if title_matches(item.get('title', ''))]
        print(f"🔍 {len(filtered_items)} items match all keywords: {keywords}")
        audio_items = filtered_items

    if not audio_items:
        print("❌ No audio items found in JSON file (after filtering)")
        sys.exit(1)

    # Apply skip count if specified
    if skip_count > 0:
        if skip_count >= len(audio_items):
            print(f"❌ Error: skip count ({skip_count}) is >= total items ({len(audio_items)})")
            sys.exit(1)
        audio_items = audio_items[skip_count:]
        print(f"⏭️  Skipped first {skip_count} items, {len(audio_items)} remaining")

    # Apply reverse order if requested
    if reverse_order:
        audio_items = list(reversed(audio_items))
        print("🔄 Audio items order reversed")

    # Confirm before starting bulk download
    order_text = " (in reverse order)" if reverse_order else ""
    skip_text = f" (skipping first {skip_count})" if skip_count > 0 else ""
    # response = input(f"\n⚠️  Ready to download {len(audio_items)} audio items{order_text}{skip_text}. Continue? (y/N): ")
    # if response.lower() not in ['y', 'yes']:
    #     print("❌ Download cancelled by user")
    #     sys.exit(0)

    # Process each URL
    successful = 0
    failed = 0
    start_time = time.time()

    print(f"\n🚀 Starting bulk download of {len(audio_items)} items...")
    print("=" * 60)

    for i, item in enumerate(audio_items, 1):
        url = item.get('url')
        title = item.get('title', 'Unknown')

        # Calculate actual position (taking skip_count into account)
        actual_position = i + skip_count
        total_original = len(audio_items) + skip_count

        print(f"\n\n\n[{actual_position}/{total_original}] Processing: {title[:60]}...")
        print(f"URL: {url}")

        try:
            success = process_single_url(url, reverse_order, show_header=False, max_workers=max_workers)
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

def process_single_url(audio_url, reverse_order=False, show_header=True, max_workers=10):
    """Process a single URL"""
    if show_header:
        print(f"🎯 Target URL: {audio_url}")
        if reverse_order:
            print("� Reverse order mode enabled")
        print()

    # Try to auto-load cookies from curl_cmd.txt first
    auto_cookies, auto_nonce, curl_action, manual_wpcp, curl_headers = load_cookies_from_curl()

    if auto_cookies and auto_nonce:
        print(f"🔄 Auto-loaded cookies from curl_cmd.txt")
        if curl_action:
            if curl_action == 'shareonedrive-get-playlist':
                print(f"✅ Perfect! Found audio download nonce")
            else:
                print(f"⚠️  Warning: Nonce is for '{curl_action}', not 'shareonedrive-get-playlist'")
                print(f"   You need to capture audio play request, not page load request")
        
        # Use all cookies as captured (site's WAF also requires non-wordpress
        # cookies like _secure_session / wp_lang to be present, not just the
        # wordpress_/WPCP_/cf_clearance ones)
        cookies_dict = dict(auto_cookies)
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
    
    success = downloader.download_from_url(audio_url, cookies_dict, ajax_nonce, reverse_order, manual_wpcp=manual_wpcp, extra_headers=curl_headers, max_workers=max_workers)
    
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