import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from services.transaction_service import get_financial_summary, get_report_by_category

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user_id = user_id
        # Retrasar la carga de la UI 50ms para que el cambio de pestaña sea instantáneo visualmente
        self.after(50, self.build_ui)

    def build_ui(self):
        try:
            summary = get_financial_summary(self.user_id)
            total_inc = summary["total_income"]
            total_exp = summary["total_expense"]
            net_bal = summary["net_balance"]
            
            lbl_title = ctk.CTkLabel(self, text="Resumen Financiero", font=ctk.CTkFont(size=24, weight="bold"))
            lbl_title.pack(pady=(30, 20))
            
            # Cards frame
            cards_frame = ctk.CTkFrame(self, fg_color="transparent")
            cards_frame.pack(fill="x", padx=40, pady=10)
            cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Card Ingresos
            card_inc = ctk.CTkFrame(cards_frame, corner_radius=15)
            card_inc.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card_inc, text="Total Ingresos", text_color="green", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
            ctk.CTkLabel(card_inc, text=f"S/. {total_inc:,.2f}", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(0, 20))
            
            # Card Gastos
            card_exp = ctk.CTkFrame(cards_frame, corner_radius=15)
            card_exp.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card_exp, text="Total Gastos", text_color="#FF5252", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
            ctk.CTkLabel(card_exp, text=f"S/. {total_exp:,.2f}", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(0, 20))
            
            # Card Balance
            card_bal = ctk.CTkFrame(cards_frame, corner_radius=15)
            card_bal.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
            bal_color = "green" if net_bal >= 0 else "#FF5252"
            ctk.CTkLabel(card_bal, text="Balance Neto", text_color=bal_color, font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
            ctk.CTkLabel(card_bal, text=f"S/. {net_bal:,.2f}", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(0, 20))
            
            # Panel Insight de IA
            this_m = summary.get("this_month_expense", 0)
            last_m = summary.get("last_month_expense", 0)
            
            if last_m > 0:
                diff = ((this_m - last_m) / last_m) * 100
                if diff > 0:
                    insight = f"¡Atención! Has gastado un {abs(diff):.1f}% MÁS que el mes pasado en estas fechas. Te sugiero revisar tus categorías altas."
                    color_insight = "orange"
                else:
                    insight = f"¡Genial! Has gastado un {abs(diff):.1f}% MENOS que el mes pasado. Excelente control financiero."
                    color_insight = "green"
            elif this_m > 0:
                insight = "Recién comenzamos a registrar tus datos. ¡Sigue así para obtener análisis predictivos el próximo mes!"
                color_insight = "gray90"
            else:
                insight = "No hay suficientes datos de gastos este mes para generar predicciones o comparativas."
                color_insight = "gray90"
                
            insight_frame = ctk.CTkFrame(self, fg_color="#1F2A38", corner_radius=10)
            insight_frame.pack(fill="x", padx=50, pady=(10, 20))
            ctk.CTkLabel(insight_frame, text="💡 Nota de la Inteligencia Artificial", text_color="#4FC3F7", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
            ctk.CTkLabel(insight_frame, text=insight, text_color=color_insight, wraplength=700, justify="left").pack(anchor="w", padx=20, pady=(5, 15))
            
            # Barra de progreso
            if total_inc > 0:
                pct = (total_exp / total_inc) * 100
                prog_frame = ctk.CTkFrame(self)
                prog_frame.pack(fill="x", padx=50, pady=40)
                ctk.CTkLabel(prog_frame, text=f"Ratio Gasto/Ingreso ({pct:.1f}%)", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
                bar = ctk.CTkProgressBar(prog_frame, height=20, corner_radius=10)
                bar.pack(fill="x", padx=20, pady=(0, 15))
                bar.set(min(1.0, total_exp / total_inc))
                if pct > 90:
                    bar.configure(progress_color="#FF5252")
                elif pct > 70:
                    bar.configure(progress_color="orange")
                else:
                    bar.configure(progress_color="green")
                    
            # Add a frame for charts below the progress bar
            charts_frame = ctk.CTkFrame(self, fg_color="transparent")
            charts_frame.pack(fill="both", expand=True, padx=40, pady=10)
            charts_frame.grid_columnconfigure((0,1), weight=1)
            
            # Pie Chart: Gastos por Categoria
            reporte = get_report_by_category(self.user_id, "gasto")
            if reporte:
                fig, ax = plt.subplots(figsize=(4, 4), facecolor='#2b2b2b')
                cat_totals = {}
                for cat, sub, tot in reporte:
                    cat_totals[cat] = cat_totals.get(cat, 0) + tot
                
                # Filtrar solo mayores a 0
                cat_totals = {k: v for k, v in cat_totals.items() if v > 0}
                if cat_totals:
                    labels = list(cat_totals.keys())
                    sizes = list(cat_totals.values())
                    
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'color': 'white'})
                    ax.axis('equal')
                    ax.set_title("Gastos por Categoría", color="white", pad=10)
                    
                    canvas = FigureCanvasTkAgg(fig, master=charts_frame)
                    canvas.draw()
                    canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
            
            # Bar Chart: Ingresos vs Gastos
            if total_inc > 0 or total_exp > 0:
                fig2, ax2 = plt.subplots(figsize=(4, 4), facecolor='#2b2b2b')
                ax2.bar(['Ingresos', 'Gastos'], [total_inc, total_exp], color=['green', '#FF5252'])
                ax2.tick_params(colors='white')
                ax2.set_title("Ingresos vs Gastos", color="white", pad=10)
                
                # Para evitar fondo blanco en el borde
                fig2.patch.set_facecolor('#2b2b2b')
                ax2.set_facecolor('#2b2b2b')
                
                canvas2 = FigureCanvasTkAgg(fig2, master=charts_frame)
                canvas2.draw()
                canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)
            
        except Exception as e:
            ctk.CTkLabel(self, text=f"Error cargando dashboard: {e}").pack(pady=20)
