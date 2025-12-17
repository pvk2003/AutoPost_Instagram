import logging
import gspread
import re
import unicodedata
import random
import requests
from oauth2client.service_account import ServiceAccountCredentials
logger = logging.getLogger(__name__)

# -------------------------------------------------------
# CLEAN TAG (fix invisible character & weird @)
# -------------------------------------------------------
def clean_tag(t: str) -> str:
    """Làm sạch tag và đảm bảo luôn có @ ở đầu."""

    if not t:
        return ""

    # 1) Normalize @ full-width -> ASCII @
    replacements = {
        "＠": "@", "﹫": "@", "ﹺ": "@", "ﹻ": "@",
        "\uFF20": "@",   # full-width @
        "\uFE6B": "@",   # small @
    }
    for k, v in replacements.items():
        t = t.replace(k, v)

    # 2) Loại mọi ký tự vô hình
    invisible = [
        "\u200b", "\u200c", "\u200d",
        "\ufeff", "\u2060", "\u00a0",
        "\u180e", "\u202f",
        "\u202a", "\u202b", "\u202c",  # ← các ký tự LEFT-TO-RIGHT mà IG cực ghét
        "\u2066", "\u2067", "\u2068", "\u2069"
    ]
    for ch in invisible:
        t = t.replace(ch, "")

    # 3) Chỉ giữ lại ký tự hợp lệ: @ A-Z a-z 0-9 _
    t = re.sub(r"[^@A-Za-z0-9_]", "", t)

    # 4) Nếu chưa có @ ở đầu thì tự thêm
    if not t.startswith("@"):
        t = "@" + t

    # Nếu chỉ còn mỗi @ → bỏ
    if t == "@":
        return ""

    print("CLEANED:", repr(t))  # debug
    return t

def safe_mention(t: str) -> str:
    if not t:
        return ""

    # remove ALL invisible chars (double guard)
    BAD = [
        "\u200b", "\u200c", "\u200d",
        "\ufeff", "\u2060",
        "\u202a", "\u202b", "\u202c",
        "\u202d", "\u202e",
        "\u2066", "\u2067", "\u2068", "\u2069"
    ]
    for ch in BAD:
        t = t.replace(ch, "")

    t = t.strip()

    # must start with @
    if not t.startswith("@"):
        t = "@" + t

    # IG-safe chars only
    t = re.sub(r"[^@A-Za-z0-9_.]", "", t)

    if t == "@":
        return ""

    return t

# -------------------------------------------------------
# FIX DUPLICATE OR EMPTY HEADERS
# -------------------------------------------------------
def _rows_to_records(rows):
    if not rows:
        return []
    headers = rows[0]
    unique_headers = []
    seen = {}

    for idx, h in enumerate(headers):
        h = (h or "").strip()
        if not h:
            h = f"column_{idx+1}"
        base = h
        if base in seen:
            seen[base] += 1
            h = f"{base}_{seen[base]}"
        else:
            seen[base] = 0
        unique_headers.append(h)

    records = []
    for row in rows[1:]:
        rec = {}
        for i, key in enumerate(unique_headers):
            rec[key] = row[i] if i < len(row) else ""
        records.append(rec)
    return records

# -------------------------------------------------------
# READ SHEET SAFELY
# -------------------------------------------------------
def read_sheet(sheet_url, credentials_file):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(sheet_url).sheet1

    try:
        return sheet.get_all_records(head=2)
    except:
        rows = sheet.get_all_values()
        return _rows_to_records(rows[1:] if len(rows) > 1 else [])

# -------------------------------------------------------
# Extract username from TikTok URL
# -------------------------------------------------------
def extract_tiktok_username(url: str) -> str:
    url = url.strip()

    if "/@" in url:
        return "@" + url.split("/@")[1].split("/")[0].strip()

    try:
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
        match = re.search(r'"uniqueId":"(.*?)"', html)
        if match:
            return "@" + match.group(1)
    except:
        pass

    return None

# -------------------------------------------------------
# READ TAGS + CLEAN + RANDOM
# -------------------------------------------------------
def read_tags(tag_sheet_url, credential_file):
    rows = read_sheet(tag_sheet_url, credential_file)
    tags = []

    if not rows:
        return ""

    header_keys = list(rows[0].keys())
    possible_keywords = ["url", "link", "tiktok", "profile", "username", "account"]

    url_col = None
    for key in header_keys:
        if any(k in key.lower() for k in possible_keywords):
            url_col = key
            break

    if not url_col:
        return ""

    for r in rows:
        raw_url = str(r.get(url_col, "")).strip()
        if not raw_url:
            continue

        username = extract_tiktok_username(raw_url)
        if not username:
            continue

        cleaned = clean_tag(username)
        if cleaned:
            tags.append(cleaned)

    # 🔒 FINAL VALIDATION – CỰC KỲ QUAN TRỌNG
    final_tags = []
    for t in tags:
        t = safe_mention(t)
        if t:
            final_tags.append(t)

    final_tags = list(set(final_tags))

    if len(final_tags) <= 5:
        return " ".join(final_tags)

    pick_count = random.randint(5, min(10, len(final_tags)))
    picked = random.sample(final_tags, pick_count)

    return " ".join(picked)


# -------------------------------------------------------
# READ SPECIFIC TAB
# -------------------------------------------------------
def read_sheet_tab(sheet_url, tab_name, credentials_file):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url(sheet_url).worksheet(tab_name)

    try:
        return sheet.get_all_records(head=2)
    except:
        rows = sheet.get_all_values()
        return _rows_to_records(rows[1:] if len(rows) > 1 else [])
