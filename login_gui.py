import tkinter as tk
from tkinter import ttk, messagebox
from instagram_bot import InstagramBot, login_with_sessionid
import threading

# ======================================================
#                CUSTOM ROUNDED BUTTON
# ======================================================
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None,
                 radius=16, padding_x=28, padding_y=14,
                 bg="#2563eb", fg="white",
                 hover_bg="#1d4ed8", pressed_bg="#1e40af",
                 font=("Segoe UI", 11, "bold")):

        safe_bg = parent.winfo_toplevel().cget("background")

        tk.Canvas.__init__(self, parent, highlightthickness=0, bg=safe_bg)
        self.command = command

        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.pressed_bg = pressed_bg
        self.font = font
        self.radius = radius

        # Tính kích thước
        temp = self.create_text(0, 0, text=text, font=font, anchor="nw")
        bbox = self.bbox(temp)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        self.delete(temp)

        width = text_w + padding_x * 2
        height = text_h + padding_y * 2

        self.configure(width=width, height=height)

        # Bóng very soft
        self.shadow = self.create_rounded_rect(
            2, 4, width - 2, height + 3, radius,
            fill="#b3b3b3",
            outline=""
        )

        # Nút chính
        self.rect = self.create_rounded_rect(0, 0, width, height, radius, fill=bg, outline=bg)

        # Text
        self.text_obj = self.create_text(
            width // 2,
            height // 2,
            text=text, font=font,
            fill=fg, anchor="center"
        )

        self.tag_raise(self.rect)
        self.tag_raise(self.text_obj)

        # Events
        self.bind("<Enter>", lambda e: self._set_color(self.hover_bg))
        self.bind("<Leave>", lambda e: self._set_color(self.bg))
        self.bind("<ButtonPress-1>", lambda e: self._set_color(self.pressed_bg))
        self.bind("<ButtonRelease-1>", self._on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y1 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kw)

    def _set_color(self, color):
        self.itemconfig(self.rect, fill=color, outline=color)

    def _on_click(self, e):
        self._set_color(self.hover_bg)
        if self.command:
            self.command()


# ======================================================
#                    LOGIN GUI
# ======================================================
def open_login_gui(after_login_callback=None):
    root = tk.Tk()
    root.title("Instagram Login")
    root.geometry("780x470")
    root.resizable(False, False)

    # ----------------- SET GLOBAL BACKGROUND -----------------
    root.configure(bg="#f3f4f6")

    # ----------------- STYLE (TTK) -----------------
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Sidebar.TFrame", background="#0f172a")
    style.configure("SidebarTitle.TLabel", background="#0f172a",
                    foreground="white", font=("Segoe UI", 18, "bold"))
    style.configure("Sidebar.TLabel", background="#0f172a",
                    foreground="white", font=("Segoe UI", 11))

    style.configure("Main.TFrame", background="#f3f4f6")

    style.configure("Card.TFrame", background="#ffffff",
                    relief="solid", borderwidth=1)
    style.configure("CardTitle.TLabel", background="#ffffff",
                    foreground="#111827", font=("Segoe UI", 16, "bold"))

    # ----------------- MAIN LAYOUT -----------------
    root.columnconfigure(0, weight=0)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    # ----------------- SIDEBAR -----------------
    sidebar = ttk.Frame(root, style="Sidebar.TFrame", padding=32)
    sidebar.grid(row=0, column=0, sticky="ns")

    ttk.Label(sidebar, text="Auto IG Poster",
              style="SidebarTitle.TLabel").pack(anchor="w")

    ttk.Label(sidebar,
              text="\nĐăng nhập để bắt đầu\nsử dụng hệ thống đăng bài.",
              style="Sidebar.TLabel",
              justify="left").pack(anchor="w")

    # ----------------- MAIN AREA -----------------
    main = ttk.Frame(root, style="Main.TFrame", padding=40)
    main.grid(row=0, column=1, sticky="nsew")
    main.columnconfigure(0, weight=1)

    card = ttk.Frame(main, style="Card.TFrame", padding=24)
    card.grid(row=0, column=0, sticky="nsew")
    card.columnconfigure(0, weight=1)
    card.rowconfigure(1, weight=1)

    ttk.Label(card, text="Đăng nhập Instagram",
              style="CardTitle.TLabel").grid(row=0, column=0, pady=(0, 16), sticky="w")

    # ----------------- NOTEBOOK 2 TAB -----------------
    notebook = ttk.Notebook(card)
    notebook.grid(row=1, column=0, sticky="nsew")

    # ==== TAB 1: PASSWORD LOGIN ====
    pw_tab = ttk.Frame(notebook)
    notebook.add(pw_tab, text="Đăng nhập bằng mật khẩu")

    # Username
    ttk.Label(pw_tab, text="Username / Email:",
              background="#ffffff", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(8, 2))
    username_var = tk.StringVar()
    ttk.Entry(pw_tab, textvariable=username_var, width=40).grid(row=1, column=0, sticky="w", pady=(0, 8))

    # Password
    ttk.Label(pw_tab, text="Password:",
              background="#ffffff", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w", pady=(8, 2))
    password_var = tk.StringVar()
    password_entry = ttk.Entry(pw_tab, textvariable=password_var, width=40, show="*")
    password_entry.grid(row=3, column=0, sticky="w", pady=(0, 8))

    show_pw_var = tk.BooleanVar(value=False)

    def toggle_pw():
        password_entry.config(show="" if show_pw_var.get() else "*")

    ttk.Checkbutton(pw_tab, text="Hiện mật khẩu",
                    variable=show_pw_var,
                    command=toggle_pw).grid(row=4, column=0, sticky="w", pady=(0, 8))

    loading_pw_var = tk.StringVar(value="")
    ttk.Label(pw_tab, textvariable=loading_pw_var,
              background="#ffffff", foreground="#2563eb",
              font=("Segoe UI", 10, "italic")).grid(row=5, column=0, sticky="w", pady=(4, 4))

    # ==== TAB 2: SESSIONID LOGIN ====
    sid_tab = ttk.Frame(notebook)
    notebook.add(sid_tab, text="Login bằng SESSIONID")

    info_text = (
        "Hướng dẫn lấy SESSIONID:\n"
        "1. Mở instagram.com trên Chrome và đăng nhập tài khoản.\n"
        "2. Nhấn F12 → tab Application → Cookies → instagram.com.\n"
        "3. Tìm dòng 'sessionid' → copy giá trị.\n"
        "4. Dán vào ô bên dưới và bấm Đăng nhập."
    )
    ttk.Label(sid_tab, text=info_text,
              background="#ffffff",
              justify="left",
              font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=(4, 8))

    ttk.Label(sid_tab, text="SessionID:",
              background="#ffffff",
              font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", pady=(4, 2))

    sessionid_var = tk.StringVar()
    ttk.Entry(sid_tab, textvariable=sessionid_var, width=50).grid(row=2, column=0, sticky="w", pady=(0, 8))

    loading_sid_var = tk.StringVar(value="")
    ttk.Label(sid_tab, textvariable=loading_sid_var,
              background="#ffffff", foreground="#2563eb",
              font=("Segoe UI", 10, "italic")).grid(row=3, column=0, sticky="w", pady=(4, 4))

    # ----------------- LOGIN FUNCTIONS -----------------
    def do_login_password(event=None):
        username = username_var.get().strip()
        password = password_var.get().strip()

        if not username or not password:
            return messagebox.showerror("Lỗi", "Vui lòng nhập đủ Username và Password.")

        loading_pw_var.set("⏳ Đang đăng nhập vào Instagram...")
        pw_login_btn._set_color("#475569")
        pw_login_btn.unbind("<ButtonPress-1>")

        def login_bg():
            try:
                InstagramBot(username, password)

                def on_success():
                    loading_pw_var.set("⭐ Đăng nhập thành công!")
                    messagebox.showinfo("Thành công", "Đăng nhập thành công!")

                    root.destroy()
                    if after_login_callback:
                        after_login_callback(username)

                root.after(0, on_success)

            except Exception as e:
                def on_fail(error=e):
                    loading_pw_var.set("")
                    messagebox.showerror("Đăng nhập thất bại", str(error))
                    pw_login_btn._set_color(pw_login_btn.bg)

                root.after(0, on_fail)

        threading.Thread(target=login_bg, daemon=True).start()

    def do_login_sessionid():
        sid = sessionid_var.get().strip()
        if not sid:
            return messagebox.showerror("Lỗi", "Vui lòng dán SESSIONID trước.")

        loading_sid_var.set("⏳ Đang đăng nhập bằng SESSIONID...")

        def login_bg():
            try:
                username = login_with_sessionid(sid)

                def on_success():
                    loading_sid_var.set("⭐ Đăng nhập bằng SessionID thành công!")
                    messagebox.showinfo(
                        "Thành công",
                        f"Đăng nhập thành công với user: {username}"
                    )
                    root.destroy()
                    if after_login_callback:
                        after_login_callback(username)

                root.after(0, on_success)

            except Exception as e:
                def on_fail(error=e):
                    loading_sid_var.set("")
                    messagebox.showerror("Đăng nhập thất bại", str(error))

                root.after(0, on_fail)

        threading.Thread(target=login_bg, daemon=True).start()

    # ----------------- BUTTONS -----------------
    pw_login_btn = RoundedButton(
        pw_tab,
        text="Đăng nhập",
        command=do_login_password,
        bg="#2563eb",
        hover_bg="#1d4ed8",
        pressed_bg="#1e40af",
        fg="white",
    )
    pw_login_btn.grid(row=6, column=0, pady=(8, 4), sticky="w")

    sid_login_btn = RoundedButton(
        sid_tab,
        text="Đăng nhập bằng SessionID",
        command=do_login_sessionid,
        bg="#2563eb",
        hover_bg="#1d4ed8",
        pressed_bg="#1e40af",
        fg="white",
    )
    sid_login_btn.grid(row=4, column=0, pady=(8, 4), sticky="w")

    # Enter ở tab password = login
    root.bind("<Return>", do_login_password)

    root.mainloop()
