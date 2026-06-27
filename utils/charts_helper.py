import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import theme as T

def embed_net_worth_chart(parent_widget, net_bal, user_id):
    """
    Dibuja el gráfico de barras azules para Net Worth y lo incrusta en parent_widget.
    """
    fig, ax = plt.subplots(figsize=(6, 2.5), facecolor=T.COLOR_CHART_BG)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    random.seed(user_id) # Datos consistentes para el usuario
    vals = [random.uniform(max(10, net_bal*0.2), max(100, net_bal*1.2)) for _ in range(12)]
    vals[-1] = max(0, net_bal)
    
    ax.bar(months, vals, color=T.COLOR_PRIMARY, width=0.5, zorder=3)
    ax.grid(axis='y', color=T.COLOR_BORDER, linestyle='-', linewidth=0.5, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(T.COLOR_BORDER)
    ax.tick_params(axis='x', colors=T.COLOR_TEXT_SECONDARY, labelsize=9)
    ax.tick_params(axis='y', colors=T.COLOR_TEXT_SECONDARY, labelsize=9)
    
    fig.patch.set_facecolor(T.COLOR_CHART_BG)
    ax.set_facecolor(T.COLOR_CHART_BG)
    fig.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=parent_widget)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    return canvas


def embed_sparkline(parent_widget, amount, color):
    """
    Dibuja un sparkline minimalista y lo incrusta en parent_widget.
    """
    fig, ax = plt.subplots(figsize=(2.5, 1.2), facecolor=T.COLOR_CHART_BG)
    x = list(range(10))
    y = [random.uniform(amount*0.5, amount*1.5) for _ in x]
    y[-1] = amount
    
    ax.plot(x, y, color=color, linewidth=2)
    ax.axis('off')
    
    fig.patch.set_facecolor(T.COLOR_CHART_BG)
    ax.set_facecolor(T.COLOR_CHART_BG)
    fig.tight_layout(pad=0)
    
    canvas = FigureCanvasTkAgg(fig, master=parent_widget)
    canvas.draw()
    canvas.get_tk_widget().pack(side="right", padx=10, pady=10)
    
    return canvas
