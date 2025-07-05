from customtkinter import CTkToplevel, CTkLabel, CTkButton
from utils.style import APP_FONT
from utils.layout import center_window

def show_sms_sent_feedback(parent, phone: str):
    popup = CTkToplevel(parent)
    popup.title("PIN Sent")
    popup.geometry("360x200")
    popup.resizable(False, False)
    popup.grab_set()
    popup.focus_force()

    center_window(popup, 360, 200)

    CTkLabel(popup, text="PIN was sent successfully", font=("Helvetica", 16, "bold")).pack(pady=(20, 10))
    CTkLabel(popup, text=f"Phone: {phone}", font=APP_FONT).pack(pady=(0, 5))
    CTkLabel(popup, text=f"Your recovery PIN has been sent via SMS.", font=APP_FONT).pack(pady=(0, 15))

    CTkButton(popup, text="Close", command=popup.destroy).pack(pady=(5, 10))
