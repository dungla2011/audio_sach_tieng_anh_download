import requests
import json
import os
import time
from urllib.parse import urlparse, unquote
import re

def create_safe_filename(name):
    """Create a safe filename from the given name"""
    # Remove invalid characters for Windows filenames
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Replace forward slashes with underscores
    safe_name = safe_name.replace('/', '_')
    return safe_name

def download_audio_files():
    """Download all audio files from the JSON data"""
    
    print("🎵 AUDIO DOWNLOADER FOR NOW I KNOW 2")
    print("=" * 50)
    
    # Load the JSON data
    try:
        with open('curl_ajax_response.json', 'r', encoding='utf-8') as f:
            audio_data = json.load(f)
        print(f"✅ Loaded {len(audio_data)} audio files from JSON")
    except FileNotFoundError:
        print("❌ curl_ajax_response.json not found. Run the previous script first.")
        return
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return
    
    # Create session with the same cookies as before
    session = requests.Session()
    
    # Set cookies from curl (same as previous script)
    cookies = {
        'wordpress_sec_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cb984eebd3a05e7b131895605fd52653484673051cce89fafd0b5e85f5e9e1fe0',
        'wordpress_logged_in_5a61016ccd1690fb96ec8b28ebc99c52': 'dungla2011%7C1759247431%7CkUEVdPHnEvOIwExtb5NpkysLyWiwLmt9N61glLX18Af%7Cd6fe7e2f45f8ee1a6a8177eebcba9d856ccaef8918d9ba93a0d80eb22bc1e565',
        'cf_clearance': 'I1i63KhgLPNUKKPECrRj9nP6FnBCP3ZeColxfnsFVAM-1758331351-1.2.1.1-NTTIQrqghh4ouAu95VvVnWzqrKQfgo17qpGutEcbR4BMGKto.jmFv6yYr6Kq.AFuX6OR3TcUeu_QdJJlct2TJxRcWs2QPGPWqJe_C6g7o5pVMLR0a48Dh_HPOLAW9tk0Y9qUaMt2fyROlLKoOdfUvHUsZPgmj7i53AS5r53GD9IKnbBNsCq.txAOzoY4oKqIfwXGZE3BU_XGwU6Gnj2Y6YWuuunAcVbmQOIirFC8MWg'
    }
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='sachtienganhhanoi.com')
    
    # Set headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': 'audio/mpeg,audio/*,*/*',
        'Referer': 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/',
        'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7'
    }
    
    # Create download directories
    base_dir = "Now_I_Know_2_Audio"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"📁 Created directory: {base_dir}")
    
    # Statistics
    total_files = len(audio_data)
    downloaded = 0
    failed = 0
    skipped = 0
    
    print(f"\n🚀 Starting download of {total_files} files...")
    print("-" * 50)
    
    # Process each audio file
    for i, (track_path, track_info) in enumerate(audio_data.items(), 1):
        try:
            title = track_info.get('title', 'Unknown')
            download_url = track_info.get('download', '')
            size = track_info.get('size', 0)
            folder = track_info.get('folder', '')
            
            if not download_url:
                print(f"{i:3d}/{total_files} ❌ No download URL for {title}")
                failed += 1
                continue
            
            # Create safe filename
            safe_title = create_safe_filename(title)
            if not safe_title.endswith('.mp3'):
                safe_title += '.mp3'
            
            # Create subdirectory based on folder
            if folder:
                safe_folder = create_safe_filename(folder)
                file_dir = os.path.join(base_dir, safe_folder)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
            else:
                file_dir = base_dir
            
            file_path = os.path.join(file_dir, safe_title)
            
            # Check if file already exists
            if os.path.exists(file_path):
                existing_size = os.path.getsize(file_path)
                if existing_size == size:
                    print(f"{i:3d}/{total_files} ⏭️  Already exists: {safe_title}")
                    skipped += 1
                    continue
            
            print(f"{i:3d}/{total_files} 📥 Downloading: {title}")
            print(f"          Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
            print(f"          URL: {download_url[:80]}...")
            
            # Download the file
            start_time = time.time()
            response = session.get(download_url, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                # Save the file
                with open(file_path, 'wb') as f:
                    downloaded_size = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                
                end_time = time.time()
                duration = end_time - start_time
                speed = downloaded_size / (1024 * 1024) / duration if duration > 0 else 0
                
                print(f"          ✅ Downloaded in {duration:.1f}s ({speed:.1f} MB/s)")
                downloaded += 1
                
                # Verify file size
                actual_size = os.path.getsize(file_path)
                if actual_size != size:
                    print(f"          ⚠️  Size mismatch: expected {size:,}, got {actual_size:,}")
                
            else:
                print(f"          ❌ Failed: HTTP {response.status_code}")
                failed += 1
                
                # Save error response for debugging
                with open(f'error_{i}.txt', 'w', encoding='utf-8') as f:
                    f.write(f"URL: {download_url}\n")
                    f.write(f"Status: {response.status_code}\n")
                    f.write(f"Response: {response.text[:500]}\n")
            
            # Small delay to be respectful to the server
            time.sleep(0.5)
            
        except requests.exceptions.Timeout:
            print(f"{i:3d}/{total_files} ❌ Timeout downloading {title}")
            failed += 1
        except requests.exceptions.RequestException as e:
            print(f"{i:3d}/{total_files} ❌ Network error downloading {title}: {e}")
            failed += 1
        except Exception as e:
            print(f"{i:3d}/{total_files} ❌ Unexpected error downloading {title}: {e}")
            failed += 1
    
    # Final statistics
    print("\n" + "=" * 50)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 50)
    print(f"📁 Total files: {total_files}")
    print(f"✅ Downloaded: {downloaded}")
    print(f"⏭️  Skipped (already exists): {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📂 Files saved to: {os.path.abspath(base_dir)}")
    
    if downloaded > 0:
        print(f"\n🎉 Success! Downloaded {downloaded} audio files.")
    
    if failed > 0:
        print(f"\n⚠️  {failed} files failed to download. Check error_*.txt files for details.")

def create_download_list():
    """Create a text file with all download URLs for external download managers"""
    print("\n📋 Creating download list for external download managers...")
    
    try:
        with open('curl_ajax_response.json', 'r', encoding='utf-8') as f:
            audio_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return
    
    with open('download_urls.txt', 'w', encoding='utf-8') as f:
        f.write("# Now I Know 2 Audio Download URLs\n")
        f.write("# Generated by Python script\n")
        f.write(f"# Total files: {len(audio_data)}\n\n")
        
        for track_path, track_info in audio_data.items():
            title = track_info.get('title', 'Unknown')
            download_url = track_info.get('download', '')
            size = track_info.get('size', 0)
            
            if download_url:
                f.write(f"# {title} ({size:,} bytes)\n")
                f.write(f"{download_url}\n\n")
    
    print("📄 Download URLs saved to 'download_urls.txt'")
    print("   You can use this file with download managers like:")
    print("   - Internet Download Manager (IDM)")
    print("   - Free Download Manager (FDM)")
    print("   - JDownloader")
    print("   - aria2c")

if __name__ == "__main__":
    print("🎯 NOW I KNOW 2 AUDIO DOWNLOADER")
    print("=" * 50)
    
    # Ask user what they want to do
    print("Choose an option:")
    print("1. Download all files directly with Python")
    print("2. Create URL list for external download manager")
    print("3. Both")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice in ['1', '3']:
            download_audio_files()
        
        if choice in ['2', '3']:
            create_download_list()
            
        if choice not in ['1', '2', '3']:
            print("Invalid choice. Running direct download...")
            download_audio_files()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()