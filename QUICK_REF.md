# QUICK REFERENCE - AUDIO DOWNLOADER

## Lệnh chính (dùng hàng ngày)
```bash
python 01-ok-auto_downloader.py <URL>
```

## Khi cookies hết hạn
1. Chrome → DevTools → Network → Tìm admin-ajax.php → Copy as cURL
2. Paste vào `curl_cmd.txt`
3. Chạy: `python extract_cookies.py`
4. Thử lại lệnh chính

## Các URL thường dùng
- Now I Know 1: https://sachtienganhhanoi.com/audio-now-i-know-1-student-book-audio-cd/
- Now I Know 2: https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/
- Now I Know 5: https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/

## Files quan trọng
- `01-ok-auto_downloader.py` - Script chính
- `extract_cookies.py` - Lấy cookies mới
- `curl_cmd.txt` - Lưu cURL command
- `QUY_TRINH.md` - Hướng dẫn chi tiết