import customtkinter as ctk
from tkinter import messagebox
from services.transaction_service import get_budgets, set_budget
from services.category_service import get_all_categories

class BudgetView(ctk.CTkFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_instance
        self.user_id = app_instance.user_id
        # Retrasar la carga de la UI 50ms
        self.after(50, self.build_ui)

    def build_ui(self):
        lbl_title = ctk.CTkLabel(self, text="Presupuestos Mensuales", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_title.pack(pady=(30, 20))
        
        btn_add = ctk.CTkButton(self, text="+ Establecer Presupuesto", command=self._open_add_budget_dialog)
        btn_add.pack(pady=(0, 20))
        
        budgets = get_budgets(self.user_id)
        
        table_frame = ctk.CTkScrollableFrame(self, height=400)
        table_frame.pack(fill="both", expand=True, padx=40, pady=10)
        table_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        headers = ["Categoría", "Límite", "Gastado Mes Actual", "Estado"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(table_frame, text=h, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, sticky="w", padx=20, pady=5)
            
        for row, (c_id, cat_name, limit, spent) in enumerate(budgets, 1):
            ctk.CTkLabel(table_frame, text=cat_name).grid(row=row, column=0, sticky="w", padx=20, pady=5)
            ctk.CTkLabel(table_frame, text=f"S/.{limit:.2f}").grid(row=row, column=1, sticky="w", padx=20, pady=5)
            
            color = "#FF5252" if spent > limit else "green"
            ctk.CTkLabel(table_frame, text=f"S/.{spent:.2f}", text_color=color).grid(row=row, column=2, sticky="w", padx=20, pady=5)
            estado = "Excedido" if spent > limit else "En margen"
            ctk.CTkLabel(table_frame, text=estado, text_color=color).grid(row=row, column=3, sticky="w", padx=20, pady=5)

    def _open_add_budget_dialog(self):
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Establecer Presupuesto")
        self.app.center_toplevel(dialog, 400, 300)
        dialog.transient(self.app)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Categoría (Solo gastos)", font=ctk.CTkFont(weight="bold")).pack(pady=(20,5))
        cats = [c for c in get_all_categories() if c.id_subcategory is None and c.type_category == "gasto"]
        cat_names = [c.description for c in cats]
        
        combo_cat = ctk.CTkOptionMenu(dialog, values=cat_names if cat_names else ["Ninguna"])
        combo_cat.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Monto Límite (S/.)", font=ctk.CTkFont(weight="bold")).pack(pady=(10,5))
        entry_limit = ctk.CTkEntry(dialog)
        entry_limit.pack(pady=5)
        
        def save():
            cat_desc = combo_cat.get()
            cat_id = next((c.id_category for c in cats if c.description == cat_desc), None)
            if not cat_id:
                return
            try:
                lim = float(entry_limit.get())
                set_budget(self.user_id, cat_id, lim)
                dialog.destroy()
                self.app.show_presupuestos()
            except ValueError:
                messagebox.showerror("Error", "Monto inválido.")
                
        ctk.CTkButton(dialog, text="Guardar", command=save).pack(pady=20)
