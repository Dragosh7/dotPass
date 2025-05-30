from customtkinter import *
import os, json, hashlib
from tkinter import messagebox
from core.hashing import get_or_create_salt
from core.encryption import derive_key, encrypt_data
from utils.config import SALT_PATH, MASTER_HASH_PATH, DUMMY_HASH_PATH, PROFILE_PATH
from utils.setup import protect_file
from utils.style import TITLE_FONT, SUB_FONT, APP_FONT, SMALL_FONT, HEADER_FONT  # 👈 fonturi globale


class CreateProfilePage:
    def __init__(self):
        self.root = CTk()
        self.root.title("Create Profile")
        self.root.geometry("400x520")
        self.root.resizable(False, False)
        self.center_window(self.root)

        CTkLabel(self.root, text="👤", font=TITLE_FONT).pack(pady=(20, 5))

        self.name_entry = CTkEntry(self.root, placeholder_text="Full Name", font=APP_FONT)
        self.name_entry.pack(pady=10, padx=30)

        self.master_entry = CTkEntry(self.root, placeholder_text="Master Password", show="*", font=APP_FONT)
        self.master_entry.pack(pady=10, padx=30)

        self.confirm_entry = CTkEntry(self.root, placeholder_text="Confirm Password", show="*", font=APP_FONT)
        self.confirm_entry.pack(pady=10, padx=30)

        self.dummy_entry = CTkEntry(self.root, placeholder_text="Dummy Password", show="*", font=APP_FONT)
        self.dummy_entry.pack(pady=10, padx=30)

        self.dummy_warning_shown = False

        self.show_pw_var = BooleanVar()
        CTkCheckBox(self.root, text="Show Passwords", variable=self.show_pw_var,
                    command=self.toggle_password, font=SMALL_FONT).pack(pady=5)

        CTkButton(self.root, text="Create Profile", command=self.create_profile, font=APP_FONT).pack(pady=25)

        self.root.mainloop()

    def toggle_password(self):
        state = "" if self.show_pw_var.get() else "*"
        self.master_entry.configure(show=state)
        self.confirm_entry.configure(show=state)
        self.dummy_entry.configure(show=state)

    def center_window(self, win):
        win.update_idletasks()
        w, h = 400, 520
        x = (win.winfo_screenwidth() // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

    def show_restart_popup(self):
        popup = CTkToplevel(self.root)
        popup.title("dotPass - Configuring")
        popup.geometry("340x160")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()

        popup.attributes("-alpha", 1.0)
        self.center_window(popup)

        CTkLabel(popup, text="Configuring dotPass...", font=HEADER_FONT, text_color="#2F80ED").pack(pady=(25, 8))
        CTkLabel(popup, text="App will close automatically.", font=SUB_FONT).pack()

        progress = CTkProgressBar(popup, orientation="horizontal", mode="indeterminate", width=220)
        progress.pack(pady=20)
        progress.start()

        def shutdown():
            popup.destroy()
            self.root.destroy()
            os._exit(0)

        popup.after(3500, shutdown)

    def create_profile(self):
        name = self.name_entry.get().strip()
        master = self.master_entry.get()
        confirm = self.confirm_entry.get()
        dummy = self.dummy_entry.get()

        if not all([name, master, confirm]):
            messagebox.showerror("Error", "Please fill in name and master password.")
            return

        if master != confirm:
            messagebox.showerror("Error", "Master passwords do not match.")
            return

        if master == dummy:
            messagebox.showerror("Error", "Master password must not match with dummy password.")
            return


        if dummy.strip() == "":
            if not self.dummy_warning_shown:
                self.dummy_warning_shown = True
                messagebox.showwarning(
                    "Missing Dummy Password",
                    "We recommend setting a dummy password for emergency situations.\n\nClick 'Create Profile' again to continue without it."
                )
                return

        salt = get_or_create_salt(SALT_PATH)
        master_hash = hashlib.sha256(master.encode() + salt).hexdigest()

        with open(MASTER_HASH_PATH, 'w') as f:
            f.write(master_hash)
            protect_file(MASTER_HASH_PATH)

        if dummy.strip():
            dummy_hash = hashlib.sha256(dummy.encode() + salt).hexdigest()
            with open(DUMMY_HASH_PATH, 'w') as f:
                f.write(dummy_hash)
                protect_file(DUMMY_HASH_PATH)

        with open(PROFILE_PATH, 'w') as f:
            json.dump({"name": name}, f)

        self.show_restart_popup()
