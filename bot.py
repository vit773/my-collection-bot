import telebot
import os
from flask import Flask, request

# ==================== НАСТРОЙКИ ====================
TOKEN = os.getenv("TOKEN")          # ← Render сам подставит
GROUP_ID = int(os.getenv("GROUP_ID"))  # ← Render сам подставит
# ===================================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Приветствие
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
        "✅ Привет! Я твой сборщик контента.\n\n"
        "Присылай мне в личку любые сообщения, фото, видео, ролики, файлы — "
        "я сразу перешлю их в твою супергруппу.")

# Пересылка всего из лички
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def forward_to_group(message):
    try:
        bot.forward_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        bot.send_message(message.chat.id, "✅ Получено и переслано!")
    except:
        bot.send_message(message.chat.id, "⚠️ Ошибка пересылки.")

# ==================== WEBHOOK ====================
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return 'Бот работает! 🚀'

# Автоматическая установка webhook при запуске (если указано в Render)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if WEBHOOK_URL:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/" + TOKEN)
    print(f"✅ Webhook установлен на {WEBHOOK_URL}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)