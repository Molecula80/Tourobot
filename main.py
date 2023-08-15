from telebot import TeleBot
from decouple import config

from db_connection import create_tables
from logger import init_logger
from botrequests.query import Query
from botrequests.bestdeal import BestDeal
from botrequests.history import history
from botrequests.help_command import help_command

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
                     'Бот для поиска отелей. Введите команду /help для '
                     'получения помощи.'.format(us_name))
    create_tables(user_id=us_id,
                  user_name=us_name,
                  user_surname=us_surname,
                  username=username)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    """ Функция. Реагирует на текстовые сообщения. """
    if message.text == "/lowprice":
        Query(bot=bot, message=message, sort_order='PRICE')
    elif message.text == "/highprice":
        Query(bot=bot, message=message, sort_order='PRICE_HIGHEST_FIRST')
    elif message.text == "/bestdeal":
        BestDeal(bot=bot, message=message)
    elif message.text == "/history":
        history(bot=bot, user_id=message.from_user.id)
    elif message.text == "/help":
        help_command(bot=bot, user_id=message.from_user.id)
    else:
        bot.send_message(message.from_user.id, "Я не понимаю.")


if __name__ == '__main__':
    init_logger()
    bot.polling(none_stop=True, interval=0)
