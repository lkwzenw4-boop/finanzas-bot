"""
telegram_bot/handlers/reports.py
Comandos /balance, /historial y /ayuda.
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.db import get_user_by_telegram_id, get_summary_bot, get_recent_bot


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el resumen financiero del usuario."""
    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)

    if not user:
        await update.message.reply_text(
            "❌ No tienes cuenta vinculada. Usa /start primero."
        )
        return

    user_id, username = user
    s = get_summary_bot(user_id)

    if not s:
        await update.message.reply_text("❌ Error al obtener tu balance.")
        return

    net = s['net_balance']
    net_emoji = "💚" if net >= 0 else "🔴"
    net_label  = "Ahorro" if net >= 0 else "Déficit"

    this_m = s['this_month_expense']
    last_m = s['last_month_expense']

    # Comparativa mensual
    comparison = ""
    if last_m > 0:
        diff = ((this_m - last_m) / last_m) * 100
        if diff > 0:
            comparison = f"\n📈 Gastas {diff:.1f}% *MÁS* que el mes pasado ⚠️"
        elif diff < 0:
            comparison = f"\n📉 Gastas {abs(diff):.1f}% *MENOS* que el mes pasado 🎉"
        else:
            comparison = "\n↔️ Mismo gasto que el mes pasado"
    elif this_m > 0:
        comparison = "\n🆕 Primer mes con datos"

    pct = (s['total_expense'] / s['total_income'] * 100) if s['total_income'] > 0 else 0
    bar_len = 15
    filled  = min(bar_len, int((pct / 100) * bar_len))
    bar     = "█" * filled + "░" * (bar_len - filled)

    msg = (
        f"📊 *Balance — {username}*\n"
        f"{'─' * 30}\n"
        f"💵 Ingresos:   S/.{s['total_income']:>10,.2f}\n"
        f"💸 Gastos:     S/.{s['total_expense']:>10,.2f}\n"
        f"{'─' * 30}\n"
        f"{net_emoji} Balance:    S/.{abs(net):>10,.2f}  _{net_label}_\n\n"
        f"📅 *Este mes:*\n"
        f"   Gastos:    S/.{this_m:,.2f}\n"
        f"   Mes ant.:  S/.{last_m:,.2f}\n"
        f"{comparison}\n\n"
        f"📊 Ratio gasto/ingreso: `[{bar}]` {pct:.0f}%"
    )

    await update.message.reply_text(msg, parse_mode='Markdown')


async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra las últimas transacciones."""
    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)

    if not user:
        await update.message.reply_text(
            "❌ No tienes cuenta vinculada. Usa /start primero."
        )
        return

    user_id, username = user
    txns = get_recent_bot(user_id, limit=8)

    if not txns:
        await update.message.reply_text(
            "📋 No tienes transacciones registradas aún.\n\n"
            "Prueba enviando `50 almuerzo` para registrar tu primer gasto.",
            parse_mode='Markdown'
        )
        return

    msg = f"📋 *Últimas transacciones — {username}*\n{'─' * 30}\n"

    for desc, amount, type_txn, cat_name, fecha in txns:
        signo = "+" if type_txn == 'ingreso' else "-"
        emoji = "💵" if type_txn == 'ingreso' else "💸"
        fecha_str = str(fecha)[:10] if fecha else "---"
        # Limitar descripción a 20 caracteres
        desc_short = desc[:20] + "…" if len(desc) > 20 else desc
        msg += (
            f"{emoji} `{fecha_str}`  *{signo}S/.{amount:.2f}*\n"
            f"    📝 {desc_short}  •  🏷️ _{cat_name}_\n"
        )

    await update.message.reply_text(msg, parse_mode='Markdown')


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la ayuda completa del bot."""
    msg = (
        "🤖 *Finanzas Personales Bot — Ayuda*\n\n"
        "━━━ *Registrar transacciones* ━━━\n"
        "• `50 pizza`           → Gasto S/.50\n"
        "• `+100 sueldo`        → Ingreso S/.100\n"
        "• `-30 taxi`           → Gasto S/.30\n"
        "• `gasto 45 almuerzo`  → Gasto S/.45\n"
        "• `ingreso 500 free`   → Ingreso S/.500\n\n"
        "━━━ *Comandos* ━━━\n"
        "/balance   → 📊 Ver resumen financiero\n"
        "/historial → 📋 Últimas 8 transacciones\n"
        "/start     → 🔗 Vincular / revisar cuenta\n"
        "/ayuda     → ❓ Esta ayuda\n\n"
        "━━━ *Categorización automática* ━━━\n"
        "El bot detecta la categoría por palabras clave.\n"
        "Si no acierta, puedes cambiarla con los botones.\n\n"
        "_Powered by FinanzasIA 🚀_"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')
