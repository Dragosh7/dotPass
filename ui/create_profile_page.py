from customtkinter import *
import os, json, hashlib
import datetime
from tkinter import messagebox
from core.hashing import get_or_create_salt
import re
from core.pin_logic import PinLogic
from ui.dialogs.pin_sending_dialog import PinSendingDialog
from utils.config import SALT_PATH, MASTER_HASH_PATH, DUMMY_HASH_PATH, PROFILE_PATH
from utils.setup import protect_file
from utils.style import TITLE_FONT, SUB_FONT, APP_FONT, SMALL_FONT, HEADER_FONT
from utils.tooltip import SimpleTooltip

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

        self.phone_entry = CTkEntry(self.root, placeholder_text="Phone Number", font=APP_FONT)
        self.phone_entry.pack(pady=10, padx=30)

        self.master_entry = CTkEntry(self.root, placeholder_text="Master Password", show="*", font=APP_FONT)
        self.master_entry.pack(pady=10, padx=30)

        self.confirm_entry = CTkEntry(self.root, placeholder_text="Confirm Password", show="*", font=APP_FONT)
        self.confirm_entry.pack(pady=10, padx=30)

        self.dummy_entry = CTkEntry(self.root, placeholder_text="Dummy Password", show="*", font=APP_FONT)
        self.dummy_entry.pack(pady=10, padx=30)

        self.dummy_warning_shown = False

        SimpleTooltip(self.name_entry, "Your full name (for display only)", force=True)
        SimpleTooltip(self.master_entry, "Main password that unlocks your vault", force=True)
        SimpleTooltip(self.confirm_entry, "Repeat your master password to confirm", force=True)
        SimpleTooltip(self.dummy_entry, "Emergency password to open a decoy vault in emergencies\nTo read more about this functionality consult our app documentation", force=True)
        SimpleTooltip(self.phone_entry, "Trusted contact’s phone number to receive your recovery PIN\nInclude country code!", force=True)

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
        phone = self.phone_entry.get().strip()

        if not all([name, phone, master, confirm]):
            messagebox.showerror("Error", "Please fill in name and master password.")
            return

        if master != confirm:
            messagebox.showerror("Error", "Master passwords do not match.")
            return

        if master == dummy:
            messagebox.showerror("Error", "Master password must not match with dummy password.")
            return

        if not re.fullmatch(r"^\+?\d{10,15}$", phone):
            messagebox.showerror(
                "Invalid Phone Number",
                "Please enter a valid phone number and include country code (Use '+' or '00')."
            )
            return

        if dummy.strip() == "":
            if not self.dummy_warning_shown:
                self.dummy_warning_shown = True
                messagebox.showwarning(
                    "Missing Dummy Password",
                    "We recommend setting a dummy password for emergency situations.\n\nClick 'Create Profile' again to continue without it."
                )
                return

        messagebox.showinfo(
            "PIN Info",
            "A recovery PIN will be sent to the provided phone number.\n\nMake sure the number is correct. You will be asked to confirm it again after logging in."
        )

        # pin_logic = PinLogic()
        # pin = pin_logic.generate_pin()
        #
        # try:
        #     messagebox.showinfo(
        #         "Recovery PIN Generated",
        #         f"Recovery PIN: {pin}\n\nSave this code somewhere safe.\nYou will need it to recover your vault on another device."
        #     )
        # except:
        #     pass

        def after_send(success):
            if not success:
                try:
                    with open(PROFILE_PATH, "r+") as f:
                        profile_data = json.load(f)
                        profile_data["pin_sent"] = False
                        f.seek(0)
                        json.dump(profile_data, f)
                        f.truncate()
                except Exception as e:
                    print(f"[dotPass] Could not update profile.json: {e}")

                messagebox.showerror("SMS Failed", "Could not send PIN. Check network connectivity.")
                self.show_restart_popup()
                return

            self.show_restart_popup()

        salt = get_or_create_salt(SALT_PATH)
        self.finalize_profile(name, phone, master, dummy, salt)
        self.show_restart_popup()
        #self.root.after(100, lambda: PinSendingDialog(self.root, phone, pin, after_send))

    def finalize_profile(self, name, phone, master, dummy, salt):
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
            json.dump({
                "name": name,
                "phone": phone,
                "pin_sent": False,
                "lastCheck": datetime.datetime.now().isoformat(),
                "reminder": datetime.datetime.now().isoformat()
            }, f)

