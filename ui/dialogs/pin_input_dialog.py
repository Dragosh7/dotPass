from customtkinter import *
from tkinter import messagebox
from utils.config import SALT_PATH
from core.salt_manager import decrypt_salt_with_pin
from utils.layout import center_window


class PinInputDialog:
    def __init__(self, on_submit):
        self.pin = None
        self.on_submit = on_submit

        self.root = CTk()
        self.root.withdraw()

        self.dialog = CTkToplevel(self.root)
        self.dialog.title("Enter Recovery PIN")
        self.dialog.geometry("400x260")
        self.dialog.resizable(False, False)
        center_window(self.root, 400, 360)
        self.dialog.grab_set()
        self.dialog.focus_force()

        CTkLabel(self.dialog, text="🔐 Recovery PIN Required", font=("Helvetica", 18, "bold")).pack(pady=(20, 5))
        CTkLabel(self.dialog,
                 text="The PIN was sent to your trusted contact when you created your profile.\nEnter it below to decrypt your backup.",
                 font=("Helvetica", 12), wraplength=360, justify="center").pack(pady=(0, 10))

        self.entry = CTkEntry(self.dialog, show="*", font=("Helvetica", 14), width=240)
        self.entry.pack(pady=(10, 10))

        CTkButton(self.dialog, text="Confirm", command=self.submit, width=120).pack(pady=(10, 20))

        self.dialog.mainloop()

    def submit(self):
        pin_value = self.entry.get().strip()
        if pin_value:
            self.pin = pin_value
            self.dialog.after(100, lambda: self.root.destroy())
            self.dialog.destroy()
            self.on_submit(pin_value)
        else:
            messagebox.showwarning("Input Required", "Please enter your PIN.")
