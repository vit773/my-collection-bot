import telebot
import os
from flask import Flask, request
import traceback

# ==================== НАСТРОЙКИ ====================
TOKEN = os.getenv("TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
# ===================================================

# ←←← ГЛАВНОЕ ИСПРАВЛЕНИЕ ←←←
bot = telebot.TeleBot(TOKEN, threaded=False)

app = Flask(__name__)

print("🤖 Бот запущен в режиме отладки (threaded=False)")

# Супер-отладочный хендлер — ловит ВСЁ
@bot.message_handler(func=lambda m: True)
def debug_all_messages(message):
    print(f"📨 DEBUG: Сообщение получено! Chat type = '{message.chat.type}' | Content type = '{message.content_type}' | From = {message.chat.id}")
    if message.text:
        print(f"Текст: {message.text}")

# Основной обработчик (теперь должен сработать)
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
        error_text = f"❌ Ошибка: {str(e)}\n{traceback.format_exc()}"
        print(error_text)
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}")

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
    return 'Бот работает! 🚀 (threaded=False версия)'

# Установка webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if WEBHOOK_URL:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + "/" + TOKEN)
    print(f"✅ Webhook установлен на {WEBHOOK_URL}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
