from telebot import TeleBot
from decouple import config
from db_connection import db_table_val
from botrequests.query import Query

TOKEN = config('TOKEN')
bot = TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message) -> None:
    """ Функция. Создает пользователя, если его нет в базе данных. """
    us_id = message.from_user.id
    us_name = message.from_user.first_name
    us_surname = message.from_user.last_name
    username = message.from_user.username
    bot.send_message(message.chat.id,
                     'Здравствуйте {}. Меня зовут Tourobot. '
                     'Бот для поиска отелей.'.format(us_name))
    db_table_val(user_id=us_id,
                 user_name=us_name,
                 user_surname=us_surname,
                 username=username)


@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message) -> None:
    """ Функция. Реагирует на текстовые сообщения. """
    if message.text == "/lowprice":
        Query(bot=bot, message=message, sort_order='PRICE')
    elif message.text == "/highprice":
        Query(bot=bot, message=message, sort_order='PRICE_HIGHEST_FIRST')
    else:
        bot.send_message(message.from_user.id, "Я не понимаю.")


bot.polling(none_stop=True, interval=0)
