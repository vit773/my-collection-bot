import telebot
import os
from flask import Flask, request

# ==================== НАСТРОЙКИ ====================
TOKEN = os.getenv("TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
# ===================================================

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

print("🤖 Бот запущен и работает")

# Приветствие при /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "Привет! Отправь фото, видео или интересную новость которой хочешь поделиться. Спасибо!")

# Пересылка всего из лички + ответ «Спасибо!»
@bot.message_handler(content_types=[
    'text', 'photo', 'video', 'document', 'audio', 'voice',
    'video_note', 'sticker', 'animation', 'poll', 'dice'
])
def forward_to_group(message):
    if message.chat.type != 'private':
        return
    
    try:
        bot.forward_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        # Новый ответ пользователю
        bot.send_message(message.chat.id, "Спасибо!")
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.send_message(message.chat.id, "Спасибо!")  # даже при ошибке говорим спасибо

# ==================== WEBHOOK ====================
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return 'Бот работает! 🚀'

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if WEBHOOK_URL:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/" + TOKEN)
    print(f"✅ Webhook установлен на {WEBHOOK_URL}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
