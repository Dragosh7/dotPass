from customtkinter import *
from tkinter import messagebox
import json
import re
from utils.config import PROFILE_PATH
from utils.style import TITLE_FONT, APP_FONT
from utils.layout import center_window
from utils.tooltip import SimpleTooltip

class ChangePhoneNumberDialog:
    def __init__(self):
        self.root = CTk()
        self.root.title("Change Trusted Number")
        self.root.geometry("400x400")
        center_window(self.root, 400, 300)
        self.root.resizable(False, False)

        CTkLabel(self.root, text="🔒 Trusted Contact Update", font=TITLE_FONT).pack(pady=(20, 8))
        CTkLabel(self.root, text="Enter your new phone number", font=APP_FONT).pack(pady=5)

        self.phone_entry = CTkEntry(self.root, placeholder_text="New Phone Number", font=APP_FONT, width=200)
        self.phone_entry.pack(pady=(10, 5), padx=80)
        SimpleTooltip(self.phone_entry, "Ensure to include country code (e.g. +40...)", force=True)

        self.confirm_entry = CTkEntry(self.root, placeholder_text="Confirm Phone Number", font=APP_FONT,width=200)
        self.confirm_entry.pack(pady=(5, 10), padx=80)
        SimpleTooltip(self.confirm_entry, "Repeat the same number for confirmation", force=True)

        CTkButton(self.root, text="Update", command=self.update_phone, font=APP_FONT).pack(pady=10)

        self.root.mainloop()

    def update_phone(self):
        phone = self.phone_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not phone or not confirm:
            messagebox.showerror("Missing Fields", "Please fill in both phone number fields.")
            return

        if phone != confirm:
            messagebox.showerror("Mismatch", "Phone numbers do not match.")
            return

        if not re.fullmatch(r"^\+?\d{10,15}$", phone):
            messagebox.showerror(
                "Invalid Format",
                "Enter a valid number"
            )
            return

        try:
            with open(PROFILE_PATH, 'r+') as f:
                profile = json.load(f)
                profile["phone"] = phone
                f.seek(0)
                json.dump(profile, f)
                f.truncate()
        except Exception as e:
            print(f"[dotPass] Could not update profile: {e}")
            messagebox.showerror("Error", "Failed to save profile.")
            return

        messagebox.showinfo("Updated", "Phone number updated. Restart the app to continue.")
        self.root.destroy()
