from telebot import TeleBot
from decouple import config
import sqlite3

TOKEN = config('TOKEN')
bot = TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message) -> None:
    bot.send_message(message.chat.id, 'Приивет. Меня зовут Tourobot. '
                                      'Бот для поиска отелей.')


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    if message.text == "/hello-world":
        bot.send_message(message.from_user.id, "Добро пожаловать!")
    elif message.text == "Привет":
        bot.send_message(message.from_user.id,
                         "Привет, чем я могу тебе помочь?")
    else:
        bot.send_message(message.from_user.id,
                         "Я тебя не понимаю. Напиши 'Привет' "
                         "или '/hello-world'.")


bot.polling(none_stop=True, interval=0)
