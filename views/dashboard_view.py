import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from services.transaction_service import get_financial_summary, get_report_by_category
import theme as T

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
            
            lbl_title = ctk.CTkLabel(self, text="Resumen Financiero", font=ctk.CTkFont(*T.FONT_TITLE))
            lbl_title.pack(pady=(T.SP_LG, T.SP_MD))
            
            # Cards frame
            cards_frame = ctk.CTkFrame(self, fg_color="transparent")
            cards_frame.pack(fill="x", padx=40, pady=10)
            cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            def create_summary_card(parent, title, amount, accent_color, icon, col):
                card = ctk.CTkFrame(parent, corner_radius=T.RADIUS_CARD, fg_color=T.COLOR_CARD, 
                                    border_width=1, border_color=T.COLOR_BORDER)
                card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
                
                # Barra lateral de acento
                indicator = ctk.CTkFrame(card, width=4, corner_radius=2, fg_color=accent_color)
                indicator.pack(side="left", fill="y", pady=15, padx=(15, 0))
                
                # Contenedor para texto
                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=15)
                
                header = ctk.CTkFrame(content, fg_color="transparent")
                header.pack(fill="x", anchor="w")
                ctk.CTkLabel(header, text=icon, text_color=accent_color, font=ctk.CTkFont(*T.FONT_SECTION)).pack(side="left", padx=(0, 5))
                ctk.CTkLabel(header, text=title, text_color=T.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(*T.FONT_SECTION)).pack(side="left")
                
                ctk.CTkLabel(content, text=f"S/. {amount:,.2f}", text_color=T.COLOR_TEXT_PRIMARY, font=ctk.CTkFont(*T.FONT_VALUE)).pack(anchor="w", pady=(10, 0))
                
            create_summary_card(cards_frame, "Total Ingresos", total_inc, T.COLOR_SUCCESS, "💰", 0)
            create_summary_card(cards_frame, "Total Gastos", total_exp, T.COLOR_DANGER, "💸", 1)
            
            bal_color = T.COLOR_SUCCESS if net_bal >= 0 else T.COLOR_DANGER
            bal_icon = "📈" if net_bal >= 0 else "📉"
            create_summary_card(cards_frame, "Balance Neto", net_bal, bal_color, bal_icon, 2)
            
            # Panel Insight de IA
            this_m = summary.get("this_month_expense", 0)
            last_m = summary.get("last_month_expense", 0)
            
            if last_m > 0:
                diff = ((this_m - last_m) / last_m) * 100
                if diff > 0:
                    insight = f"¡Atención! Has gastado un {abs(diff):.1f}% MÁS que el mes pasado en estas fechas. Te sugiero revisar tus categorías altas."
                else:
                    insight = f"¡Genial! Has gastado un {abs(diff):.1f}% MENOS que el mes pasado. Excelente control financiero."
            elif this_m > 0:
                insight = "Recién comenzamos a registrar tus datos. ¡Sigue así para obtener análisis predictivos el próximo mes!"
            else:
                insight = "No hay suficientes datos de gastos este mes para generar predicciones o comparativas."
                
            insight_frame = ctk.CTkFrame(self, fg_color=T.COLOR_PRIMARY_BG, corner_radius=T.RADIUS_CARD, border_width=1, border_color=T.COLOR_BORDER)
            insight_frame.pack(fill="x", padx=40, pady=(10, 20))
            
            # Círculo con ícono
            icon_frame = ctk.CTkFrame(insight_frame, width=36, height=36, corner_radius=18, fg_color=T.COLOR_PRIMARY)
            icon_frame.pack(side="left", padx=20, pady=15)
            icon_frame.pack_propagate(False)
            ctk.CTkLabel(icon_frame, text="💡", text_color="white", font=ctk.CTkFont(size=18)).pack(expand=True)
            
            text_frame = ctk.CTkFrame(insight_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, pady=15, padx=(0, 20))
            
            ctk.CTkLabel(text_frame, text="Insight de la IA", text_color=T.COLOR_PRIMARY, font=ctk.CTkFont(*T.FONT_SECTION)).pack(anchor="w")
            ctk.CTkLabel(text_frame, text=insight, text_color=T.COLOR_TEXT_PRIMARY, wraplength=700, justify="left", font=ctk.CTkFont(*T.FONT_LABEL)).pack(anchor="w", pady=(2, 0))
            
            # Barra de progreso
            if total_inc > 0:
                pct = (total_exp / total_inc) * 100
                prog_frame = ctk.CTkFrame(self, fg_color="transparent")
                prog_frame.pack(fill="x", padx=40, pady=10)
                
                header_prog = ctk.CTkFrame(prog_frame, fg_color="transparent")
                header_prog.pack(fill="x")
                ctk.CTkLabel(header_prog, text="Ratio Gasto/Ingreso", text_color=T.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(*T.FONT_LABEL)).pack(side="left")
                ctk.CTkLabel(header_prog, text=f"{pct:.1f}%", text_color=T.COLOR_TEXT_PRIMARY, font=ctk.CTkFont(family="Roboto", size=12, weight="bold")).pack(side="right")
                
                # Canvas para barra
                canvas = ctk.CTkCanvas(prog_frame, height=10, bg=T.COLOR_BG, highlightthickness=0)
                canvas.pack(fill="x", pady=(8, 15))
                
                def draw_bar(event):
                    canvas.delete("all")
                    w = event.width
                    h = event.height
                    
                    # Calcular color interpolado o usar thresholds
                    if pct <= 40: color = T.COLOR_SUCCESS
                    elif pct <= 75: color = T.COLOR_WARNING
                    else: color = T.COLOR_DANGER
                    
                    fill_w = w * min(1.0, total_exp / total_inc)
                    
                    # Dibujar fondo (border color) y relleno
                    canvas.create_rectangle(0, 0, w, h, fill=T.COLOR_BORDER, outline="", width=0)
                    if fill_w > 0:
                        canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="", width=0)
                        
                canvas.bind("<Configure>", draw_bar)
                    
            # Add a frame for charts below the progress bar
            charts_frame = ctk.CTkFrame(self, fg_color="transparent")
            charts_frame.pack(fill="both", expand=True, padx=40, pady=10)
            charts_frame.grid_columnconfigure((0,1), weight=1)
            
            # Gráficos con diseño Premium
            chart_bg = T.COLOR_CHART_BG
            
            # Pie Chart: Gastos por Categoria (Donut)
            reporte = get_report_by_category(self.user_id, "gasto")
            if reporte:
                fig, ax = plt.subplots(figsize=(5.5, 5), dpi=100, facecolor=chart_bg)
                cat_totals = {}
                for cat, sub, tot in reporte:
                    cat_totals[cat] = cat_totals.get(cat, 0) + tot
                
                cat_totals = {k: v for k, v in cat_totals.items() if v > 0}
                if cat_totals:
                    labels = list(cat_totals.keys())
                    sizes = list(cat_totals.values())
                    
                    colors = T.CHART_PALETTE * (len(sizes) // len(T.CHART_PALETTE) + 1)
                    
                    def my_autopct(pct):
                        return ('%1.1f%%' % pct) if pct > 5 else ''
                    
                    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct=my_autopct, 
                                                      startangle=90, colors=colors, pctdistance=0.75,
                                                      textprops={'color': 'white', 'fontsize': 10, 'weight': 'bold'},
                                                      wedgeprops=dict(width=0.35, edgecolor=chart_bg, linewidth=3))
                    
                    import numpy as np
                    for i, p in enumerate(wedges):
                        pct = sizes[i]/sum(sizes)*100
                        if pct <= 5:
                            ang = (p.theta2 - p.theta1)/2. + p.theta1
                            y = np.sin(np.deg2rad(ang))
                            x = np.cos(np.deg2rad(ang))
                            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                            connectionstyle = f"angle,angleA=0,angleB={ang}"
                            ax.annotate(f"{pct:.1f}%", xy=(x, y), xytext=(1.2*np.sign(x), 1.3*y),
                                        horizontalalignment=horizontalalignment, color=T.COLOR_TEXT_PRIMARY, weight="bold", size=9,
                                        arrowprops=dict(arrowstyle="-", color=T.COLOR_BORDER, connectionstyle=connectionstyle))

                    ax.axis('equal')
                    ax.set_title("Estructura de Gastos", color=T.COLOR_TEXT_PRIMARY, fontdict={'weight': 'bold', 'size': 14}, pad=20)
                    
                    ax.legend(wedges, labels, title="Categorías", loc="center left", bbox_to_anchor=(1, 0.5),
                              facecolor=chart_bg, edgecolor='none', labelcolor=T.COLOR_TEXT_PRIMARY)
                              
                    fig.tight_layout()
                    
                    canvas = FigureCanvasTkAgg(fig, master=charts_frame)
                    canvas.draw()
                    canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            
            # Bar Chart: Ingresos vs Gastos
            if total_inc > 0 or total_exp > 0:
                fig2, ax2 = plt.subplots(figsize=(5.5, 5), dpi=100, facecolor=chart_bg)
                
                # Función helper para dibujar barras con sombra y bordes redondeados
                import matplotlib.patches as patches
                def draw_premium_bar(ax, x, y, width, height, color):
                    # Sombra
                    shadow = patches.FancyBboxPatch((x - width/2 + 0.05, y - 0.05), width, height,
                                                    boxstyle="round,pad=0,rounding_size=0.1",
                                                    fc="black", alpha=0.2, ec="none")
                    ax.add_patch(shadow)
                    # Barra principal
                    bar = patches.FancyBboxPatch((x - width/2, y), width, height,
                                                 boxstyle="round,pad=0,rounding_size=0.1",
                                                 fc=color, ec=T.COLOR_BORDER, lw=1)
                    ax.add_patch(bar)

                # Configuramos límites antes de dibujar parches manuales
                max_val = max(total_inc, total_exp)
                ax2.set_xlim(-0.5, 1.5)
                ax2.set_ylim(0, max_val * 1.15)
                
                draw_premium_bar(ax2, 0, 0, 0.45, total_inc, T.GRADIENT_INCOME[0])
                draw_premium_bar(ax2, 1, 0, 0.45, total_exp, T.GRADIENT_EXPENSE[0])
                
                ax2.set_xticks([0, 1])
                ax2.set_xticklabels(['Ingresos', 'Gastos'])
                ax2.set_title("Flujo de Caja", color=T.COLOR_TEXT_PRIMARY, fontdict={'weight': 'bold', 'size': 14}, pad=20)
                
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.spines['left'].set_visible(False)
                ax2.spines['bottom'].set_color(T.COLOR_BORDER)
                
                ax2.get_yaxis().set_visible(False)
                ax2.tick_params(axis='x', colors=T.COLOR_TEXT_SECONDARY, labelsize=12)
                
                ax2.text(0, total_inc + (max_val*0.03), f'S/. {total_inc:,.2f}', ha='center', va='bottom', color=T.COLOR_TEXT_PRIMARY, weight='bold', size=14)
                ax2.text(1, total_exp + (max_val*0.03), f'S/. {total_exp:,.2f}', ha='center', va='bottom', color=T.COLOR_TEXT_PRIMARY, weight='bold', size=14)
                
                fig2.patch.set_facecolor(chart_bg)
                ax2.set_facecolor(chart_bg)
                fig2.tight_layout()
                
                canvas2 = FigureCanvasTkAgg(fig2, master=charts_frame)
                canvas2.draw()
                canvas2.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

            
        except Exception as e:
            ctk.CTkLabel(self, text=f"Error cargando dashboard: {e}").pack(pady=20)
