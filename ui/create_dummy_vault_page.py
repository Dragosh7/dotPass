from customtkinter import *
from tkinter import messagebox
import hashlib
from utils.layout import center_window
from utils.config import SALT_PATH, DUMMY_HASH_PATH
from core.hashing import get_or_create_salt
from utils.style import TITLE_FONT, SUB_FONT, APP_FONT, SMALL_FONT
from PIL import Image
from customtkinter import CTkImage

class CreateDummyVaultPage:
    def __init__(self, parent, on_done):
        self.on_done = on_done

        self.root = CTkToplevel(parent)
        self.root.title("Create Dummy Password")
        self.root.geometry("400x360")
        self.root.resizable(False, False)
        center_window(self.root, 400, 360)
        self.root.grab_set()
        self.root.focus_force()

        # Optional icon at top
        try:
            icon = CTkImage(Image.open("ui/images/sun.png"), size=(64, 64))
            CTkLabel(self.root, text="", image=icon).pack(pady=(15, 0))
        except:
            pass

        CTkLabel(self.root, text="Dummy Vault Setup", font=TITLE_FONT, text_color="#2F80ED").pack(pady=(10, 5))
        CTkLabel(self.root,
                 text="You have not yet configured a Dummy Vault. This is used for emergency situations.\nEnter and confirm a password:",
                 font=SUB_FONT,
                 justify="center",
                 wraplength=360).pack(pady=(0, 10))

        self.entry1 = CTkEntry(self.root, placeholder_text="Enter Dummy Password", show="*", font=APP_FONT, width=280)
        self.entry1.pack(pady=5)

        self.entry2 = CTkEntry(self.root, placeholder_text="Confirm Dummy Password", show="*", font=APP_FONT, width=280)
        self.entry2.pack(pady=5)

        # Show/hide password
        self.show_pw_var = BooleanVar()
        CTkCheckBox(self.root, text="Show Password", variable=self.show_pw_var, command=self.toggle_password,
                    font=SMALL_FONT).pack(pady=(5, 10))

        CTkButton(self.root, text="Create Dummy Vault", font=APP_FONT, command=self.create_dummy, width=200).pack(pady=10)

    def toggle_password(self):
        state = "" if self.show_pw_var.get() else "*"
        self.entry1.configure(show=state)
        self.entry2.configure(show=state)

    def create_dummy(self):
        p1 = self.entry1.get()
        p2 = self.entry2.get()

        if not p1 or not p2:
            messagebox.showerror("Error", "Please fill in both fields.")
            return
        if p1 != p2:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        salt = get_or_create_salt(SALT_PATH)
        dummy_hash = hashlib.sha256(p1.encode() + salt).hexdigest()

        with open(DUMMY_HASH_PATH, 'w') as f:
            f.write(dummy_hash)

        self.root.destroy()
        self.on_done(p1)
