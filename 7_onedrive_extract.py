import json
import re
import urllib.parse

def extract_onedrive_urls():
    """Extract and decode OneDrive URLs from the JSON data"""
    
    print("🔍 EXTRACTING ONEDRIVE DIRECT URLs")  
    print("=" * 50)
    
    # Load JSON
    with open('curl_ajax_response.json', 'r', encoding='utf-8') as f:
        audio_data = json.load(f)
    
    # Check first few items to understand the structure
    first_items = list(audio_data.items())[:3]
    
    for track_name, track_info in first_items:
        print(f"\nTrack: {track_name}")
        print(f"Title: {track_info.get('title')}")
        print(f"Size: {track_info.get('size'):,} bytes")
        print(f"ID: {track_info.get('id')}")
        
        # Look at poster URL which contains OneDrive info
        poster_url = track_info.get('poster', '')
        if poster_url:
            print(f"Poster URL: {poster_url[:100]}...")
            
            # Extract the docid parameter which contains the actual OneDrive URL
            docid_match = re.search(r'docid=([^&]+)', poster_url)
            if docid_match:
                encoded_docid = docid_match.group(1)
                decoded_docid = urllib.parse.unquote(encoded_docid)
                print(f"Decoded OneDrive URL: {decoded_docid}")
                
                # Extract the actual file URL from OneDrive
                # Format: https://my.microsoftpersonalcontent.com/_api/v2.0/drives/{drive}/items/{item_id}
                if 'drives/' in decoded_docid and 'items/' in decoded_docid:
                    # Extract drive and item info
                    drive_match = re.search(r'drives/([^/]+)', decoded_docid)
                    item_match = re.search(r'items/([^?]+)', decoded_docid)
                    
                    if drive_match and item_match:
                        drive_id = drive_match.group(1)
                        item_id = item_match.group(1)
                        print(f"Drive ID: {drive_id}")
                        print(f"Item ID: {item_id}")
                        
                        # Try to construct direct download URL
                        direct_url = f"https://my.microsoftpersonalcontent.com/_api/v2.0/drives/{drive_id}/items/{item_id}/content"
                        print(f"Potential direct URL: {direct_url}")
                        
        print("-" * 40)

def try_onedrive_direct_download():
    """Try to download directly from OneDrive URLs"""
    
    print(f"\n{'='*50}")
    print("🎯 TESTING ONEDRIVE DIRECT DOWNLOAD")
    print(f"{'='*50}")
    
    import requests
    
    # Load JSON
    with open('curl_ajax_response.json', 'r', encoding='utf-8') as f:
        audio_data = json.load(f)
    
    # Get first item
    first_key = list(audio_data.keys())[0]
    first_item = audio_data[first_key]
    
    poster_url = first_item.get('poster', '')
    
    if poster_url:
        # Extract OneDrive URL from poster
        docid_match = re.search(r'docid=([^&]+)', poster_url)
        if docid_match:
            encoded_docid = docid_match.group(1)
            decoded_docid = urllib.parse.unquote(encoded_docid)
            
            print(f"Original OneDrive API URL: {decoded_docid}")
            
            # Try the original URL first (might work for thumbnails)
            session = requests.Session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'Accept': 'audio/mpeg,audio/*,*/*'
            }
            
            print("\n1. Testing original OneDrive URL...")
            try:
                response = session.get(decoded_docid, headers=headers, timeout=10)
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('Content-Type')}")
                print(f"   Content-Length: {response.headers.get('Content-Length', 'Not specified')}")
                
                if response.content:
                    print(f"   Response size: {len(response.content)} bytes")
                    
                    # Check if it's audio or other content
                    try:
                        text_content = response.content.decode('utf-8')
                        print(f"   Content (text): {text_content[:100]}...")
                    except UnicodeDecodeError:
                        print(f"   Content appears to be binary data")
                        print(f"   First 20 bytes (hex): {response.content[:20].hex()}")
                        
                        # Save sample
                        with open('onedrive_direct_sample.bin', 'wb') as f:
                            f.write(response.content)
                        print(f"   Sample saved to onedrive_direct_sample.bin")
                
            except Exception as e:
                print(f"   Error: {e}")
            
            # Try to modify URL for direct content download
            if '/items/' in decoded_docid:
                content_url = decoded_docid.split('?')[0] + '/content'
                print(f"\n2. Testing modified content URL...")
                print(f"   URL: {content_url}")
                
                try:
                    response = session.get(content_url, headers=headers, timeout=10)
                    print(f"   Status: {response.status_code}")
                    print(f"   Content-Type: {response.headers.get('Content-Type')}")
                    print(f"   Content-Length: {response.headers.get('Content-Length', 'Not specified')}")
                    
                    if response.content:
                        print(f"   Response size: {len(response.content)} bytes")
                        
                        # Check if it's audio
                        try:
                            text_content = response.content.decode('utf-8')
                            print(f"   Content (text): {text_content[:100]}...")
                        except UnicodeDecodeError:
                            print(f"   SUCCESS! Content appears to be binary audio data!")
                            print(f"   First 20 bytes (hex): {response.content[:20].hex()}")
                            
                            # Save sample
                            with open('onedrive_content_sample.mp3', 'wb') as f:
                                f.write(response.content)
                            print(f"   Audio sample saved to onedrive_content_sample.mp3")
                            
                            return True
                    
                except Exception as e:
                    print(f"   Error: {e}")
    
    return False

def create_onedrive_download_list():
    """Create a list of direct OneDrive URLs for all tracks"""
    
    print(f"\n{'='*50}")
    print("📋 CREATING ONEDRIVE DOWNLOAD LIST")
    print(f"{'='*50}")
    
    # Load JSON
    with open('curl_ajax_response.json', 'r', encoding='utf-8') as f:
        audio_data = json.load(f)
    
    onedrive_urls = []
    
    for track_name, track_info in audio_data.items():
        title = track_info.get('title', 'Unknown')
        size = track_info.get('size', 0)
        poster_url = track_info.get('poster', '')
        
        if poster_url:
            # Extract OneDrive URL
            docid_match = re.search(r'docid=([^&]+)', poster_url)
            if docid_match:
                encoded_docid = docid_match.group(1)
                decoded_docid = urllib.parse.unquote(encoded_docid)
                
                # Create content URL
                if '/items/' in decoded_docid:
                    content_url = decoded_docid.split('?')[0] + '/content'
                    onedrive_urls.append({
                        'title': title,
                        'size': size,
                        'track_path': track_name,
                        'onedrive_url': content_url
                    })
    
    print(f"Found {len(onedrive_urls)} OneDrive URLs")
    
    # Save to file
    with open('onedrive_urls.json', 'w', encoding='utf-8') as f:
        json.dump(onedrive_urls, f, indent=2, ensure_ascii=False)
    
    # Also create a simple text list
    with open('onedrive_urls.txt', 'w', encoding='utf-8') as f:
        f.write("# Now I Know 2 Audio - OneDrive Direct URLs\n")
        f.write(f"# Total tracks: {len(onedrive_urls)}\n\n")
        
        for item in onedrive_urls:
            f.write(f"# {item['title']} ({item['size']:,} bytes)\n")
            f.write(f"{item['onedrive_url']}\n\n")
    
    print("📄 OneDrive URLs saved to:")
    print("   - onedrive_urls.json (structured data)")
    print("   - onedrive_urls.txt (simple list)")
    
    return onedrive_urls

if __name__ == "__main__":
    extract_onedrive_urls()
    
    if try_onedrive_direct_download():
        print("\n🎉 OneDrive direct download works! Creating full list...")
        create_onedrive_download_list()
    else:
        print("\n❌ OneDrive direct download doesn't work")
        print("Creating list anyway for manual testing...")
        create_onedrive_download_list()