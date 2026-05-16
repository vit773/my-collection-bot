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

print("🤖 Бот запущен — ВСЁ (текст + медиа) работает")

# Приветствие
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Привет! Присылай что угодно — текст, фото, видео, ролики, файлы — всё будет в группе.")

# ←←← ГЛАВНОЕ ИСПРАВЛЕНИЕ: ловим ВСЕ типы контента из лички ←←←
@bot.message_handler(content_types=[
    'text', 'photo', 'video', 'document', 'audio', 'voice',
    'video_note', 'sticker', 'animation', 'poll', 'dice'
])
def forward_to_group(message):
    if message.chat.type != 'private':
        return
    
    print(f"📨 Приватное сообщение от {message.chat.id} | Тип: {message.content_type} | ID: {message.message_id}")
    try:
        bot.forward_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        print("✅ Успешно переслано в группу")
        bot.send_message(message.chat.id, "✅ Получено и переслано в группу!")
    except Exception as e:
        error = f"❌ Ошибка: {str(e)}"
        print(error)
        bot.send_message(message.chat.id, error)

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
