#!/usr/bin/env python3
"""
Universal Audio Downloader for sachtienganhhanoi.com
=====================================
This script can download audio files from any audio page on the website.
It requires you to manually provide cookies and nonce from Chrome DevTools.

Instructions:
1. Login to sachtienganhhanoi.com in Chrome
2. Go to the audio page you want to download
3. Open Chrome DevTools -> Network tab
4. Refresh the page and look for admin-ajax.php calls
5. Right-click on admin-ajax.php -> Copy -> Copy as cURL
6. Extract cookies and nonce from the cURL command
7. Update this script with your cookies and run it

Usage:
    python browser_session_downloader.py
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import unquote, urlparse
import time
import sys

class BrowserSessionDownloader:
    def __init__(self):
        self.session = requests.Session()
        
        # Headers from browser
        self.session.headers.update({
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        })
        
    def set_browser_cookies(self, cookies_dict):
        """Set cookies from browser session"""
        for name, value in cookies_dict.items():
            self.session.cookies.set(name, value, domain='sachtienganhhanoi.com')
        print(f"✅ Set {len(cookies_dict)} cookies from browser session")
        
    def extract_wpcp_data(self, audio_page_url):
        """Extract wpcp-container data from audio page"""
        print(f"🔍 Analyzing audio page: {audio_page_url}")
        
        response = self.session.get(audio_page_url)
        if response.status_code != 200:
            print(f"❌ Failed to access audio page: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all wpcp-module divs with required data attributes
        wpcp_modules = soup.find_all('div', {'class': lambda x: x and 'wpcp-module' in x and 'ShareoneDrive' in x})
        
        if not wpcp_modules:
            print("❌ No wpcp-module ShareoneDrive divs found on this page")
            return None
        
        valid_modules = []
        
        for i, module in enumerate(wpcp_modules, 1):
            data_token = module.get('data-token')
            data_account_id = module.get('data-account-id')
            data_drive_id = module.get('data-drive-id')
            
            if all([data_token, data_account_id, data_drive_id]):
                print(f"✅ Found wpcp module {i}:")
                print(f"   Token: {data_token}")
                print(f"   Account ID: {data_account_id}")
                print(f"   Drive ID: {data_drive_id}")
                
                valid_modules.append({
                    'token': data_token,
                    'account_id': data_account_id,
                    'drive_id': data_drive_id,
                    'module_number': i
                })
            else:
                print(f"⚠️  Module {i} missing required data attributes")
        
        if not valid_modules:
            print("❌ No valid modules with complete data attributes found")
            return None
        
        return valid_modules
    
    def get_playlist_data(self, wpcp_data, ajax_nonce, page_url):
        """Get playlist data using AJAX call with browser session data"""
        print("📡 Fetching playlist data...")
        
        ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
        
        # Prepare AJAX data (matching the working 3.py format)
        ajax_data = {
            'action': 'shareonedrive-get-playlist',
            'account_id': wpcp_data['account_id'],
            'drive_id': wpcp_data['drive_id'],
            'lastFolder': '',
            'sort': 'name:asc',
            'listtoken': wpcp_data['token'],
            'page_url': page_url,
            '_ajax_nonce': ajax_nonce
        }
        
        print(f"📤 AJAX Parameters:")
        print(f"   Action: {ajax_data['action']}")
        print(f"   Account ID: {ajax_data['account_id']}")
        print(f"   Drive ID: {ajax_data['drive_id']}")
        print(f"   Token: {ajax_data['listtoken']}")
        print(f"   Nonce: {ajax_data['_ajax_nonce']}")
        
        # Headers for AJAX request
        ajax_headers = {
            'origin': 'https://sachtienganhhanoi.com',
            'referer': page_url,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }
        
        # Make AJAX request
        response = self.session.post(ajax_url, data=ajax_data, headers=ajax_headers)
        
        print(f"📊 Response: {response.status_code} | Length: {len(response.text)} chars")
        
        if response.status_code != 200:
            print(f"❌ AJAX request failed: {response.status_code}")
            return None
        
        if not response.text.strip():
            print("❌ Empty response")
            return None
        
        try:
            playlist_data = response.json()
            if isinstance(playlist_data, dict):
                # Convert to format expected by download function
                # Check if this looks like a track-based playlist (Track 01, Track 02, etc.)
                if any(key for key in playlist_data.keys() if key.lower().startswith('track') or '/' in key):
                    files = []
                    for key, file_info in playlist_data.items():
                        if isinstance(file_info, dict) and not file_info.get('is_dir', False):
                            files.append({
                                'name': file_info.get('title', file_info.get('name', key)),
                                'size': file_info.get('size', 0),
                                'downloadUrl': file_info.get('download', file_info.get('downloadUrl', '')),
                                'id': file_info.get('id', ''),
                                'poster': file_info.get('poster', ''),
                                'source': file_info.get('source', '')
                            })
                    
                    print(f"✅ Found {len(files)} audio files")
                    return {'files': files}
                else:
                    print(f"✅ Found playlist data with keys: {list(playlist_data.keys())}")
                    return playlist_data
            else:
                print("❌ Invalid playlist data format")
                return None
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"Response preview: {response.text[:200]}...")
            return None
    
    def extract_onedrive_url(self, download_url):
        """Extract OneDrive direct download URL"""
        # Look for OneDrive URL in the download_url
        onedrive_pattern = r'https://[^"\']*1drv\.ms[^"\']*|https://[^"\']*onedrive[^"\']*'
        match = re.search(onedrive_pattern, download_url)
        
        if match:
            base_url = match.group()
            decoded_url = unquote(base_url)
            return decoded_url
        
        return download_url
    
    def safe_filename(self, filename):
        """Create safe filename for Windows"""
        name_without_ext = os.path.splitext(filename)[0]
        safe_chars = re.sub(r'[<>:"/\\|?*]', '_', name_without_ext)
        return safe_chars[:100]
    
    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"
    
    def download_files(self, playlist_data, page_title="Audio_Files"):
        """Download all audio files from playlist"""
        files = playlist_data.get('files', [])
        if not files:
            print("❌ No files found in playlist")
            return
        
        # Create download directory in Download folder
        safe_title = self.safe_filename(page_title)
        base_download_dir = "Download"
        download_dir = os.path.join(base_download_dir, safe_title)
        os.makedirs(download_dir, exist_ok=True)
        print(f"📁 Created directory: {download_dir}")
        
        print(f"🚀 Starting download of {len(files)} files...")
        print("-" * 50)
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, file_info in enumerate(files, 1):
            name = file_info.get('name', f'audio_{i}')
            safe_name = self.safe_filename(name)
            download_url = file_info.get('downloadUrl', '')
            file_size = file_info.get('size', 0)
            
            print(f"{i:3d}/{len(files)} 📥 Downloading: {safe_name}")
            print(f"          Size: {file_size:,} bytes ({self.format_size(file_size)})")
            
            if not download_url:
                print("          ❌ No download URL found")
                failed_downloads += 1
                continue
            
            # Extract OneDrive URL
            onedrive_url = self.extract_onedrive_url(download_url)
            
            # Try different URL variants
            url_variants = [
                onedrive_url,
                onedrive_url.replace('&download=1', '') + '&download=1',
                onedrive_url + ('&' if '?' in onedrive_url else '?') + 'download=1'
            ]
            
            downloaded = False
            for variant_num, url in enumerate(url_variants, 1):
                print(f"          Trying URL variant {variant_num}...")
                
                try:
                    start_time = time.time()
                    response = self.session.get(url, stream=True, timeout=30)
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/json' in content_type or 'text/html' in content_type:
                        print(f"          ⚪ Got {content_type}, not file content")
                        continue
                    
                    # Download file
                    file_path = os.path.join(download_dir, f"{safe_name}.mp3")
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    end_time = time.time()
                    download_time = end_time - start_time
                    actual_size = os.path.getsize(file_path)
                    
                    if actual_size > 0:
                        speed = actual_size / download_time / (1024*1024)  # MB/s
                        print(f"          ✅ Downloaded {actual_size:,} bytes in {download_time:.1f}s ({speed:.1f} MB/s)")
                        
                        # Verify file size
                        if file_size > 0:
                            if actual_size == file_size:
                                print(f"          ✅ Size match perfect!")
                            else:
                                print(f"          ⚠️  Size mismatch: expected {file_size:,}, got {actual_size:,}")
                        
                        successful_downloads += 1
                        downloaded = True
                        break
                    else:
                        print(f"          ❌ Downloaded file is empty")
                        os.remove(file_path)
                
                except Exception as e:
                    print(f"          ❌ Error: {str(e)}")
            
            if not downloaded:
                print(f"          ❌ Failed to download after trying all variants")
                failed_downloads += 1
        
        print("\n" + "=" * 50)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 50)
        print(f"📁 Total files: {len(files)}")
        print(f"✅ Downloaded: {successful_downloads}")
        print(f"❌ Failed: {failed_downloads}")
        print(f"📂 Files saved to: {os.path.abspath(download_dir)}")
        
        if successful_downloads == len(files):
            print(f"\n🎉 Success! Downloaded all {successful_downloads} audio files!")
        elif successful_downloads > 0:
            print(f"\n⚠️  Partial success: {successful_downloads}/{len(files)} files downloaded")
        else:
            print(f"\n❌ No files were downloaded successfully")
    
    def get_page_title(self, audio_page_url):
        """Extract page title for folder naming"""
        try:
            response = self.session.get(audio_page_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()
                
                # Remove various forms of "Sách tiếng Anh Hà Nội" (case insensitive)
                title = re.sub(r'\s*-\s*Sách [Tt]iếng [Aa]nh [Hh]à [Nn]ội\s*', '', title)
                title = re.sub(r'\s*\|\s*Sách [Tt]iếng [Aa]nh [Hh]à [Nn]ội\s*', '', title)
                title = re.sub(r'Sách [Tt]iếng [Aa]nh [Hh]à [Nn]ội\s*-?\s*', '', title)
                title = re.sub(r'\s*Sách [Tt]iếng [Aa]nh [Hh]à [Nn]ội\s*', '', title)
                
                # Remove "[Audio]" or "[AUDIO]" (case insensitive)
                title = re.sub(r'\[?[Aa][Uu][Dd][Ii][Oo]\]?\s*', '', title)
                
                # Remove "Audio " prefix
                title = title.replace('Audio ', '')
                
                # Clean up extra spaces and dashes
                title = re.sub(r'\s*-\s*$', '', title)  # Remove trailing dash
                title = re.sub(r'^\s*-\s*', '', title)  # Remove leading dash
                title = re.sub(r'\s+', ' ', title).strip()  # Normalize spaces
                
                return title
        except:
            pass
        
        # Fallback: extract from URL
        path = urlparse(audio_page_url).path
        return path.split('/')[-2] if path.endswith('/') else path.split('/')[-1]
    
    def download_from_url(self, audio_page_url, cookies_dict, ajax_nonce):
        """Complete workflow: set cookies -> extract data -> download files"""
        print("🎯 BROWSER SESSION AUDIO DOWNLOADER")
        print("=" * 50)
        
        # Step 1: Set browser cookies
        self.set_browser_cookies(cookies_dict)
        
        # Step 2: Extract wpcp data
        wpcp_modules = self.extract_wpcp_data(audio_page_url)
        if not wpcp_modules:
            return False
        
        # Step 3: Get page title for folder naming
        page_title = self.get_page_title(audio_page_url)
        
        # Step 4: Process each module
        overall_success = True
        
        for module_data in wpcp_modules:
            module_num = module_data.get('module_number', 1)
            print(f"\n📀 Processing Module {module_num}...")
            print("-" * 30)
            
            # Get playlist data for this module
            playlist_data = self.get_playlist_data(module_data, ajax_nonce, audio_page_url)
            if not playlist_data:
                print(f"❌ Failed to get playlist data for module {module_num}")
                overall_success = False
                continue
            
            # Create module-specific folder name
            if len(wpcp_modules) > 1:
                module_folder = f"{page_title}_Module_{module_num}"
            else:
                module_folder = page_title
            
            # Download files for this module
            self.download_files(playlist_data, module_folder)
        
        return overall_success

def get_cookies_and_nonce():
    """Interactive function to get cookies and nonce from user"""
    print("🔧 SETUP BROWSER SESSION DATA")
    print("=" * 50)
    print("Instructions:")
    print("1. Login to sachtienganhhanoi.com in Chrome")
    print("2. Go to your target audio page")
    print("3. Open Chrome DevTools (F12) -> Network tab")
    print("4. Refresh the page")
    print("5. Look for 'admin-ajax.php' request")
    print("6. Right-click -> Copy -> Copy as cURL")
    print("7. Extract cookies and nonce from the cURL command")
    print()
    
    # Pre-filled example from working session
    example_cookies = {
        'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
        'WPCP_UUID': '1820fbed-abf7-47e7-aab2-117f2564139c',
        'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
        'cf_clearance': 'I1i63KhgLPNUKKPECrRj9nP6FnBCP3ZeColxfnsFVAM-1758331351-1.2.1.1-NTTIQrqghh4ouAu95VvVnWzqrKQfgo17qpGutEcbR4BMGKto.jmFv6yYr6Kq.AFuX6OR3TcUeu_QdJJlct2TJxRcWs2QPGPWqJe_C6g7o5pVMLR0a48Dh_HPOLAW9tk0Y9qUaMt2fyROlLKoOdfUvHUsZPgmj7i53AS5r53GD9IKnbBNsCq.txAOzoY4oKqIfwXGZE3BU_XGwU6Gnj2Y6YWuuunAcVbmQOIirFC8MWg'
    }
    
    example_nonce = 'e5b9dce6c4'
    
    print("⚠️  Note: The example cookies below are from a previous session and may be expired.")
    print("For best results, get fresh cookies from your current browser session.")
    print()
    
    use_example = input("Use example cookies? (y/n): ").strip().lower()
    
    if use_example == 'y':
        return example_cookies, example_nonce
    else:
        print("\n📝 Please provide your browser session data:")
        print("Enter cookies as Python dict format:")
        print("Example: {'cookie_name': 'cookie_value', 'another_cookie': 'another_value'}")
        
        cookies_input = input("Cookies dict: ").strip()
        nonce_input = input("AJAX nonce: ").strip()
        
        try:
            cookies_dict = eval(cookies_input)
            return cookies_dict, nonce_input
        except:
            print("❌ Invalid cookies format. Using example cookies.")
            return example_cookies, example_nonce

def main():
    """Main function"""
    downloader = BrowserSessionDownloader()
    
    # Get browser session data
    cookies_dict, ajax_nonce = get_cookies_and_nonce()
    
    # Get URL from user
    default_url = "https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/"
    
    print(f"\n🎵 Browser Session Audio Downloader")
    print("=" * 60)
    print(f"Default URL: {default_url}")
    
    user_input = input(f"\nEnter audio page URL (press Enter for default): ").strip()
    audio_url = user_input if user_input else default_url
    
    print(f"\n🎯 Will download audio from: {audio_url}")
    print(f"🔐 Using {len(cookies_dict)} cookies and nonce: {ajax_nonce}")
    
    # Start download process
    success = downloader.download_from_url(audio_url, cookies_dict, ajax_nonce)
    
    if success:
        print("\n✅ Download process completed!")
    else:
        print("\n❌ Download process failed!")

if __name__ == "__main__":
    main()