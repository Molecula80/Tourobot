from telebot import TeleBot
from decouple import config
from db_connection import db_table_val


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
                     'Бот для поиска отелей. Ваше имя внесено '
                     'в базу данных.'.format(us_name))
    db_table_val(user_id=us_id,
                 user_name=us_name,
                 user_surname=us_surname,
                 username=username)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    """ Функция. Реагирует на текстовые сообщения. """
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
