# theme.py — Paleta de colores para la app de finanzas

# === FONDOS ===
COLOR_BG = "#0F1117"          # Fondo general de la ventana (casi negro, no negro puro)
COLOR_CARD = "#161A23"        # Fondo de las tarjetas
COLOR_CARD_HOVER = "#1C212C"  # Hover sutil sobre tarjetas
COLOR_BORDER = "#262B38"      # Bordes sutiles (1px)

# === ACENTOS PRINCIPALES ===
COLOR_PRIMARY = "#6366F1"     # Violeta/índigo — insight IA, elementos destacados
COLOR_PRIMARY_BG = "#1A1A2E"  # Fondo del bloque "Insight de la IA"

# === SEMÁNTICOS ===
COLOR_SUCCESS = "#22C55E"     # Verde — ingresos, balance positivo
COLOR_SUCCESS_BG = "#0F2418"  # Fondo sutil card ingreso
COLOR_DANGER = "#EF4444"      # Rojo — gastos, balance negativo
COLOR_DANGER_BG = "#2A1414"   # Fondo sutil card gasto
COLOR_WARNING = "#F59E0B"     # Naranja/ámbar — ratio, alertas medias

# === TEXTO ===
COLOR_TEXT_PRIMARY = "#F1F2F6"    # Texto principal
COLOR_TEXT_SECONDARY = "#8A8F9C"  # Labels secundarios
COLOR_TEXT_MUTED = "#5A5F6B"      # Texto terciario

# === GRÁFICOS (Matplotlib) ===
COLOR_CHART_BG = "#0F1117"        # Fondo igual a COLOR_BG, para fusión perfecta

# Paleta categórica para el donut
CHART_PALETTE = [
    "#6366F1",  # violeta
    "#A855F7",  # púrpura
    "#F59E0B",  # ámbar
    "#FBBF24",  # amarillo
    "#22C55E",  # verde
    "#EF4444",  # rojo
    "#38BDF8",  # celeste
    "#FB923C",  # naranja
]

# Gradientes barras de Flujo de Caja
GRADIENT_INCOME = ["#22C55E", "#16A34A"]
GRADIENT_EXPENSE = ["#EF4444", "#DC2626"]

# Gradiente barra Ratio Gasto/Ingreso
RATIO_GRADIENT = [
    (0.0,  "#22C55E"),
    (0.5,  "#F59E0B"),
    (1.0,  "#EF4444"),
]

# === SPACING (múltiplos de 8) ===
SP_XS  = 8
SP_SM  = 16
SP_MD  = 24
SP_LG  = 32

# === TIPOGRAFÍA ===
FONT_TITLE   = ("Roboto", 28, "bold")   # Título de sección
FONT_SECTION = ("Roboto", 14, "bold")   # Subtítulo/header de card
FONT_VALUE   = ("Roboto", 26, "bold")   # Valor numérico grande
FONT_LABEL   = ("Roboto", 11)           # Label pequeño/secundario

# === BORDER RADIUS ===
RADIUS_CARD = 14
RADIUS_SM   = 8
