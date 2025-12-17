# instagram_bot.py
from instagrapi import Client
import json, os, time, random

def drop_invalid_mentions(caption: str) -> str:
    """
    Chỉ xử lý dòng mention (@...), KHÔNG đụng body caption.
    Drop token không bắt đầu bằng @ trong dòng mention.
    """
    new_lines = []

    for line in caption.splitlines():
        stripped = line.strip()

        # ✅ CHỈ xử lý dòng có mention
        if stripped.startswith("@"):
            words = stripped.split()
            kept = []

            for w in words:
                # giữ tag hợp lệ
                if w.startswith("@"):
                    kept.append(w)
                else:
                    print(f"⚠ DROP invalid tag in mention line: {w}")

            if kept:
                new_lines.append(" ".join(kept))
            # nếu dòng mention bị drop hết → bỏ dòng luôn
        else:
            # body caption → giữ nguyên
            new_lines.append(line)

    return "\n".join(new_lines)


class InstagramBot:
    def __init__(self, username=None, password=None):
        if not username:
            # Thử tìm file session
            sessions = [f for f in os.listdir() if f.startswith("session_") and f.endswith(".json")]
            if not sessions:
                raise Exception("❌ Thiếu username và không có session!")
            
            username = sessions[0].replace("session_", "").replace(".json", "")
            print(f"📌 Auto username from session: {username}")

        self.username = username
        self.password = password
        self.session_file = f"session_{username}.json"
        self.cl = Client()
        # Throttle cho TẤT CẢ request IG (best-practice instagrapi)
        # Mặc định: mỗi request cách nhau ~4–9s
        self.cl.delay_range = [4, 9]
        # ====== LOAD SESSION ======
        if os.path.exists(self.session_file):
            print(f"📂 Found session: {self.session_file}")
            try:
                self.cl.load_settings(self.session_file)

                # Nếu CÓ password → login đầy đủ
                if password:
                    self.cl.login(username, password)
                else:
                    # Không có password → dùng session id để login
                    if not self.cl.login_by_sessionid(self.cl.sessionid):
                        print("⚠ Session ID login thất bại, cần đăng nhập lại")
                        raise Exception("Session hỏng")

                if self.cl.user_id:
                    print("🔵 Session login OK")
                    return

            except Exception as e:
                print("⚠ Session lỗi:", e)

        # ====== LOGIN MỚI (KHÔNG CÓ SESSION) ======
        if not password:
            raise Exception("❌ Thiếu password để đăng nhập mới!")

        self.login_new(username, password)

    def login_new(self, username, password):
        print("🔐 Đang đăng nhập mới...")

        try:
            self.cl.login(username, password)
        except Exception as e:
            raise Exception(f"❌ Login thất bại: {e}")

        # Kiểm tra login có ok không
        if not self.cl.user_id:
            raise Exception("❌ Login thất bại (user_id=None) – IG reject login.")

        # LƯU FULL SETTINGS
        self.cl.dump_settings(self.session_file)
        print(f"💾 Saved session → {self.session_file}")

    def logout(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
            print("🗑 Session deleted")

    def post_photo(self, path, caption):
        # Làm sạch caption tránh ký tự lỗi làm IG reject
        caption = caption.replace("\r", "").replace("\x00", "")
        caption = caption.encode("utf-8", "ignore").decode("utf-8")

        # 🧹 Remove invisible characters
        invisible_chars = [
            "\u200b", "\u200c", "\u200d",
            "\ufeff", "\u2060", "\u00a0",
            "\u180e", "\u202f",
            "\u202a", "\u202b", "\u202c",
            "\u2066", "\u2067", "\u2068", "\u2069"
        ]
        for ch in invisible_chars:
            caption = caption.replace(ch, "")

        # Remove non-printable characters
        caption = ''.join(c for c in caption if c.isprintable() or c == "\n")

        # 🔥 AUTO DROP TAG LỖI (CHỈ 1 LẦN)
        caption = drop_invalid_mentions(caption)

        print("=== FINAL CAPTION ===")
        print(caption)
        print("=====================")

        # ⏳ Delay tự nhiên trước khi đăng
        time.sleep(random.uniform(3, 8))

        # ✅ UPLOAD DUY NHẤT 1 LẦN
        media = self.cl.photo_upload(path, caption)

        # ⏳ Cooldown sau khi đăng
        time.sleep(random.uniform(2, 6))

        return f"https://www.instagram.com/p/{media.code}/"


# ================== LOGIN BẰNG SESSIONID (DÙNG CHO TAB 2) ==================

def login_with_sessionid(sessionid: str) -> str:
    """
    Login Instagram bằng SESSIONID lấy từ trình duyệt,
    sau đó lưu settings vào file session_<username>.json
    và trả về username tương ứng.
    """
    if not sessionid or not sessionid.strip():
        raise Exception("❌ SessionID đang trống.")

    cl = Client()
    print("🔐 Đang đăng nhập bằng SESSIONID...")

    try:
        cl.login_by_sessionid(sessionid.strip())
    except Exception as e:
        raise Exception(f"❌ Login bằng SessionID thất bại: {e}")

    if not cl.user_id:
        raise Exception("❌ Login bằng SessionID thất bại (user_id=None).")

    # Lấy username hiện tại
    try:
        me = cl.user_info(cl.user_id)
        username = me.username
    except Exception:
        username = cl.username or "unknown"

    if not username:
        raise Exception("❌ Không lấy được username từ sessionid.")

    session_file = f"session_{username}.json"
    cl.dump_settings(session_file)
    print(f"💾 Saved session (sessionid) → {session_file}")

    return username
