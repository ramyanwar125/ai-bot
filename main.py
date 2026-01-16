import os
import logging
import httpx
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعدادات التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_url = "https://shbot.haltaelam.com/api_proxy.php"

    async def get_ai_response(self, text: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_url,
                    json={"message": text},
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"API Error: {e}")
                return "⚠️ عذراً، واجهت مشكلة في الاتصال."

class TelegramAIBot:
    def __init__(self, token: str):
        self.token = token
        self.ai_service = AIService()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🌟 أهلاً بك! أنا بوت ذكي جاهز للرد على استفساراتك.")

    async def handle_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_msg = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
        response = await self.ai_service.get_ai_response(user_msg)
        await update.message.reply_text(response, parse_mode=constants.ParseMode.MARKDOWN)

    def run(self):
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_messages))

        # إعدادات Render الخاصة بـ Webhook
        PORT = int(os.environ.get("PORT", 8000))
        # ملاحظة: Render يزودنا برابط الخدمة عبر RENDER_EXTERNAL_URL
        URL = os.environ.get("RENDER_EXTERNAL_URL") 

        if URL:
            logger.info(f"Starting Webhook on {URL}")
            app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=self.token,
                webhook_url=f"{URL}/{self.token}"
            )
        else:
            # تشغيل عادي في حال كنت تجربه على جهازك الشخصي
            logger.info("Starting Polling...")
            app.run_polling()

if __name__ == '__main__':
    # سيحاول البوت جلب التوكن من Environment Variables أولاً، وإذا لم يجده سيستخدم الذي زودتني به
    TOKEN = os.environ.get("TELEGRAM_TOKEN", "8304738811:AAEhX2c7DzwrcafAX-cbxgzBPNDZiS7LhUM")
    bot = TelegramAIBot(TOKEN)
    bot.run()
