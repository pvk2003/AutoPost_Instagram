import os
from login_gui import open_login_gui
from gui import open_main_gui

def start_app(username=None):
    print(">>> start_app RUN, username =", username)

    if username:
        return open_main_gui(username=username, after_logout_callback=start_app)

    sessions = [f for f in os.listdir() if f.startswith("session_") and f.endswith(".json")]

    if sessions:
        username = sessions[0].replace("session_", "").replace(".json", "")
        return open_main_gui(username=username, after_logout_callback=start_app)

    open_login_gui(after_login_callback=start_app)


if __name__ == "__main__":
    start_app()
