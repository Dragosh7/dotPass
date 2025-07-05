import secrets
import threading

from customtkinter import *
from core.salt_manager import save_encrypted_salt
from ui.dialogs.pin_sending_dialog import PinSendingDialog
from ui.dialogs.sms_feedback_dialog import show_sms_sent_feedback
from utils.resource_path import resource_path
from utils.tooltip import SimpleTooltip
from core.password_generator import generate_password
from utils.layout import center_window
import datetime
from core.breach_check import check_password_breach
import sqlite3
import re
import json
import os
from tkinter import messagebox
from utils.config import PROFILE_PATH, DB_PATH, DUMMY_PATH, SALT_PATH
from ui.sync_vault_page import SyncVaultPage
from core.db import save_vault
from utils.style import APP_FONT, TITLE_FONT, SUB_FONT, SMALL_FONT, HEADER_FONT, MONO_FONT
from PIL import Image
from customtkinter import CTkImage
from ui.breach_popup import BreachResultPopup
from core.pin_logic import should_remind_pin, PinLogic


class MainPage:
    def __init__(self, master_key: bytes, connection: sqlite3.Connection, on_logout: None, is_dummy=False, conn_dummy=None, was_maximized=False):
        self.master_key = master_key
        self.conn = connection
        self.conn_dummy = conn_dummy
        self.on_logout = on_logout
        self.is_dummy = is_dummy
        self.profile_name = self.get_profile_name()

        self.root = CTkToplevel()

        center_window(self.root, 900, 600)
        if was_maximized:
            self.root.state("zoomed")

        self.root.title("dotPass Vault")
        self.root.protocol("WM_DELETE_WINDOW", self.logout)

        try:
            warning_icon = Image.open(resource_path("ui/images/flag_icon.png")).resize((18, 18))
            self.warning_image = CTkImage(warning_icon)
        except Exception as e:
            print("Failed to load warning image:", e)
            self.warning_image = None

        self.setup_layout()

        if not self.is_dummy and should_remind_pin():
            self.root.after(300, lambda: self.ask_send_pin_reminder())

        # if self.is_dummy:
        #     threading.Thread(target=self.send_emergency_sms_in_background, daemon=True).start()

        self.breached_accounts = set()

        self.check_breaches_if_needed()

        self.refresh_account_list()

        self.root.mainloop()

    def ask_send_pin_reminder(self):
        if not os.path.exists(PROFILE_PATH):
            return

        try:
            with open(PROFILE_PATH, "r+") as f:
                profile_data = json.load(f)

                if profile_data.get("pin_sent", True):
                    return

                reminder_str = profile_data.get("reminder")
                if reminder_str:
                    try:
                        reminder_date = datetime.datetime.fromisoformat(reminder_str)
                        if reminder_date > datetime.datetime.now():
                            return
                    except Exception:
                        pass

                phone = profile_data.get("phone")

                if not phone:
                    return

                should_send = messagebox.askyesnocancel(
                    "Security Reminder",
                    f"The recovery PIN was not sent. A code will be sent shortly after.\n\n"
                    f"Do you want to keep the same phone number?\n\n"
                    f"{phone}"
                )

                if should_send is None:
                    profile_data["reminder"] = (datetime.datetime.now() + datetime.timedelta(days=3)).isoformat()
                    f.seek(0)
                    json.dump(profile_data, f)
                    f.truncate()
                    return  # Cancel (with reminder)
                elif should_send is False:
                    from ui.dialogs.change_phone_dialog import ChangePhoneNumberDialog
                    ChangePhoneNumberDialog()
                    return

                from utils.config import ENCRYPTED_SALT_PATH
                if os.path.exists(ENCRYPTED_SALT_PATH):
                    os.remove(ENCRYPTED_SALT_PATH)

                pin_logic = PinLogic()
                pin = pin_logic.generate_pin()
                if os.path.exists(SALT_PATH):
                    if pin:
                        try:
                            with open(SALT_PATH, "rb") as sfile:
                                salt = sfile.read()
                                save_encrypted_salt(salt, pin)
                        except Exception as e:
                            print(f"[dotPass] Failed to save encrypted salt: {e}")

                profile_data["reminder"] = (datetime.datetime.now() + datetime.timedelta(days=90)).isoformat()
                profile_data["pin_sent"] = True
                f.seek(0)
                json.dump(profile_data, f)
                f.truncate()
                print(pin)
                success= True
                # success = PinSendingDialog.send_sms_direct(phone, pin)
                if success:
                    show_sms_sent_feedback(self.root, phone)
                else:
                    messagebox.showerror("Error", "Could not send PIN. Check your internet connection.")

        except Exception as e:
            print(f"[dotPass - Reminder PIN] Error: {e}")

    def logout(self):
        if self.on_logout:
            current_state = self.root.state() == "zoomed"
            self.on_logout(current_state)
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
                text="⟳ Sync Dummy Vault",
                font=APP_FONT,
                command=lambda: SyncVaultPage(self.root, self.master_key, self.conn, self.logout, self.profile_name)
            )
            self.sync_dummy_button.pack(pady=(5, 10), padx=10)

        self.detail_frame = CTkFrame(self.root)
        self.detail_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.detail_label = CTkLabel(self.detail_frame, text="Select an account", font=HEADER_FONT)
        self.detail_label.pack(pady=(20, 10))

        self.detail_info = CTkTextbox(self.detail_frame, width=600, height=400, font=MONO_FONT)
        self.detail_info.pack(pady=10, padx=20)

        if not self.is_dummy:
            self.breach_check_button = CTkButton(
                self.sidebar,
                text="🔎 Check Password Safety",
                font=APP_FONT,
                command=lambda: self.check_breaches_if_needed(manual=True)
            )
            self.breach_check_button.pack(pady=(5, 10), padx=10)

        self.logout_button = CTkButton(self.sidebar, text="Logout", font=APP_FONT, command=self.logout)
        self.logout_button.pack(pady=(5, 10), padx=10)

    def send_emergency_sms_in_background(self):
            try:
                if not os.path.exists(PROFILE_PATH):
                    return
                with open(PROFILE_PATH, 'r') as f:
                    profile = json.load(f)
                    phone = profile.get("phone", "").strip()
                    if not phone:
                        return
                    PinSendingDialog.send_dummy_emergency_sms(phone)
            except Exception as e:
                print(f"[dotPass - Emergency SMS] Failed to send in background: {e}")

    def get_profile_name(self):
        if os.path.exists(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, 'r') as f:
                    return json.load(f).get("name", "")
            except:
                return ""
        return ""

    def check_breaches_if_needed(self, manual=False):
        if self.is_dummy:
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts")
        count = cursor.fetchone()[0]
        if count == 0:
            if manual:
                messagebox.showinfo("No Passwords", "You have no passwords saved yet to check for breaches.")
            return

        try:
            if os.path.exists(PROFILE_PATH):
                with open(PROFILE_PATH, "r+") as f:
                    profile_data = json.load(f)
                    last_check_str = profile_data.get("lastCheck")

                    if not manual and last_check_str:
                        last_check = datetime.datetime.fromisoformat(last_check_str)
                        if (datetime.datetime.now() - last_check).days < 7:
                            return

                    cursor = self.conn.cursor()
                    rows = cursor.execute("SELECT site, username, password FROM accounts").fetchall()
                    breached = []

                    self.breached_accounts.clear()

                    for site, user, pwd in rows:
                        count = check_password_breach(pwd)
                        if count > 0:
                            self.breached_accounts.add((site, user))
                            breached.append((site, user, count))

                    BreachResultPopup(self.root, breached)

                    profile_data["lastCheck"] = datetime.datetime.now().isoformat()
                    f.seek(0)
                    json.dump(profile_data, f)
                    f.truncate()

                    self.refresh_account_list()

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
        self.detail_frame.destroy()
        self.detail_frame = CTkFrame(self.root, corner_radius=16)
        self.detail_frame.pack(side="right", expand=True, fill="both", padx=16, pady=16)

        cursor = self.conn.cursor()
        cursor.execute("SELECT site, username, password FROM accounts WHERE rowid=?", (rowid,))
        row = cursor.fetchone()
        if not row:
            return

        site, user, pwd = row

        self.current_rowid = rowid
        self.view_mode = True

        self.detail_title = CTkLabel(self.detail_frame, text="View Account", font=("Helvetica", 20, "bold"))
        self.detail_title.pack(pady=(10, 20))

        # ---- WEBSITE ----
        CTkLabel(self.detail_frame, text="Website:", font=SMALL_FONT, text_color="#AAAAAA").pack(anchor="w", padx=75,
                                                                                                 pady=(5, 0))

        self.site_entry = CTkEntry(self.detail_frame, font=APP_FONT, width=320)
        self.site_entry.insert(0, site)
        self.site_entry.configure(state="disabled")
        self.site_entry.pack(pady=(0, 10), padx=25)

        # ---- USERNAME ----
        CTkLabel(self.detail_frame, text="Username:", font=SMALL_FONT, text_color="#AAAAAA").pack(anchor="w", padx=75,
                                                                                                  pady=(5, 0))

        self.user_entry = CTkEntry(self.detail_frame, font=APP_FONT, width=320)
        self.user_entry.insert(0, user)
        self.user_entry.configure(state="disabled")
        self.user_entry.pack(pady=(0, 10), padx=25)

        # ---- PASSWORD ----
        CTkLabel(self.detail_frame, text="Password:", font=SMALL_FONT, text_color="#AAAAAA").pack(anchor="w", padx=75,
                                                                                                  pady=(5, 0))

        self.pwd_entry = CTkEntry(self.detail_frame, font=APP_FONT, width=320, show="*")
        self.pwd_entry.insert(0, pwd)
        self.pwd_entry.configure(state="disabled")
        self.pwd_entry.pack(pady=(0, 10), padx=25)

        # self.site_entry = CTkEntry(self.detail_frame, font=APP_FONT, width=320)
        # self.site_entry.insert(0, site)
        # self.site_entry.configure(state="disabled")
        # self.site_entry.pack(pady=(5, 10))
        #
        # self.user_entry = CTkEntry(self.detail_frame, font=APP_FONT, width=320)
        # self.user_entry.insert(0, user)
        # self.user_entry.configure(state="disabled")
        # self.user_entry.pack(pady=(5, 10))
        #
        # self.pwd_entry = CTkEntry(self.detail_frame, font=APP_FONT, show="*", width=320)
        # self.pwd_entry.insert(0, pwd)
        # self.pwd_entry.configure(state="disabled")
        # self.pwd_entry.pack(pady=(5, 10))

        self.show_password = BooleanVar(value=False)

        def toggle_show_pwd():
            self.pwd_entry.configure(show="" if self.show_password.get() else "*")

        CTkCheckBox(self.detail_frame, text="Show password", variable=self.show_password,
                    command=toggle_show_pwd, font=SMALL_FONT).pack(pady=(10, 10))


        self.strength_label = CTkLabel(self.detail_frame, text="", font=SMALL_FONT)
        self.strength_label.pack()


        self.suggest_button = CTkButton(self.detail_frame, text="Suggest Strong Password",
                                        command=self.suggest_strong_password, font=APP_FONT, width=220)
        self.suggest_button.pack(pady=(10, 10))
        self.suggest_button.pack_forget()

        self.edit_btn = CTkButton(self.detail_frame, text="Edit Account",
                                  command=self.toggle_edit_view, font=APP_FONT, width=150)
        self.edit_btn.pack(pady=(0, 8))

        CTkButton(
            self.detail_frame,
            text="Delete Account",
            command=self.delete_account,
            font=APP_FONT,
            fg_color="#E53935",
            hover_color="#C62828",
            width=150
        ).pack(pady=(0, 10))

    def delete_account(self):
        if not hasattr(self, "current_rowid"):
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this account?")
        if not confirm:
            return

        with self.conn:
            self.conn.execute("DELETE FROM accounts WHERE rowid=?", (self.current_rowid,))

        db_file = DUMMY_PATH if self.is_dummy else DB_PATH
        save_vault(self.conn, self.master_key, db_file)


        self.detail_frame.destroy()
        self.refresh_account_list()

    def toggle_edit_view(self):
        if self.view_mode:
            self.view_mode = False
            self.site_entry.configure(state="normal")
            self.user_entry.configure(state="normal")
            self.pwd_entry.configure(state="normal")
            self.detail_title.configure(text="Edit Account")
            self.edit_btn.configure(text="Confirm")

            self.suggest_button.pack(pady=(10, 10))
            self.pwd_entry.bind("<KeyRelease>", self.check_password_strength)
            self.check_password_strength()

        else:
            site = self.site_entry.get().strip()
            user = self.user_entry.get().strip()
            pwd = self.pwd_entry.get().strip()

            if not all([site, user, pwd]):
                messagebox.showerror("Error", "All fields are required.")
                return

            self.conn.execute("UPDATE accounts SET site=?, username=?, password=? WHERE rowid=?",
                              (site, user, pwd, self.current_rowid))
            self.conn.commit()
            save_vault(self.conn, self.master_key, DUMMY_PATH if self.is_dummy else DB_PATH)

            self.refresh_account_list()
            self.load_account_details(self.current_rowid)

    def password_strength(self, password):
        score = 0

        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1

        if re.search(r"[a-z]", password):
            score += 1
        if re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"[0-9]", password):
            score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>_\[\]\\\/+=\-]", password):
            score += 1

        if score <= 2:
            return "weak", "#E53935"
        elif 3 <= score <= 4:
            return "medium", "#FBC02D"
        else:
            return "strong", "#43A047"

    def check_password_strength(self, event=None):
        pwd = self.pwd_entry.get()
        strength, color = self.password_strength(pwd)
        self.strength_label.configure(text=f"Password Strength: {strength}", text_color=color)

    def suggest_strong_password(self):
        new_pwd = generate_password(14)
        self.pwd_entry.delete(0, END)
        self.pwd_entry.insert(0, new_pwd)
        self.check_password_strength()

    def generate_dummy_password(self):
        prefix = "123"
        suffix = str(secrets.randbelow(9000) + 1000)
        name_part = self.profile_name.split()[0] if self.profile_name else "password"
        return prefix + name_part + suffix

    def add_account_window(self):
        popup = CTkToplevel(self.root)
        center_window(popup, 400, 580)
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

        pwd_entry = CTkEntry(popup, placeholder_text="Password", show="*", font=APP_FONT,width=320)
        pwd_entry.pack(pady=(15, 5), padx=25)

        confirm_entry = CTkEntry(popup, placeholder_text="Confirm Password", show="*", font=APP_FONT,width=320)
        confirm_entry.pack(pady=(10, 5), padx=25)

        match_label = CTkLabel(popup, text="", font=SMALL_FONT)
        match_label.pack()

        pwd_strength_label = CTkLabel(popup, text="", font=SMALL_FONT)
        pwd_strength_label.pack()

        length_var = IntVar(value=16)
        length_slider = CTkSlider(popup, from_=12, to=28, number_of_steps=16, variable=length_var, width=200)
        length_slider.pack(pady=8)

        length_label = CTkLabel(popup, text="Length: 16", font=SMALL_FONT)
        length_label.pack()

        def update_length_label(value):
            length_label.configure(text=f"Length: {int(value)}")

        length_slider.configure(command=update_length_label)

        def fill_generated_password():
            pwd = generate_password(length_var.get())
            pwd_entry.delete(0, END)
            pwd_entry.insert(0, pwd)
            confirm_entry.delete(0, END)
            confirm_entry.insert(0, pwd)
            on_key_update()

        generate_btn = CTkButton(
            popup,
            text="Generate Password",
            font=APP_FONT,
            command=fill_generated_password,
            state="disabled"
        )
        generate_btn.pack(pady=(10, 4))

        SimpleTooltip(generate_btn, "Please fill in Website and Username before generating a password.")

        # --- CheckBox: Show Password ---
        def toggle_password():
            show = "" if show_password.get() else "*"
            pwd_entry.configure(show=show)
            confirm_entry.configure(show=show)

        show_password = BooleanVar(value=False)
        CTkCheckBox(
            popup,
            text="Show password",
            variable=show_password,
            command=toggle_password,
            font=SMALL_FONT
        ).pack(pady=(5, 10))

        def check_enable_generate(event=None):
            if site_entry.get().strip() and user_entry.get().strip():
                generate_btn.configure(state="normal")
            else:
                generate_btn.configure(state="disabled")

        site_entry.bind("<KeyRelease>", check_enable_generate)
        user_entry.bind("<KeyRelease>", check_enable_generate)

        def on_key_update(event=None):
            pwd = pwd_entry.get()
            confirm = confirm_entry.get()
            strength, color = self.password_strength(pwd)
            pwd_strength_label.configure(text=f"Strength: {strength}", text_color=color)
            if confirm == "":
                match_label.configure(text="")
            elif confirm == pwd:
                match_label.configure(text="Passwords match", text_color="#43A047")
            else:
                match_label.configure(text="Passwords do not match", text_color="#E53935")

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

            stored_pwd = pwd
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

        CTkButton(popup, text="Save Account", command=save, width=240, font=APP_FONT).pack(pady=10)
