from customtkinter import *
from utils.layout import center_window
import webbrowser


class BreachResultPopup:
    def __init__(self, parent, breached_data: list):
        self.popup = CTkToplevel(parent)
        self.popup.title("Breach Results")
        self.popup.geometry("520x500")
        self.popup.resizable(False, False)
        self.popup.grab_set()
        center_window(self.popup, 520, 500)

        CTkLabel(self.popup, text="Password Breach Results", font=("Helvetica", 20, "bold")).pack(pady=(15, 10))

        container = CTkScrollableFrame(self.popup, width=480, height=380, corner_radius=12)
        container.pack(pady=10, padx=20, fill="both", expand=True)

        if breached_data:
            for site, user, hits in breached_data:
                frame = CTkFrame(
                    container,
                    corner_radius=12,
                    border_width=2,
                    border_color="#2F80ED"
                )
                frame.pack(fill="x", pady=8, padx=12)

                original_fg = frame.cget("fg_color")

                def on_enter(e, fr=frame):
                    highlight_color = "#E0F0FF" if get_appearance_mode() == "Light" else "#263238"
                    fr.configure(fg_color=highlight_color)

                def on_leave(e, fr=frame, original=original_fg):
                    fr.configure(fg_color=original)

                frame.bind("<Enter>", on_enter)
                frame.bind("<Leave>", on_leave)
                for child in frame.winfo_children():
                    child.bind("<Enter>", on_enter)
                    child.bind("<Leave>", on_leave)

                def on_click(e, s=site):
                    confirm = CTkToplevel(self.popup)
                    confirm.title("Vulnerable Password")
                    confirm.geometry("420x260")
                    confirm.grab_set()
                    center_window(confirm, 420, 260)

                    card = CTkFrame(confirm, corner_radius=14)
                    card.pack(padx=20, pady=20, fill="both", expand=True)

                    CTkLabel(card, text="🔑 Your Password Is Not Safe", font=("Helvetica", 18, "bold")).pack(pady=(20, 6))
                    CTkLabel(card,
                             text="Do you want to change your password\nfor this website right now?",
                             font=("Helvetica", 14),
                             justify="center").pack()

                    CTkButton(
                        card,
                        text="Change Password",
                        width=200,
                        font=("Helvetica", 14, "bold"),
                        command=lambda: (webbrowser.open(f"https://www.google.com/search?q={s}+change+password"),
                                         confirm.destroy())
                    ).pack(pady=(20, 6))

                    CTkButton(
                        card,
                        text="Not now",
                        width=200,
                        font=("Helvetica", 13),
                        command=confirm.destroy
                    ).pack(pady=(0, 16))

                frame.bind("<Button-1>", on_click)
                for child in frame.winfo_children():
                    child.bind("<Button-1>", on_click)

                CTkLabel(frame, text=f"🔗 Site: {site}", font=("Helvetica", 15, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
                CTkLabel(frame, text=f"👤 Username: {user}", font=("Helvetica", 14)).pack(anchor="w", padx=15)
                CTkLabel(frame, text=f"🔐 Password found in {hits:,} breaches", font=("Helvetica", 13), text_color="#FF6B6B").pack(anchor="w", padx=15, pady=(5, 10))
        else:
            safe_frame = CTkFrame(container, corner_radius=12)
            safe_frame.pack(fill="x", pady=30, padx=10)
            CTkLabel(safe_frame, text="✅ All your saved passwords appear safe!", font=("Helvetica", 15, "bold"), text_color="#388E3C").pack(pady=20)

        CTkButton(self.popup, text="Close", font=("Helvetica", 14), command=self.popup.destroy).pack(pady=(10, 15))
