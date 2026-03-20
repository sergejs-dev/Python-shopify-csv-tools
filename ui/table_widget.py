import customtkinter as ctk


class TableWidget(ctk.CTkFrame):
    def __init__(self, parent, on_row_select=None):
        super().__init__(parent)

        self.on_row_select = on_row_select
        self.data = []

    def load_data(self, df):
        self.data = df.to_dict("records")

        # очистка
        for widget in self.winfo_children():
            widget.destroy()

        headers = list(df.columns)

        # headers
        for col, header in enumerate(headers):
            lbl = ctk.CTkLabel(self, text=header, anchor="w")
            lbl.grid(row=0, column=col, padx=5, pady=3, sticky="w")

        # rows
        for row_index, row in enumerate(self.data):
            for col_index, key in enumerate(headers):
                value = str(row.get(key, ""))

                lbl = ctk.CTkLabel(self, text=value, anchor="w")
                lbl.grid(row=row_index + 1, column=col_index, padx=5, pady=2, sticky="w")

                lbl.bind(
                    "<Button-1>",
                    lambda e, r=row_index: self.select_row(r)
                )

    def select_row(self, index):
        if self.on_row_select:
            self.on_row_select(index, self.data[index]) 
