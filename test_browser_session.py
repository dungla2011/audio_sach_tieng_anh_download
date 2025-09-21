#!/usr/bin/env python3
"""
Quick test of browser session downloader with hardcoded values
"""

from browser_session_downloader import BrowserSessionDownloader

# Test with Now I Know 2 using cookies from 3.py
cookies_dict = {
    'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
    'WPCP_UUID': '1820fbed-abf7-47e7-aab2-117f2564139c',
    'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
    'cf_clearance': 'I1i63KhgLPNUKKPECrRj9nP6FnBCP3ZeColxfnsFVAM-1758331351-1.2.1.1-NTTIQrqghh4ouAu95VvVnWzqrKQfgo17qpGutEcbR4BMGKto.jmFv6yYr6Kq.AFuX6OR3TcUeu_QdJJlct2TJxRcWs2QPGPWqJe_C6g7o5pVMLR0a48Dh_HPOLAW9tk0Y9qUaMt2fyROlLKoOdfUvHUsZPgmj7i53AS5r53GD9IKnbBNsCq.txAOzoY4oKqIfwXGZE3BU_XGwU6Gnj2Y6YWuuunAcVbmQOIirFC8MWg'
}

ajax_nonce = 'e5b9dce6c4'
audio_url = "https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/"

print("🧪 Testing Browser Session Downloader")
print("=" * 50)

downloader = BrowserSessionDownloader()
success = downloader.download_from_url(audio_url, cookies_dict, ajax_nonce)

if success:
    print("\n✅ Test completed successfully!")
else:
    print("\n❌ Test failed!")