# 🎵 QUY TRÌNH DOWNLOAD AUDIO SACHTIENGANHHANOI.COM

## 🚀 Sử dụng cơ bản

```bash
# Download bất kỳ trang audio nào
python 01-ok-auto_downloader.py <URL>

# Download từ JSON file (5879 items)
python 01-ok-auto_downloader.py file=ALL_AUDIO_ITEMS_5879_items.json

# Download theo thứ tự ngược lại
python 01-ok-auto_downloader.py <URL> revert
python 01-ok-auto_downloader.py file=ALL_AUDIO_ITEMS_5879_items.json revert

# Ví dụ:
python 01-ok-auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-1-student-book-audio-cd/
python 01-ok-auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/ revert

# Script tự động load cookies từ curl_cmd.txt (nếu có):
# 🔄 Auto-loaded cookies from curl_cmd.txt
# ✅ Perfect! Found audio download nonce
```

## ❌ Khi gặp lỗi "Empty response"

### Dấu hiệu cookies hết hạn:
```
📊 Response: 200 | Length: 0 chars
❌ Empty response
❌ Failed to get playlist data
```

### Script tự cảnh báo nonce sai:
```
⚠️  Warning: Nonce is for 'ptp_load_posts', not 'shareonedrive-get-playlist'
   You need to capture audio play request, not page load request
```

### Giải pháp: Lấy cURL từ audio play request

#### Bước 1: Lấy cURL đúng từ Chrome
1. **Login** vào https://sachtienganhhanoi.com
2. **Vào trang audio** bất kỳ
3. **Mở DevTools** (F12) → **Network tab**
4. **⚠️ QUAN TRỌNG: PLAY 1 file audio** (click nút play!)
5. **Tìm request `admin-ajax.php`** với `action=shareonedrive-get-playlist`
6. **Right-click** → **Copy as cURL (cmd)** (Windows format)
7. **Paste vào file `curl_cmd.txt`**

**⚠️ Lưu ý:** Phải copy cURL **khi play audio**, không phải khi load trang!

#### Bước 2: Script tự động load cookies
- ✅ **Tự động đọc từ `curl_cmd.txt`**
- ✅ **Tự động decode Windows format** (`^%^` → `%`)
- ✅ **Tự động cảnh báo nếu action sai**
- ❌ **Không cần `extract_cookies.py` nữa!**

#### Bước 3: Test lại
```bash
python 01-ok-auto_downloader.py <URL>
```

## 📁 Kết quả tự động

### Trang 1 CD:
```
[Audio] Now I Know 5/
├── NOW_I_KNOW_SBK_5_CD1_TK01.mp3
├── NOW_I_KNOW_SBK_5_CD1_TK02.mp3
└── ... (86 files)
```

### Trang nhiều CD:
```
[Audio] Now I Know 1/
├── CD1/
│   ├── NIK_L1_CD1_Track02.mp3
│   └── ... (116 files)
└── CD2/
    ├── NIK_L1_CD2_Track02.mp3
    └── ... (135 files)
```

## 🔧 Files quan trọng

| File | Chức năng |
|------|-----------|
| `01-ok-auto_downloader.py` | **Script chính** - Chạy file này (tự load cookies) |
| `curl_cmd.txt` | **Lưu cURL** - Paste cURL audio play request vào đây |
| `browser_session_downloader.py` | **Core engine** - Không cần chạm |
| ~~`extract_cookies.py`~~ | ~~Không cần nữa~~ - Script tự load cookies |

## ⏰ Lưu ý

- **Cookies hết hạn:** 6-24 giờ
- **Khi nào cập nhật:** Khi thấy "Empty response"
- **Tần suất:** Thường 1-2 lần/ngày

## 🎯 Quy trình tóm tắt

1. **Chạy:** `python 01-ok-auto_downloader.py <URL>`
2. **Nếu lỗi:** Lấy cURL từ **audio play request** → Paste vào `curl_cmd.txt` → Thử lại
3. **Thành công:** Files tự động tải về và được tổ chức theo CD!

---

**💡 Ghi nhớ:** Chỉ cần nhớ 1 lệnh chính:
- `python 01-ok-auto_downloader.py <URL>` (tự động load cookies từ curl_cmd.txt)