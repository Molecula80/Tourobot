from decouple import config
import requests
import json


class Query:
    __x_rapid_api_key = config('X-RapidAPI-Key')
    __headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': __x_rapid_api_key
    }
    __city = ''
    __hotels_count = 0

    def __init__(self, bot, message, sort_order):
        self.__bot = bot
        self.__message = message
        self.__sort_order = sort_order
        self.input_start(message)

    def input_start(self, message):
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
            self.output_hotels()
        except ValueError:
            self.__bot.send_message(message.from_user.id,
                                    'Цифрами пожалуйста')

    def output_hotels(self):
        hotels = self.find_hotels()
        if not hotels:
            self.__bot.send_message(self.__message.from_user.id,
                                    'По вашему запросу ничего не найдено.')
            return
        for hotel in hotels:
            self.output_hotel(hotel)

    def find_hotels(self):
        properties_url = "https://hotels4.p.rapidapi.com/properties/list"
        destination_id = self.get_destination_id()
        if not destination_id:
            return None
        properties_querystring = {"destinationId": destination_id,
                                  "pageNumber": "1",
                                  "pageSize": self.__hotels_count,
                                  "checkIn": "2022-01-25",
                                  "checkOut": "2020-02-01",
                                  "adults1": "1",
                                  "sortOrder": self.__sort_order,
                                  "locale": "ru_RU",
                                  "currency": "USD"}
        properties_r = self.json_deserialization(url=properties_url,
                                                 headers=self.__headers,
                                                 querystring=
                                                 properties_querystring)
        try:
            return properties_r["data"]["body"]["searchResults"]["results"]
        except KeyError:
            return None

    def get_destination_id(self):
        search_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        search_querystring = {"query": self.__city,
                              "locale": "ru_RU",
                              "currency": "USD"}
        search_r = self.json_deserialization(url=search_url,
                                             headers=self.__headers,
                                             querystring=search_querystring)
        try:
            return search_r["suggestions"][0]["entities"][0]["destinationId"]
        except LookupError:
            return None

    @classmethod
    def json_deserialization(cls, url: str, headers: dict,
                             querystring: dict) -> dict:
        """ Функция. Ищет результаты по url и строке запроса. """
        response = requests.request("GET", url, headers=headers,
                                    params=querystring)
        return json.loads(response.text)

    def output_hotel(self, hotel):
        name = self.get_param(hotel, "name")
        address = self.get_param(hotel, "address", "streetAddress")
        center_dist = self.get_param(hotel, "landmarks", 0, "distance")
        price = self.get_param(hotel, "ratePlan", "price", "current")
        hotel_info = '{name}\nАдрес: {address}\n' \
                     'Расстояние от цетра города: {center_dist}\n' \
                     'Цена: {price}'.format(name=name,
                                            address=address,
                                            center_dist=center_dist,
                                            price=price)
        self.__bot.send_message(self.__message.from_user.id,
                                hotel_info,
                                disable_web_page_preview=True)

    @classmethod
    def get_param(cls, hotel, *args):
        param = hotel
        for arg in args:
            try:
                param = param[arg]
            except LookupError:
                return 'Нет данных'
        return param

