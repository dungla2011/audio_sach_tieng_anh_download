"""
Script cuối cùng để lấy nội dung audio từ sachtienganhhanoi.com
Sử dụng payload chính xác từ trang web
"""

import requests
import json
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import parse_qs, urlencode

class AudioFetcherFinal:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://sachtienganhhanoi.com"
        self.ajax_url = f"{self.base_url}/wp-admin/admin-ajax.php"
        self.stream_url = f"{self.base_url}/audio_stream/"
        
        # Headers chính xác
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': self.base_url,
            'Referer': self.stream_url,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        self.session.headers.update(self.headers)
        
        self.table_id = None
        self.ajax_nonce = None
    
    def get_initial_data(self):
        """Lấy trang ban đầu để có nonce và table_id"""
        print("📄 Đang tải trang web để lấy thông tin...")
        
        try:
            response = self.session.get(self.stream_url)
            if response.status_code == 200:
                print("✓ Tải trang thành công")
                
                # Tìm ajax_nonce
                nonce_patterns = [
                    r'_ajax_nonce["\']?\s*:\s*["\']([^"\']+)["\']',
                    r'ajax_nonce["\']?\s*:\s*["\']([^"\']+)["\']', 
                    r'nonce["\']?\s*:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in nonce_patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        self.ajax_nonce = match.group(1)
                        print(f"  ✓ Tìm thấy ajax_nonce: {self.ajax_nonce}")
                        break
                
                # Tìm table_id
                table_match = re.search(r'table_id["\']?\s*:\s*["\']([^"\']+)["\']', response.text)
                if not table_match:
                    # Tìm trong HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    tables = soup.find_all('table', id=re.compile(r'ptp_'))
                    if tables:
                        self.table_id = tables[0].get('id')
                        print(f"  ✓ Tìm thấy table_id: {self.table_id}")
                else:
                    self.table_id = table_match.group(1)
                    print(f"  ✓ Tìm thấy table_id: {self.table_id}")
                
                return True
            else:
                print(f"✗ Lỗi: Status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Lỗi: {e}")
            return False
    
    def build_datatables_payload(self, draw=1, start=0, length=10, search_value=""):
        """Xây dựng payload theo format DataTables chính xác"""
        
        # Sử dụng table_id và nonce đã lấy được, hoặc giá trị mặc định
        table_id = self.table_id or "ptp_38232b3504e57e95_1"
        ajax_nonce = self.ajax_nonce or "fc0a67ee6e"
        
        payload = {
            'draw': str(draw),
            'columns[0][data]': 'image',
            'columns[0][name]': 'image',
            'columns[0][searchable]': 'false',
            'columns[0][orderable]': 'false',
            'columns[0][search][value]': '',
            'columns[0][search][regex]': 'false',
            'columns[1][data]': 'title',
            'columns[1][name]': 'title',
            'columns[1][searchable]': 'true',
            'columns[1][orderable]': 'true',
            'columns[1][search][value]': '',
            'columns[1][search][regex]': 'false',
            'columns[2][data]': 'tags',
            'columns[2][name]': 'tags',
            'columns[2][searchable]': 'true',
            'columns[2][orderable]': 'false',
            'columns[2][search][value]': '',
            'columns[2][search][regex]': 'false',
            'columns[3][data]': 'hf:tags',
            'columns[3][name]': 'hf_tags',
            'columns[3][searchable]': 'true',
            'columns[3][orderable]': 'true',
            'columns[3][search][value]': '',
            'columns[3][search][regex]': 'false',
            'start': str(start),
            'length': str(length),
            'search[value]': search_value,
            'search[regex]': 'false',
            'table_id': table_id,
            'action': 'ptp_load_posts',
            '_ajax_nonce': ajax_nonce
        }
        
        return payload
    
    def fetch_audio_data(self, start=0, length=10, search_term=""):
        """Gửi request để lấy dữ liệu audio"""
        print(f"\n📡 Đang gửi request (start={start}, length={length})...")
        
        payload = self.build_datatables_payload(
            draw=1,
            start=start,
            length=length,
            search_value=search_term
        )
        
        try:
            response = self.session.post(
                self.ajax_url,
                data=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                try:
                    # Parse JSON response
                    data = response.json()
                    print(f"✓ Nhận được JSON response!")
                    
                    # Phân tích response
                    if 'data' in data:
                        print(f"  • Tìm thấy {len(data.get('data', []))} items")
                        print(f"  • Total records: {data.get('recordsTotal', 'N/A')}")
                        print(f"  • Filtered records: {data.get('recordsFiltered', 'N/A')}")
                        
                        return data
                    else:
                        print(f"  • Response keys: {list(data.keys())}")
                        return data
                        
                except json.JSONDecodeError:
                    print(f"⚠️ Response không phải JSON")
                    print(f"  Response text: {response.text[:200]}...")
                    
                    # Có thể là error message
                    if "Error" in response.text:
                        print(f"  ✗ Error message: {response.text}")
                        
                        # Thử lại với nonce mới nếu error về nonce
                        if "nonce" in response.text.lower():
                            print("\n🔄 Thử lấy lại nonce mới...")
                            if self.get_initial_data():
                                print("  → Thử lại với nonce mới...")
                                return self.fetch_audio_data(start, length, search_term)
                    
                    return None
            else:
                print(f"✗ Error: Status code {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error: {e}")
            return None
    
    def parse_audio_items(self, data):
        """Parse và trích xuất thông tin audio từ response"""
        if not data or 'data' not in data:
            return []
        
        audio_items = []
        
        print("\n📋 Phân tích dữ liệu audio...")
        
        for i, row in enumerate(data['data'], 1):
            item = {}
            
            # Row có thể là array hoặc object
            if isinstance(row, list):
                # Format: [image, title, tags, hf_tags]
                if len(row) >= 2:
                    # Parse image column
                    if row[0]:
                        soup = BeautifulSoup(row[0], 'html.parser')
                        img = soup.find('img')
                        if img:
                            item['image'] = img.get('src', '')
                    
                    # Parse title column
                    if row[1]:
                        soup = BeautifulSoup(row[1], 'html.parser')
                        links = soup.find_all('a', href=True)
                        if links:
                            item['title'] = links[0].text.strip()
                            item['url'] = links[0]['href']
                        else:
                            item['title'] = soup.get_text(strip=True)
                    
                    # Parse tags
                    if len(row) > 2 and row[2]:
                        soup = BeautifulSoup(row[2], 'html.parser')
                        item['tags'] = soup.get_text(strip=True)
                    
                    # Parse hf_tags
                    if len(row) > 3 and row[3]:
                        soup = BeautifulSoup(row[3], 'html.parser')
                        item['hf_tags'] = soup.get_text(strip=True)
                        
            elif isinstance(row, dict):
                # Direct object format
                item = {
                    'image': row.get('image', ''),
                    'title': row.get('title', ''),
                    'tags': row.get('tags', ''),
                    'hf_tags': row.get('hf:tags', row.get('hf_tags', '')),
                    'url': row.get('url', '')
                }
                
                # Parse HTML nếu cần
                if '<' in str(item.get('title', '')):
                    soup = BeautifulSoup(item['title'], 'html.parser')
                    links = soup.find_all('a', href=True)
                    if links:
                        item['title'] = links[0].text.strip()
                        item['url'] = links[0]['href']
            
            if item.get('title'):
                audio_items.append(item)
                print(f"  {i}. {item['title'][:60]}...")
                if item.get('url'):
                    print(f"     URL: {item['url']}")
        
        return audio_items
    
    def save_results(self, data, audio_items):
        """Lưu kết quả vào file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Lưu raw JSON
        json_file = f"audio_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Đã lưu raw data vào {json_file}")
        
        # Lưu parsed items
        if audio_items:
            items_file = f"audio_items_{timestamp}.json"
            with open(items_file, 'w', encoding='utf-8') as f:
                json.dump(audio_items, f, ensure_ascii=False, indent=2)
            print(f"💾 Đã lưu {len(audio_items)} audio items vào {items_file}")
            
            # Tạo file HTML để xem dễ hơn
            html_file = f"audio_list_{timestamp}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Audio List</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:hover { background-color: #f5f5f5; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Danh sách Audio</h1>
    <table>
        <thead>
            <tr>
                <th>STT</th>
                <th>Tiêu đề</th>
                <th>Tags</th>
                <th>Link</th>
            </tr>
        </thead>
        <tbody>
""")
                
                for i, item in enumerate(audio_items, 1):
                    # Escape HTML để tránh lỗi
                    title = str(item.get('title', '')).replace('<', '&lt;').replace('>', '&gt;')
                    tags = str(item.get('tags', '')).replace('<', '&lt;').replace('>', '&gt;')
                    url = item.get('url', '#')
                    
                    f.write(f"""
            <tr>
                <td>{i}</td>
                <td>{title}</td>
                <td>{tags}</td>
                <td><a href="{url}" target="_blank">Xem</a></td>
            </tr>
""")
                
                f.write("""
        </tbody>
    </table>
</body>
</html>""")
            
            print(f"💾 Đã tạo file HTML: {html_file}")

def fetch_all_pages(fetcher, total_items=100, page_size=10):
    """Lấy nhiều trang dữ liệu
    
    Args:
        fetcher: AudioFetcherFinal instance
        total_items: Tổng số items muốn lấy
        page_size: Số items mỗi trang (thường là 10)
    
    Returns:
        list: Danh sách tất cả audio items
    """
    all_items = []
    
    print(f"\n📚 Bắt đầu lấy {total_items} items (mỗi trang {page_size} items)...")
    print("-"*40)
    
    # Tính số trang cần lấy
    num_pages = (total_items + page_size - 1) // page_size
    
    for page in range(num_pages):
        # QUAN TRỌNG: start phải là 0, 10, 20, 30... (bội số của page_size)
        start = page * page_size
        
        print(f"\n📄 Trang {page + 1}/{num_pages} (start={start}, length={page_size})")
        
        data = fetcher.fetch_audio_data(start=start, length=page_size)
        
        if data and 'data' in data:
            items = fetcher.parse_audio_items(data)
            all_items.extend(items)
            print(f"   ✓ Đã lấy {len(items)} items (Tổng: {len(all_items)})")
            
            # Delay để không spam server
            if page < num_pages - 1:
                time.sleep(1)
        else:
            print("   ✗ Không lấy được dữ liệu")
            break
    
    return all_items

def main():
    print("🎵 Audio Fetcher Final - sachtienganhhanoi.com")
    print("="*60)
    
    fetcher = AudioFetcherFinal()
    
    # Bước 1: Lấy thông tin ban đầu
    print("\nBƯỚC 1: LẤY THÔNG TIN BAN ĐẦU")
    print("-"*40)
    if not fetcher.get_initial_data():
        print("⚠️ Sử dụng giá trị mặc định từ payload được cung cấp")
    
    # Bước 2: Gửi request
    print("\nBƯỚC 2: GỬI REQUEST LẤY DỮ LIỆU")
    print("-"*40)
    
    # Lấy trang đầu tiên
    data = fetcher.fetch_audio_data(start=0, length=10)
    
    if data:
        # Bước 3: Parse và lưu kết quả
        print("\nBƯỚC 3: XỬ LÝ VÀ LƯU KẾT QUẢ")
        print("-"*40)
        
        audio_items = fetcher.parse_audio_items(data)
        fetcher.save_results(data, audio_items)
        
        # Hiển thị thông tin tổng quan
        print("\n" + "="*60)
        print("📊 TỔNG KẾT")
        print("="*60)
        
        if 'recordsTotal' in data:
            total_records = data['recordsTotal']
            print(f"  • Tổng số records: {total_records}")
            print(f"  • Số records đã lấy: {len(audio_items)}")
            
            # Demo lấy nhiều trang
            if total_records > 10:
                print(f"\n💡 Lấy thêm dữ liệu:")
                print(f"   - start phải là: 0, 10, 20, 30, 40... (bội số của length)")
                print(f"   - Ví dụ: Trang 1: start=0, Trang 2: start=10, Trang 3: start=20...")
                
                # Demo lấy thêm 2 trang nữa
                print("\n🔄 Demo lấy thêm 2 trang tiếp theo...")
                
                # Trang 2: start=10
                print("\n  📄 Trang 2 (start=10):")
                page2 = fetcher.fetch_audio_data(start=10, length=10)
                if page2 and 'data' in page2:
                    items2 = fetcher.parse_audio_items(page2)
                    print(f"     → Lấy được {len(items2)} items")
                
                time.sleep(1)
                
                # Trang 3: start=20
                print("\n  📄 Trang 3 (start=20):")
                page3 = fetcher.fetch_audio_data(start=20, length=10)
                if page3 and 'data' in page3:
                    items3 = fetcher.parse_audio_items(page3)
                    print(f"     → Lấy được {len(items3)} items")
                
                print(f"\n💡 Để lấy nhiều trang tự động, dùng hàm fetch_all_pages()")
                print(f"   Ví dụ: all_items = fetch_all_pages(fetcher, total_items=50)")
        
        print("\n✅ Hoàn thành! Kiểm tra các file đã tạo.")
    else:
        print("\n✗ Không thể lấy dữ liệu")
        print("\n💡 Kiểm tra:")
        print("  1. Kết nối internet")
        print("  2. Website có thể đã thay đổi cấu trúc")
        print("  3. Cần update nonce/table_id")

if __name__ == "__main__":
    main()
