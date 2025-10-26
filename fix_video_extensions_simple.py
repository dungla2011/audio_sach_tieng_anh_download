#!/usr/bin/env python3
"""
Fix Video Extensions (No Dependencies Version)
===============================================
Scan G:/Download_TiengAnhAudio and rename .mp3 files that are actually MP4 videos to .mp4

This script uses file size and magic bytes to detect MP4 files without external libraries.

Usage:
    python fix_video_extensions_simple.py
"""

import os

def is_video_file(filepath):
    """Check if file is a video using magic bytes and file size"""
    try:
        # Get file size first - videos are typically larger
        file_size = os.path.getsize(filepath)
        
        # Read first 32 bytes to check for MP4 signature
        with open(filepath, 'rb') as f:
            header = f.read(32)
        
        # MP4 signatures:
        # - 'ftyp' typically at bytes 4-8
        # - Common ftyp brands: 'isom', 'mp42', 'mp41', 'M4V ', 'avc1'
        if b'ftyp' in header[:12]:
            # Check for video-specific brands
            if any(brand in header for brand in [b'mp42', b'mp41', b'isom', b'M4V', b'avc1']):
                return True
        
        # Additional check: MP4 with 'moov' atom
        if b'moov' in header:
            return True
        
        # Check for other video signatures
        # AVI: 'RIFF' + 'AVI '
        if header.startswith(b'RIFF') and b'AVI ' in header[:20]:
            return True
        
        # MOV/QuickTime
        if b'moov' in header or b'mdat' in header or b'wide' in header:
            return True
        
        # Heuristic: if file is very large (> 10MB), it might be video
        # But this is unreliable, so we'll skip it
        
        return False
        
    except Exception as e:
        print(f"    ⚠️  Error checking file: {e}")
        return False

def scan_and_fix_extensions(base_dir, dry_run=False):
    """Scan directory and fix .mp3 files that are actually videos"""
    print(f"🔍 Scanning directory: {base_dir}")
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be renamed")
    print("=" * 60)
    
    if not os.path.exists(base_dir):
        print(f"❌ Directory not found: {base_dir}")
        return
    
    fixed_count = 0
    checked_count = 0
    video_files = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_dir):
        # Filter only .mp3 files
        mp3_files = [f for f in files if f.lower().endswith('.mp3')]
        
        if not mp3_files:
            continue
        
        relative_path = os.path.relpath(root, base_dir)
        print(f"\n📁 {relative_path}")
        
        for filename in mp3_files:
            filepath = os.path.join(root, filename)
            checked_count += 1
            file_size = os.path.getsize(filepath)
            
            print(f"  [{checked_count}] {filename} ({file_size:,} bytes)...", end=" ")
            
            # Check if it's actually a video
            if is_video_file(filepath):
                # Rename to .mp4
                new_filename = filename[:-4] + '.mp4'  # Remove .mp3, add .mp4
                new_filepath = os.path.join(root, new_filename)
                
                video_files.append({
                    'old': filepath,
                    'new': new_filepath,
                    'name': filename,
                    'new_name': new_filename,
                    'size': file_size
                })
                
                if not dry_run:
                    try:
                        os.rename(filepath, new_filepath)
                        print(f"✅ RENAMED → {new_filename}")
                        fixed_count += 1
                    except Exception as e:
                        print(f"❌ ERROR: {e}")
                else:
                    print(f"🔍 WOULD RENAME → {new_filename}")
                    fixed_count += 1
            else:
                print("✓ OK (audio)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"📝 Total .mp3 files checked: {checked_count}")
    print(f"🎥 Video files found: {fixed_count}")
    print(f"🎵 Audio files: {checked_count - fixed_count}")
    
    if video_files:
        print(f"\n📋 Video files detected:")
        for vf in video_files:
            print(f"  • {vf['name']} → {vf['new_name']} ({vf['size']:,} bytes)")
    
    if dry_run and video_files:
        print(f"\n⚠️  This was a DRY RUN. Run with actual rename? (y/n): ", end="")
        response = input().strip().lower()
        if response == 'y':
            print("\n🔄 Running actual rename...")
            for vf in video_files:
                try:
                    os.rename(vf['old'], vf['new'])
                    print(f"  ✅ {vf['name']} → {vf['new_name']}")
                except Exception as e:
                    print(f"  ❌ {vf['name']}: {e}")
            print("✅ Done!")

def main():
    """Main function"""
    base_dir = "G:/Download_TiengAnhAudio"
    
    print("🎥 Video Extension Fixer (Simple Version)")
    print("=" * 60)
    print(f"Target directory: {base_dir}")
    print("\nThis script will:")
    print("  1. Scan all .mp3 files recursively")
    print("  2. Check file headers to detect MP4 videos")
    print("  3. Rename .mp3 → .mp4 for video files")
    print()
    
    # Offer dry run first
    response = input("Start with dry run (preview only)? (y/n): ").strip().lower()
    dry_run = (response == 'y')
    
    scan_and_fix_extensions(base_dir, dry_run=dry_run)
    
    print("\n✅ Complete!")

if __name__ == "__main__":
    main()
