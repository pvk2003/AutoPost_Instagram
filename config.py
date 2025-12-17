# IG_USERNAME = "thanhduong2025ca@gmail.com"
# IG_PASSWORD = "FbHenry@2024CA"

# 1 URL CHUNG – KHÔNG CÓ gid hoặc #gid
SERVICE_SHEET_URL = "https://docs.google.com/spreadsheets/d/19SNOSF4UzB4FtTh2Uvv74MWa4Pc7l0ldpjIdmA6moI4/edit"

# Mapping: Tên lĩnh vực -> Tên TAB y chang trong Google Sheets
SERVICE_TABS = {
    "Internship": "Internship",
    "Human Resource Management (HRM)": "Human Resource Management (HRM)",
    "Volunteer": "Volunteer",
    "Tokenization": "Tokenization",
    "Compound Option Leadership": "Compound Option Leadership ",  # ← có space cuối
    "Billion/Trillionaire": "Billion/Trillionaire ",            # ← có space cuối
    "Open source": "Open source  ",                             # ← 2 space cuối
    "Gen AI & AI": "Gen AI & AI ",                              # ← space cuối
    "Funding": "Funding"
}

# TAG SHEET — CŨNG PHẢI BỎ gid/#gid
TAG_SHEET_URL = "https://docs.google.com/spreadsheets/d/1XDlQ51k9tw04B5i0Ux8HmOV6VOrHCb2CsFWPd66hnDU/edit"

CREDENTIAL_FILE = "credentials.json"

TOP_HASHTAG_MAP = {
    "Internship": "#internship",
    "Human Resource Management (HRM)": "#humanresource",
    "Volunteer": "#volunteer",
    "Tokenization": "#tokenization",
    "Compound Option Leadership": "#compoundoptionleadership",
    "Billion/Trillionaire": "#billion #trillionaire",   # ← sửa lại, bỏ space 2 bên dấu /
    "Open source": "#opensource",
    "Gen AI & AI": "#ai",
    "Funding": "#funding"
}

HISTORY_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Wmwl8MkHRO5a8ObiECSvwcVTzYl9sNRQ8Spl9PAXiro/edit"

# Tab lịch sử dùng cùng tên tab với SERVICE_TABS
HISTORY_TABS = SERVICE_TABS
