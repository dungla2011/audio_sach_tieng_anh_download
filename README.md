# Audio Sách Tiếng Anh Downloader

🎵 Tự động tải audio từ sachtienganhhanoi.com với tổ chức theo CD

## ✨ Tính năng

- 🚀 **Tự động tải toàn bộ audio** từ bất kỳ trang nào trên sachtienganhhanoi.com
- 📁 **Tự động tổ chức theo CD** (CD1/, CD2/, etc.) cho các bộ sách nhiều CD
- 🔐 **Sử dụng browser session** để bypass authentication
- 💻 **CLI đơn giản** - chỉ cần nhập URL
- 🎯 **Universal** - hoạt động với tất cả các trang audio

## 🚀 Cách sử dụng

### 1. Cài đặt dependencies
```bash
pip install requests beautifulsoup4
```

### 2. Download audio từ URL
```bash
python 01-ok-auto_downloader.py <URL>
```

### 3. Ví dụ
```bash
# Tải Now I Know 1 (tự động chia thành CD1, CD2)
python 01-ok-auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-1-student-book-audio-cd/

# Tải Now I Know 5
python 01-ok-auto_downloader.py https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/
```

### 4. Khi cookies hết hạn (Empty response)
```bash
# 1. Lấy cURL từ Chrome DevTools → Paste vào curl_cmd.txt
# 2. Chạy cookie extractor:
python extract_cookies.py
# 3. Thử lại download
```

📖 **Chi tiết:** Xem file `QUY_TRINH.md`

## 📂 Cấu trúc kết quả

```
[Audio] Now I Know! 1 Student Book/
├── CD1/
│   ├── NIK_L1_CD1_Track02.mp3
│   ├── NIK_L1_CD1_Track03.mp3
│   └── ... (116 files)
└── CD2/
    ├── NIK_L1_CD2_Track02.mp3
    ├── NIK_L1_CD2_Track03.mp3
    └── ... (135 files)
```

## 🔧 Files chính

- **`01-ok-auto_downloader.py`** - Script chính với CLI và tổ chức CD
- **`browser_session_downloader.py`** - Core downloader engine
- **`universal_audio_downloader.py`** - Universal downloader cho mọi trang

## 🔐 Authentication

Script sử dụng cookies từ browser session đã login. Khi cookies hết hạn:

1. Login vào sachtienganhhanoi.com bằng Chrome
2. Mở DevTools → Network tab
3. Tìm request `admin-ajax.php`
4. Copy as cURL và extract cookies/nonce mới
5. Update trong script

## 🎯 Tested với

- ✅ Now I Know 1 (251 files, 2 CDs)
- ✅ Now I Know 2 (115 files, 1 CD)  
- ✅ Now I Know 5 (86 files, 1 CD)

## 📝 Lịch sử phát triển

1. **1.py - 3.py**: Test login và AJAX calls
2. **4_download_audio.py - 6_test_stream.py**: Thử nghiệm download
3. **7_onedrive_extract.py - 8_onedrive_download.py**: OneDrive integration
4. **universal_audio_downloader.py**: Universal solution
5. **01-ok-auto_downloader.py**: Final CLI với tổ chức CD

## 🤝 Đóng góp

1. Fork dự án
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

## ⚠️ Lưu ý

- Chỉ sử dụng với tài khoản hợp lệ
- Cookies có thời hạn, cần update định kỳ
- Respect server resources, không spam requests

## 📜 License

MIT License - Xem file LICENSE để biết chi tiết