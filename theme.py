# theme.py — Paleta de colores para la app de finanzas

# === FONDOS ===
COLOR_BG = "#12151C"          # Fondo principal (Azul muy oscuro casi negro)
COLOR_CARD = "#1A1D24"        # Fondo de las tarjetas (Gris oscuro)
COLOR_CARD_HOVER = "#242831"  # Hover sutil
COLOR_BORDER = "#2E3643"      # Bordes de separación y botones outline

# === ACENTOS PRINCIPALES ===
COLOR_PRIMARY = "#3B82F6"     # Azul brillante (Botón Add Transaction, barras)
COLOR_PRIMARY_BG = "#1E3A8A"  # Fondo azul oscuro para destacados

# === SEMÁNTICOS ===
COLOR_SUCCESS = "#10B981"     # Verde (Ingresos, tendencias positivas, sparkline)
COLOR_SUCCESS_BG = "#064E3B"  # Verde oscuro transparente
COLOR_DANGER = "#EF4444"      # Rojo (Gastos, tendencias negativas)
COLOR_DANGER_BG = "#7F1D1D"   # Rojo oscuro transparente
COLOR_WARNING = "#F59E0B"     # Naranja

# === TEXTO ===
COLOR_TEXT_PRIMARY = "#F9FAFB"    # Texto principal (Casi blanco puro)
COLOR_TEXT_SECONDARY = "#9CA3AF"  # Texto secundario (Gris claro)
COLOR_TEXT_MUTED = "#4B5563"      # Texto desactivado/oscuro

# === GRÁFICOS (Matplotlib) ===
COLOR_CHART_BG = "#1A1D24"        # Fondo de gráficos = Fondo de tarjeta para fusión

# Paleta categórica (Píldoras de categorías en la tabla)
CHART_PALETTE = [
    "#3B82F6",  # Blue
    "#8B5CF6",  # Purple
    "#EC4899",  # Pink
    "#10B981",  # Green
    "#F59E0B",  # Orange
    "#EF4444",  # Red
]

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
