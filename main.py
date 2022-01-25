from telebot import TeleBot
from decouple import config
import requests
import json
from db_connection import db_table_val

TOKEN = config('TOKEN')
bot = TeleBot(TOKEN)

x_rapid_api_key = config('X-RapidAPI-Key')

search_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
properties_url = "https://hotels4.p.rapidapi.com/properties/list"

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': x_rapid_api_key
    }


def find_results(url, querystring):
    """ Функция. Ищет результаты по url и строке запроса. """
    response = requests.request("GET", url, headers=headers,
                                params=querystring)
    return json.loads(response.text)


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
    # Ищем destination_id города Нью-Йорк.
    search_querystring = {"query": "new york",
                          "locale": "en_US",
                          "currency": "USD"}
    search_r = find_results(url=search_url, querystring=search_querystring)
    destination_id = \
        search_r["suggestions"][0]["entities"][0]["destinationId"]
    # Ищем 10 самых дешевых отелей.
    properties_querystring = {"destinationId": destination_id,
                              "pageNumber": "1",
                              "pageSize": "10",
                              "checkIn": "2022-01-25",
                              "checkOut": "2020-02-01",
                              "adults1": "1",
                              "sortOrder": "PRICE",
                              "locale": "en_US",
                              "currency": "USD"}
    properties_r = find_results(url=properties_url,
                                querystring=properties_querystring)
    if message.text == "/new-york":
        answer = '\n'.join(hotel["name"] for hotel in properties_r["data"][
            "body"]["searchResults"]["results"])
        bot.send_message(message.from_user.id, answer)
    else:
        bot.send_message(message.from_user.id, "Я не понимаю.")


bot.polling(none_stop=True, interval=0)
