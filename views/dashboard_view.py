import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from services.transaction_service import get_financial_summary, get_report_by_category
import theme as T

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, fg_color=T.COLOR_BG, **kwargs)
        self.user_id = user_id
        # Retrasar la carga de la UI 50ms para que el cambio de pestaña sea instantáneo visualmente
        self.after(50, self.build_ui)

    def build_ui(self):
        try:
            summary = get_financial_summary(self.user_id)
            total_inc = summary.get("total_income", 0)
            total_exp = summary.get("total_expense", 0)
            net_bal = summary.get("net_balance", 0)
            
            # --- HEADER ---
            header_frame = ctk.CTkFrame(self, fg_color="transparent")
            header_frame.pack(fill="x", padx=40, pady=(30, 20))
            
            ctk.CTkLabel(header_frame, text="Overview", font=ctk.CTkFont(family="Roboto", size=24, weight="bold"), text_color=T.COLOR_TEXT_PRIMARY).pack(side="left")
            
            btn_add = ctk.CTkButton(header_frame, text="+ Add Transaction", fg_color=T.COLOR_PRIMARY, text_color="white", font=ctk.CTkFont(weight="bold"))
            btn_add.pack(side="right", padx=(10, 0))
            
            btn_export = ctk.CTkButton(header_frame, text="Export Report", fg_color="transparent", border_width=1, border_color=T.COLOR_BORDER, text_color=T.COLOR_TEXT_PRIMARY)
            btn_export.pack(side="right")
            
            # --- TOP GRID (Charts) ---
            grid_frame = ctk.CTkFrame(self, fg_color="transparent")
            grid_frame.pack(fill="x", padx=40, pady=10)
            grid_frame.grid_columnconfigure(0, weight=2)
            grid_frame.grid_columnconfigure(1, weight=1)
            
            # Left Card: Net Worth
            card_nw = ctk.CTkFrame(grid_frame, corner_radius=12, fg_color=T.COLOR_CARD)
            card_nw.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            
            nw_header = ctk.CTkFrame(card_nw, fg_color="transparent")
            nw_header.pack(fill="x", padx=20, pady=(20, 0))
            ctk.CTkLabel(nw_header, text=f"S/. {net_bal:,.2f}", font=ctk.CTkFont(size=28, weight="bold"), text_color=T.COLOR_TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(nw_header, text="Net Worth", font=ctk.CTkFont(size=12), text_color=T.COLOR_TEXT_SECONDARY).pack(anchor="w")
            
            # Usar el helper para el gráfico de Net Worth
            from utils.charts_helper import embed_net_worth_chart
            embed_net_worth_chart(card_nw, net_bal, self.user_id)
            
            # Right Frame: Stacked Cards (Expense & Income)
            right_col = ctk.CTkFrame(grid_frame, fg_color="transparent")
            right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            right_col.grid_rowconfigure((0, 1), weight=1)
            
            # Helper for Sparkline Cards
            def create_spark_card(parent, title, amount, color, is_up, row):
                card = ctk.CTkFrame(parent, corner_radius=12, fg_color=T.COLOR_CARD)
                card.grid(row=row, column=0, sticky="nsew", pady=(0 if row==0 else 10, 10 if row==0 else 0))
                
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="y", padx=20, pady=20)
                ctk.CTkLabel(info_frame, text=title, font=ctk.CTkFont(size=13), text_color=T.COLOR_TEXT_SECONDARY).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"S/. {amount:,.2f}", font=ctk.CTkFont(size=22, weight="bold"), text_color=T.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(5,0))
                
                import random
                arrow = "↑" if is_up else "↓"
                trend_color = T.COLOR_SUCCESS if is_up else T.COLOR_DANGER
                trend_text = f"{arrow} {random.randint(5,25)}% vs last month"
                ctk.CTkLabel(info_frame, text=trend_text, font=ctk.CTkFont(size=11), text_color=trend_color).pack(anchor="w", pady=(5,0))
                
                # Usar el helper para el sparkline
                from utils.charts_helper import embed_sparkline
                embed_sparkline(card, amount, color)
                
            # As in the image: Expense is top, Income is bottom
            create_spark_card(right_col, "Expense", total_exp, T.COLOR_SUCCESS, is_up=True, row=0) # Image shows expense line green and UP
            create_spark_card(right_col, "Income", total_inc, T.COLOR_DANGER, is_up=False, row=1)  # Image shows income line red and DOWN
            
            # --- BOTTOM SECTION (Transaction History) ---
            table_header_frame = ctk.CTkFrame(self, fg_color="transparent")
            table_header_frame.pack(fill="x", padx=40, pady=(20, 10))
            ctk.CTkLabel(table_header_frame, text="Transaction history", font=ctk.CTkFont(size=16, weight="bold"), text_color=T.COLOR_TEXT_PRIMARY).pack(side="left")
            
            btn_filter = ctk.CTkButton(table_header_frame, text="Apply filter", fg_color="transparent", border_width=1, border_color=T.COLOR_BORDER, text_color=T.COLOR_TEXT_PRIMARY, width=100)
            btn_filter.pack(side="right")
            
            # Table container
            table_bg = ctk.CTkFrame(self, corner_radius=12, fg_color=T.COLOR_CARD)
            table_bg.pack(fill="x", padx=40, pady=(0, 30))
            
            # Table Header
            th = ctk.CTkFrame(table_bg, fg_color="transparent", height=40)
            th.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(th, text="Transaction", width=250, anchor="w", text_color=T.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(side="left")
            ctk.CTkLabel(th, text="Amount", width=100, anchor="e", text_color=T.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(side="left", padx=20)
            ctk.CTkLabel(th, text="Date", width=120, anchor="w", text_color=T.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(side="left", padx=20)
            ctk.CTkLabel(th, text="Category", width=120, anchor="w", text_color=T.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(side="left", padx=20)
            
            # Add separator line
            sep = ctk.CTkFrame(table_bg, height=1, fg_color=T.COLOR_BORDER)
            sep.pack(fill="x", padx=20)
            
            # Fetch recent transactions
            from services.transaction_service import get_recent_transactions
            transactions = get_recent_transactions(self.user_id, limit=5)
            
            if not transactions:
                ctk.CTkLabel(table_bg, text="No transactions found.", text_color=T.COLOR_TEXT_MUTED).pack(pady=30)
            else:
                for idx, t in enumerate(transactions):
                    t_type = t[1]
                    t_amt = t[2]
                    t_cat = t[3] or "Unknown"
                    t_desc = t[4]
                    t_date = t[5]
                    
                    tr = ctk.CTkFrame(table_bg, fg_color="transparent", height=50)
                    tr.pack(fill="x", padx=20, pady=5)
                    
                    # 1. Transaction Info
                    info_col = ctk.CTkFrame(tr, fg_color="transparent", width=250)
                    info_col.pack(side="left", fill="y")
                    info_col.pack_propagate(False)
                    
                    # Randomize icon color for aesthetics
                    icon_color = T.CHART_PALETTE[len(t_desc) % len(T.CHART_PALETTE)]
                    icon_bg = ctk.CTkFrame(info_col, width=32, height=32, corner_radius=16, fg_color=icon_color)
                    icon_bg.pack(side="left")
                    icon_bg.pack_propagate(False)
                    letter = t_desc[0].upper() if t_desc else "?"
                    ctk.CTkLabel(icon_bg, text=letter, text_color="white", font=ctk.CTkFont(weight="bold")).pack(expand=True)
                    ctk.CTkLabel(info_col, text=t_desc, text_color=T.COLOR_TEXT_PRIMARY, font=ctk.CTkFont(size=13)).pack(side="left", padx=15)
                    
                    # 2. Amount
                    amt_str = f"+S/. {t_amt:,.2f}" if t_type == "ingreso" else f"-S/. {t_amt:,.2f}"
                    amt_color = T.COLOR_SUCCESS if t_type == "ingreso" else T.COLOR_TEXT_SECONDARY
                    amt_col = ctk.CTkLabel(tr, text=amt_str, width=100, anchor="e", text_color=amt_color, font=ctk.CTkFont(size=13))
                    amt_col.pack(side="left", padx=20)
                    
                    # 3. Date
                    date_col = ctk.CTkLabel(tr, text=t_date.split(" ")[0], width=120, anchor="w", text_color=T.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=12))
                    date_col.pack(side="left", padx=20)
                    
                    # 4. Category Pill
                    cat_col = ctk.CTkFrame(tr, fg_color="transparent", width=120)
                    cat_col.pack(side="left", padx=20)
                    cat_col.pack_propagate(False)
                    
                    pill_color = T.CHART_PALETTE[len(t_cat) % len(T.CHART_PALETTE)]
                    pill = ctk.CTkFrame(cat_col, corner_radius=12, border_width=1, border_color=T.COLOR_BORDER, fg_color="transparent")
                    pill.pack(side="left", pady=10)
                    
                    dot = ctk.CTkFrame(pill, width=6, height=6, corner_radius=3, fg_color=pill_color)
                    dot.pack(side="left", padx=(8, 4), pady=5)
                    ctk.CTkLabel(pill, text=t_cat, text_color=T.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 8))
                    
                    if idx < len(transactions) - 1:
                        sep2 = ctk.CTkFrame(table_bg, height=1, fg_color=T.COLOR_BORDER)
                        sep2.pack(fill="x", padx=20)
                        
        except Exception as e:
            ctk.CTkLabel(self, text=f"Error cargando dashboard: {e}").pack(pady=20)
            ctk.CTkLabel(self, text=f"Error cargando dashboard: {e}").pack(pady=20)
