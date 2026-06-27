"""
telegram_bot/handlers/transactions.py
Maneja el registro de gastos e ingresos desde Telegram.
"""
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.db import get_user_by_telegram_id, get_categories_bot, insert_transaction_bot

# ─────────────────────────────────────────────
# Palabras clave para categorización simple
# ─────────────────────────────────────────────
KEYWORDS = {
    # Gastos
    'Alimentacion': [
        'comida', 'almuerzo', 'cena', 'desayuno', 'pizza', 'burger', 'hamburguesa',
        'restaurante', 'pollo', 'arroz', 'sopa', 'ceviche', 'mercado', 'verdura',
        'fruta', 'pan', 'snack', 'bebida', 'cafe', 'helado', 'ensalada',
        'lomo', 'chicha', 'anticucho', 'taco', 'sandwich', 'menu', 'lonche'
    ],
    'Transporte': [
        'taxi', 'bus', 'uber', 'indriver', 'moto', 'combustible', 'gasolina',
        'pasaje', 'metro', 'tren', 'colectivo', 'combi', 'cabify', 'beat'
    ],
    'Salud': [
        'farmacia', 'medicina', 'doctor', 'medico', 'consulta', 'clinica',
        'hospital', 'pastilla', 'remedio', 'analisis', 'examen', 'vacuna'
    ],
    'Entretenimiento': [
        'cine', 'pelicula', 'juego', 'deporte', 'gym', 'gimnasio', 'streaming',
        'netflix', 'spotify', 'disney', 'hbo', 'prime', 'youtube', 'concierto',
        'evento', 'fiesta', 'karaoke', 'discoteca', 'bar'
    ],
    'Educacion': [
        'universidad', 'colegio', 'curso', 'libro', 'matricula', 'mensualidad',
        'educacion', 'taller', 'diplomado', 'carrera', 'certificado', 'capacitacion'
    ],
    'Vivienda': [
        'alquiler', 'luz', 'agua', 'internet', 'gas', 'cable', 'renta',
        'mantenimiento', 'condominio', 'limpieza', 'departamento'
    ],
    'Servicios': [
        'telefono', 'celular', 'suscripcion', 'plan', 'recarga', 'movistar',
        'claro', 'entel', 'bitel'
    ],
    'Tecnologia': [
        'laptop', 'computadora', 'electronico', 'celular', 'tablet', 'audifonos',
        'cargador', 'cable', 'software', 'app', 'programa'
    ],
    'Ropa': [
        'ropa', 'camisa', 'pantalon', 'zapatos', 'vestido', 'polo', 'zapatillas',
        'tenis', 'chompas', 'casaca', 'cartera', 'bolsa', 'mochila'
    ],
    # Ingresos
    'Salario': [
        'sueldo', 'salario', 'pago', 'quincena', 'mensual', 'remuneracion',
        'haberes', 'nomina', 'planilla'
    ],
    'Freelance': [
        'proyecto', 'freelance', 'trabajo', 'servicio', 'consultoria',
        'honorarios', 'encargo', 'cliente'
    ],
    'Inversiones': [
        'dividendo', 'interes', 'rendimiento', 'acciones', 'cripto', 'bitcoin',
        'inversion', 'utilidad'
    ],
    'Ventas': [
        'venta', 'vendido', 'vendi', 'mercaderia', 'producto', 'tienda'
    ],
}

# Palabras clave que identifican claramente un INGRESO
# Si el usuario escribe '1500 salario' sin prefijo, lo detectamos como ingreso
INCOME_KEYWORDS = [
    'salario', 'sueldo', 'quincena', 'quincena', 'remuneracion', 'haberes',
    'nomina', 'planilla', 'pago de sueldo',
    'freelance', 'honorarios', 'consultoria', 'encargo',
    'dividendo', 'rendimiento', 'inversion', 'utilidad', 'utilidades',
    'venta', 'vendido', 'vendi',
    'bono', 'bonificacion', 'gratificacion', 'aguinaldo',
    'cobro', 'cobrado', 'deposito recibido',
    'ingreso', 'ganancia', 'comision', 'regalias',
]


def _norm(text: str) -> str:
    """Normaliza tildes para comparación de keywords."""
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u')]:
        text = text.replace(a, b)
    return text.lower()


def is_income_desc(desc: str) -> bool:
    """Retorna True si la descripción claramente corresponde a un ingreso."""
    d = _norm(desc)
    return any(kw in d for kw in INCOME_KEYWORDS)


def parse_transaction(text: str):
    """
    Parsea texto libre a (amount, description, type_txn) o None.
    Formatos soportados:
      '50 pizza'          → gasto
      '+100 sueldo'       → ingreso
      '-30 taxi'          → gasto
      'gasto 45 almuerzo' → gasto
      'ingreso 500 free'  → ingreso
      'i 200 alquiler'    → ingreso
      'g 80 mercado'      → gasto
    """
    text = text.strip()
    type_txn = 'gasto'  # por defecto
    explicit_type = False  # ¿el usuario especificó el tipo explícitamente?

    # Prefijo de tipo explícito
    lo = text.lower()
    if re.match(r'^(ingreso|ingresos|i)\s+', lo):
        type_txn = 'ingreso'
        explicit_type = True
        text = re.sub(r'^(ingreso|ingresos|i)\s+', '', text, flags=re.IGNORECASE).strip()
    elif re.match(r'^(gasto|gastos|g)\s+', lo):
        type_txn = 'gasto'
        explicit_type = True
        text = re.sub(r'^(gasto|gastos|g)\s+', '', text, flags=re.IGNORECASE).strip()

    # Signo +/-
    if text.startswith('+'):
        type_txn = 'ingreso'
        explicit_type = True
        text = text[1:].strip()
    elif text.startswith('-'):
        type_txn = 'gasto'
        explicit_type = True
        text = text[1:].strip()

    # Extraer monto y descripción: "50.00 descripcion" o "50 descripcion"
    match = re.match(r'^(\d+(?:[.,]\d+)?)\s+(.+)$', text)
    if not match:
        return None

    amount_str = match.group(1).replace(',', '.')
    desc = match.group(2).strip()

    try:
        amount = float(amount_str)
    except ValueError:
        return None

    if amount <= 0 or not desc:
        return None

    # ── Detección automática por palabras clave ──
    # Si el usuario no especificó +/- ni ingreso/gasto, revisamos la descripción
    if not explicit_type and is_income_desc(desc):
        type_txn = 'ingreso'

    return amount, desc, type_txn


def guess_category(desc: str, categories: list):
    """
    Búsqueda de categoría por palabras clave.
    Retorna (id_category, name) o (None, None).
    """
    desc_lower = desc.lower()
    # Normalizar tildes básicas
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u')]:
        desc_lower = desc_lower.replace(a, b)

    for cat_id, cat_name in categories:
        cat_key = cat_name.lower().replace(' ', '')
        for kw_key, words in KEYWORDS.items():
            kw_norm = kw_key.lower().replace(' ', '')
            if kw_norm in cat_key or cat_key in kw_norm:
                for word in words:
                    if word in desc_lower:
                        return cat_id, cat_name
    return None, None


def build_category_keyboard(categories: list) -> InlineKeyboardMarkup:
    """Construye un teclado inline con las categorías en 2 columnas."""
    buttons = []
    row = []
    for cat_id, cat_name in categories:
        label = cat_name[:15]  # Limitar largo
        row.append(InlineKeyboardButton(label, callback_data=f"cat_{cat_id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Cancelar", callback_data="cat_cancel")])
    return InlineKeyboardMarkup(buttons)


# ─────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa cualquier mensaje de texto libre como posible transacción."""
    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)

    if not user:
        await update.message.reply_text(
            "❌ No tienes una cuenta vinculada.\nUsa /start para vincular tu cuenta."
        )
        return

    user_id, username = user
    text = update.message.text

    parsed = parse_transaction(text)
    if not parsed:
        await update.message.reply_text(
            "🤔 No entendí ese mensaje.\n\n"
            "Para registrar una transacción:\n"
            "• `50 pizza` → Gasto S/.50\n"
            "• `+100 sueldo` → Ingreso S/.100\n"
            "• `-30 taxi` → Gasto S/.30\n\n"
            "Usa /ayuda para ver más opciones.",
            parse_mode='Markdown'
        )
        return

    amount, desc, type_txn = parsed
    categories = get_categories_bot(type_txn)
    guessed_id, guessed_name = guess_category(desc, categories)

    tipo_label = "Ingreso" if type_txn == 'ingreso' else "Gasto"
    signo = "+" if type_txn == 'ingreso' else "-"
    emoji = "💵" if type_txn == 'ingreso' else "💸"

    # Guardar transacción pendiente en memoria del usuario
    context.user_data['pending'] = {
        'user_id':    user_id,
        'amount':     amount,
        'desc':       desc,
        'type_txn':   type_txn,
        'categories': categories,
    }

    if guessed_id:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{guessed_id}"),
                InlineKeyboardButton("🔄 Cambiar cat.", callback_data="change_cat"),
            ],
            [InlineKeyboardButton("❌ Cancelar", callback_data="confirm_cancel")],
        ])
        await update.message.reply_text(
            f"{emoji} *{tipo_label} detectado*\n"
            f"{'─' * 28}\n"
            f"📝 *{desc}*\n"
            f"💰 *{signo} S/.{amount:.2f}*\n"
            f"🏷️ Categoría sugerida: *{guessed_name}*\n\n"
            "¿Confirmamos?",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        # Sin sugerencia → mostrar lista de categorías
        await update.message.reply_text(
            f"{emoji} *{tipo_label} detectado*\n"
            f"{'─' * 28}\n"
            f"📝 *{desc}*\n"
            f"💰 *{signo} S/.{amount:.2f}*\n\n"
            "Selecciona la categoría:",
            reply_markup=build_category_keyboard(categories),
            parse_mode='Markdown'
        )


async def confirm_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: usuario confirma la categoría sugerida."""
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_cancel":
        context.user_data.pop('pending', None)
        await query.edit_message_text("❌ Transacción cancelada.")
        return

    cat_id = int(query.data.replace("confirm_", ""))
    pending = context.user_data.get('pending')

    if not pending:
        await query.edit_message_text("❌ Error: no hay transacción pendiente. Inténtalo de nuevo.")
        return

    # Obtener nombre de la categoría
    cat_name = next(
        (name for cid, name in pending['categories'] if cid == cat_id),
        "Categoría"
    )

    ok = insert_transaction_bot(
        pending['user_id'], pending['desc'],
        pending['amount'],  pending['type_txn'], cat_id
    )
    context.user_data.pop('pending', None)

    signo = "+" if pending['type_txn'] == 'ingreso' else "-"
    tipo_label = "Ingreso" if pending['type_txn'] == 'ingreso' else "Gasto"
    emoji = "✅💵" if pending['type_txn'] == 'ingreso' else "✅💸"

    if ok:
        await query.edit_message_text(
            f"{emoji} *{tipo_label} guardado*\n"
            f"{'─' * 28}\n"
            f"📝 {pending['desc']}\n"
            f"💰 {signo} S/.{pending['amount']:.2f}\n"
            f"🏷️ {cat_name}",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❌ Error al guardar. Intenta de nuevo.")


async def change_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: el usuario quiere cambiar la categoría sugerida."""
    query = update.callback_query
    await query.answer()

    pending = context.user_data.get('pending')
    if not pending:
        await query.edit_message_text("❌ Error: no hay transacción pendiente.")
        return

    await query.edit_message_text(
        f"🔄 Selecciona la categoría para *{pending['desc']}* (S/.{pending['amount']:.2f}):",
        reply_markup=build_category_keyboard(pending['categories']),
        parse_mode='Markdown'
    )


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback: el usuario seleccionó una categoría del teclado."""
    query = update.callback_query
    await query.answer()

    if query.data == "cat_cancel":
        context.user_data.pop('pending', None)
        await query.edit_message_text("❌ Transacción cancelada.")
        return

    cat_id = int(query.data.replace("cat_", ""))
    pending = context.user_data.get('pending')

    if not pending:
        await query.edit_message_text("❌ Error: no hay transacción pendiente.")
        return

    cat_name = next(
        (name for cid, name in pending['categories'] if cid == cat_id),
        "Categoría"
    )

    ok = insert_transaction_bot(
        pending['user_id'], pending['desc'],
        pending['amount'],  pending['type_txn'], cat_id
    )
    context.user_data.pop('pending', None)

    signo = "+" if pending['type_txn'] == 'ingreso' else "-"
    tipo_label = "Ingreso" if pending['type_txn'] == 'ingreso' else "Gasto"
    emoji = "✅💵" if pending['type_txn'] == 'ingreso' else "✅💸"

    if ok:
        await query.edit_message_text(
            f"{emoji} *{tipo_label} guardado*\n"
            f"{'─' * 28}\n"
            f"📝 {pending['desc']}\n"
            f"💰 {signo} S/.{pending['amount']:.2f}\n"
            f"🏷️ {cat_name}",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❌ Error al guardar. Intenta de nuevo.")
