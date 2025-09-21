import requests
import json
import os
import time
import re
from urllib.parse import unquote

def download_from_onedrive_full_urls():
    """Download using complete OneDrive URLs with tempauth tokens"""
    
    print("🎯 DOWNLOADING FROM COMPLETE ONEDRIVE URLs")
    print("=" * 50)
    
    # Load JSON
    with open('curl_ajax_response.json', 'r', encoding='utf-8') as f:
        audio_data = json.load(f)
    
    # Create download directory
    base_dir = "Now_I_Know_2_Audio_OneDrive"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"📁 Created directory: {base_dir}")
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': 'audio/mpeg,audio/*,*/*',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    downloaded = 0
    failed = 0
    skipped = 0
    total = len(audio_data)
    
    print(f"🚀 Starting download of {total} files...")
    print("-" * 50)
    
    for i, (track_path, track_info) in enumerate(audio_data.items(), 1):
        try:
            title = track_info.get('title', 'Unknown')
            size = track_info.get('size', 0)
            poster_url = track_info.get('poster', '')
            folder = track_info.get('folder', '')
            
            if not poster_url:
                print(f"{i:3d}/{total} ❌ No poster URL for {title}")
                failed += 1
                continue
            
            # Extract complete OneDrive URL with tempauth
            docid_match = re.search(r'docid=([^&]+)', poster_url)
            if not docid_match:
                print(f"{i:3d}/{total} ❌ No docid found for {title}")
                failed += 1
                continue
            
            encoded_docid = docid_match.group(1)
            full_onedrive_url = unquote(encoded_docid)
            
            # Create safe filename
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
            if not safe_title.endswith('.mp3'):
                safe_title += '.mp3'
            
            # Create subdirectory
            if folder:
                safe_folder = re.sub(r'[<>:"/\\|?*]', '_', folder)
                file_dir = os.path.join(base_dir, safe_folder)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
            else:
                file_dir = base_dir
            
            file_path = os.path.join(file_dir, safe_title)
            
            # Check if exists
            if os.path.exists(file_path):
                existing_size = os.path.getsize(file_path)
                if existing_size == size:
                    print(f"{i:3d}/{total} ⏭️  Already exists: {safe_title}")
                    skipped += 1
                    continue
            
            print(f"{i:3d}/{total} 📥 Downloading: {title}")
            print(f"          Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
            
            # Try different URL variations
            urls_to_try = [
                # 1. Original full URL (metadata)
                full_onedrive_url,
                # 2. Content URL (direct file)
                full_onedrive_url.split('?')[0] + '/content?' + full_onedrive_url.split('?')[1] if '?' in full_onedrive_url else full_onedrive_url + '/content',
                # 3. Alternative content URL
                full_onedrive_url.replace('/items/', '/items/').replace('?', '/content?') if '/items/' in full_onedrive_url else None
            ]
            
            success = False
            for url_idx, test_url in enumerate(urls_to_try, 1):
                if not test_url:
                    continue
                    
                try:
                    print(f"          Trying URL variant {url_idx}...")
                    
                    start_time = time.time()
                    response = session.get(test_url, headers=headers, stream=True, timeout=30)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('Content-Type', '')
                        
                        # Check if it's actual audio content
                        if 'audio' in content_type or 'application/octet-stream' in content_type or 'binary' in content_type:
                            # This looks like audio file!
                            with open(file_path, 'wb') as f:
                                downloaded_size = 0
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded_size += len(chunk)
                            
                            end_time = time.time()
                            duration = end_time - start_time
                            speed = downloaded_size / (1024 * 1024) / duration if duration > 0 else 0
                            
                            print(f"          ✅ Downloaded {downloaded_size:,} bytes in {duration:.1f}s ({speed:.1f} MB/s)")
                            
                            # Verify size
                            if downloaded_size == size:
                                print(f"          ✅ Size match perfect!")
                            elif downloaded_size > 0:
                                print(f"          ⚠️  Size different: expected {size:,}, got {downloaded_size:,}")
                            
                            downloaded += 1
                            success = True
                            break
                            
                        elif 'json' in content_type:
                            # This is metadata, not the file
                            print(f"          ⚪ Got JSON metadata, not file content")
                            continue
                            
                        else:
                            # Try to download anyway and check content
                            first_chunk = next(response.iter_content(chunk_size=1024), b'')
                            if first_chunk:
                                # Check if it looks like audio (MP3 starts with ID3 or direct audio data)
                                if first_chunk.startswith(b'ID3') or first_chunk.startswith(b'\xff\xfb') or first_chunk.startswith(b'\xff\xf3'):
                                    print(f"          ✅ Detected audio content despite content-type: {content_type}")
                                    
                                    with open(file_path, 'wb') as f:
                                        f.write(first_chunk)
                                        downloaded_size = len(first_chunk)
                                        for chunk in response.iter_content(chunk_size=8192):
                                            if chunk:
                                                f.write(chunk)
                                                downloaded_size += len(chunk)
                                    
                                    end_time = time.time()
                                    duration = end_time - start_time
                                    speed = downloaded_size / (1024 * 1024) / duration if duration > 0 else 0
                                    
                                    print(f"          ✅ Downloaded {downloaded_size:,} bytes in {duration:.1f}s ({speed:.1f} MB/s)")
                                    downloaded += 1
                                    success = True
                                    break
                                else:
                                    print(f"          ❌ Content doesn't look like audio: {first_chunk[:20].hex()}")
                            else:
                                print(f"          ❌ No content received")
                    
                    elif response.status_code == 401:
                        print(f"          ❌ Unauthorized - token may be expired")
                    elif response.status_code == 404:
                        print(f"          ❌ Not found")
                    else:
                        print(f"          ❌ HTTP {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    print(f"          ❌ Timeout")
                except requests.exceptions.RequestException as e:
                    print(f"          ❌ Network error: {e}")
                except Exception as e:
                    print(f"          ❌ Unexpected error: {e}")
            
            if not success:
                print(f"          💥 All URL variants failed for {title}")
                failed += 1
            
            # Be respectful to server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"{i:3d}/{total} ❌ Unexpected error: {e}")
            failed += 1
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 ONEDRIVE DOWNLOAD SUMMARY")
    print("=" * 50)
    print(f"📁 Total files: {total}")
    print(f"✅ Downloaded: {downloaded}")
    print(f"⏭️  Skipped (already exists): {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📂 Files saved to: {os.path.abspath(base_dir)}")
    
    if downloaded > 0:
        print(f"\n🎉 Success! Downloaded {downloaded} audio files from OneDrive!")
    else:
        print(f"\n❌ No files were successfully downloaded.")
        print("This might be because:")
        print("- OneDrive tokens have expired")
        print("- Authentication is required")
        print("- URLs have changed format")

if __name__ == "__main__":
    download_from_onedrive_full_urls()