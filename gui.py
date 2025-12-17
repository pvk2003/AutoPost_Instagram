import os
from glob import glob
import tkinter as tk
import threading
from tkinter import ttk, filedialog, messagebox

from config import HISTORY_SHEET_URL, CREDENTIAL_FILE, SERVICE_TABS
import webbrowser
import gspread
from oauth2client.service_account import ServiceAccountCredentials


from autopost import post_manual, get_posted_services  # cần hàm này trong autopost.py
from sheet_reader import read_sheet_tab, read_tags
from caption_builder import build_caption
from config import (
    SERVICE_TABS,
    SERVICE_SHEET_URL,
    TAG_SHEET_URL,
    TOP_HASHTAG_MAP,
    CREDENTIAL_FILE,
)
from instagram_bot import InstagramBot


def open_main_gui(username, after_logout_callback=None):
    root = tk.Tk()
    app = AutoPosterGUI(root, username, after_logout_callback)
    root.mainloop()


class AutoPosterGUI:
    def __init__(self, root, username, after_logout_callback=None):
        self.root = root
        self.after_logout_callback = after_logout_callback
        self.logged_in_username = username  # ⬅⬅⬅ FIX QUAN TRỌNG

        self.root.title("Auto IG Poster – Single Post")
        self.root.geometry("980x620")
        self.root.minsize(900, 580)

        # ---- ttk style ----
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background="#0f172a")
        style.configure("Main.TFrame", background="#f3f4f6")
        style.configure("Card.TLabelframe", background="#ffffff")
        style.configure("Card.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 16, "bold"), foreground="#111827")
        style.configure("Sidebar.TLabel", background="#0f172a", foreground="white", font=("Segoe UI", 10))
        style.configure(
            "SidebarTitle.TLabel",
            background="#0f172a",
            foreground="white",
            font=("Segoe UI", 14, "bold"),
        )
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 10))

        # ---- main layout: sidebar + main ----
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

    # ================== UI ==================
    def _build_sidebar(self):
        sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", padding=16)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.rowconfigure(3, weight=1)

        ttk.Label(sidebar, text="Auto IG Poster", style="SidebarTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            sidebar,
            text="Đăng 1 bài Instagram\ncho từng lĩnh vực",
            style="Sidebar.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 12))

        ttk.Button(
            sidebar,
            text="Đổi tài khoản Instagram",
            command=self.change_account,
            style="Accent.TButton",
            width=26,
        ).grid(row=2, column=0, sticky="ew", pady=(4, 4))

        ttk.Button(
            sidebar,
            text="📄 Lịch sử đã đăng",
            command=self.open_history_window,
            style="Accent.TButton",
            width=26,
        ).grid(row=3, column=0, sticky="ew", pady=(4, 4))

        ttk.Separator(sidebar).grid(row=4, column=0, sticky="ew", pady=(12, 12))

        steps_text = (
            "B1. Chọn lĩnh vực\n"
            "B2. Chọn service (chưa đăng)\n"
            "B3. Chọn ảnh\n"
            "B4. Tạo / chỉnh caption\n"
            "B5. Bấm ĐĂNG BÀI"
        )
        ttk.Label(sidebar, text="Quy trình:", style="Sidebar.TLabel").grid(
            row=5, column=0, sticky="w"
        )
        ttk.Label(
            sidebar,
            text=steps_text,
            style="Sidebar.TLabel",
            justify="left",
        ).grid(row=6, column=0, sticky="w", pady=(4, 12))

        self.status_var = tk.StringVar(value="Sẵn sàng.")
        ttk.Label(
            sidebar,
            textvariable=self.status_var,
            style="Sidebar.TLabel",
            wraplength=180,
        ).grid(row=7, column=0, sticky="sw", pady=(12, 0))

    def open_history_window(self):

        # --- Connect Sheet ---
        def connect_sheet():
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)
            client = gspread.authorize(creds)

            first_tab = list(SERVICE_TABS.values())[0]
            return client.open_by_url(HISTORY_SHEET_URL).worksheet(first_tab)

        # --- Load Data ---
        try:
            sheet = connect_sheet()
            records = sheet.get_all_records()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tải được lịch sử Google Sheet:\n{e}")
            return

        # --- UI Window ---
        win = tk.Toplevel(self.root)
        win.title("📄 Lịch sử service đã đăng (Google Sheet)")
        win.geometry("850x600")
        win.resizable(True, True)

        frame = ttk.Frame(win, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Lịch sử đăng bài (Google Sheet)",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 12))

        # --- Table ---
        columns = ("service", "url", "date")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)

        tree.heading("service", text="Service Name")
        tree.heading("url", text="Post URL")
        tree.heading("date", text="Date")

        tree.column("service", width=280)
        tree.column("url", width=320)
        tree.column("date", width=120)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        # --- Load rows ---
        for r in records:
            tree.insert("", "end", values=(
                r.get("Service Name", ""),
                r.get("Post URL", ""),
                r.get("Date", "")
            ))

        # --- Double click open URL ---
        def open_url(event):
            item = tree.selection()
            if not item:
                return
            url = tree.item(item, "values")[1]
            if url.startswith("http"):
                webbrowser.open(url)

        tree.bind("<Double-1>", open_url)

        # ======================
        # Buttons
        # ======================
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=12)

        # Delete one row
        def delete_selected():
            sel = tree.selection()
            if not sel:
                return messagebox.showwarning("Thông báo", "Hãy chọn dòng để xóa.")

            index = tree.index(sel)
            tree.delete(sel)

            try:
                sheet.delete_rows(index + 2)
                messagebox.showinfo("OK", "Đã xóa khỏi Google Sheet.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không xóa được:\n{e}")

        # Delete all
        def delete_all():
            if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa toàn bộ lịch sử?"):
                return

            try:
                sheet.clear()
                sheet.append_row(["Service Name", "Post URL", "Date"])
                tree.delete(*tree.get_children())
                messagebox.showinfo("OK", "Đã xóa toàn bộ lịch sử.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa:\n{e}")

        ttk.Button(btn_frame, text="❌ Xóa dòng chọn", width=20, command=delete_selected).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="🗑 Xóa toàn bộ", width=20, command=delete_all).grid(row=0, column=1, padx=10)


    def _build_main_area(self):
        main = ttk.Frame(self.root, style="Main.TFrame", padding=18)
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)

        ttk.Label(
            main,
            text="Đăng bài Instagram theo service",
            style="Heading.TLabel",
        ).grid(row=0, column=0, sticky="w")

        # ---- Card 1: chọn lĩnh vực / service / ảnh ----
        form_card = ttk.Labelframe(
            main,
            text="Bước 1–3: Chọn dịch vụ & ảnh",
            style="Card.TLabelframe",
            padding=16,
        )
        form_card.grid(row=1, column=0, sticky="ew", pady=(12, 8))
        for i in range(3):
            form_card.columnconfigure(i, weight=1)

        # Lĩnh vực
        ttk.Label(form_card, text="Lĩnh vực:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.field_var = tk.StringVar()
        self.field_box = ttk.Combobox(
            form_card,
            textvariable=self.field_var,
            values=list(SERVICE_TABS.keys()),
            state="readonly",
        )
        self.field_box.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(2, 8))
        self.field_box.bind("<<ComboboxSelected>>", self.load_services)

        # Service
        ttk.Label(form_card, text="Service:", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=1, sticky="w"
        )
        self.service_var = tk.StringVar()
        self.service_box = ttk.Combobox(
            form_card,
            textvariable=self.service_var,
            state="readonly",
        )
        self.service_box.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(2, 8))

        # Ảnh
        ttk.Label(
            form_card,
            text="Ảnh Instagram:",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=2, sticky="w")
        img_frame = ttk.Frame(form_card)
        img_frame.grid(row=1, column=2, sticky="ew", pady=(2, 8))
        img_frame.columnconfigure(0, weight=1)

        self.image_path_var = tk.StringVar(value="")
        self.image_label = ttk.Label(img_frame, textvariable=self.image_path_var, width=32)
        self.image_label.grid(row=0, column=0, sticky="w")

        ttk.Button(img_frame, text="Chọn ảnh...", command=self.select_image).grid(
            row=0, column=1, padx=(8, 0)
        )

        # ---- Card 2: caption ----
        caption_card = ttk.Labelframe(
            main,
            text="Bước 4: Caption (có thể chỉnh sửa trước khi đăng)",
            style="Card.TLabelframe",
            padding=16,
        )
        caption_card.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        caption_card.columnconfigure(0, weight=1)
        caption_card.rowconfigure(1, weight=1)

        btn_frame = ttk.Frame(caption_card)
        btn_frame.grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Button(
            btn_frame,
            text="Tạo / Refresh caption",
            command=self.preview_caption,
        ).grid(row=0, column=0)

        self.caption_box = tk.Text(
            caption_card,
            height=12,
            wrap="word",
            font=("Segoe UI", 10),
        )
        self.caption_box.grid(row=1, column=0, sticky="nsew")

        # ---- Action bottom: nút Đăng bài ----
        action_frame = ttk.Frame(main, style="Main.TFrame", padding=(0, 8, 0, 0))
        action_frame.grid(row=3, column=0, sticky="ew")
        action_frame.columnconfigure(0, weight=1)

        ttk.Button(
            action_frame,
            text="🚀 ĐĂNG BÀI LÊN INSTAGRAM",
            command=self.post_now,
            style="Accent.TButton",
        ).grid(row=0, column=0, sticky="ew")

    # ================== LOGIC ==================
    def load_services(self, *_):
        field = self.field_var.get()
        if not field:
            return

        tab_name = SERVICE_TABS[field]
        self.status_var.set(f"Đang tải service từ tab: {tab_name!r} ...")
        self.root.update_idletasks()

        def load_bg():
            try:
                rows = read_sheet_tab(SERVICE_SHEET_URL, tab_name, CREDENTIAL_FILE)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không đọc được tab '{tab_name}': {e}"))
                self.root.after(0, lambda: self.status_var.set("Lỗi đọc Google Sheet."))
                return

            self.root.after(0, lambda: self._populate_services(rows, tab_name))

        threading.Thread(target=load_bg, daemon=True).start()

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Chọn ảnh để đăng",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.image_path_var.set(path)

    def _populate_services(self, rows, tab_name):
        if not rows:
            messagebox.showwarning("Thông báo", f"Tab '{tab_name}' chưa có dữ liệu.")
            self.service_box["values"] = []
            self.service_var.set("")
            self.status_var.set("Không có service nào.")
            return

        # Xác định cột service
        header_keys = list(rows[0].keys())
        service_col = None
        for h in header_keys:
            if "service" in h.lower():
                service_col = h
                break

        if not service_col:
            service_col = header_keys[1] if len(header_keys) >= 2 else header_keys[0]

        all_services = [
            str(r.get(service_col, "")).strip()
            for r in rows
            if str(r.get(service_col, "")).strip()
        ]

        try:
            posted = set(get_posted_services())
        except:
            posted = set()

        available = [s for s in all_services if s not in posted]

        self.service_box["values"] = available
        if available:
            self.service_var.set(available[0])
            self.status_var.set(f"Đã tải {len(available)} service (chưa đăng).")
        else:
            self.service_var.set("")
            messagebox.showinfo("Thông báo", "🎉 Tất cả service đã đăng hết!")
            self.status_var.set("Không còn service chưa đăng.")

    def preview_caption(self):
        field = self.field_var.get()
        service = self.service_var.get()

        if not field or not service:
            messagebox.showerror("Lỗi", "Hãy chọn Lĩnh vực và Service trước.")
            return

        try:
            tags = read_tags(TAG_SHEET_URL, CREDENTIAL_FILE)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không đọc được sheet tags: {e}")
            return

        top_hashtag = TOP_HASHTAG_MAP.get(field, "")
        caption = build_caption(service, top_hashtag, tags)

        self.caption_box.delete("1.0", tk.END)
        self.caption_box.insert(tk.END, caption)
        self.status_var.set("Đã tạo caption. Bạn có thể chỉnh lại trước khi đăng.")

    def post_now(self):
        service = self.service_var.get()
        img = self.image_path_var.get()
        caption = self.caption_box.get("1.0", tk.END).strip()

        if not service:
            return messagebox.showerror("Lỗi", "Chưa chọn service.")
        if not img:
            return messagebox.showerror("Lỗi", "Chưa chọn ảnh.")
        if not caption:
            return messagebox.showerror("Lỗi", "Caption đang trống.")

        if not messagebox.askyesno("Xác nhận",
            f"Bạn chắc chắn muốn đăng service:\n\n{service}\n\nlên Instagram?"):
            return

        self.status_var.set("Đang đăng bài lên Instagram ...")
        self.root.update_idletasks()

        def post_bg():
            try:
                field = self.field_var.get()
                url = post_manual(service, field, img, caption, username=self.logged_in_username)

                self.root.after(0, lambda: setattr(self, "loading", False))  # ⬅ THÊM DÒNG NÀY

                self.root.after(0, lambda:
                    messagebox.showinfo("Thành công", f"Đăng bài thành công!\n\nLink: {url}")
                )
                self.root.after(0, self.load_services)
                self.root.after(0, lambda: self.status_var.set("Đã đăng xong."))

            except Exception as e:
                self.root.after(0, lambda: setattr(self, "loading", False))  # ⬅ THÊM DÒNG NÀY
                self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
                self.root.after(0, lambda: self.status_var.set("Lỗi khi đăng bài."))

        threading.Thread(target=post_bg, daemon=True).start()

        # --- SPINNER LOADING ---
        self.loading = True
        def spin(i=0):
            if not self.loading:
                return
            symbols = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
            self.status_var.set("Đang đăng bài... " + symbols[i % len(symbols)])
            self.root.after(120, lambda: spin(i+1))
        spin()

    def change_account(self):
        # import os
        # from glob import glob

        print("\n=== BẮT ĐẦU XOÁ SESSION ===")

        # Xóa tất cả session_*.json
        sessions = glob("session_*.json")
        if not sessions:
            print("Không có file session nào để xoá.")
        else:
            for f in sessions:
                try:
                    os.remove(f)
                    print(f"🗑 Đã xoá session: {f}")
                except Exception as e:
                    print(f"⚠ Lỗi khi xoá {f}: {e}")

        print("=== XOÁ SESSION HOÀN TẤT ===\n")

        messagebox.showinfo(
            "Đăng xuất",
            "Đã đăng xuất khỏi Instagram.\nVui lòng đăng nhập lại.",
        )

        # ĐÓNG GUI HIỆN TẠI
        self.root.destroy()

        # GỌI LẠI LOGIN GUI
        if self.after_logout_callback:
            self.after_logout_callback()

if __name__ == "__main__":
    open_main_gui()
