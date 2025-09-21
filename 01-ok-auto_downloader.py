#!/usr/bin/env python3
"""
Auto Audio Downloader for sachtienganhhanoi.com
===============================================
Automatically downloads audio files from any audio page using command line arguments.

Usage:
    python auto_downloader.py <audio_page_url>
    
Example:
    python auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/
    python auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-3-student-book-audio-cd/
    
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
        print("❌ Error: No URL provided")
        print("\nUsage:")
        print(f"    python {os.path.basename(__file__)} <audio_page_url>")
        print("\nExamples:")
        print("    python auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/")
        print("    python auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-3-student-book-audio-cd/")
        sys.exit(1)
    
    audio_url = sys.argv[1]
    
    # Validate URL
    if not audio_url.startswith('https://sachtienganhhanoi.com/'):
        print(f"❌ Error: Invalid URL. Must start with 'https://sachtienganhhanoi.com/'")
        print(f"   Provided: {audio_url}")
        sys.exit(1)
    
    # Working cookies and nonce from browser session
    # Note: Update these if they expire (usually every few hours/days)
    cookies_dict = {
        'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
        'WPCP_UUID': '1820fbed-abf7-47e7-aab2-117f2564139c',
        'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
        'cf_clearance': 'I1i63KhgLPNUKKPECrRj9nP6FnBCP3ZeColxfnsFVAM-1758331351-1.2.1.1-NTTIQrqghh4ouAu95VvVnWzqrKQfgo17qpGutEcbR4BMGKto.jmFv6yYr6Kq.AFuX6OR3TcUeu_QdJJlct2TJxRcWs2QPGPWqJe_C6g7o5pVMLR0a48Dh_HPOLAW9tk0Y9qUaMt2fyROlLKoOdfUvHUsZPgmj7i53AS5r53GD9IKnbBNsCq.txAOzoY4oKqIfwXGZE3BU_XGwU6Gnj2Y6YWuuunAcVbmQOIirFC8MWg'
    }
    
    ajax_nonce = 'e5b9dce6c4'
    
    print(f"🎯 Target URL: {audio_url}")
    print(f"🔐 Using {len(cookies_dict)} browser cookies")
    print(f"🔑 Using nonce: {ajax_nonce}")
    print()
    
    # Create downloader and start process
    downloader = BrowserSessionDownloader()
    
    print("🚀 Starting download process...")
    success = downloader.download_from_url(audio_url, cookies_dict, ajax_nonce)
    
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