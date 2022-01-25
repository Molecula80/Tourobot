from telebot import TeleBot
from decouple import config
from db_connection import db_table_val
import requests
import json

TOKEN = config('TOKEN')
bot = TeleBot(TOKEN)

x_rapid_api_key = config('X-RapidAPI-Key')

url = "https://hotels4.p.rapidapi.com/properties/list"

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': x_rapid_api_key
    }


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
    querystring = {"destinationId": "1506246",
                   "pageNumber": "1",
                   "pageSize": "10",
                   "checkIn": "2022-01-25",
                   "checkOut": "2020-02-01",
                   "adults1": "1",
                   "sortOrder": "PRICE",
                   "locale": "en_US",
                   "currency": "USD"}
    response = requests.request("GET", url, headers=headers,
                                params=querystring)
    results = json.loads(response.text)
    if message.text == "/new-york":
        answer = '\n'.join(hotel["name"] for hotel in results["data"]["body"][
            "searchResults"]["results"])
        bot.send_message(message.from_user.id, answer)
    else:
        bot.send_message(message.from_user.id, "Я не понимаю.")


bot.polling(none_stop=True, interval=0)
