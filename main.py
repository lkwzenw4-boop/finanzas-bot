import warnings
warnings.filterwarnings("ignore")
import multiprocessing
import customtkinter as ctk
from tkinter import messagebox
from threading import Thread

# Import custom services
from services.transaction_service import process_recurring_transactions
from models.user import User
from ai.clasificadorIA import ClasificadorIA
from services.init_service import setup_database
from services.user_service import login, create_user, get_security_question, reset_password

# Views
from views.dashboard_view import DashboardView
from views.history_view import HistoryView
from views.budget_view import BudgetView
from views.recurring_view import RecurringView
from views.registration_view import RegistrationView

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Finanzas Personales - Asistente IA")
        self.geometry("900x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.user_id = None
        self.username = None
        self.ia = None
        
        self.show_loading_screen()
        
        Thread(target=self.init_app, daemon=True).start()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askyesno("Salir", "¿Estás seguro de que deseas salir del programa?"):
            self.destroy()

    def center_toplevel(self, toplevel, width, height):
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (height // 2)
        toplevel.geometry(f"{width}x{height}+{x}+{y}")

    def show_loading_screen(self):
        self.loading_frame = ctk.CTkFrame(self)
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.loading_label = ctk.CTkLabel(self.loading_frame, text="Iniciando base de datos...", font=ctk.CTkFont(size=18, weight="bold"))
        self.loading_label.pack(pady=20, padx=20)
        self.progress_bar = ctk.CTkProgressBar(self.loading_frame, width=300)
        self.progress_bar.pack(pady=(0, 20), padx=20)
        self.progress_bar.set(0)
        self.progress_bar.start()

    def init_app(self):
        try:
            setup_database()
            self.after(0, lambda: self.loading_label.configure(text="Cargando modelo de Inteligencia Artificial (ONNX)..."))
            self.ia = ClasificadorIA()
            self.after(0, self.show_login_ui)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error de Inicialización", f"No se pudo iniciar: {e}"))
            self.after(0, self.destroy)

    def show_login_ui(self):
        self.loading_frame.destroy()
        
        self.login_frame = ctk.CTkFrame(self, corner_radius=15)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(self.login_frame, text="Iniciar Sesión", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 20), padx=50)
        
        self.entry_user = ctk.CTkEntry(self.login_frame, placeholder_text="Usuario", width=200)
        self.entry_user.pack(pady=10)
        
        self.entry_pass = ctk.CTkEntry(self.login_frame, placeholder_text="Contraseña", show="*", width=200)
        self.entry_pass.pack(pady=10)
        
        self.lbl_login_err = ctk.CTkLabel(self.login_frame, text="", text_color="#FF5252")
        self.lbl_login_err.pack(pady=(0, 10))
        
        self.btn_login = ctk.CTkButton(self.login_frame, text="Ingresar", command=self.do_login)
        self.btn_login.pack(pady=(10, 10))
        
        self.btn_register = ctk.CTkButton(self.login_frame, text="Crear nuevo perfil", fg_color="gray25", hover_color="gray35", command=self.show_register_ui)
        self.btn_register.pack(pady=5)
        
        self.btn_recover = ctk.CTkButton(self.login_frame, text="¿Olvidaste tu contraseña?", fg_color="transparent", text_color="#1f6aa5", hover_color="gray15", command=self.show_recovery_ui)
        self.btn_recover.pack(pady=(0, 20))
        
        self.bind("<Return>", lambda e: self.do_login())
        
    def do_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        
        if not username or not password:
            self.lbl_login_err.configure(text="Completa ambos campos.")
            return
            
        user_data = login(username, password)
        if user_data:
            self.user_id, self.username = user_data
            self.unbind("<Return>")
            self.login_frame.destroy()
            
            Thread(target=process_recurring_transactions, args=(self.user_id,), daemon=True).start()
            
            self.setup_main_ui()
        else:
            self.lbl_login_err.configure(text="Credenciales incorrectas.")

    def show_register_ui(self):
        reg = ctk.CTkToplevel(self)
        reg.title("Crear Nuevo Perfil")
        self.center_toplevel(reg, 400, 500)
        reg.attributes("-topmost", True)
        reg.grab_set()
        
        ctk.CTkLabel(reg, text="Registro", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        entry_usr = ctk.CTkEntry(reg, placeholder_text="Nombre de Usuario", width=250)
        entry_usr.pack(pady=10)
        entry_pwd = ctk.CTkEntry(reg, placeholder_text="Contraseña", show="*", width=250)
        entry_pwd.pack(pady=10)
        
        ctk.CTkLabel(reg, text="Pregunta de Seguridad:").pack(pady=(10, 0))
        entry_q = ctk.CTkEntry(reg, placeholder_text="Ej. ¿Nombre de mi mascota?", width=250)
        entry_q.pack(pady=5)
        
        ctk.CTkLabel(reg, text="Respuesta Secreta:").pack(pady=(10, 0))
        entry_a = ctk.CTkEntry(reg, placeholder_text="Ej. Firulais", width=250)
        entry_a.pack(pady=5)
        
        lbl_err = ctk.CTkLabel(reg, text="", text_color="#FF5252")
        lbl_err.pack(pady=5)
        
        def save():
            u, p, q, a = entry_usr.get().strip(), entry_pwd.get().strip(), entry_q.get().strip(), entry_a.get().strip()
            if not u or not p or not q or not a:
                lbl_err.configure(text="Completa todos los campos.")
                return
            try:
                user = User(username=u, password=p, security_question=q, security_answer=a)
                create_user(user)
                messagebox.showinfo("Éxito", "Perfil creado correctamente.")
                reg.destroy()
            except Exception as e:
                lbl_err.configure(text="Error al crear perfil (¿Usuario ya existe?)")
                
        ctk.CTkButton(reg, text="Registrarse", command=save).pack(pady=20)

    def show_recovery_ui(self):
        rec = ctk.CTkToplevel(self)
        rec.title("Recuperar Contraseña")
        self.center_toplevel(rec, 400, 450)
        rec.attributes("-topmost", True)
        rec.grab_set()
        
        ctk.CTkLabel(rec, text="Recuperación", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        frame_step1 = ctk.CTkFrame(rec, fg_color="transparent")
        frame_step1.pack(fill="both", expand=True, padx=20)
        
        entry_usr = ctk.CTkEntry(frame_step1, placeholder_text="Ingresa tu usuario", width=250)
        entry_usr.pack(pady=10)
        lbl_err1 = ctk.CTkLabel(frame_step1, text="", text_color="#FF5252")
        lbl_err1.pack()
        
        frame_step2 = ctk.CTkFrame(rec, fg_color="transparent")
        
        lbl_q = ctk.CTkLabel(frame_step2, text="", font=ctk.CTkFont(weight="bold"))
        entry_a = ctk.CTkEntry(frame_step2, placeholder_text="Tu respuesta secreta", width=250)
        entry_newpwd = ctk.CTkEntry(frame_step2, placeholder_text="Nueva Contraseña", show="*", width=250)
        lbl_err2 = ctk.CTkLabel(frame_step2, text="", text_color="#FF5252")
        
        current_user = {"username": ""}
        
        def check_user():
            u = entry_usr.get().strip()
            if not u:
                lbl_err1.configure(text="Ingresa tu usuario.")
                return
            q = get_security_question(u)
            if not q:
                lbl_err1.configure(text="El usuario no existe o no tiene pregunta configurada.")
            else:
                current_user["username"] = u
                frame_step1.pack_forget()
                frame_step2.pack(fill="both", expand=True, padx=20)
                lbl_q.configure(text=q)
                lbl_q.pack(pady=10)
                entry_a.pack(pady=10)
                entry_newpwd.pack(pady=10)
                lbl_err2.pack()
                ctk.CTkButton(frame_step2, text="Restablecer", command=do_reset).pack(pady=20)
                
        ctk.CTkButton(frame_step1, text="Siguiente", command=check_user).pack(pady=20)
        
        def do_reset():
            ans = entry_a.get().strip()
            npwd = entry_newpwd.get().strip()
            if not ans or not npwd:
                lbl_err2.configure(text="Completa los campos.")
                return
            if reset_password(current_user["username"], ans, npwd):
                messagebox.showinfo("Éxito", "Contraseña restablecida correctamente.")
                rec.destroy()
            else:
                lbl_err2.configure(text="Respuesta incorrecta.")

    def setup_main_ui(self):
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.nav_label = ctk.CTkLabel(self.navigation_frame, text=f"Hola,\n{self.username}", font=ctk.CTkFont(size=20, weight="bold"))
        self.nav_label.grid(row=0, column=0, padx=20, pady=20)

        self.btn_dashboard = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Dashboard",
                                           fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                           command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, sticky="ew")

        self.btn_ingresos = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Registrar Ingreso",
                                          fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                          command=lambda: self.show_registro("ingreso"))
        self.btn_ingresos.grid(row=2, column=0, sticky="ew")

        self.btn_gastos = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Registrar Gasto",
                                        fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                        command=lambda: self.show_registro("gasto"))
        self.btn_gastos.grid(row=3, column=0, sticky="ew")

        self.btn_historial = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Historial Reciente",
                                           fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                           command=self.show_historial)
        self.btn_historial.grid(row=4, column=0, sticky="ew")
        
        self.btn_presupuestos = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Presupuestos",
                                           fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                           command=self.show_presupuestos)
        self.btn_presupuestos.grid(row=5, column=0, sticky="ew")

        self.btn_fijos = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Suscripciones/Fijos",
                                           fg_color="transparent", text_color=("gray10", "gray90"), anchor="w",
                                           command=self.show_fijos)
        self.btn_fijos.grid(row=6, column=0, sticky="ew")
        
        self.navigation_frame.grid_rowconfigure(7, weight=1)
        
        self.btn_logout = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Cambiar Usuario",
                                        fg_color="transparent", text_color="#FF5252", hover_color="#D32F2F", anchor="w",
                                        command=self.do_logout)
        self.btn_logout.grid(row=8, column=0, sticky="ew", pady=(0, 20))
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        self.show_dashboard()

    def do_logout(self):
        if messagebox.askyesno("Cambiar Usuario", "¿Estás seguro que deseas cerrar sesión?"):
            self.navigation_frame.destroy()
            self.main_frame.destroy()
            self.user_id = None
            self.username = None
            self.show_login_ui()

    def select_menu(self, name):
        self.btn_dashboard.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.btn_ingresos.configure(fg_color=("gray75", "gray25") if name == "ingreso" else "transparent")
        self.btn_gastos.configure(fg_color=("gray75", "gray25") if name == "gasto" else "transparent")
        self.btn_historial.configure(fg_color=("gray75", "gray25") if name == "historial" else "transparent")
        self.btn_presupuestos.configure(fg_color=("gray75", "gray25") if name == "presupuestos" else "transparent")
        self.btn_fijos.configure(fg_color=("gray75", "gray25") if name == "fijos" else "transparent")
        
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _check_budget_alert(self, id_categoria):
        # Migrated from main to support alert in RegistrationView
        from services.transaction_service import get_budgets
        budgets = get_budgets(self.user_id)
        for b_id, desc, limit, spent in budgets:
            if b_id == id_categoria and spent > limit:
                messagebox.showwarning("¡Alerta de Presupuesto!", 
                    f"Has excedido tu presupuesto mensual para {desc}.\n\nLímite: S/.{limit:.2f}\nGastado: S/.{spent:.2f}")

    def show_dashboard(self):
        self.select_menu("dashboard")
        view = DashboardView(self.main_frame, self.user_id)
        view.pack(fill="both", expand=True)
        
    def show_registro(self, tipo):
        self.select_menu(tipo)
        view = RegistrationView(self.main_frame, self, tipo)
        view.pack(fill="both", expand=True)
        
    def show_historial(self):
        self.select_menu("historial")
        view = HistoryView(self.main_frame, self.user_id)
        view.pack(fill="both", expand=True)
        
    def show_presupuestos(self):
        self.select_menu("presupuestos")
        view = BudgetView(self.main_frame, self)
        view.pack(fill="both", expand=True)
        
    def show_fijos(self):
        self.select_menu("fijos")
        view = RecurringView(self.main_frame, self)
        view.pack(fill="both", expand=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = App()
    app.mainloop()