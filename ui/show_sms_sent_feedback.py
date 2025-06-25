from customtkinter import CTkToplevel, CTkLabel, CTkButton

def show_sms_sent_feedback(root, phone: str, pin: str):
    dialog = CTkToplevel(root)
    dialog.title("PIN Sent")
    dialog.geometry("400x240")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.focus_force()

    # Center window
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (240 // 2)
    dialog.geometry(f"400x240+{x}+{y}")

    CTkLabel(dialog, text="PIN Sent Successfully", font=("Helvetica", 18, "bold"), text_color="#3CB371").pack(pady=(20, 10))
    CTkLabel(dialog, text=f"A recovery PIN was sent to:\n{phone}", font=("Helvetica", 13), text_color="#888888", justify="center").pack(pady=5)
    CTkLabel(dialog, text=f"(for debug/testing)\nPIN: {pin}", font=("Courier", 14, "bold"), text_color="#0077CC").pack(pady=(10, 5))

    def close():
        dialog.destroy()

    CTkButton(dialog, text="Close", command=close).pack(pady=15)
