from customtkinter import *
import sqlite3
import re

class MainPage:
    def __init__(self, master_key: bytes, connection: sqlite3.Connection, on_logout:None):
        self.master_key = master_key
        self.conn = connection
        self.on_logout = on_logout

        self.root = CTkToplevel()
        self.root.geometry("900x600")
        self.root.title("dotPass Vault")

        self.root.protocol("WM_DELETE_WINDOW", self.logout)

        self.setup_layout()
        self.load_mock_data()
        self.refresh_account_list()

        self.root.mainloop()

    def on_close(self):
        self.root.destroy()

    def logout(self):
        if self.on_logout:
            self.on_logout()
        self.root.destroy()

    def setup_layout(self):
        # Sidebar list
        self.sidebar = CTkFrame(self.root, width=250)
        self.sidebar.pack(side="left", fill="y")

        self.account_list = CTkScrollableFrame(self.sidebar, width=250)
        self.account_list.pack(expand=True, fill="both", padx=10, pady=10)

        self.add_button = CTkButton(self.sidebar, text="+ Add Account", command=self.add_account_window)
        self.add_button.pack(pady=10, padx=10)

        # Detail view
        self.detail_frame = CTkFrame(self.root)
        self.detail_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.detail_label = CTkLabel(self.detail_frame, text="Select an account", font=("Arial", 18))
        self.detail_label.pack(pady=(20, 10))

        self.detail_info = CTkTextbox(self.detail_frame, width=600, height=400, font=("Consolas", 12))
        self.detail_info.pack(pady=10, padx=20)

        self.logout_button = CTkButton(self.sidebar, text="Logout", command=self.logout)
        self.logout_button.pack(pady=(5, 10), padx=10)

    def load_mock_data(self):
        with self.conn:
            self.conn.execute("DELETE FROM accounts")
            self.conn.executemany("INSERT INTO accounts (site, username, password) VALUES (?, ?, ?)", [
                ("Facebook", "emily@enpass.io", "12345678"),
                ("Twitter", "emily@enpass.io", "abcd1234"),
                ("Bank", "emily@bank.com", "securepass"),
                ("Driving License", "D1451252", "LMV|01/01/1990|Emily"),
                ("Passport", "ZA65342", "emily@enpass.io"),
                ("Credit Card", "**** 1234", "CVV: 456")
            ])

    def refresh_account_list(self):
        for widget in self.account_list.winfo_children():
            widget.destroy()

        cursor = self.conn.cursor()
        cursor.execute("SELECT rowid, site FROM accounts")
        for rowid, site in cursor.fetchall():
            btn = CTkButton(self.account_list, text=site, anchor="w", command=lambda rid=rowid: self.load_account_details(rid))
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

    def add_account_window(self):
        popup = CTkToplevel(self.root)
        popup.geometry("400x420")
        popup.title("Add Account")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()

        popup.configure(corner_radius=16)

        CTkLabel(popup, text="Add New Account", font=("Arial Bold", 20)).pack(pady=(15, 5))

        # Site field
        site_entry = CTkEntry(popup, placeholder_text="Website / Service")
        site_entry.pack(pady=(10, 5), padx=25)

        # Username/email
        user_entry = CTkEntry(popup, placeholder_text="Username or Email")
        user_entry.pack(pady=5, padx=25)

        # Password field
        pwd_entry = CTkEntry(popup, placeholder_text="Password", show="*")
        pwd_entry.pack(pady=(15, 5), padx=25)

        pwd_strength_label = CTkLabel(popup, text="", font=("Arial", 10))
        pwd_strength_label.pack()

        # Confirm password field
        confirm_entry = CTkEntry(popup, placeholder_text="Confirm Password", show="*")
        confirm_entry.pack(pady=(15, 5), padx=25)

        match_label = CTkLabel(popup, text="", font=("Arial", 10))
        match_label.pack()

        # Show password checkbox
        def toggle_password():
            show = "" if show_password.get() else "*"
            pwd_entry.configure(show=show)
            confirm_entry.configure(show=show)

        show_password = BooleanVar(value=False)
        CTkCheckBox(popup, text="Show password", variable=show_password, command=toggle_password).pack(pady=5)

        # Logic for live feedback
        def on_key_update(event=None):
            pwd = pwd_entry.get()
            confirm = confirm_entry.get()

            # Strength
            strength, color = self.password_strength(pwd)
            pwd_strength_label.configure(text=f"Strength: {strength}", text_color=color)

            # Match
            if confirm == "":
                match_label.configure(text="")
            elif confirm == pwd:
                match_label.configure(text="✓ Passwords match", text_color="#43A047")
            else:
                match_label.configure(text="✗ Passwords do not match", text_color="#E53935")

        pwd_entry.bind("<KeyRelease>", on_key_update)
        confirm_entry.bind("<KeyRelease>", on_key_update)

        # Save action
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

            with self.conn:
                self.conn.execute("INSERT INTO accounts (site, username, password) VALUES (?, ?, ?)",
                                  (site, user, pwd))
            popup.destroy()
            self.refresh_account_list()

        CTkButton(popup, text="Save Account", command=save, width=240).pack(pady=20)
