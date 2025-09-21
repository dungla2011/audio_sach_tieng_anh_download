"""
Script để lấy TẤT CẢ các trang từ sachtienganhhanoi.com
⚠️ CHÚ Ý: Sẽ lấy 5,879 items - có thể mất vài phút
"""

from fetch_audio_final import AudioFetcherFinal
import time
import json
import math

def fetch_all_audio_items():
    """
    Lấy tất cả audio items từ website
    """
    print("🎵 FETCH ALL AUDIO ITEMS - sachtienganhhanoi.com")
    print("="*70)
    print("⚠️  CẢNH BÁO: Sẽ lấy TẤT CẢ 5,879+ items")
    print("⏱️  Thời gian ước tính: 10-15 phút")
    print("🚫 Nhấn Ctrl+C để dừng bất cứ lúc nào")
    print("="*70)
    
    # Xác nhận từ user
    confirm = input("\n🤔 Bạn có chắc muốn tiếp tục? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Đã hủy.")
        return
    
    fetcher = AudioFetcherFinal()
    
    # Lấy thông tin ban đầu
    print("\n📄 Đang lấy thông tin từ trang web...")
    if not fetcher.get_initial_data():
        print("❌ Không thể lấy thông tin ban đầu")
        return
    
    # Cấu hình
    ITEMS_PER_PAGE = 50  # Tăng lên 50 để giảm số request
    DELAY_BETWEEN_REQUESTS = 2  # 2 giây delay để không spam server
    
    # Lấy thông tin tổng số items
    print("\n📊 Đang kiểm tra tổng số items...")
    first_page = fetcher.fetch_audio_data(start=0, length=ITEMS_PER_PAGE)
    
    if not first_page or 'recordsTotal' not in first_page:
        print("❌ Không thể lấy thông tin tổng số items")
        return
    
    total_items = first_page['recordsTotal']
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
    
    print(f"📈 Tổng số items: {total_items:,}")
    print(f"📄 Tổng số trang: {total_pages:,} (mỗi trang {ITEMS_PER_PAGE} items)")
    print(f"⏱️  Thời gian ước tính: {(total_pages * DELAY_BETWEEN_REQUESTS) / 60:.1f} phút")
    
    # Xác nhận lần cuối
    final_confirm = input(f"\n🚀 Bắt đầu lấy {total_items:,} items? (y/N): ").strip().lower()
    if final_confirm not in ['y', 'yes']:
        print("❌ Đã hủy.")
        return
    
    # Bắt đầu lấy dữ liệu
    all_items = []
    failed_pages = []
    start_time = time.time()
    
    print(f"\n🎯 BẮT ĐẦU LẤY DỮ LIỆU")
    print("-" * 50)
    
    # Parse items từ trang đầu tiên
    if 'data' in first_page:
        first_items = fetcher.parse_audio_items(first_page)
        all_items.extend(first_items)
        print(f"📄 Trang 1/{total_pages}: ✅ {len(first_items)} items (Tổng: {len(all_items)})")
    
    # Lấy các trang còn lại
    for page in range(2, total_pages + 1):
        start = (page - 1) * ITEMS_PER_PAGE
        
        try:
            print(f"📄 Trang {page}/{total_pages}: ", end="", flush=True)
            
            data = fetcher.fetch_audio_data(start=start, length=ITEMS_PER_PAGE)
            
            if data and 'data' in data:
                items = fetcher.parse_audio_items(data)
                all_items.extend(items)
                
                # Tính thời gian còn lại
                elapsed = time.time() - start_time
                avg_time_per_page = elapsed / page
                remaining_pages = total_pages - page
                eta = remaining_pages * avg_time_per_page
                
                print(f"✅ {len(items)} items (Tổng: {len(all_items):,}) - ETA: {eta/60:.1f}p")
                
                # Lưu progress mỗi 20 trang
                if page % 20 == 0:
                    save_progress(all_items, page, total_pages)
                
            else:
                print(f"❌ Lỗi")
                failed_pages.append(page)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Đã dừng tại trang {page}/{total_pages}")
            print(f"📊 Đã lấy được: {len(all_items):,} items")
            break
            
        except Exception as e:
            print(f"❌ Lỗi: {str(e)[:50]}...")
            failed_pages.append(page)
        
        # Delay giữa các request
        if page < total_pages:
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Kết quả cuối cùng
    total_time = time.time() - start_time
    print(f"\n" + "="*70)
    print("📊 KẾT QUẢ CUỐI CÙNG")
    print("="*70)
    print(f"✅ Đã lấy thành công: {len(all_items):,} items")
    print(f"⏱️  Tổng thời gian: {total_time/60:.1f} phút")
    print(f"📄 Trang thành công: {total_pages - len(failed_pages)}/{total_pages}")
    
    if failed_pages:
        print(f"❌ Trang lỗi: {len(failed_pages)} trang")
        print(f"   Danh sách: {failed_pages[:10]}{'...' if len(failed_pages) > 10 else ''}")
    
    # Lưu kết quả
    if all_items:
        save_final_results(all_items, total_time)
    
    return all_items

def save_progress(items, current_page, total_pages):
    """Lưu tiến trình"""
    filename = f"progress_{len(items)}_items_page_{current_page}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"   💾 Đã lưu progress: {filename}")

def save_final_results(all_items, total_time):
    """Lưu kết quả cuối cùng"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Lưu JSON
    json_file = f"ALL_AUDIO_ITEMS_{len(all_items)}_items_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"💾 Đã lưu JSON: {json_file}")
    
    # Lưu HTML
    html_file = f"ALL_AUDIO_ITEMS_{len(all_items)}_items_{timestamp}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>TẤT CẢ Audio Items - {len(all_items):,} items</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .stat {{ background: white; padding: 15px; border-radius: 8px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .search-box {{ margin: 20px 0; }}
        .search-box input {{ width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #4CAF50; color: white; position: sticky; top: 0; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #e8f5e8; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .page-info {{ font-size: 12px; color: #666; }}
    </style>
    <script>
        function searchTable() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toUpperCase();
            const table = document.getElementById('audioTable');
            const rows = table.getElementsByTagName('tr');
            
            for (let i = 1; i < rows.length; i++) {{
                const cells = rows[i].getElementsByTagName('td');
                let found = false;
                
                for (let j = 0; j < cells.length; j++) {{
                    if (cells[j].innerHTML.toUpperCase().indexOf(filter) > -1) {{
                        found = true;
                        break;
                    }}
                }}
                
                rows[i].style.display = found ? '' : 'none';
            }}
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>🎵 TẤT CẢ Audio/Video Items</h1>
        <p>Tổng cộng {len(all_items):,} items từ sachtienganhhanoi.com</p>
        <p class="page-info">Thời gian lấy: {total_time/60:.1f} phút | Tạo lúc: {time.strftime("%d/%m/%Y %H:%M:%S")}</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <h3>{len(all_items):,}</h3>
            <p>Tổng Items</p>
        </div>
        <div class="stat">
            <h3>{len([item for item in all_items if '[Audio]' in item.get('title', '')]):,}</h3>
            <p>Audio Items</p>
        </div>
        <div class="stat">
            <h3>{len([item for item in all_items if '[Video]' in item.get('title', '') or '[VIDEO]' in item.get('title', '')]):,}</h3>
            <p>Video Items</p>
        </div>
        <div class="stat">
            <h3>{total_time/60:.1f}p</h3>
            <p>Thời gian lấy</p>
        </div>
    </div>
    
    <div class="search-box">
        <input type="text" id="searchInput" onkeyup="searchTable()" placeholder="🔍 Tìm kiếm audio/video... (IELTS, Cambridge, Oxford, etc.)">
    </div>
    
    <table id="audioTable">
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
        
        for i, item in enumerate(all_items, 1):
            title = str(item.get('title', '')).replace('<', '&lt;').replace('>', '&gt;')
            tags = str(item.get('tags', ''))[:100].replace('<', '&lt;').replace('>', '&gt;')
            if len(str(item.get('tags', ''))) > 100:
                tags += "..."
            url = item.get('url', '#')
            
            f.write(f"""
            <tr>
                <td>{i:,}</td>
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
    
    print(f"💾 Đã lưu HTML: {html_file}")
    print(f"\n🌐 Mở file HTML trong trình duyệt để xem kết quả!")

if __name__ == "__main__":
    try:
        fetch_all_audio_items()
    except KeyboardInterrupt:
        print("\n\n⏹️  Đã dừng bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
    finally:
        print("\n👋 Kết thúc chương trình")
