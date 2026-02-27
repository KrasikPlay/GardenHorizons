import telebot
import re
import os
import time

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = -1002664137906
TARGET_USERNAME = "gardenhorizons_robot"

bot = telebot.TeleBot(TOKEN)

# Растения
plant_emoji = {
    "plum": "🫐",
    "potato": "🥔",
    "cabbage": "🥬",
    "cherry": "🍒",
}

# Снаряжение
gear_emoji = {
    "super sprinkler": "💦",
}

# Ключевые слова погоды (чтобы не ломать)
weather_keywords = ["rain", "snow", "storm", "sunny", "cloudy", "weather"]

last_message_id = None

@bot.channel_post_handler(func=lambda m: m.from_user.username == TARGET_USERNAME)
def handle_new_message(message):
    global last_message_id

    print(f"📩 Новое сообщение от @{TARGET_USERNAME}, ID: {message.message_id}")

    # Проверяем, не погода ли это
    is_weather = any(word in message.text.lower() for word in weather_keywords)

    # 1. Удаляем предыдущее сообщение
    if last_message_id:
        try:
            bot.delete_message(CHANNEL_ID, last_message_id)
            print(f"🗑️ Удалено предыдущее сообщение ID: {last_message_id}")
        except Exception as e:
            print(f"⚠️ Не удалось удалить предыдущее: {e}")

    # 2. Обрабатываем текущее сообщение
    lines = message.text.split('\n')
    new_lines = []

    for i, line in enumerate(lines):
        # Убираем кружки из любой строки
        line = re.sub(r'[🟣🟡]', '', line)

        # Первая строка: добавляем ‼️
        if i == 0:
            line = '‼️ ' + line.lstrip()
        else:
            # Если это погода — не трогаем вторую строку
            if is_weather:
                line = line.lstrip()
            else:
                # Ищем растение
                replaced = False
                for plant, emoji in plant_emoji.items():
                    if plant.lower() in line.lower():
                        line = emoji + ' ' + line.lstrip()
                        replaced = True
                        break
                # Если не растение — ищем снаряжение
                if not replaced:
                    for gear, emoji in gear_emoji.items():
                        if gear.lower() in line.lower():
                            line = emoji + ' ' + line.lstrip()
                            break

        new_lines.append(line)

    new_text = '\n'.join(new_lines)

    # 3. Редактируем текущее сообщение
    try:
        time.sleep(0.5)
        bot.edit_message_text(
            chat_id=CHANNEL_ID,
            message_id=message.message_id,
            text=new_text
        )
        print(f"✅ Текущее сообщение отредактировано")
    except Exception as e:
        print(f"❌ Ошибка при редактировании: {e}")

    # 4. Запоминаем ID
    last_message_id = message.message_id

print("🤖 Бот запущен (с защитой погоды)...")
bot.infinity_polling()
