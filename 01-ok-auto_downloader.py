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
from browser_session_downloader import BrowserSessionDownloader

def main():
    """Main function with command line argument support"""
    
    print("🎵 Auto Audio Downloader for sachtienganhhanoi.com")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("❌ Error: No input provided")
        print("\nUsage:")
        print(f"    python {os.path.basename(__file__)} <audio_page_url>")
        print(f"    python {os.path.basename(__file__)} file=<json_filename>")
        print("\nExamples:")
        print("    python auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/")
        print("    python auto_downloader.py file=ALL_AUDIO_ITEMS_5879_items.json")
        sys.exit(1)
    
    argument = sys.argv[1]
    
    # Check if it's a file parameter
    if argument.startswith('file='):
        json_filename = argument[5:]  # Remove 'file=' prefix
        process_json_file(json_filename)
    else:
        # Single URL mode
        audio_url = argument
        
        # Validate URL
        if not audio_url.startswith('https://sachtienganhhanoi.com/'):
            print(f"❌ Error: Invalid URL. Must start with 'https://sachtienganhhanoi.com/'")
            print(f"   Provided: {audio_url}")
            sys.exit(1)
        
        process_single_url(audio_url)

def process_json_file(json_filename):
    """Process all URLs from JSON file"""
    import json
    import time
    
    print(f"📄 Processing JSON file: {json_filename}")
    
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
    
    # Confirm before starting bulk download
    response = input(f"\n⚠️  Ready to download {len(audio_items)} audio items. Continue? (y/N): ")
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
            success = process_single_url(url, show_header=False)
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

def process_single_url(audio_url, show_header=True):
    """Process a single URL"""
    if show_header:
        print(f"🎯 Target URL: {audio_url}")
        print(f"🔐 Using browser cookies")
        print(f"🔑 Using stored nonce")
        print()
    
    # Working cookies and nonce from browser session
    # Note: Update these if they expire (usually every few hours/days)
    cookies_dict = {
        'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
        'WPCP_UUID': '1820fbed-abf7-47e7-aab2-117f2564139c',
        'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
        'cf_clearance': '2XL5jmOApKVYAMAF7tuglnjSuS5UBN32ds9Qr2cNbN0-1758424117-1.2.1.1-Ni9yBBVKZ7qFGbJRIZZy92sQEM9HiRkjECcwC0bXsi23qg30X1z0wm9iNdmg83py9CMes0C6O1bw8wS_qg04LMNHj7t07Esm9qABY5aqCh51lpa3tNbumRtHJMLfK1JbwkKKm4mVkxMQbKQCtwZ9OSWapmYn5fuBKsCTTyHxkmIc.dgDtipXAsGOTaFoPc6wa_qL5YgF44yvUfShMndd6IBGIYEU_Jbx9XMSNYUz5Ao',
    }
    
    ajax_nonce = '4a9c170df5'
    
    # Working cookies and nonce from browser session
    # Note: Update these if they expire (usually every few hours/days)
    cookies_dict = {
        'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
        'WPCP_UUID': '1820fbed-abf7-47e7-aab2-117f2564139c',
        'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
        'cf_clearance': '2XL5jmOApKVYAMAF7tuglnjSuS5UBN32ds9Qr2cNbN0-1758424117-1.2.1.1-Ni9yBBVKZ7qFGbJRIZZy92sQEM9HiRkjECcwC0bXsi23qg30X1z0wm9iNdmg83py9CMes0C6O1bw8wS_qg04LMNHj7t07Esm9qABY5aqCh51lpa3tNbumRtHJMLfK1JbwkKKm4mVkxMQbKQCtwZ9OSWapmYn5fuBKsCTTyHxkmIc.dgDtipXAsGOTaFoPc6wa_qL5YgF44yvUfShMndd6IBGIYEU_Jbx9XMSNYUz5Ao',
    }
    
    ajax_nonce = '4a9c170df5'
    
    # Create downloader and start process
    downloader = BrowserSessionDownloader()
    
    if show_header:
        print("🚀 Starting download process...")
    
    success = downloader.download_from_url(audio_url, cookies_dict, ajax_nonce)
    
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