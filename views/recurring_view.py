import customtkinter as ctk
from tkinter import messagebox
from services.transaction_service import get_recurring, add_recurring, delete_recurring
from services.category_service import get_all_categories

class RecurringView(ctk.CTkFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_instance
        self.user_id = app_instance.user_id
        # Retrasar la carga de la UI 50ms
        self.after(50, self.build_ui)

    def build_ui(self):
        lbl_title = ctk.CTkLabel(self, text="Gastos Fijos Automáticos", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_title.pack(pady=(30, 20))
        
        btn_add = ctk.CTkButton(self, text="+ Agregar Gasto Fijo", command=self._open_add_recurring_dialog)
        btn_add.pack(pady=(0, 20))
        
        recs = get_recurring(self.user_id)
        
        table_frame = ctk.CTkScrollableFrame(self, height=400)
        table_frame.pack(fill="both", expand=True, padx=40, pady=10)
        table_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        
        headers = ["Descripción", "Categoría", "Monto", "Día de Cobro", "Acciones"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(table_frame, text=h, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, sticky="w", padx=20, pady=5)
            
        for row, (r_id, desc, amount, t_txn, cat_name, day) in enumerate(recs, 1):
            ctk.CTkLabel(table_frame, text=desc).grid(row=row, column=0, sticky="w", padx=20, pady=5)
            ctk.CTkLabel(table_frame, text=cat_name).grid(row=row, column=1, sticky="w", padx=20, pady=5)
            ctk.CTkLabel(table_frame, text=f"S/.{amount:.2f}").grid(row=row, column=2, sticky="w", padx=20, pady=5)
            ctk.CTkLabel(table_frame, text=f"Día {day}").grid(row=row, column=3, sticky="w", padx=20, pady=5)
            btn_del = ctk.CTkButton(table_frame, text="🗑️ Eliminar", width=60, fg_color="#FF5252", hover_color="#D32F2F",
                                    command=lambda rid=r_id: self._delete_recurring(rid))
            btn_del.grid(row=row, column=4, sticky="w", padx=20, pady=5)
            
    def _delete_recurring(self, r_id):
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este gasto fijo?"):
            delete_recurring(r_id)
            self.app.show_fijos()

    def _open_add_recurring_dialog(self):
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Agregar Gasto Fijo")
        self.app.center_toplevel(dialog, 400, 450)
        dialog.transient(self.app)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Descripción", font=ctk.CTkFont(weight="bold")).pack(pady=(20,5))
        entry_desc = ctk.CTkEntry(dialog)
        entry_desc.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Categoría (Gasto)", font=ctk.CTkFont(weight="bold")).pack(pady=(10,5))
        cats = [c for c in get_all_categories() if c.id_subcategory is None and c.type_category == "gasto"]
        cat_names = [c.description for c in cats]
        combo_cat = ctk.CTkOptionMenu(dialog, values=cat_names if cat_names else ["Ninguna"])
        combo_cat.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Monto (S/.)", font=ctk.CTkFont(weight="bold")).pack(pady=(10,5))
        entry_monto = ctk.CTkEntry(dialog)
        entry_monto.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Día del mes (1-31)", font=ctk.CTkFont(weight="bold")).pack(pady=(10,5))
        combo_dia = ctk.CTkOptionMenu(dialog, values=[str(i) for i in range(1,32)])
        combo_dia.pack(pady=5)
        
        def save():
            desc = entry_desc.get().strip()
            if not desc:
                messagebox.showerror("Error", "Ingresa una descripción.")
                return
            cat_desc = combo_cat.get()
            cat_id = next((c.id_category for c in cats if c.description == cat_desc), None)
            if not cat_id:
                return
            try:
                monto = float(entry_monto.get())
                dia = int(combo_dia.get())
                add_recurring(self.user_id, desc, monto, "gasto", cat_id, dia)
                dialog.destroy()
                self.app.show_fijos()
            except ValueError:
                messagebox.showerror("Error", "Monto inválido.")
                
        ctk.CTkButton(dialog, text="Guardar", command=save).pack(pady=20)
