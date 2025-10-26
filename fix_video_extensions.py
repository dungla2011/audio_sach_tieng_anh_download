#!/usr/bin/env python3
"""
Fix Video Extensions
====================
Scan G:/Download_TiengAnhAudio and rename .mp3 files that are actually MP4 videos to .mp4

This script:
1. Recursively scans all folders in G:/Download_TiengAnhAudio
2. Checks each .mp3 file to see if it's actually a video (MP4)
3. Renames .mp3 to .mp4 if the file is a video

Usage:
    python fix_video_extensions.py
"""

import os
import magic  # python-magic library for file type detection

def is_video_file(filepath):
    """Check if file is a video using magic bytes"""
    try:
        # Using python-magic to detect file type
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(filepath)
        
        # Check if it's a video type
        return file_type.startswith('video/')
    except Exception as e:
        # Fallback: check first few bytes for MP4 signature
        try:
            with open(filepath, 'rb') as f:
                header = f.read(12)
                # MP4 files typically start with 'ftyp' at offset 4-8
                if b'ftyp' in header or b'moov' in header:
                    return True
        except:
            pass
        return False

def scan_and_fix_extensions(base_dir):
    """Scan directory and fix .mp3 files that are actually videos"""
    print(f"🔍 Scanning directory: {base_dir}")
    print("=" * 60)
    
    if not os.path.exists(base_dir):
        print(f"❌ Directory not found: {base_dir}")
        return
    
    fixed_count = 0
    checked_count = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_dir):
        # Filter only .mp3 files
        mp3_files = [f for f in files if f.lower().endswith('.mp3')]
        
        if not mp3_files:
            continue
        
        print(f"\n📁 Checking folder: {root}")
        
        for filename in mp3_files:
            filepath = os.path.join(root, filename)
            checked_count += 1
            
            print(f"  [{checked_count}] Checking: {filename}...", end=" ")
            
            # Check if it's actually a video
            if is_video_file(filepath):
                # Rename to .mp4
                new_filename = filename[:-4] + '.mp4'  # Remove .mp3, add .mp4
                new_filepath = os.path.join(root, new_filename)
                
                try:
                    os.rename(filepath, new_filepath)
                    print(f"✅ FIXED → {new_filename}")
                    fixed_count += 1
                except Exception as e:
                    print(f"❌ ERROR: {e}")
            else:
                print("✓ OK (audio)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"📝 Total .mp3 files checked: {checked_count}")
    print(f"✅ Files fixed (renamed to .mp4): {fixed_count}")
    print(f"✓  Files OK (actual audio): {checked_count - fixed_count}")

def main():
    """Main function"""
    base_dir = "G:/Download_TiengAnhAudio"
    
    print("🎥 Video Extension Fixer")
    print("=" * 60)
    print(f"Target directory: {base_dir}")
    print("\nThis script will:")
    print("  1. Scan all .mp3 files in the directory")
    print("  2. Check if they are actually MP4 videos")
    print("  3. Rename .mp3 → .mp4 for video files")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled by user")
        return
    
    scan_and_fix_extensions(base_dir)
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
