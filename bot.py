import os
from flask import Flask, request
import telebot

# ==================== НАСТРОЙКИ ====================
TOKEN = os.getenv("TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# ===================================================

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Увеличиваем таймаут на случай медленного ответа Telegram
telebot.apihelper.READ_TIMEOUT = 60

print("🤖 Бот запущен")

# Приветствие при /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Отправь фото, видео или интересную новость которой хочешь поделиться. Спасибо!"
    )

# Пересылка всего из лички
@bot.message_handler(content_types=[
    'text', 'photo', 'video', 'document', 'audio', 'voice',
    'video_note', 'sticker', 'animation', 'poll', 'dice'
])
def forward_to_group(message):
    if message.chat.type != 'private':
        return

    user_id = message.chat.id

    # 1. Пытаемся переслать
    try:
        bot.forward_message(
            chat_id=GROUP_ID,
            from_chat_id=user_id,
            message_id=message.message_id
        )
    except Exception as e:
        print(f"Ошибка forward: {e}")
        # Fallback — копируем без метки «Переслано»
        try:
            bot.copy_message(
                chat_id=GROUP_ID,
                from_chat_id=user_id,
                message_id=message.message_id
            )
        except Exception as e2:
            print(f"Ошибка copy: {e2}")

    # 2. Пытаемся ответить «Спасибо!» (игнорируем, если пользователь заблокировал)
    try:
        bot.send_message(user_id, "Спасибо!")
    except Exception as e:
        print(f"Не смог отправить «Спасибо!»: {e}")

# ==================== WEBHOOK ====================
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.get_json())
        bot.process_new_updates([update])
    except Exception as e:
        print(f"Ошибка в webhook: {e}")
    return 'OK', 200

@app.route('/')
def index():
    return 'Бот работает! 🚀'

# Устанавливаем webhook безопасно (чтобы не падал при старте)
if WEBHOOK_URL:
    try:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL + "/" + TOKEN)
        print(f"✅ Webhook установлен на {WEBHOOK_URL}")
    except Exception as e:
        print(f"⚠️ Не удалось установить webhook: {e}")
        print("Бот запущен, но webhook не установлен. Попробуй перезапустить позже.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
