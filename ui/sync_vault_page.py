from customtkinter import *
from tkinter import messagebox
from utils.layout import center_window
from core.encryption import derive_key
from core.hashing import get_or_create_salt
from utils.config import SALT_PATH, DUMMY_PATH
from core.db import load_or_create_vault, save_vault

import sqlite3
import hashlib
import os
import random


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

        CTkLabel(self.root, text="Sync Dummy Vault", font=("Arial Bold", 20)).pack(pady=(20, 10))
        CTkLabel(self.root, text="Enter dummy password to continue:", font=("Arial", 12)).pack(pady=5)

        self.dummy_entry = CTkEntry(self.root, placeholder_text="Dummy Password", show="*")
        self.dummy_entry.pack(pady=(10, 5), padx=30)

        CTkButton(self.root, text="Start Sync", command=self.start_sync).pack(pady=20)

    def generate_fake_password(self):
        prefix = "D_"
        suffix = str(random.randint(1000, 9999))
        name_part = self.profile_name.split()[0] if self.profile_name else "user"
        return prefix + name_part + suffix

    def show_loading_screen(self):
        popup = CTkToplevel(self.root)
        popup.title("dotPass - Syncing")
        popup.geometry("340x160")
        popup.resizable(False, False)
        center_window(popup, 340, 160)
        popup.grab_set()
        popup.focus_force()

        CTkLabel(popup, text="Syncing dummy vault...", font=("Arial Bold", 14), text_color="#2F80ED").pack(pady=(25, 8))
        CTkLabel(popup, text="App will log out after this step.", font=("Arial", 11)).pack()

        # Spinner fallback
        dots_label = CTkLabel(popup, text="", font=("Arial", 12))
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
        dummy_password = self.dummy_entry.get()
        if not dummy_password:
            messagebox.showerror("Error", "Please enter dummy password.")
            return

        try:
            salt = get_or_create_salt(SALT_PATH)
            dummy_key = derive_key(dummy_password, salt)

            # Extragem datele reale înainte să închidem conexiunea
            cursor = self.conn.cursor()
            rows = cursor.execute("SELECT site, username FROM accounts").fetchall()

            self.conn.close()

            # Încărcăm baza dummy
            conn_dummy = load_or_create_vault(dummy_key, DUMMY_PATH)

            # Ștergem vechiul conținut
            with conn_dummy:
                conn_dummy.execute("DELETE FROM accounts")

            # Inserăm cu parole false
            for site, user in rows:
                fake_pwd = self.generate_fake_password()
                conn_dummy.execute("INSERT INTO accounts (site, username, password) VALUES (?, ?, ?)",
                                   (site, user, fake_pwd))

            save_vault(conn_dummy, dummy_key, DUMMY_PATH)
            conn_dummy.close()

            self.show_loading_screen()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync dummy vault:\n{str(e)}")
