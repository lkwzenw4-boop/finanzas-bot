import customtkinter as ctk
from tkinter import messagebox
from threading import Thread
from models.transaction import Transaction
from services.transaction_service import insert_transaction, get_category_from_history
from services.category_service import get_all_categories, get_category_name_by_id

class RegistrationView(ctk.CTkFrame):
    def __init__(self, master, app_instance, tipo, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_instance
        self.user_id = app_instance.user_id
        self.ia = app_instance.ia
        self.tipo = tipo
        self.build_ui()
        
    def build_ui(self):
        label = "Ingreso" if self.tipo == "ingreso" else "Gasto"
        
        lbl_title = ctk.CTkLabel(self, text=f"Registrar Nuevo {label}", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_title.pack(pady=(40, 20))
        
        form_frame = ctk.CTkFrame(self, width=400)
        form_frame.pack(pady=10, padx=50, fill="y")
        
        ctk.CTkLabel(form_frame, text="Monto (S/.)", anchor="w").pack(fill="x", padx=30, pady=(20, 5))
        self.entry_monto = ctk.CTkEntry(form_frame, placeholder_text="0.00", font=ctk.CTkFont(size=18))
        self.entry_monto.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="Descripción", anchor="w").pack(fill="x", padx=30, pady=(0, 5))
        self.entry_desc = ctk.CTkEntry(form_frame, placeholder_text="Ej. Almuerzo en restaurante")
        self.entry_desc.pack(fill="x", padx=30, pady=(0, 30))
        
        self.btn_guardar = ctk.CTkButton(form_frame, text="Guardar con IA ✨", height=40, font=ctk.CTkFont(weight="bold"), 
                                         command=self.guardar_transaccion)
        self.btn_guardar.pack(fill="x", padx=30, pady=(0, 30))
        
        self.lbl_estado = ctk.CTkLabel(form_frame, text="", text_color="green", font=ctk.CTkFont(size=12))
        self.lbl_estado.pack(pady=(0, 10))
        
    def guardar_transaccion(self):
        try:
            monto_str = self.entry_monto.get().strip()
            desc = self.entry_desc.get().strip()
            
            if not monto_str or not desc:
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
                
            amount = float(monto_str)
            if amount <= 0:
                messagebox.showwarning("Error", "El monto debe ser mayor a cero")
                return
                
            self.btn_guardar.configure(state="disabled", text="Analizando...")
            self.lbl_estado.configure(text="La IA está categorizando...", text_color="orange")
            
            Thread(target=self._procesar_transaccion, args=(amount, desc), daemon=True).start()
            
        except ValueError:
            messagebox.showwarning("Error", "Ingresa un monto numérico válido")
            
    def _procesar_transaccion(self, amount, desc):
        try:
            if self.tipo == "gasto" and desc.lower() == "tc":
                self.after(0, lambda: self._mostrar_dialogo_tc(amount))
                return
                
            if "yape" in desc.lower():
                if self.tipo == "gasto":
                    self.after(0, lambda: self._mostrar_dialogo_yape(amount, desc))
                    return
                elif self.tipo == "ingreso":
                    if "(Yape)" not in desc:
                        desc = f"{desc} (Yape)"
            
            self._procesar_transaccion_ia(amount, desc)
            
        except Exception as e:
            self.after(0, lambda: self._fin_registro(False, str(e)))
            
    def _procesar_transaccion_ia(self, amount, desc):
        try:
            # ACTIVE LEARNING: Check database history first
            hist_cat_id = get_category_from_history(self.user_id, desc)
            subcat_nombre = None
            
            if hist_cat_id:
                id_final = hist_cat_id
                cat_nombre = get_category_name_by_id(id_final) or "Categoría Histórica"
                msg = f"Auto-categorizado por historial:\n\n{cat_nombre}"
            else:
                # Fallback to ONNX AI
                id_categoria, cat_nombre = self.ia.categorizar_y_mapear(desc, self.tipo)
                from services.category_service import get_subcategories_by_parent
                subcats = get_subcategories_by_parent(id_categoria)
                id_final = id_categoria
                
                if subcats:
                    id_sub, s_name = self.ia.categorizar_y_mapear_subcategoria(desc, subcats)
                    if id_sub:
                        id_final = id_sub
                        subcat_nombre = s_name
                        
                msg = f"Categorizado por IA como:\n\n{cat_nombre}"
                if subcat_nombre:
                    msg += f" -> {subcat_nombre}"

            txn = Transaction(
                description=desc,
                amount=amount,
                type_txn=self.tipo,
                id_user=self.user_id,
                id_category=id_final
            )
            insert_transaction(txn)
            
            if self.tipo == "gasto":
                self.after(500, lambda: self.app._check_budget_alert(id_final))
                
            self.after(0, lambda: self._fin_registro(True, msg))
            
        except Exception as e:
            self.after(0, lambda: self._fin_registro(False, str(e)))
            
    def _mostrar_dialogo_tc(self, amount):
        bancos = [(49, 'BCP'), (50, 'Interbank'), (51, 'BBVA'), (52, 'Falabella'), (53, 'Ripley'), (54, 'Scotiabank')]
        
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Seleccionar Tarjeta")
        self.app.center_toplevel(dialog, 300, 400)
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="¿De qué banco es?", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        def on_select(id_final, banco):
            desc = f"Pago de Tarjeta - {banco}"
            txn = Transaction(
                description=desc,
                amount=amount,
                type_txn=self.tipo,
                id_user=self.user_id,
                id_category=id_final
            )
            insert_transaction(txn)
            dialog.destroy()
            self._fin_registro(True, f"Tarjetas de Credito -> {banco}")
            
        for (id_banco, banco_name) in bancos:
            btn = ctk.CTkButton(dialog, text=banco_name, fg_color="gray25", 
                                command=lambda i=id_banco, n=banco_name: on_select(i, n))
            btn.pack(pady=10, padx=40, fill="x")
            
        dialog.protocol("WM_DELETE_WINDOW", lambda: [dialog.destroy(), self._fin_registro(False, "Cancelado")])
        
    def _mostrar_dialogo_yape(self, amount, desc):
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Registro de Yape")
        self.app.center_toplevel(dialog, 300, 300)
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="¿Qué tipo de pago Yape es?", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        def on_prestamo():
            txn = Transaction(
                description=desc,
                amount=amount,
                type_txn=self.tipo,
                id_user=self.user_id,
                id_category=58
            )
            insert_transaction(txn)
            dialog.destroy()
            self._fin_registro(True, "Préstamos -> Préstamo Yape")
            
        def on_pago_normal():
            dialog.destroy()
            nueva_desc = desc if "(Yape)" in desc else f"{desc} (Yape)"
            self.lbl_estado.configure(text="La IA está categorizando el pago Yape...", text_color="orange")
            Thread(target=self._procesar_transaccion_ia, args=(amount, nueva_desc), daemon=True).start()

        btn_prestamo = ctk.CTkButton(dialog, text="Préstamo Yape", fg_color="#6F239A", hover_color="#541B75", command=on_prestamo)
        btn_prestamo.pack(pady=10, padx=40, fill="x")
        
        btn_pago = ctk.CTkButton(dialog, text="Pago Normal", fg_color="gray25", hover_color="gray35", command=on_pago_normal)
        btn_pago.pack(pady=10, padx=40, fill="x")
        
        dialog.protocol("WM_DELETE_WINDOW", lambda: [dialog.destroy(), self._fin_registro(False, "Cancelado")])
        
    def _fin_registro(self, exito, mensaje):
        self.btn_guardar.configure(state="normal", text="Guardar con IA ✨")
        if exito:
            self.lbl_estado.configure(text=f"¡Guardado!\n{mensaje}", text_color="green")
            self.entry_desc.delete(0, 'end')
            self.entry_monto.delete(0, 'end')
        else:
            if mensaje != "Cancelado":
                self.lbl_estado.configure(text=f"Error: {mensaje}", text_color="#FF5252")
            else:
                self.lbl_estado.configure(text="")
