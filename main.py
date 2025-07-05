from tkinter import messagebox, filedialog
import os
from core.salt_manager import decrypt_salt_with_pin
from ui.create_basic_profile_page import CreateProfileOnlyPage
from ui.dialogs.pin_input_dialog import PinInputDialog
from utils.config import SALT_PATH
from utils.setup import check_integrity
from ui.interface import launch_app
from ui.create_profile_page import CreateProfilePage

def try_decrypt_salt(path):
    def handle_pin(pin):
        try:
            with open(path, "rb") as f:
                encrypted = f.read()
            salt = decrypt_salt_with_pin(encrypted, pin)

            with open(SALT_PATH, "wb") as f:
                f.write(salt)

            messagebox.showinfo("Success", "Salt restored successfully. Please restart dotPass.")
            os._exit(0)
        except Exception as e:
            messagebox.showerror("Failed", f"Could not decrypt salt\n{str(e)}")
            os._exit(1)

    PinInputDialog(handle_pin)

if __name__ == "__main__":
    status = check_integrity()

    if status == "new_install":
        CreateProfilePage()

    elif status == "create_profile_only":
        CreateProfileOnlyPage()

    elif status.startswith("warn:"):
        warning = status.split(":")[1]
        messagebox.showwarning(
            "dotPass Warning",
            f"The following files are missing but will be restored automatically if possible:\n\n{warning}\n\n"
            "You can continue normally."
        )
        launch_app()

    elif status.startswith("missing:"):
        missing = status.split(":")[1]

        response = messagebox.askyesno(
            "dotPass - Files Missing",
            f"The following critical files are missing:\n\n{missing}\n\n"
            "Would you like to load a recovery file (salt.enc) manually?"
        )

        if response:
            salt_enc_path = filedialog.askopenfilename(
                title="Select salt.enc file",
                filetypes=[("Encrypted Salt", "*.enc *.dotpass")]
            )

            if salt_enc_path:
                try_decrypt_salt(salt_enc_path)
            else:
                messagebox.showinfo(
                    "dotPass Info",
                    "Please consult our documentation:\nhttps://github.com/Dragosh7/dotPass - Restore App Section"
                )

    elif status == "ok":
        launch_app()