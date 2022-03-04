from telebot import TeleBot
from decouple import config
from db_connection import db_users_val, db_commands_val
from botrequests.query import Query
from botrequests.bestdeal import BestDeal
from logger import init_logger
from botrequests.history import history

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
                     'Бот для поиска отелей.\n'
                     '/lowprice - поиск самых дешевых отелей.\n'
                     '/highprice - поиск самых дорогих отелей.\n'
                     '/bestdeal - поиск отелей, наиболее подходящих по цене '
                     'и расстоянию от центра города.'.format(us_name))
    db_users_val(user_id=us_id,
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
    else:
        bot.send_message(message.from_user.id, "Я не понимаю.")


if __name__ == '__main__':
    init_logger()
    bot.polling(none_stop=True, interval=0)
