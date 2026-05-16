import telebot
import os
from flask import Flask, request
import traceback

# debug redeploy 3

# ==================== НАСТРОЙКИ ====================
TOKEN = os.getenv("TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
# ===================================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

print("🤖 Бот запущен в режиме отладки")

# Приветствие
@bot.message_handler(commands=['start'])
def start(message):
    print(f"[START] от {message.chat.id}")
    bot.send_message(message.chat.id, "✅ Привет! Я в режиме отладки. Присылай что угодно.")

# ←←← НОВЫЙ ОТЛАДОЧНЫЙ ХЕНДЛЕР ←←←
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def forward_to_group(message):
    print(f"📨 Получено приватное сообщение от {message.chat.id} | Тип: {message.content_type}")
    try:
        # Пересылаем в группу
        bot.forward_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        print("✅ Успешно переслано в группу")
        bot.send_message(message.chat.id, "✅ Получено и переслано в группу!")
    except Exception as e:
        error_text = f"❌ Ошибка: {str(e)}\n{traceback.format_exc()}"
        print(error_text)
        try:
            bot.send_message(message.chat.id, f"⚠️ Ошибка пересылки:\n{str(e)}")
        except:
            print("Не удалось даже отправить сообщение об ошибке пользователю")

# Webhook
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
    return 'Бот работает! 🚀 (отладочная версия)'

# Установка webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if WEBHOOK_URL:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/" + TOKEN)
    print(f"✅ Webhook установлен на {WEBHOOK_URL}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
