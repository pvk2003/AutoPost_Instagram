import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from instagram_bot import InstagramBot
from config import CREDENTIAL_FILE, SERVICE_TABS, HISTORY_SHEET_URL

MAX_POSTS_PER_DAY = 15


# ============================
#  KẾT NỐI GOOGLE SHEET
# ============================
def connect_sheet(tab_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)
    client = gspread.authorize(creds)
    return client.open_by_url(HISTORY_SHEET_URL).worksheet(tab_name)


# ============================
#  LẤY LIST SERVICE ĐÃ ĐĂNG
# ============================
def get_posted_services():
    posted = set()

    for _, tab_name in SERVICE_TABS.items():
        try:
            sheet = connect_sheet(tab_name)
            rows = sheet.get_all_values()

            for row in rows[1:]:
                service = row[1].strip() if len(row) > 1 else ""   # Cột B
                link = row[3].strip() if len(row) > 3 else ""      # Cột D

                if service and link:
                    posted.add(service)

        except Exception as e:
            print(f"⚠ Lỗi đọc tab {tab_name}:", e)

    return posted


# ============================
#  ĐẾM SỐ BÀI ĐĂNG HÔM NAY (CỘT E)
# ============================
def count_posts_today(field):
    today = datetime.now().strftime("%Y-%m-%d")
    tab_name = SERVICE_TABS[field]

    sheet = connect_sheet(tab_name)
    rows = sheet.get_all_values()

    count = 0
    for row in rows[1:]:
        date = row[4].strip() if len(row) > 4 else ""   # Cột E
        if date == today:
            count += 1

    return count


# ============================
#  LƯU LỊCH SỬ
# ============================
def save_history(field, service, url):
    tab_name = SERVICE_TABS[field]
    sheet = connect_sheet(tab_name)

    rows = sheet.get_all_values()

    for i, row in enumerate(rows[1:], start=2):
        service_name = row[1].strip() if len(row) > 1 else ""
        if service_name == service:
            sheet.update_cell(i, 4, url)  # Cột D
            sheet.update_cell(i, 5, datetime.now().strftime("%Y-%m-%d"))  # Cột E
            return

    # Nếu chưa có thì thêm dòng mới
    sheet.append_row([
        "",                        # cột A
        service,                   # cột B
        "",                        # cột C (Báo giá)
        url,                       # cột D (Link post)
        datetime.now().strftime("%Y-%m-%d")  # cột E (Date)
    ])


# ============================
#  ĐĂNG BÀI
# ============================
def post_manual(service, field, image_path, caption, username):
    today_count = count_posts_today(field)

    if today_count >= MAX_POSTS_PER_DAY:
        raise Exception(
            f"Hôm nay lĩnh vực '{field}' đã đạt giới hạn {MAX_POSTS_PER_DAY} bài."
        )

    bot = InstagramBot(username=username)
    post_url = bot.post_photo(image_path, caption)

    save_history(field, service, post_url)

    return post_url
