import json
import os
import hashlib
from utils.config import PROFILE_PATH
from customtkinter import *
from PIL import Image
from utils.layout import center_window
from core.encryption import derive_key
from core.hashing import get_or_create_salt
from utils.config import SALT_PATH, MASTER_HASH_PATH
from customtkinter import get_appearance_mode
from ui.main_page import MainPage
from core.db import load_or_create_vault

# Variabile globale
feedback_label = None
appearance_switch = None
app = None


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
    global feedback_label, app

    if feedback_label is not None:
        feedback_label.destroy()
        feedback_label = None

    feedback_label = CTkLabel(app_frame, text="Validating password...", font=("Arial", 14))
    feedback_label.pack(pady=10)

    password = password_entry.get()
    if validate_password(password):
        feedback_label.configure(text="Success! Access granted.")
        salt = get_or_create_salt(SALT_PATH)
        key = derive_key(password, salt)
        conn = load_or_create_vault(key)

        feedback_label.destroy()
        password_entry.delete(0, END)

        app.withdraw()
        MainPage(master_key=key, connection=conn, on_logout=lambda: app.deiconify())

    else:
        feedback_label.configure(
            text="Master password is incorrect",
            text_color="#E53935",
            font=("Arial", 13, "bold")
        )

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
    # app.geometry("600x480")
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

    if username and len(username) > 10:
        welcome_text = f"Welcome to dotPass,\n{username}!"
    elif username:
        welcome_text = f"Welcome to dotPass, {username}!"
    else:
        welcome_text = "Welcome to dotPass"
    CTkLabel(master=frame, text=welcome_text,
             anchor="w", justify="left",
             font=("Arial Bold", 22)).pack(anchor="w", pady=(40, 5), padx=(25, 0))

    CTkLabel(master=frame, text="Enter your Master Password", text_color="#7E7E7E", anchor="w",
             justify="left", font=("Arial", 12)).pack(anchor="w", padx=(25, 0))

    password_entry = CTkEntry(master=frame, placeholder_text="Master Password", show="*", width=240)
    password_entry.pack(anchor="w", pady=(20, 0), padx=(25, 0))

    CTkButton(master=frame, text="Login", width=240,
              command=lambda: show_loading_and_validate(password_entry, frame)).pack(anchor="w", pady=(20, 0),
                                                                                     padx=(25, 0))

    # --- THEME DROPDOWN SWITCHER ---
    theme_frame = CTkFrame(master=app, fg_color="transparent")
    theme_frame.place(relx=0.97, rely=0.93, anchor="se")

    CTkLabel(master=theme_frame,
             text="Select App Theme",
             text_color="#7E7E7E",
             font=("Arial", 10),
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
