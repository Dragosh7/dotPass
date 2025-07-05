import hashlib
import secrets

from customtkinter import *
from tkinter import messagebox
from utils.layout import center_window
from core.encryption import derive_key
from core.hashing import get_or_create_salt
from utils.config import SALT_PATH, DUMMY_PATH, DUMMY_HASH_PATH
from core.db import load_or_create_vault, save_vault
from ui.create_dummy_vault_page import CreateDummyVaultPage
from utils.style import TITLE_FONT, SUB_FONT, APP_FONT
import os

class SyncVaultPage:
    def __init__(self, parent, master_key, conn, on_complete_logout, profile_name):
        self.parent = parent
        self.master_key = master_key
        self.conn = conn
        self.profile_name = profile_name
        self.on_complete_logout = on_complete_logout

        self.root = CTkToplevel(parent)
        self.root.title("Sync Dummy Vault")
        self.root.geometry("380x260")
        self.root.resizable(False, False)
        center_window(self.root, 380, 260)
        self.root.grab_set()
        self.root.focus_force()

        CTkLabel(self.root, text="Sync Dummy Vault", font=TITLE_FONT).pack(pady=(20, 10))
        CTkLabel(self.root, text="Enter dummy password to continue:", font=SUB_FONT).pack(pady=5)

        self.dummy_entry = CTkEntry(self.root, placeholder_text="Dummy Password", show="*", font=APP_FONT)
        self.dummy_entry.pack(pady=(10, 5), padx=30)

        CTkButton(self.root, text="Start Sync", command=self.start_sync, font=APP_FONT).pack(pady=20)

    def generate_fake_password(self):
        prefix = "" if self.profile_name else "123"
        suffix = str(secrets.randbelow(9000) + 1000)
        name_part = self.profile_name.split()[0] if self.profile_name else "Adminpass"
        return prefix + name_part + suffix + "!"

    def show_loading_screen(self):
        popup = CTkToplevel(self.root)
        popup.title("dotPass - Syncing")
        popup.geometry("340x160")
        popup.resizable(False, False)
        center_window(popup, 340, 160)
        popup.grab_set()
        popup.focus_force()

        CTkLabel(popup, text="Syncing dummy vault...", font=TITLE_FONT, text_color="#2F80ED").pack(pady=(25, 8))
        CTkLabel(popup, text="App will log out after this step.", font=SUB_FONT).pack()

        # Spinner fallback
        dots_label = CTkLabel(popup, text="", font=SUB_FONT)
        dots_label.pack(pady=15)

        def animate(count=0):
            dots = "." * (count % 4)
            dots_label.configure(text=f"Loading{dots}")
            popup.after(500, lambda: animate(count + 1))

        animate()  # Start animation

        def shutdown():
            popup.destroy()
            self.root.destroy()
            try:
                self.conn.close()
            except:
                pass
            self.on_complete_logout()

        popup.after(3500, shutdown)

    def start_sync(self):
        if not os.path.exists(DUMMY_HASH_PATH):
            def after_create(dummy_password):
                self.dummy_entry.delete(0, END)
                self.dummy_entry.insert(0, dummy_password)
                self.start_sync()

            CreateDummyVaultPage(self.root, on_done=after_create)
            return

        dummy_password = self.dummy_entry.get()
        if not dummy_password:
            messagebox.showerror("Error", "Please enter dummy password.")
            return

        try:
            salt = get_or_create_salt(SALT_PATH)
            dummy_key = derive_key(dummy_password, salt)

            with open(DUMMY_HASH_PATH, 'r') as f:
                stored_hash = f.read().strip()
            hash_input = hashlib.sha256(dummy_password.encode() + salt).hexdigest()
            if stored_hash != hash_input:
                messagebox.showerror("Error", "Incorrect dummy password.")
                return

            cursor = self.conn.cursor()
            rows = cursor.execute("SELECT site, username FROM accounts").fetchall()

            self.conn.close()

            conn_dummy = load_or_create_vault(dummy_key, DUMMY_PATH)

            with conn_dummy:
                conn_dummy.execute("DELETE FROM accounts")

            for site, user in rows:
                fake_pwd = self.generate_fake_password()
                conn_dummy.execute("INSERT INTO accounts (site, username, password) VALUES (?, ?, ?)",
                                   (site, user, fake_pwd))

            save_vault(conn_dummy, dummy_key, DUMMY_PATH)
            conn_dummy.close()

            self.show_loading_screen()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync dummy vault:\n{str(e)}")
