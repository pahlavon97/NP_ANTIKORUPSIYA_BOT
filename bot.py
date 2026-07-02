import os
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from app.handlers.start import start
from app.handlers.language import language
from app.handlers.appeal import (
    full_name,
    phone,
    invalid_phone,
    region,
    appeal_type,
    message,
    cancel,
)
from app.handlers.admin import (
    admin_reply_start,
    admin_reply_text,
    ADMIN_REPLY_TEXT,
)
from app.states.user_state import LANGUAGE, FULL_NAME, PHONE, REGION, APPEAL_TYPE, MESSAGE

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Health server started on port {port}")


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is not set")

    start_health_server()

    app = Application.builder().token(BOT_TOKEN).build()

    admin_reply_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_reply_start, pattern="^reply_")
        ],
        states={
            ADMIN_REPLY_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply_text)
            ],
        },
        fallbacks=[],
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, invalid_phone),
            ],
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, region)],
            APPEAL_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, appeal_type)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(admin_reply_conv)
    app.add_handler(conv_handler)

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()