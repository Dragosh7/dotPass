from customtkinter import *
from tkinter import messagebox
import hashlib
import os
from utils.layout import center_window
from utils.config import SALT_PATH, DUMMY_HASH_PATH
from core.hashing import get_or_create_salt


class CreateDummyVaultPage:
    def __init__(self, parent, on_done):
        self.on_done = on_done

        self.root = CTkToplevel(parent)
        self.root.title("Create Dummy Password")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        center_window(self.root, 400, 300)
        self.root.grab_set()
        self.root.focus_force()

        CTkLabel(self.root, text="Dummy Vault Setup", font=("Arial Bold", 20)).pack(pady=(20, 5))
        CTkLabel(self.root, text="This vault is used for emergency situations.\nEnter and confirm a password:",
                 font=("Arial", 11), justify="center", wraplength=340).pack(pady=(0, 10))

        self.entry1 = CTkEntry(self.root, placeholder_text="Enter Dummy Password", show="*")
        self.entry1.pack(pady=5, padx=30)

        self.entry2 = CTkEntry(self.root, placeholder_text="Confirm Dummy Password", show="*")
        self.entry2.pack(pady=5, padx=30)

        CTkButton(self.root, text="Create Dummy Vault", command=self.create_dummy).pack(pady=20)

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
