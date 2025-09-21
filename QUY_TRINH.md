# 🎵 QUY TRÌNH DOWNLOAD AUDIO SACHTIENGANHHANOI.COM

## 🚀 Sử dụng cơ bản

```bash
# Download bất kỳ trang audio nào
python 01-ok-auto_downloader.py <URL>

# Ví dụ:
python 01-ok-auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-1-student-book-audio-cd/
python 01-ok-auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/
```

## ❌ Khi gặp lỗi "Empty response"

### Dấu hiệu cookies hết hạn:
```
📊 Response: 200 | Length: 0 chars
❌ Empty response
❌ Failed to get playlist data
```

### Giải pháp: Lấy cookies mới

#### Bước 1: Lấy cURL từ Chrome
1. **Login** vào https://sachtienganhhanoi.com
2. **Vào trang audio** bất kỳ
3. **Mở DevTools** (F12) → **Network tab**
4. **Reload trang**
5. **Tìm request `admin-ajax.php`** (action=shareonedrive-get-playlist)
6. **Right-click** → **Copy as cURL**
7. **Paste vào file `curl_cmd.txt`**

#### Bước 2: Extract cookies tự động
```bash
python extract_cookies.py
```
- Paste cURL command
- Script tự động extract và update

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
| `01-ok-auto_downloader.py` | **Script chính** - Chạy file này |
| `extract_cookies.py` | **Lấy cookies mới** - Chạy khi hết hạn |
| `curl_cmd.txt` | **Lưu cURL** - Paste cURL vào đây |
| `browser_session_downloader.py` | **Core engine** - Không cần chạm |

## ⏰ Lưu ý

- **Cookies hết hạn:** 6-24 giờ
- **Khi nào cập nhật:** Khi thấy "Empty response"
- **Tần suất:** Thường 1-2 lần/ngày

## 🎯 Quy trình tóm tắt

1. **Chạy:** `python 01-ok-auto_downloader.py <URL>`
2. **Nếu lỗi:** Lấy cURL → `python extract_cookies.py` → Thử lại
3. **Thành công:** Files tự động tải về và được tổ chức theo CD!

---

**💡 Ghi nhớ:** Chỉ cần nhớ 2 lệnh chính:
- `python 01-ok-auto_downloader.py <URL>` (dùng hàng ngày)
- `python extract_cookies.py` (dùng khi hết cookies)