import customtkinter as ctk
from ui.main_window import MainWindow
from utils.licence import resource_path


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------- THEME ----------------
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ---------------- WINDOW ----------------
        self.title("Shopify CSV Tool")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # ---------------- ICON ----------------
        try:
            icon_path = resource_path("assets/icon.ico")
            self.iconbitmap(icon_path)
        except:
            pass

        # ---------------- MAIN UI ----------------
        self.main_window = MainWindow(self)
        self.main_window.pack(fill="both", expand=True)

        # ---------------- CENTER ----------------
        self._center_window()

    def _center_window(self):
        self.update_idletasks()

        width = 1200
        height = 750

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        self.geometry(f"{width}x{height}+{x}+{y}")


# ---------------- START ----------------
if __name__ == "__main__":
    app = App()
    app.mainloop() 