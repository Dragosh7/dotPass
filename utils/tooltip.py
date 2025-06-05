import tkinter as tk

class SimpleTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.alpha = 0
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.hide)

    def on_enter(self, event=None):
        # ✅ Afișează doar dacă butonul e DISABLED
        if str(self.widget.cget("state")) == "disabled":
            self.show()

    def show(self):
        if self.tipwindow or not self.text:
            return

        x = self.widget.winfo_rootx() + 40
        y = self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        tw.wm_attributes("-alpha", 0.0)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#2B2B2B",
            foreground="#F0F0F0",
            borderwidth=1,
            relief="solid",
            font=("Helvetica", 9)
        )
        label.pack(ipadx=6, ipady=3)

        self.alpha = 0.0
        self.fade_in()

    def fade_in(self):
        if self.tipwindow and self.alpha < 0.95:
            self.alpha += 0.1
            self.tipwindow.wm_attributes("-alpha", self.alpha)
            self.tipwindow.after(30, self.fade_in)

    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None
