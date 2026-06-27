"""
telegram_bot/handlers/auth.py
Maneja el flujo de login y vinculación de cuenta Telegram ↔ Finanzas.
Login en 2 pasos: primero usuario, luego contraseña (se borra el mensaje por privacidad).
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram_bot.db import get_user_by_telegram_id, link_telegram_id, unlink_telegram_id

# Estados del ConversationHandler
WAITING_USERNAME = 1
WAITING_PASSWORD = 2

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
    """Punto de entrada. Si ya está vinculado, saluda; si no, pide usuario."""
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

    # Limpiar datos previos
    context.user_data.clear()

    await update.message.reply_text(
        f"👋 ¡Hola, *{name}*! Soy tu asistente de *Finanzas Personales* 💰\n\n"
        "Para comenzar, necesito vincular tu cuenta.\n\n"
        "Envíame tu *nombre de usuario*:\n"
        "_Ejemplo:_ `kevin`\n\n"
        "_Usa /cancelar para salir._",
        parse_mode='Markdown'
    )
    return WAITING_USERNAME


async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el nombre de usuario y pide la contraseña."""
    username = update.message.text.strip()

    if not username or ' ' in username:
        await update.message.reply_text(
            "❌ El usuario no debe tener espacios.\n\nEnvía solo tu nombre de usuario:",
            parse_mode='Markdown'
        )
        return WAITING_USERNAME

    # Guardar username en memoria
    context.user_data['pending_username'] = username

    await update.message.reply_text(
        f"👤 Usuario: *{username}*\n\n"
        "🔒 Ahora envíame tu *contraseña*:\n\n"
        "⚠️ _Tip de seguridad: borra el mensaje con tu contraseña después de enviarlo._",
        parse_mode='Markdown'
    )
    return WAITING_PASSWORD


async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la contraseña, verifica, vincula y borra el mensaje por seguridad."""
    password = update.message.text.strip()
    username = context.user_data.get('pending_username')
    telegram_id = update.effective_user.id

    # Intentar borrar el mensaje con la contraseña para mayor privacidad
    try:
        await update.message.delete()
    except Exception:
        pass  # Si no tiene permisos de borrar, continuar igual

    if not username:
        await update.message.reply_text(
            "❌ Sesión expirada. Usa /start para comenzar de nuevo."
        )
        return ConversationHandler.END

    success, result = link_telegram_id(username, password, telegram_id)

    # Limpiar datos sensibles de memoria inmediatamente
    context.user_data.pop('pending_username', None)

    if success:
        await update.effective_chat.send_message(
            f"✅ ¡Cuenta *{result}* vinculada exitosamente! 🎉\n\n"
            "🔒 _Tu mensaje con contraseña fue eliminado por seguridad._\n\n"
            + HELP_TEXT,
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    else:
        await update.effective_chat.send_message(
            f"❌ {result}\n\nEnvíame tu *usuario* nuevamente para intentar de nuevo:",
            parse_mode='Markdown'
        )
        return WAITING_USERNAME


async def cancel_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela el proceso de vinculación."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Proceso cancelado.\nUsa /start cuando quieras vincular tu cuenta."
    )
    return ConversationHandler.END
