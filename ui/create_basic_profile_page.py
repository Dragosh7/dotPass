from customtkinter import *
from tkinter import messagebox
import json
import re
from utils.config import PROFILE_PATH
from utils.style import TITLE_FONT, APP_FONT
from utils.layout import center_window
from utils.tooltip import SimpleTooltip

class CreateProfileOnlyPage:
    def __init__(self):
        self.root = CTk()
        self.root.title("Complete Profile")
        self.root.geometry("380x280")
        center_window(self.root, 380, 280)
        self.root.resizable(False, False)

        CTkLabel(self.root, text="Welcome Back", font=TITLE_FONT).pack(pady=(20, 10))
        CTkLabel(self.root, text="Re-enter your full name and phone number", font=APP_FONT).pack(pady=5)

        self.name_entry = CTkEntry(self.root, placeholder_text="Full Name", font=APP_FONT)
        self.name_entry.pack(pady=(10, 5), padx=30)
        SimpleTooltip(self.name_entry, "Used for profile identification", force=True)

        self.phone_entry = CTkEntry(self.root, placeholder_text="Phone Number", font=APP_FONT)
        self.phone_entry.pack(pady=(5, 10), padx=30)
        SimpleTooltip(self.phone_entry, "Trusted contact’s phone number to receive your recovery PIN\nInclude country code!", force=True)

        CTkButton(self.root, text="Save", command=self.save_profile, font=APP_FONT).pack(pady=15)

        self.root.mainloop()

    def save_profile(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not name or not phone:
            messagebox.showerror("Error", "Please enter both your name and phone number.")
            return

        if not re.fullmatch(r"^\+?\d{10,15}$", phone):
            messagebox.showerror(
                "Invalid Phone Number",
                "Please enter a valid phone number (Use '+' or '00')."
            )
            return

        with open(PROFILE_PATH, 'w') as f:
            json.dump({
                "name": name,
                "phone": phone,
                "pin_sent": False,
                "lastCheck": None,
                "reminder": None,
                "maximized": False
            }, f)

        messagebox.showinfo("Success", "Profile updated. Restart the application.")
        self.root.destroy()
