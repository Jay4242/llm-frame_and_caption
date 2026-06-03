import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

from .ui.main_window import MainWindow


def main():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    root = TkinterDnD.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
