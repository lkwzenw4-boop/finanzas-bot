"""
telegram_bot/handlers/auth.py
Maneja el flujo de login y vinculación de cuenta Telegram ↔ Finanzas.
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram_bot.db import get_user_by_telegram_id, link_telegram_id

# Estado del ConversationHandler
WAITING_CREDENTIALS = 1

HELP_TEXT = (
    "📋 *Cómo usar el bot:*\n\n"
    "💸 `50 pizza` → Registra gasto de S/.50\n"
    "💵 `+100 sueldo` → Registra ingreso de S/.100\n"
    "➖ `-30 taxi` → Registra gasto de S/.30\n"
    "📝 `gasto 45 almuerzo` → Gasto explícito\n"
    "📝 `ingreso 500 freelance` → Ingreso explícito\n\n"
    "*/balance* → Ver resumen financiero 📊\n"
    "*/historial* → Últimas transacciones 📋\n"
    "*/ayuda* → Esta ayuda ❓\n"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Punto de entrada. Si ya está vinculado, saluda; si no, pide credenciales."""
    telegram_id = update.effective_user.id
    name = update.effective_user.first_name

    user = get_user_by_telegram_id(telegram_id)
    if user:
        _, username = user
        await update.message.reply_text(
            f"👋 ¡Hola de nuevo, *{username}*! Tu cuenta está vinculada ✅\n\n"
            + HELP_TEXT,
            parse_mode='Markdown'
        )
        return ConversationHandler.END

    # Usuario nuevo → pedir credenciales
    await update.message.reply_text(
        f"👋 ¡Hola, *{name}*! Soy tu asistente de *Finanzas Personales* 💰\n\n"
        "Para comenzar, necesito vincular tu cuenta.\n\n"
        "Envíame tu *usuario* y *contraseña* separados por espacio:\n"
        "Ejemplo: `kevin mi_contraseña`\n\n"
        "_Usa /cancelar para salir._",
        parse_mode='Markdown'
    )
    return WAITING_CREDENTIALS


async def receive_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe 'usuario contraseña', verifica y vincula el telegram_id."""
    text = update.message.text.strip()
    parts = text.split(' ', 1)

    if len(parts) != 2:
        await update.message.reply_text(
            "❌ Formato incorrecto.\n\nEnvía tu usuario y contraseña así:\n"
            "`kevin mi_contraseña`",
            parse_mode='Markdown'
        )
        return WAITING_CREDENTIALS

    username, password = parts
    telegram_id = update.effective_user.id

    success, result = link_telegram_id(username, password, telegram_id)

    if success:
        await update.message.reply_text(
            f"✅ ¡Cuenta *{result}* vinculada exitosamente! 🎉\n\n"
            + HELP_TEXT,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            f"❌ {result}\n\nIntenta de nuevo o usa /cancelar.",
        )
        return WAITING_CREDENTIALS


async def cancel_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el proceso de vinculación."""
    await update.message.reply_text(
        "❌ Proceso cancelado.\nUsa /start cuando quieras vincular tu cuenta."
    )
    return ConversationHandler.END
