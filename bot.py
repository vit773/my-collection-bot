import telebot
import os
from flask import Flask, request
import traceback

# ==================== НАСТРОЙКИ ====================
TOKEN = os.getenv("TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
# ===================================================

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

print("🤖 Бот запущен (исправленная версия)")

# 1. Приветствие
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Привет! Я твой сборщик. Присылай что угодно — я перешлю в группу.")

# 2. Основной обработчик — ПЕРВЫМ! (важно!)
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def forward_to_group(message):
    print(f"📨 Приватное сообщение от {message.chat.id} | Тип: {message.content_type}")
    try:
        bot.forward_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        print("✅ Успешно переслано в группу")
        bot.send_message(message.chat.id, "✅ Получено и переслано в группу!")
    except Exception as e:
        error = f"❌ Ошибка пересылки: {str(e)}"
        print(error)
        bot.send_message(message.chat.id, error)

# 3. Отладка — только если ничего выше не сработало
@bot.message_handler(func=lambda m: True)
def debug_all(message):
    print(f"📨 DEBUG (не обработано выше): Chat type = '{message.chat.type}' | From = {message.chat.id}")

# ==================== WEBHOOK ====================
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.get_json())
        bot.process_new_updates([update])
        print("✅ Update обработан успешно")
    except Exception as e:
        print(f"❌ Ошибка в webhook: {e}")
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
