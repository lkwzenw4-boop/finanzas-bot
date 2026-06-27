"""
telegram_bot/bot.py
Punto de entrada del Bot de Telegram para Finanzas Personales.
Ejecutar: python -m telegram_bot.bot
"""
import logging
import os
import sys

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from telegram_bot.handlers.auth import (
    start, receive_username, receive_password, cancel_login,
    WAITING_USERNAME, WAITING_PASSWORD
)
from telegram_bot.handlers.transactions import (
    handle_message, confirm_transaction, change_category, select_category
)
from telegram_bot.handlers.reports import balance, historial, ayuda

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
import io
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'))],
)
logger = logging.getLogger(__name__)


def main():
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    
    class DummyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive")
            
    port = int(os.environ.get("PORT", 10000))
    def run_dummy_server():
        try:
            server = HTTPServer(("0.0.0.0", port), DummyHandler)
            server.serve_forever()
        except Exception as e:
            logger.error(f"Error starting dummy server: {e}")
            
    threading.Thread(target=run_dummy_server, daemon=True).start()
    logger.info(f"Dummy HTTP server started on port {port}")

    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN no está configurado. Revisa tus variables de entorno.")
        sys.exit(1)

    # Configurar SSL con certifi (necesario en Windows / Python 3.14)
    import ssl
    import certifi
    import httpx
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_ctx)

    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.warning("[!] DATABASE_URL no configurado. Usando SQLite local.")
    else:
        logger.info("[OK] Modo PostgreSQL (Supabase) activo.")

    from telegram.request import HTTPXRequest
    request = HTTPXRequest(http_version="1.1")
    app = ApplicationBuilder().token(token).request(request).build()

    # ── ConversationHandler para login (/start → usuario → contraseña)
    login_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)
            ],
            WAITING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)
            ],
        },
        fallbacks=[CommandHandler('cancelar', cancel_login)],
        allow_reentry=True,
    )

    # ── Registrar handlers ──────────────────────────
    app.add_handler(login_handler)

    # Comandos de reportes
    app.add_handler(CommandHandler('balance',   balance))
    app.add_handler(CommandHandler('historial', historial))
    app.add_handler(CommandHandler('ayuda',     ayuda))

    # Callbacks de botones inline (transacciones)
    app.add_handler(CallbackQueryHandler(confirm_transaction, pattern=r'^confirm_'))
    app.add_handler(CallbackQueryHandler(change_category,     pattern=r'^change_cat$'))
    app.add_handler(CallbackQueryHandler(select_category,     pattern=r'^cat_'))

    # Mensajes de texto libre → registro de transacciones
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("[Bot] Iniciado. Esperando mensajes...")
    import asyncio

    async def run():
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        # Mantener el bot vivo hasta interrupcin
        import signal
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop_event.set)
            except NotImplementedError:
                pass  # Windows no soporta add_signal_handler
        try:
            await stop_event.wait()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

    asyncio.run(run())


if __name__ == '__main__':
    main()
