# 📸 Auto Instagram Poster (GUI + Google Sheets)

Tool **tự động đăng bài Instagram** theo từng *service / lĩnh vực*, kết hợp **Google Sheets** và **giao diện GUI (Tkinter)**.

Hỗ trợ đăng nhập Instagram bằng **Password** hoặc **SessionID**
👉 **Khuyến nghị dùng SessionID** (ổn định & an toàn hơn).

---

## ✨ Tính năng chính

* ✅ Đăng **1 bài Instagram / service** (tránh trùng lặp)
* ✅ Tự động đọc danh sách service từ **Google Sheets**
* ✅ Tự động tạo caption (hashtag + mention an toàn)
* ✅ Chọn ảnh thủ công (chuẩn Instagram – vuông `1080x1080`)
* ✅ Lưu **lịch sử đã đăng** vào Google Sheets
* ✅ Giới hạn số bài đăng mỗi ngày (anti-spam)
* ✅ GUI thân thiện – dễ dùng cho người không rành kỹ thuật

---

## 🧱 Cấu trúc thư mục

```bash
.
├── main.py                # Entry point
├── gui.py                 # Giao diện chính
├── login_gui.py           # Giao diện đăng nhập Instagram
├── instagram_bot.py       # Logic đăng bài Instagram
├── autopost.py            # Đăng bài + lưu lịch sử
├── sheet_reader.py        # Đọc & xử lý Google Sheets
├── caption_builder.py     # Tạo caption tự động
├── image_downloader.py    # Xử lý ảnh (nếu dùng link)
├── config.py              # Cấu hình hệ thống
├── credentials.json       # Google Service Account (⚠ bí mật)
├── requirements.txt
└── README.md
```

---

## ⚙️ Yêu cầu môi trường

* Python **3.10+**
* Tài khoản **Instagram**
  👉 Khuyến nghị đăng nhập bằng **SessionID**
* **Google Sheets**
* **Google Service Account**

---

## 📦 Cài đặt

### 1️⃣ Tạo virtual environment (khuyến nghị)

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2️⃣ Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

## 🔐 Cấu hình Google Sheets

### 1️⃣ Tạo Google Service Account

* Truy cập: [https://console.cloud.google.com/](https://console.cloud.google.com/)
* Tạo **Service Account**
* Tải file **credentials.json**

### 2️⃣ Chia sẻ Google Sheet

* Mở Google Sheet
* Nhấn **Share**
* Chia sẻ cho email trong trường `client_email` của `credentials.json`
* Quyền: **Editor**

### 3️⃣ Cấu hình trong `config.py`

```python
SERVICE_SHEET_URL = "https://docs.google.com/spreadsheets/d/..."
TAG_SHEET_URL     = "https://docs.google.com/spreadsheets/d/..."
HISTORY_SHEET_URL = "https://docs.google.com/spreadsheets/d/..."
```

⚠️ **Lưu ý**: URL **KHÔNG được chứa** `#gid=` hoặc `gid=`

---

## 🚀 Cách chạy tool

```bash
python main.py
```

---

## 🔄 Luồng hoạt động

1. Mở app
2. Đăng nhập Instagram

   * Password **hoặc**
   * SessionID (**khuyến nghị – ổn định & an toàn**)
3. Chọn **Lĩnh vực**
4. Chọn **Service** (chưa đăng)
5. Chọn **Ảnh**
6. Tạo / chỉnh **Caption**
7. Bấm 🚀 **ĐĂNG BÀI**

---

## 🔑 Đăng nhập Instagram (khuyến nghị)

### ✅ Login bằng SessionID

1. Mở `instagram.com` và đăng nhập
2. Nhấn **F12** → tab **Application**
3. Vào **Cookies → instagram.com**
4. Copy giá trị **`sessionid`**
5. Dán vào tab **SESSIONID** trong tool

### ✅ Ưu điểm

* ✔ Ít checkpoint
* ✔ Không cần mật khẩu
* ✔ Ổn định lâu dài

---

## 📝 Caption & Mention an toàn

Tool tự động:

* Loại bỏ **ký tự vô hình** (Instagram rất dễ reject)
* Chuẩn hóa **@mention**
* Random **5–10 tag hợp lệ**
* Không làm hỏng body caption

👉 Fix triệt để các lỗi phổ biến:

* ❌ Đăng xong nhưng không thấy caption
* ❌ Mention bị mất `@`
* ❌ Instagram reject silently

---

## 📊 Lịch sử đăng bài

* Lưu vào **Google Sheet**
* Hiển thị trong GUI
* Double click để mở link bài đăng

Có thể:

* ❌ Xóa 1 dòng
* 🗑 Xóa toàn bộ lịch sử

---

## ⛔ Giới hạn & an toàn

* Tối đa **15 bài / ngày / lĩnh vực**
* Delay ngẫu nhiên khi đăng
* Không spam API
* Không đăng trùng service

---

## ⚠️ Lưu ý quan trọng

* ❌ **Không commit** `credentials.json`
* ❌ Không public project có file session
* ❌ Không đăng quá nhiều bài / ngày
* ❌ Caption quá dài → Instagram / Threads có thể fail

---

## 📌 Ghi chú

Tool được thiết kế cho:

* Đăng bán / marketing tự động
* Ưu tiên **an toàn tài khoản**
* Tránh bị **Instagram shadowban / silent reject**
