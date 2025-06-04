import json
import hashlib
import datetime
from core.breach_check import check_password_breach
from utils.config import PROFILE_PATH
from customtkinter import *
from PIL import Image
from utils.layout import center_window
from core.encryption import derive_key
from core.hashing import get_or_create_salt
from utils.config import SALT_PATH, MASTER_HASH_PATH, DUMMY_HASH_PATH, DB_PATH, DUMMY_PATH
from ui.main_page import MainPage
from core.db import load_or_create_vault
from customtkinter import get_appearance_mode
from utils.style import APP_FONT, TITLE_FONT, SUB_FONT, SMALL_FONT  # 👈 fonturi globale

feedback_label = None
appearance_switch = None
app = None
is_dummy_mode = False

def validate_password(master_password):
    salt = get_or_create_salt(SALT_PATH)
    hash_input = hashlib.sha256(master_password.encode() + salt).hexdigest()

    if not os.path.exists(MASTER_HASH_PATH):
        with open(MASTER_HASH_PATH, 'w') as f:
            f.write(hash_input)
        return True
    else:
        with open(MASTER_HASH_PATH, 'r') as f:
            saved_hash = f.read().strip()
        return hash_input == saved_hash

def show_loading_and_validate(password_entry, app_frame):
    global feedback_label, app, is_dummy_mode

    was_maximized = app.state() == "zoomed"

    try:
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, "r+") as f:
                profile_data = json.load(f)
                profile_data["maximized"] = was_maximized
                f.seek(0)
                json.dump(profile_data, f)
                f.truncate()
    except Exception as e:
        print("Failed to update profile.json with maximized state:", e)

    try:
        with open(PROFILE_PATH, "r") as f:
            was_maximized = json.load(f).get("maximized", False)
    except:
        was_maximized = False

    if feedback_label is not None:
        feedback_label.destroy()
        feedback_label = None

    feedback_label = CTkLabel(app_frame, text="Validating password...", font=SUB_FONT)
    feedback_label.pack(pady=10)

    password = password_entry.get()
    salt = get_or_create_salt(SALT_PATH)
    hash_input = hashlib.sha256(password.encode() + salt).hexdigest()

    with open(MASTER_HASH_PATH, 'r') as f:
        master_hash = f.read().strip()

    dummy_hash = None
    if os.path.exists(DUMMY_HASH_PATH):
        with open(DUMMY_HASH_PATH, 'r') as f:
            dummy_hash = f.read().strip()

    if hash_input == master_hash:
        is_dummy_mode = False
        db_path = DB_PATH
    elif dummy_hash and hash_input == dummy_hash:
        is_dummy_mode = True
        db_path = DUMMY_PATH
    else:
        feedback_label.configure(
            text="Master password is incorrect",
            text_color="#E53935",
            font=SMALL_FONT
        )
        return

    feedback_label.configure(text="Success! Access granted.", font=SUB_FONT)
    key = derive_key(password, salt)
    conn = load_or_create_vault(key, db_path)
    feedback_label.destroy()
    password_entry.delete(0, END)

    app.withdraw()
    MainPage(master_key=key, connection=conn, on_logout=lambda: app.deiconify(), is_dummy=is_dummy_mode, was_maximized=was_maximized)

def update_dropdown_style():
    global appearance_switch
    if appearance_switch:
        mode = get_appearance_mode()
        bg_color = "#FFFFFF" if mode == "Light" else "#1E1E1E"
        appearance_switch.configure(
            fg_color=bg_color,
            button_color=bg_color,
            dropdown_fg_color=bg_color,
            dropdown_hover_color="#2F80ED",
            text_color="#2F80ED"
        )

def launch_app():
    global feedback_label, appearance_switch, app

    if app is not None:
        app.deiconify()
        return

    feedback_label = None
    appearance_switch = None

    username = ""
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, 'r') as f:
                data = json.load(f)
                full_name = data.get("name", "").strip()
                username = full_name.split()[0] if full_name else ""
        except Exception:
            pass

    set_appearance_mode("System")
    set_default_color_theme("ui/themes/premium-blue.json")

    app = CTk()
    center_window(app, 700, 480)
    app.resizable(True, True)
    app.title("dotPass")

    # --- LEFT IMAGE ---
    try:
        side_img = CTkImage(light_image=Image.open("ui/images/side-img.png"),
                            dark_image=Image.open("ui/images/side-img.png"),
                            size=(256, 256))
        CTkLabel(master=app, text="", image=side_img).pack(expand=False, side="left")
    except:
        pass

    # --- RIGHT FRAME ---
    frame = CTkFrame(master=app, width=400, height=480)
    frame.pack_propagate(0)
    frame.pack(expand=True, side="right", fill="both")

    welcome_text = f"Welcome to dotPass{', ' + username if username else ''}!"
    CTkLabel(master=frame, text=welcome_text,
             anchor="w", justify="left", font=TITLE_FONT).pack(anchor="w", pady=(40, 5), padx=(25, 0))

    CTkLabel(master=frame, text="Enter your Master Password", text_color="#7E7E7E",
             anchor="w", justify="left", font=SUB_FONT).pack(anchor="w", padx=(25, 0))

    password_entry = CTkEntry(master=frame, placeholder_text="Master Password", show="*", width=240, font=APP_FONT)
    password_entry.pack(anchor="w", pady=(20, 0), padx=(25, 0))

    CTkButton(master=frame, text="Login", width=240, font=APP_FONT,
              command=lambda: show_loading_and_validate(password_entry, frame)).pack(anchor="w", pady=(20, 0),
                                                                                     padx=(25, 0))

    # --- THEME DROPDOWN SWITCHER ---
    theme_frame = CTkFrame(master=app, fg_color="transparent")
    theme_frame.place(relx=0.97, rely=0.93, anchor="se")

    CTkLabel(master=theme_frame,
             text="Select App Theme",
             text_color="#7E7E7E",
             font=SMALL_FONT,
             anchor="e",
             justify="right").pack(anchor="e", padx=5)

    def change_appearance(choice):
        set_appearance_mode(choice)
        update_dropdown_style()

    current_mode = get_appearance_mode()
    bg_color = "#FFFFFF" if current_mode == "Light" else "#1E1E1E"

    appearance_switch = CTkOptionMenu(master=theme_frame,
                                      values=["Light", "Dark"],
                                      command=change_appearance,
                                      fg_color=bg_color,
                                      button_color=bg_color,
                                      dropdown_fg_color=bg_color,
                                      dropdown_hover_color="#2F80ED",
                                      text_color="#2F80ED",
                                      width=120,
                                      height=28,
                                      corner_radius=8)

    appearance_switch.set(current_mode)
    appearance_switch.pack(anchor="e", padx=5, pady=(2, 0))

    app.mainloop()
