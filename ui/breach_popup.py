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

        theme_mode = get_appearance_mode()

        if theme_mode == "Dark":
            bg_color = "#10151C"
            card_color = "#1C1F26"
            card_hover = "#263238"
            text_primary = "white"
            text_secondary = "#C0C0C0"
            text_alert = "#FF6B6B"
            accent_title = "#2F80ED"
        else:
            bg_color = "#FFFFFF"
            card_color = "#F5F5F5"
            card_hover = "#E0F0FF"
            text_primary = "#1A1A1A"
            text_secondary = "#4D4D4D"
            text_alert = "#B00020"
            accent_title = "#1565C0"

        self.popup.configure(fg_color=bg_color)

        CTkLabel(self.popup, text="Password Breach Results", font=("Helvetica", 20, "bold"), text_color=accent_title).pack(pady=(15, 10))

        container = CTkScrollableFrame(self.popup, width=480, height=380, corner_radius=12, fg_color=bg_color)
        container.pack(pady=10, padx=20, fill="both", expand=True)

        if breached_data:
            for site, user, hits in breached_data:
                frame = CTkFrame(container, fg_color=card_color, corner_radius=12)
                frame.pack(fill="x", pady=8, padx=12)

                # Hover effect
                def on_enter(e, fr=frame): fr.configure(fg_color=card_hover, border_width=2, border_color=accent_title)
                def on_leave(e, fr=frame): fr.configure(fg_color=card_color, border_width=0)

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
                    confirm.configure(fg_color="#1A1D24")

                    card = CTkFrame(confirm, fg_color="#262A34", corner_radius=14)
                    card.pack(padx=20, pady=20, fill="both", expand=True)

                    CTkLabel(card, text="🔑 Your Password Is Not Safe", font=("Helvetica", 18, "bold"),
                             text_color="white").pack(pady=(20, 6))
                    CTkLabel(card,
                             text="Do you want to change your password\nfor this website right now?",
                             font=("Helvetica", 14),
                             text_color="#CFCFCF", justify="center").pack()

                    CTkButton(
                        card,
                        text="Change Password",
                        width=200,
                        fg_color="#2F80ED",
                        text_color="white",
                        hover_color="#1C63D6",
                        font=("Helvetica", 14, "bold"),
                        command=lambda: (webbrowser.open(f"https://www.google.com/search?q={s}+change+password"),
                                         confirm.destroy())
                    ).pack(pady=(20, 6))  # 🟢 distanță de sus, fără frame

                    CTkButton(
                        card,
                        text="Not now",
                        width=200,
                        fg_color="#E0E0E0",
                        text_color="#000000",
                        hover_color="#C5C5C5",
                        font=("Helvetica", 13),
                        command=confirm.destroy
                    ).pack(pady=(0, 16))

                frame.bind("<Button-1>", on_click)
                for child in frame.winfo_children():
                    child.bind("<Button-1>", on_click)

                CTkLabel(frame, text=f"🔗 Site: {site}", font=("Helvetica", 15, "bold"), text_color=text_primary).pack(anchor="w", padx=15, pady=(10, 2))
                CTkLabel(frame, text=f"👤 Username: {user}", font=("Helvetica", 14), text_color=text_secondary).pack(anchor="w", padx=15)
                CTkLabel(frame, text=f"🔐 Password found in {hits:,} breaches", font=("Helvetica", 13), text_color=text_alert).pack(anchor="w", padx=15, pady=(5, 10))

        else:
            safe_frame = CTkFrame(container, fg_color="#2E7D32" if theme_mode == "Dark" else "#A5D6A7", corner_radius=12)
            safe_frame.pack(fill="x", pady=30, padx=10)
            CTkLabel(safe_frame, text="✅ All your saved passwords appear safe!", font=("Helvetica", 15, "bold"), text_color="white" if theme_mode == "Dark" else "#1B5E20").pack(pady=20)

        CTkButton(self.popup, text="Close", font=("Helvetica", 14), command=self.popup.destroy).pack(pady=(10, 15))
