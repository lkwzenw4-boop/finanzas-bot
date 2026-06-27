import customtkinter as ctk
from tkinter import messagebox
import os
import csv
from datetime import datetime
from services.transaction_service import get_recent_transactions, delete_transaction

class HistoryView(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user_id = user_id
        
        self.meses = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        current_year = datetime.now().year
        self.anios = ["Todos"] + [str(y) for y in range(current_year - 5, current_year + 1)]
        
        # Retrasar la carga de la UI 50ms
        self.after(50, self.build_ui)

    def build_ui(self):
        lbl_title = ctk.CTkLabel(self, text="Últimas Transacciones", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_title.pack(pady=(30, 10))
        
        # Filtros
        filtros_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtros_frame.pack(pady=10)
        
        ctk.CTkLabel(filtros_frame, text="Mes:").grid(row=0, column=0, padx=5)
        self.combo_mes = ctk.CTkComboBox(filtros_frame, values=self.meses, command=self.recargar_tabla)
        self.combo_mes.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(filtros_frame, text="Año:").grid(row=0, column=2, padx=5)
        self.combo_anio = ctk.CTkComboBox(filtros_frame, values=self.anios, command=self.recargar_tabla)
        self.combo_anio.grid(row=0, column=3, padx=5)
        
        self.combo_mes.set("Todos")
        self.combo_anio.set("Todos")
        
        btn_export = ctk.CTkButton(filtros_frame, text="📥 Exportar a CSV", command=self.exportar_csv)
        btn_export.grid(row=0, column=4, padx=20)
        
        # Contenedor de la tabla
        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=40, pady=10)
        
        self.recargar_tabla()
        
    def recargar_tabla(self, _=None):
        for widget in self.table_container.winfo_children():
            widget.destroy()
            
        table_frame = ctk.CTkScrollableFrame(self.table_container)
        table_frame.pack(fill="both", expand=True)
        table_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        
        headers = ["Fecha", "Tipo", "Categoría", "Descripción", "Monto", "Acciones"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(table_frame, text=h, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col, sticky="w", padx=10, pady=5)
            
        mes_idx = self.meses.index(self.combo_mes.get())
        mes_str = f"{mes_idx:02d}" if mes_idx > 0 else None
        anio_str = self.combo_anio.get() if self.combo_anio.get() != "Todos" else None
            
        transacciones = get_recent_transactions(self.user_id, limit=100, month=mes_str, year=anio_str)
        
        if not transacciones:
            ctk.CTkLabel(table_frame, text="No hay transacciones en esta fecha.").grid(row=1, column=0, columnspan=5, pady=20)
            return

        for row, (id_txn, desc, amount, type_txn, cat_name, fecha) in enumerate(transacciones, 1):
            fecha_str = str(fecha)[:10] if fecha else "---"
            tipo_color = "green" if type_txn == "ingreso" else "#FF5252"
            
            ctk.CTkLabel(table_frame, text=fecha_str).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            ctk.CTkLabel(table_frame, text=type_txn.capitalize(), text_color=tipo_color).grid(row=row, column=1, sticky="w", padx=10, pady=5)
            ctk.CTkLabel(table_frame, text=cat_name or "Sin Cat.").grid(row=row, column=2, sticky="w", padx=10, pady=5)
            ctk.CTkLabel(table_frame, text=desc[:30]).grid(row=row, column=3, sticky="w", padx=10, pady=5)
            
            signo = "+" if type_txn == "ingreso" else "-"
            ctk.CTkLabel(table_frame, text=f"{signo} S/.{amount:.2f}", text_color=tipo_color, font=ctk.CTkFont(weight="bold")).grid(row=row, column=4, sticky="e", padx=10, pady=5)
            
            actions_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            actions_frame.grid(row=row, column=5, sticky="w", padx=10, pady=5)
            
            btn_edit = ctk.CTkButton(actions_frame, text="✏️ Editar", width=60, fg_color="gray25", hover_color="gray35",
                                     command=lambda t_id=id_txn, d=desc, a=amount, t=type_txn, c=cat_name: self._mostrar_dialogo_editar(t_id, d, a, t, c))
            btn_edit.pack(side="left", padx=(0, 5))
            
            btn_delete = ctk.CTkButton(actions_frame, text="🗑️", width=30, fg_color="#E74C3C", hover_color="#C0392B",
                                     command=lambda t_id=id_txn: self._eliminar_transaccion(t_id))
            btn_delete.pack(side="left")

    def _eliminar_transaccion(self, id_txn):
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar esta transacción del historial?"):
            if delete_transaction(id_txn):
                self.recargar_tabla()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la transacción.")

    def _mostrar_dialogo_editar(self, id_txn, current_desc, current_amount, type_txn, current_cat_name):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Transacción")
        dialog.geometry("400x350")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        from services.category_service import get_all_categories
        cats = [c for c in get_all_categories() if c.type_category == type_txn]
        cat_names = [c.description for c in cats]

        ctk.CTkLabel(dialog, text="Categoría", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        combo_cat = ctk.CTkOptionMenu(dialog, values=cat_names if cat_names else ["Ninguna"])
        combo_cat.pack(pady=5)
        if current_cat_name in cat_names:
            combo_cat.set(current_cat_name)

        ctk.CTkLabel(dialog, text="Monto (S/.)", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        entry_monto = ctk.CTkEntry(dialog)
        entry_monto.pack(pady=5)
        entry_monto.insert(0, str(current_amount))

        ctk.CTkLabel(dialog, text="Descripción", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        entry_desc = ctk.CTkEntry(dialog)
        entry_desc.pack(pady=5)
        entry_desc.insert(0, current_desc)

        def save():
            try:
                new_amount = float(entry_monto.get())
                new_desc = entry_desc.get().strip()
                cat_desc = combo_cat.get()
                cat_id = next((c.id_category for c in cats if c.description == cat_desc), None)
                
                if not new_desc:
                    messagebox.showerror("Error", "La descripción no puede estar vacía")
                    return
                if not cat_id:
                    messagebox.showerror("Error", "Debes seleccionar una categoría válida")
                    return
                
                from services.transaction_service import update_transaction
                if update_transaction(id_txn, new_amount, new_desc, cat_id):
                    dialog.destroy()
                    self.recargar_tabla()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la transacción")
            except ValueError:
                messagebox.showerror("Error", "Monto inválido")

        ctk.CTkButton(dialog, text="Guardar Cambios", command=save).pack(pady=20)

    def exportar_csv(self):
        try:
            mes_idx = self.meses.index(self.combo_mes.get())
            mes_str = f"{mes_idx:02d}" if mes_idx > 0 else None
            anio_str = self.combo_anio.get() if self.combo_anio.get() != "Todos" else None
            
            transacciones = get_recent_transactions(self.user_id, limit=1000, month=mes_str, year=anio_str)
            if not transacciones:
                messagebox.showinfo("Exportar", "No hay transacciones para exportar.")
                return
                
            default_filename = f"Reporte_Finanzas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filename = ctk.filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=default_filename,
                title="Guardar reporte como",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
            )
            
            if not filename:
                return # Usuario canceló
            
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Fecha", "Tipo", "Categoría", "Descripción", "Monto"])
                for id_txn, desc, amount, type_txn, cat_name, fecha in transacciones:
                    writer.writerow([fecha, type_txn, cat_name, desc, amount])
            
            messagebox.showinfo("Éxito", f"Archivo exportado correctamente a:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")
