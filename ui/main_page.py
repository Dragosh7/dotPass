from customtkinter import *
from utils.layout import center_window
import datetime
from core.breach_check import check_password_breach
import sqlite3
import re
import random
import json
import os
from tkinter import messagebox
from utils.config import PROFILE_PATH, DB_PATH, DUMMY_PATH
from ui.sync_vault_page import SyncVaultPage
from core.db import save_vault
from utils.style import APP_FONT, TITLE_FONT, SUB_FONT, SMALL_FONT, HEADER_FONT, MONO_FONT
from PIL import Image
from customtkinter import CTkImage

class MainPage:
    def __init__(self, master_key: bytes, connection: sqlite3.Connection, on_logout: None, is_dummy=False, conn_dummy=None):
        self.master_key = master_key
        self.conn = connection
        self.conn_dummy = conn_dummy
        self.on_logout = on_logout
        self.is_dummy = is_dummy
        self.profile_name = self.get_profile_name()

        self.root = CTkToplevel()
        center_window(self.root, 900, 600)
        self.root.title("dotPass Vault")
        self.root.protocol("WM_DELETE_WINDOW", self.logout)

        try:
            warning_icon = Image.open("ui/images/triangle_icon.png").resize((16, 16))
            self.warning_image = CTkImage(warning_icon)
        except Exception as e:
            print("Failed to load warning image:", e)
            self.warning_image = None

        self.setup_layout()

        self.breached_accounts = set()
        self.check_breaches_if_needed()

        self.refresh_account_list()

        self.root.mainloop()

    def logout(self):
        if self.on_logout:
            self.on_logout()
        self.root.destroy()

    def setup_layout(self):
        self.sidebar = CTkFrame(self.root, width=250)
        self.sidebar.pack(side="left", fill="y")

        self.account_list = CTkScrollableFrame(self.sidebar, width=250)
        self.account_list.pack(expand=True, fill="both", padx=10, pady=10)

        self.add_button = CTkButton(self.sidebar, text="+ Add Account", font=APP_FONT, command=self.add_account_window)
        self.add_button.pack(pady=10, padx=10)

        if not self.is_dummy:
            self.sync_dummy_button = CTkButton(
                self.sidebar,
                text="↺ Sync Dummy Vault",
                font=APP_FONT,
                command=lambda: SyncVaultPage(self.root, self.master_key, self.conn, self.logout, self.profile_name)
            )
            self.sync_dummy_button.pack(pady=(5, 10), padx=10)

        self.logout_button = CTkButton(self.sidebar, text="Logout", font=APP_FONT, command=self.logout)
        self.logout_button.pack(pady=(5, 10), padx=10)

        self.detail_frame = CTkFrame(self.root)
        self.detail_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.detail_label = CTkLabel(self.detail_frame, text="Select an account", font=HEADER_FONT)
        self.detail_label.pack(pady=(20, 10))

        self.detail_info = CTkTextbox(self.detail_frame, width=600, height=400, font=MONO_FONT)
        self.detail_info.pack(pady=10, padx=20)

    def get_profile_name(self):
        if os.path.exists(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, 'r') as f:
                    return json.load(f).get("name", "")
            except:
                return ""
        return ""

    def check_breaches_if_needed(self):
        if self.is_dummy:
            return

        try:
            if os.path.exists(PROFILE_PATH):
                with open(PROFILE_PATH, "r+") as f:
                    profile_data = json.load(f)
                    last_check_str = profile_data.get("lastCheck")

                    if last_check_str:
                        last_check = datetime.datetime.fromisoformat(last_check_str)
                        if (datetime.datetime.now() - last_check).days < -1:
                            return

                    cursor = self.conn.cursor()
                    rows = cursor.execute("SELECT site, username, password FROM accounts").fetchall()
                    breached = []

                    for site, user, pwd in rows:
                        count = check_password_breach(pwd)
                        if count > 0:
                            self.breached_accounts.add((site, user))
                            breached.append(f"{site} ({user}) - {count} hits")

                    if breached:
                        messagebox.showwarning("Breach Alert",
                                               "The following passwords were found in known breaches:\n\n" + "\n".join(
                                                   breached))

                    # Update last check
                    profile_data["lastCheck"] = datetime.datetime.now().isoformat()
                    f.seek(0)
                    json.dump(profile_data, f)
                    f.truncate()
        except Exception as e:
            print("Failed breach check:", e)

    def refresh_account_list(self):
        for widget in self.account_list.winfo_children():
            widget.destroy()

        cursor = self.conn.cursor()
        cursor.execute("SELECT rowid, site FROM accounts")
        for rowid, site in cursor.fetchall():
            cursor2 = self.conn.cursor()
            cursor2.execute("SELECT username FROM accounts WHERE rowid=?", (rowid,))
            user = cursor2.fetchone()[0]

            label_text = site
            if (site, user) in self.breached_accounts and self.warning_image:
                btn = CTkButton(
                    self.account_list,
                    text=site,
                    image=self.warning_image,
                    compound="right",
                    anchor="w",
                    font=APP_FONT,
                    command=lambda rid=rowid: self.load_account_details(rid)
                )
            else:
                btn = CTkButton(
                    self.account_list,
                    text=site,
                    anchor="w",
                    font=APP_FONT,
                    command=lambda rid=rowid: self.load_account_details(rid)
                )

            btn.pack(fill="x", padx=5, pady=2)

    def load_account_details(self, rowid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT site, username, password FROM accounts WHERE rowid=?", (rowid,))
        row = cursor.fetchone()
        if row:
            site, user, pwd = row
            info = f"Site: {site}\nUsername: {user}\nPassword: {pwd}"
            self.detail_label.configure(text=site)
            self.detail_info.delete("1.0", "end")
            self.detail_info.insert("1.0", info)

    def password_strength(self, password):
        if len(password) < 6:
            return "weak", "#E53935"
        elif re.search(r"[A-Z]", password) and re.search(r"[0-9]", password) and len(password) >= 8:
            return "strong", "#43A047"
        else:
            return "medium", "#FBC02D"

    def generate_dummy_password(self):
        prefix = "D_"
        suffix = str(random.randint(1000, 9999))
        name_part = self.profile_name.split()[0] if self.profile_name else "user"
        return prefix + name_part + suffix

    def add_account_window(self):
        popup = CTkToplevel(self.root)
        center_window(popup, 400, 420)
        popup.title("Add Account")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()
        popup.configure(corner_radius=16)

        CTkLabel(popup, text="Add New Account", font=TITLE_FONT).pack(pady=(15, 5))

        site_entry = CTkEntry(popup, placeholder_text="Website / Service", font=APP_FONT)
        site_entry.pack(pady=(10, 5), padx=25)

        user_entry = CTkEntry(popup, placeholder_text="Username or Email", font=APP_FONT)
        user_entry.pack(pady=5, padx=25)

        pwd_entry = CTkEntry(popup, placeholder_text="Password", show="*", font=APP_FONT)
        pwd_entry.pack(pady=(15, 5), padx=25)

        pwd_strength_label = CTkLabel(popup, text="", font=SMALL_FONT)
        pwd_strength_label.pack()

        confirm_entry = CTkEntry(popup, placeholder_text="Confirm Password", show="*", font=APP_FONT)
        confirm_entry.pack(pady=(15, 5), padx=25)

        match_label = CTkLabel(popup, text="", font=SMALL_FONT)
        match_label.pack()

        def toggle_password():
            show = "" if show_password.get() else "*"
            pwd_entry.configure(show=show)
            confirm_entry.configure(show=show)

        show_password = BooleanVar(value=False)
        CTkCheckBox(popup, text="Show password", variable=show_password,
                    command=toggle_password, font=SMALL_FONT).pack(pady=5)

        def on_key_update(event=None):
            pwd = pwd_entry.get()
            confirm = confirm_entry.get()
            strength, color = self.password_strength(pwd)
            pwd_strength_label.configure(text=f"Strength: {strength}", text_color=color)
            if confirm == "":
                match_label.configure(text="")
            elif confirm == pwd:
                match_label.configure(text="\u2713 Passwords match", text_color="#43A047")
            else:
                match_label.configure(text="\u2717 Passwords do not match", text_color="#E53935")

        pwd_entry.bind("<KeyRelease>", on_key_update)
        confirm_entry.bind("<KeyRelease>", on_key_update)

        def save():
            site = site_entry.get()
            user = user_entry.get()
            pwd = pwd_entry.get()
            confirm = confirm_entry.get()

            if not all([site, user, pwd, confirm]):
                match_label.configure(text="Please fill in all fields", text_color="#E53935")
                return
            if pwd != confirm:
                match_label.configure(text="Passwords do not match", text_color="#E53935")
                return

            stored_pwd = self.generate_dummy_password() if self.is_dummy else pwd
            with self.conn:
                self.conn.execute("INSERT INTO accounts (site, username, password) VALUES (?, ?, ?)",
                                  (site, user, stored_pwd))

            db_file = DUMMY_PATH if self.is_dummy else DB_PATH
            save_vault(self.conn, self.master_key, db_file)

            if not self.is_dummy and self.conn_dummy:
                fake_pwd = self.generate_dummy_password()
                with self.conn_dummy:
                    self.conn_dummy.execute("INSERT INTO accounts (site, username, password) VALUES (?, ?, ?)",
                                            (site, user, fake_pwd))
                save_vault(self.conn_dummy, self.master_key, DUMMY_PATH)

            popup.destroy()
            self.refresh_account_list()

        CTkButton(popup, text="Save Account", command=save, width=240, font=APP_FONT).pack(pady=20)

    def sync_dummy_vault(self):
        if not self.conn_dummy:
            messagebox.showerror("Error", "Dummy database connection missing.")
            return

        with self.conn_dummy:
            self.conn_dummy.execute("DELETE FROM accounts")

        cursor = self.conn.cursor()
        cursor.execute("SELECT site, username FROM accounts")
        rows = cursor.fetchall()

        for site, user in rows:
            fake_pwd = self.generate_dummy_password()
            with self.conn_dummy:
                self.conn_dummy.execute("INSERT INTO accounts (site, username, password) VALUES (?, ?, ?)",
                                        (site, user, fake_pwd))

        messagebox.showinfo("Success", "Dummy vault has been synced with fake passwords.")
