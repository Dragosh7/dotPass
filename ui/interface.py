import tkinter as tk

def launch_app():
    root = tk.Tk()
    root.title("dotPass - Password Manager")
    root.geometry("500x400")
    label = tk.Label(root, text="Welcome to dotPass", font=("Arial", 18))
    label.pack(pady=20)
    root.mainloop()