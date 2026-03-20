import customtkinter as ctk
from tkinter import messagebox, filedialog
from utils.licence import validate_license, LICENSE_FILE
import uuid
import os

#BASE_DIR = os.path.join(os.gatenv("LOCALAPPDATA"), "MoonShopifyTool")
#os.makedirs(BASE_DIR, exist_ok =True)

#LICENCE_FILE = os.path.join(BASE_DIR, "sys.dat")

class LicenseWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("License")
        self.geometry("420x320")

        self.machine_id = str(uuid.getnode())

        # Machine ID
        ctk.CTkLabel(self, text="Machine ID").pack(pady=(10, 0))

        self.id_entry = ctk.CTkEntry(self, width=320)
        self.id_entry.insert(0, self.machine_id)
        self.id_entry.configure(state="readonly")
        self.id_entry.pack(pady=5)

        ctk.CTkButton(self, text="Copy ID", command=self.copy_id).pack(pady=5)

        # License key
        ctk.CTkLabel(self, text="License Key").pack(pady=(10, 0))

        self.license_entry = ctk.CTkEntry(self, width=320)
        self.license_entry.pack(pady=5)

        # Buttons
        ctk.CTkButton(self, text="Upload License", command=self.upload).pack(pady=5)
        ctk.CTkButton(self, text="Activate", command=self.activate).pack(pady=5)

    def copy_id(self):
        self.clipboard_clear()
        self.clipboard_append(self.machine_id)
        messagebox.showinfo("Copied", "Machine ID copied")

    def upload(self):
        path = filedialog.askopenfilename(filetypes=[("License files", "*.key")])
        if path:
            with open(path, "r") as f:
                key = f.read().strip()
                self.license_entry.delete(0, "end")
                self.license_entry.insert(0, key)

    def activate(self):
        key = self.license_entry.get().strip()

        if not key:
            messagebox.showerror("Error", "Enter license key")
            return

        if validate_license(self.machine_id, key):

            # 🔥 СОХРАНЕНИЕ В ТО ЖЕ МЕСТО, ЧТО И В licence.py
            os.makedirs(os.path.dirname(LICENSE_FILE), exist_ok=True)
            print("LICENSE PATH", LICENSE_FILE)
            with open(LICENSE_FILE, "w") as f:
                f.write(key)

            messagebox.showinfo("Success", "License activated")
            self.destroy()

        else:
            messagebox.showerror("Error", "Invalid license key") 