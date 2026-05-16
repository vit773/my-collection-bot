import telebot
import os
import time
from flask import Flask, request

# ==================== НАСТРОЙКИ ====================
TOKEN = os.getenv("TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
# ===================================================

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Запоминаем, когда в последний раз благодарили каждого пользователя
last_thanked = {}

print("🤖 Бот запущен (с одним «Спасибо!» за серию сообщений)")

# Приветствие
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "Привет! Отправь фото, видео или интересную новость которой хочешь поделиться. Спасибо!")

# Пересылка + умное «Спасибо!»
@bot.message_handler(content_types=[
    'text', 'photo', 'video', 'document', 'audio', 'voice',
    'video_note', 'sticker', 'animation', 'poll', 'dice'
])
def forward_to_group(message):
    if message.chat.type != 'private':
        return

    # Пересылаем в группу ВСЕГДА
    try:
        bot.forward_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
    except Exception as e:
        print(f"Ошибка пересылки: {e}")

    # ←←← УМНОЕ СПАСИБО ←←←
    user_id = message.chat.id
    current_time = time.time()

    # Благодарим только если прошло больше 10 секунд с прошлого «Спасибо!»
    if (user_id not in last_thanked or 
        current_time - last_thanked[user_id] > 10):
        
        bot.send_message(user_id, "Спасибо!")
        last_thanked[user_id] = current_time

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
