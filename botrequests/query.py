from decouple import config
import requests
import json


class Query:
    __city = ''
    __hotels_count = 0

    def __init__(self, bot, message, sort_order):
        self.__bot = bot
        self.__message = message
        self.__sort_order = sort_order
        self.input_params(message)

    def input_params(self, message):
        self.__bot.send_message(message.from_user.id, 'Введите город.')
        self.__bot.register_next_step_handler(message, self.input_city)

    def input_city(self, message):
        self.__city = message.text
        self.__bot.send_message(message.from_user.id,
                                'Сколько отелей нужно отобразить в '
                                'сообщении? (не больше 25)')
        self.__bot.register_next_step_handler(message,
                                              self.input_hotels_count)

    def input_hotels_count(self, message):
        try:
            self.__hotels_count = int(message.text)
            self.find_hotels()
        except ValueError:
            self.__bot.send_message(message.from_user.id,
                                    'Цифрами пожалуйста')

    @classmethod
    def get_results(cls, url: str, headers: dict, querystring: dict) -> dict:
        """ Функция. Ищет результаты по url и строке запроса. """
        response = requests.request("GET", url, headers=headers,
                                    params=querystring)
        return json.loads(response.text)

    def find_hotels(self) -> None:
        x_rapid_api_key = config('X-RapidAPI-Key')
        search_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        properties_url = "https://hotels4.p.rapidapi.com/properties/list"
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': x_rapid_api_key
        }
        search_querystring = {"query": self.__city,
                              "locale": "en_US",
                              "currency": "USD"}
        search_r = self.get_results(url=search_url,
                                    headers=headers,
                                    querystring=search_querystring)
        destination_id = \
            search_r["suggestions"][0]["entities"][0]["destinationId"]
        # Ищем отели.
        properties_querystring = {"destinationId": destination_id,
                                  "pageNumber": "1",
                                  "pageSize": self.__hotels_count,
                                  "checkIn": "2022-01-25",
                                  "checkOut": "2020-02-01",
                                  "adults1": "1",
                                  "sortOrder": self.__sort_order,
                                  "locale": "en_US",
                                  "currency": "USD"}
        properties_r = self.get_results(url=properties_url,
                                        headers=headers,
                                        querystring=properties_querystring)
        answer = '\n'.join(hotel["name"] for hotel in properties_r["data"][
            "body"]["searchResults"]["results"])
        self.__bot.send_message(self.__message.from_user.id,
                                answer,
                                disable_web_page_preview=True)
