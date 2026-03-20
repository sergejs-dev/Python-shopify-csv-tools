import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import webbrowser
from PIL import Image
import re
import uuid
import urllib.parse
from datetime import datetime
from ui.licence_window import LicenseWindow
from utils.licence import resource_path


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ===== STORAGE (ЕДИНЫЙ ПУТЬ) =====
APP_DIR = os.path.join(os.getenv("LOCALAPPDATA"), "MoonShopifyTool")
os.makedirs(APP_DIR, exist_ok=True)

LICENSE_FILE = os.path.join(APP_DIR, "sys.dat")
DEMO_FILE = os.path.join(APP_DIR, "cache.dat")

DEMO_DAYS = 14


class MainWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill="both", expand=True)

        self.df = None
        self.tree = None
        self.entries = {}
        self.selected_item = None
        self.original_values = None
        self.buttons = []

        self.licensed = False

        self.check_demo()
        self._build_menu()
        self._build_ui()

        if not self.licensed:
            self.check_demo_expired()

    # ================= DEMO =================
    def check_demo(self):
        # ✅ ЕСЛИ ЛИЦЕНЗИЯ ЕСТЬ → НЕ ДЕМО
        if os.path.exists(LICENSE_FILE):
            self.licensed = True
            return

        if not os.path.exists(DEMO_FILE):
            with open(DEMO_FILE, "w") as f:
                f.write(datetime.now().isoformat())

        with open(DEMO_FILE, "r") as f:
            start = datetime.fromisoformat(f.read())

        self.remaining_days = DEMO_DAYS - (datetime.now() - start).days

        if self.remaining_days < 0:
            self.remaining_days = 0

    def check_demo_expired(self):
        if self.remaining_days <= 0:
            messagebox.showerror(
                "Expired",
                "Demo period expired.\nPlease activate license."
            )
            self.disable_all()

    def disable_all(self):
        for btn in self.buttons:
            btn.configure(state="disabled")

        if self.tree:
            self.tree.configure(selectmode="none")

        for entry in self.entries.values():
            entry.configure(state="disabled")

    # ================= MENU =================
    def _build_menu(self):
        menubar = tk.Menu(self.parent)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="License", command=self.open_license)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.parent.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Manual", command=self.open_user_manual)
        help_menu.add_command(label="About", command=self.open_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.parent.config(menu=menubar)

    # ================= UI =================
    def _build_ui(self):
        top = ctk.CTkFrame(self)
        top.pack(fill="x", pady=10)
        logo_path = resource_path("assets/logo.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
        #if os.path.exists("assets/logo.png"):
          #  img = Image.open("assets/logo.png")
            logo = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
            ctk.CTkLabel(top, image=logo, text="").pack(side="left", padx=10)
            self.logo = logo

        ctk.CTkLabel(top, text="Shopify Custom Tool", font=("Arial", 24)).pack(side="left")

        if not self.licensed:
            ctk.CTkLabel(
                top,
                text=f"Demo ({self.remaining_days} days left)",
                text_color="orange"
            ).pack(side="right", padx=10)

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10)

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=10, pady=10)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        buttons = [
            ("Load CSV", self.load_csv),
            ("Undo", self.undo_row),
            ("Save", self.save_row),
            ("Delete", self.delete_row),
            ("Export", self.export_csv),
            ("View", self.view_row),
            ("Clear", self.clear_fields),
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = ctk.CTkButton(btn_frame, text=text, command=cmd)
            btn.grid(row=0, column=i, padx=5, pady=5)
            self.buttons.append(btn)

    # ================= LICENSE =================
    def open_license(self):
        LicenseWindow(self)

    # ================= CSV =================
    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return

        self.df = pd.read_csv(path)
        self._show_table()
        self._build_form()

    def _show_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        frame = tk.Frame(self.table_frame)
        frame.pack(fill="both", expand=True)

        y_scroll = tk.Scrollbar(frame)
        y_scroll.pack(side="right", fill="y")

        x_scroll = tk.Scrollbar(frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            frame,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        self.tree["columns"] = list(self.df.columns)

        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        for _, row in self.df.iterrows():
            self.tree.insert("", "end", values=list(row))

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def _build_form(self):
        for w in self.form_frame.winfo_children():
            w.destroy()

        self.entries.clear()

        for i, col in enumerate(self.df.columns):
            row = i // 2
            col_pos = (i % 2) * 2

            ctk.CTkLabel(self.form_frame, text=col).grid(row=row, column=col_pos, padx=5, pady=5)

            entry = ctk.CTkEntry(self.form_frame, width=250)
            entry.grid(row=row, column=col_pos + 1, padx=5, pady=5)

            self.entries[col] = entry

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        self.selected_item = selected[0]
        values = self.tree.item(self.selected_item)["values"]
        self.original_values = values.copy()

        for i, col in enumerate(self.df.columns):
            self.entries[col].delete(0, "end")
            self.entries[col].insert(0, values[i])

    def undo_row(self):
        if not self.original_values:
            return

        for i, col in enumerate(self.df.columns):
            self.entries[col].delete(0, "end")
            self.entries[col].insert(0, self.original_values[i])

    def save_row(self):
        if not self.selected_item:
            return

        values = [self.entries[col].get() for col in self.df.columns]
        self.tree.item(self.selected_item, values=values)
        messagebox.showinfo("Saved","Row updated successfully")

    def delete_row(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select at least one row to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {len(selected)} selected row(s)?"
        )

        if not confirm:
            return

        for item in selected:
            self.tree.delete(item)

        messagebox.showinfo(
            "Deleted",
            f"{len(selected)} row(s) deleted"
        ) 

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return

        rows = []
        for item in self.tree.get_children():
            rows.append(self.tree.item(item)["values"])

        pd.DataFrame(rows, columns=self.df.columns).to_csv(path, index=False)
        messagebox.showinfo(
            "Export Completed",
            f"File saved successfully:\n{path}"
        )

    def view_row(self):
        if self.df is None:
            return

        self.parent.withdraw()

        win = ctk.CTkToplevel(self)
        win.state("zoomed")

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, show="headings")
        tree.pack(fill="both", expand=True)

        tree["columns"] = list(self.df.columns)

        for col in self.df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        for item in self.tree.get_children():
            tree.insert("", "end", values=self.tree.item(item)["values"])

        def close():
            win.destroy()
            self.parent.deiconify()

        ctk.CTkButton(win, text="Close", command=close).pack(pady=10)

    def clear_fields(self):
        for e in self.entries.values():
            e.delete(0, "end")

    # ================= ABOUT =================
    def open_about(self):
        win = ctk.CTkToplevel(self)
        win.title("About")
        win.geometry("420x520")

        ctk.CTkLabel(win, text="Shopify Tool", font=("Arial", 22, "bold")).pack(pady=10)
        ctk.CTkLabel(win, text="Developed by The Moon Studio").pack()

        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack()

        ctk.CTkLabel(frame, text="Price: ").pack(side="left")

        ctk.CTkLabel(
        frame,
        text="$15",
        font=("Arial", 18, "bold")
        ).pack(side="left") 
       # ctk.CTkLabel(win, text="Developed by The Moon Studio      \nPrice: 15$").pack()
        ctk.CTkLabel(win, text="sdfreelance@inbox.lv").pack(pady=5)

        name = ctk.CTkEntry(win,width =260, placeholder_text="Your name")
        name.pack(pady=5)

        email = ctk.CTkEntry(win,width =260, placeholder_text="Your email")
        email.pack(pady=5)

        msg = ctk.CTkTextbox(win,width =260, height=100)
        msg.pack(pady=5)

        def send():
            user_name = name.get().strip()
            user_email = email.get().strip()
            user_msg = msg.get("1.0", "end-1c").strip()

            if not user_name or not user_email or not user_msg:
                messagebox.showerror("Error", "Fill all fields")
                return

            if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
                messagebox.showerror("Error", "Invalid email")
                return

            subject = urllib.parse.quote(f"Message from {user_name}")
            body = urllib.parse.quote(f"{user_msg}\nEmail: {user_email}")

            webbrowser.open(f"mailto:sdfreelance@inbox.lv?subject={subject}&body={body}")

        ctk.CTkButton(win, text="Send", command=send).pack(pady=10)

    def open_user_manual(self):
        path = os.path.abspath("help/user_manual.pdf")
        if os.path.exists(path):
            webbrowser.open(path) 