def center_window(window, width: int, height: int):
    """Centers a CTk or CTkToplevel window on the screen."""
    window.update_idletasks()  #screen size info
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 1.5)
    window.geometry(f"{width}x{height}+{x}+{y}")
