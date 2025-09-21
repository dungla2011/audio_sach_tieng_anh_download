#!/usr/bin/env python3
"""
Bulk Audio Downloader - Process ALL_AUDIO_ITEMS_5879_items.json
===============================================================
Reads the JSON file containing 5879+ audio items and downloads them all
using the 01-ok-auto_downloader.py script.

Usage:
    python bulk_download_all.py
    
Features:
    - Reads ALL_AUDIO_ITEMS_5879_items.json
    - Processes each audio URL using 01-ok-auto_downloader.py
    - Progress tracking and resume capability
    - Error handling and logging
    - Statistics reporting
"""

import json
import subprocess
import time
import os
import sys
from datetime import datetime

class BulkAudioDownloader:
    def __init__(self):
        self.json_file = "ALL_AUDIO_ITEMS_5879_items.json"
        self.downloader_script = "01-ok-auto_downloader.py"
        self.progress_file = "bulk_download_progress.json"
        self.log_file = f"bulk_download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        self.stats = {
            'total_items': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'current_item': 0
        }
        
        self.failed_urls = []
        self.successful_urls = []
        
    def load_audio_items(self):
        """Load audio items from JSON file"""
        try:
            if not os.path.exists(self.json_file):
                print(f"❌ JSON file not found: {self.json_file}")
                return None
            
            print(f"📂 Loading audio items from {self.json_file}...")
            with open(self.json_file, 'r', encoding='utf-8') as f:
                items = json.load(f)
            
            print(f"✅ Loaded {len(items)} audio items")
            self.stats['total_items'] = len(items)
            return items
            
        except Exception as e:
            print(f"❌ Error loading JSON file: {e}")
            return None
    
    def load_progress(self):
        """Load previous progress if exists"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                
                self.stats.update(progress.get('stats', {}))
                self.failed_urls = progress.get('failed_urls', [])
                self.successful_urls = progress.get('successful_urls', [])
                
                print(f"📋 Resumed from progress: {self.stats['processed']}/{self.stats['total_items']} items processed")
                return True
        except Exception as e:
            print(f"⚠️  Could not load progress: {e}")
        
        return False
    
    def save_progress(self):
        """Save current progress"""
        try:
            progress_data = {
                'stats': self.stats,
                'failed_urls': self.failed_urls,
                'successful_urls': self.successful_urls,
                'last_update': datetime.now().isoformat()
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️  Could not save progress: {e}")
    
    def log_message(self, message):
        """Log message to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        
        print(log_entry)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"⚠️  Could not write to log: {e}")
    
    def download_audio_page(self, url, title="", index=0):
        """Download a single audio page using 01-ok-auto_downloader.py"""
        try:
            # Prepare command
            cmd = [sys.executable, self.downloader_script, url]
            
            self.log_message(f"[{index}/{self.stats['total_items']}] Starting: {title[:50]}...")
            self.log_message(f"  URL: {url}")
            
            # Run the downloader
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5 minute timeout per download
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.stats['successful'] += 1
                self.successful_urls.append({
                    'url': url,
                    'title': title,
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                })
                self.log_message(f"  ✅ SUCCESS ({duration:.1f}s)")
                return True
            else:
                self.stats['failed'] += 1
                error_info = {
                    'url': url,
                    'title': title,
                    'error': result.stderr.strip() if result.stderr else 'Unknown error',
                    'stdout': result.stdout.strip() if result.stdout else '',
                    'return_code': result.returncode,
                    'timestamp': datetime.now().isoformat()
                }
                self.failed_urls.append(error_info)
                self.log_message(f"  ❌ FAILED (code {result.returncode}): {error_info['error'][:100]}")
                return False
                
        except subprocess.TimeoutExpired:
            self.stats['failed'] += 1
            error_info = {
                'url': url,
                'title': title,
                'error': 'Timeout (>5 minutes)',
                'timestamp': datetime.now().isoformat()
            }
            self.failed_urls.append(error_info)
            self.log_message(f"  ⏰ TIMEOUT")
            return False
            
        except Exception as e:
            self.stats['failed'] += 1
            error_info = {
                'url': url,
                'title': title,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.failed_urls.append(error_info)
            self.log_message(f"  ❌ ERROR: {e}")
            return False
    
    def print_statistics(self):
        """Print current statistics"""
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            elapsed_str = f"{elapsed/3600:.1f}h" if elapsed > 3600 else f"{elapsed/60:.1f}m"
        else:
            elapsed_str = "0m"
        
        print(f"\n" + "="*60)
        print("📊 DOWNLOAD STATISTICS")
        print("="*60)
        print(f"📂 Total items: {self.stats['total_items']}")
        print(f"✅ Successful: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"⏭️  Skipped: {self.stats['skipped']}")
        print(f"📈 Processed: {self.stats['processed']}/{self.stats['total_items']} ({self.stats['processed']/self.stats['total_items']*100:.1f}%)")
        print(f"⏱️  Elapsed time: {elapsed_str}")
        
        if self.stats['processed'] > 0:
            avg_time = elapsed / self.stats['processed']
            remaining = (self.stats['total_items'] - self.stats['processed']) * avg_time
            remaining_str = f"{remaining/3600:.1f}h" if remaining > 3600 else f"{remaining/60:.1f}m"
            print(f"⏳ Estimated remaining: {remaining_str}")
        
        print("="*60)
    
    def run(self):
        """Main download process"""
        print("🚀 BULK AUDIO DOWNLOADER")
        print("="*60)
        
        # Check if downloader script exists
        if not os.path.exists(self.downloader_script):
            print(f"❌ Downloader script not found: {self.downloader_script}")
            return
        
        # Load audio items
        items = self.load_audio_items()
        if not items:
            return
        
        # Load previous progress
        self.load_progress()
        
        # Initialize start time
        if not self.stats['start_time']:
            self.stats['start_time'] = time.time()
        
        self.log_message(f"Starting bulk download of {len(items)} audio items")
        
        try:
            # Process each item
            for i, item in enumerate(items, 1):
                # Skip if already processed (resume functionality)
                if i <= self.stats['processed']:
                    continue
                
                url = item.get('url', '')
                title = item.get('title', 'Unknown Title')
                
                if not url:
                    self.log_message(f"[{i}/{len(items)}] ⚠️  No URL found for item: {title}")
                    self.stats['skipped'] += 1
                    continue
                
                # Skip if URL was already successfully downloaded
                if any(success['url'] == url for success in self.successful_urls):
                    self.log_message(f"[{i}/{len(items)}] ⏭️  Already downloaded: {title[:50]}...")
                    self.stats['skipped'] += 1
                    self.stats['processed'] += 1
                    continue
                
                # Download the audio page
                self.download_audio_page(url, title, i)
                self.stats['processed'] += 1
                self.stats['current_item'] = i
                
                # Save progress every 10 items
                if i % 10 == 0:
                    self.save_progress()
                    self.print_statistics()
                
                # Add small delay to be respectful
                time.sleep(1)
            
            # Final save and statistics
            self.save_progress()
            self.print_statistics()
            
            self.log_message("🎉 Bulk download completed!")
            
            # Print summary
            print(f"\n🏁 FINAL SUMMARY:")
            print(f"  ✅ Successfully downloaded: {self.stats['successful']} items")
            print(f"  ❌ Failed downloads: {self.stats['failed']} items")
            print(f"  ⏭️  Skipped items: {self.stats['skipped']} items")
            
            if self.failed_urls:
                print(f"\n❌ Failed URLs saved to: {self.progress_file}")
                print("   You can retry failed downloads later")
            
            print(f"\n📝 Full log saved to: {self.log_file}")
            
        except KeyboardInterrupt:
            self.log_message("\n⏹️  Download interrupted by user")
            self.save_progress()
            self.print_statistics()
            print(f"\n📋 Progress saved. Run again to resume from item {self.stats['processed'] + 1}")
            
        except Exception as e:
            self.log_message(f"❌ Unexpected error: {e}")
            self.save_progress()
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    downloader = BulkAudioDownloader()
    downloader.run()

if __name__ == "__main__":
    main()