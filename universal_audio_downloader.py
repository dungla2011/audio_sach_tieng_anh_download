#!/usr/bin/env python3
"""
Universal Audio Downloader for sachtienganhhanoi.com
=====================================
This script can login and download audio files from any audio page on the website.
Just provide the audio page URL and it will automatically detect and download all files.

Usage:
    python universal_audio_downloader.py
    
Then enter the audio page URL when prompted.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import unquote, urlparse
import time
import sys

class UniversalAudioDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.login_nonce = None
        
    def login(self, email="dungla2011@gmail.com", password="11111111"):
        """Login to WordPress site"""
        print("🔑 Logging in to WordPress...")
        
        # Get login page
        login_url = "https://sachtienganhhanoi.com/my-account/"
        response = self.session.get(login_url)
        
        if response.status_code != 200:
            print(f"❌ Failed to access login page: {response.status_code}")
            return False
        
        # Parse login form
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', {'class': 'woocommerce-form-login'})
        
        if not form:
            print("❌ Login form not found")
            return False
        
        # Get nonce
        nonce_input = form.find('input', {'name': 'woocommerce-login-nonce'})
        if not nonce_input:
            print("❌ Login nonce not found")
            return False
        
        nonce = nonce_input.get('value')
        self.login_nonce = nonce  # Store login nonce for AJAX calls
        print(f"✅ Found login nonce: {nonce}")
        
        # Prepare login data
        login_data = {
            'username': email,
            'password': password,
            'woocommerce-login-nonce': nonce,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in'
        }
        
        # Submit login
        response = self.session.post(login_url, data=login_data)
        
        if response.status_code == 200 and "my-account" in response.url:
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    
    def extract_wpcp_data(self, audio_page_url):
        """Extract wpcp-container data from audio page"""
        print(f"🔍 Analyzing audio page: {audio_page_url}")
        
        response = self.session.get(audio_page_url)
        if response.status_code != 200:
            print(f"❌ Failed to access audio page: {response.status_code}")
            return None
        
        # Store page content for nonce extraction and current URL
        self.page_content = response.text
        self.current_page_url = audio_page_url
        
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
    
    def get_fresh_nonce(self):
        """Get fresh WordPress nonce for AJAX requests after login"""
        # Access login page to get fresh nonce
        login_url = "https://sachtienganhhanoi.com/my-account/"
        response = self.session.get(login_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for nonce in the logged-in page
            nonce_input = soup.find('input', {'name': 'woocommerce-login-nonce'})
            if nonce_input:
                fresh_nonce = nonce_input.get('value')
                print(f"🔄 Fresh nonce obtained: {fresh_nonce}")
                return fresh_nonce
        
        return None
        
    def get_playlist_data(self, wpcp_data):
        """Get playlist data using AJAX call"""
        print("📡 Fetching playlist data...")
        
        ajax_url = "https://sachtienganhhanoi.com/wp-admin/admin-ajax.php"
        
        # Get fresh nonce for AJAX request
        nonce = self.get_fresh_nonce()
        if nonce:
            print(f"✅ Using fresh nonce: {nonce}")
        else:
            print("⚠️  No nonce found - request may fail")
        
        # Prepare AJAX data
        ajax_data = {
            'action': 'shareonedrive-get-playlist',
            'token': wpcp_data['token'],
            'account_id': wpcp_data['account_id'],
            'drive_id': wpcp_data['drive_id']
        }
        
        # Add nonce if available
        if nonce:
            ajax_data['nonce'] = nonce
        
        # Set proper headers for AJAX request
        ajax_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://sachtienganhhanoi.com',
            'Referer': getattr(self, 'current_page_url', 'https://sachtienganhhanoi.com/'),
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Make AJAX request with proper headers
        response = self.session.post(ajax_url, data=ajax_data, headers=ajax_headers)
        
        if response.status_code != 200:
            print(f"❌ AJAX request failed: {response.status_code}")
            return None
        
        # Debug: show response content
        print(f"📝 Response content type: {response.headers.get('content-type', 'unknown')}")
        print(f"📝 Response length: {len(response.text)} chars")
        
        if len(response.text) < 500:
            print(f"📝 Response content: {response.text}")
        else:
            print(f"📝 Response preview: {response.text[:200]}...")
        
        # Check if response is empty
        if not response.text.strip():
            print("❌ Empty response - this module may not have any files")
            return None
        
        try:
            playlist_data = response.json()
            if isinstance(playlist_data, dict) and 'files' in playlist_data:
                print(f"✅ Found {len(playlist_data['files'])} audio files")
                return playlist_data
            else:
                print("❌ Invalid playlist data format")
                if isinstance(playlist_data, dict):
                    print(f"Available keys: {list(playlist_data.keys())}")
                return None
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            return None
    
    def extract_onedrive_url(self, download_url):
        """Extract OneDrive direct download URL"""
        # Look for OneDrive URL in the download_url
        onedrive_pattern = r'https://[^"\']*1drv\.ms[^"\']*|https://[^"\']*onedrive[^"\']*'
        match = re.search(onedrive_pattern, download_url)
        
        if match:
            base_url = match.group()
            # Decode URL
            decoded_url = unquote(base_url)
            return decoded_url
        
        return download_url
    
    def safe_filename(self, filename):
        """Create safe filename for Windows"""
        # Remove file extension if present
        name_without_ext = os.path.splitext(filename)[0]
        # Replace unsafe characters
        safe_chars = re.sub(r'[<>:"/\\|?*]', '_', name_without_ext)
        return safe_chars[:100]  # Limit length
    
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
                # Extract meaningful part of title
                title = title.replace(' - Sách Tiếng Anh Hà Nội', '')
                title = title.replace('Audio ', '')
                return title
        except:
            pass
        
        # Fallback: extract from URL
        path = urlparse(audio_page_url).path
        return path.split('/')[-2] if path.endswith('/') else path.split('/')[-1]
    
    def download_from_url(self, audio_page_url):
        """Complete workflow: login -> extract data -> download files"""
        print("🎯 UNIVERSAL AUDIO DOWNLOADER")
        print("=" * 50)
        
        # Step 1: Login
        if not self.login():
            return False
        
        # Step 2: Extract wpcp data (can be multiple modules)
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
            playlist_data = self.get_playlist_data(module_data)
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

def main():
    """Main function"""
    downloader = UniversalAudioDownloader()
    
    # Get URL from user
    default_url = "https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/"
    
    print("🎵 Universal Audio Downloader for sachtienganhhanoi.com")
    print("=" * 60)
    print(f"Default URL: {default_url}")
    
    user_input = input(f"\nEnter audio page URL (press Enter for default): ").strip()
    audio_url = user_input if user_input else default_url
    
    print(f"\n🎯 Will download audio from: {audio_url}")
    
    # Start download process
    success = downloader.download_from_url(audio_url)
    
    if success:
        print("\n✅ Download process completed!")
    else:
        print("\n❌ Download process failed!")

if __name__ == "__main__":
    main()