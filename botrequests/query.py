from decouple import config
import requests
import json
from telebot import types
from typing import List
from telebot.types import InputMediaPhoto
from telegram_bot_calendar import DetailedTelegramCalendar
import logging
import sqlite3
from db_connection import db_calendar_val


class Query:
    """
    Базовый класс, описывающий запрос к hotels4.p.rapidapi.com

    __x_rapid_api_key: ключ rapid api
    _headers (dict): словарь, содержащий хост и ключ rapid api

    Args:
        bot: передается бот
        message: передается сообщение
        sort_order (str): передается порядок сортировки

    Atributes:
        _city (str): город
        _hotels_count (int): количество отелей
        _check_in (str): дата въезда
        _check_out (str): дата выезда
        __photos_count (int): количество фотографий
    """
    __x_rapid_api_key = config('X-RapidAPI-Key')
    _headers: dict = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': __x_rapid_api_key
    }

    def __init__(self, bot, message, sort_order: str) -> None:
        self._bot = bot
        self.__message = message
        self.__sort_order = sort_order
        self._city = ''
        self._hotels_count = 0
        self._check_in = ''
        self._check_out = ''
        self.__photos_count = 0
        # Получаем id календарей
        self.__ci_cal_id = self.get_calendar_id(message.from_user.id)
        self.__co_cal_id = self.get_calendar_id(message.from_user.id)
        self._logger = logging.getLogger('tourobot')
        self.logger_debug()
        self._bot.send_message(message.from_user.id, 'Введите город.')
        self._bot.register_next_step_handler(message, self.input_city)

    @classmethod
    def get_calendar_id(cls, user_id: int) -> int:
        """
        Статический метод. Создает новую запись в таблице calendars в базе
        данных, вносит туда id пользователя и возвращает id календаря.
        :param user_id:
        :return calendar_id:
        """
        db_calendar_val(user_id)
        conn = sqlite3.connect('tourobot.db', check_same_thread=False)
        cursor = conn.cursor()
        conn.commit()
        calendar_ids = cursor.execute('SELECT id FROM calendars '
                                      'WHERE user_id = {}'.format(user_id))
        calendar_id = list(calendar_ids)[-1][0]
        return calendar_id

    def logger_debug(self) -> None:
        """ Метод для вывода логов. """
        self._logger.debug('user id: {user_id} | '
                           'sort: {s_order} | '
                           'ci cal id: {ci_cal_id} | '
                           'co cal id: {co_cal_id} | '
                           'city: {city} | '
                           'hotels count: {h_count} | '
                           'dates: {check_in} - {check_out} | '
                           'photos: {p_count}'.
                           format(user_id=self.__message.from_user.id,
                                  s_order=self.__sort_order,
                                  ci_cal_id=self.__ci_cal_id,
                                  co_cal_id=self.__co_cal_id,
                                  city=self._city,
                                  h_count=self._hotels_count,
                                  check_in=self._check_in,
                                  check_out=self._check_out,
                                  p_count=self.__photos_count))

    def input_city(self, message) -> None:
        """
        Метод для ввода города

        :param message: сообщение
        :return:
        """
        self._city = message.text
        self.logger_debug()
        self._bot.send_message(message.from_user.id,
                               'Сколько отелей нужно отобразить в '
                               'сообщении? (не больше 25)')
        self._bot.register_next_step_handler(message,
                                             self.input_hotels_count)

    def input_hotels_count(self, message) -> None:
        """
        Метод для ввода количества отелей

        :param message: сообщение
        :return:
        """

        @self._bot.callback_query_handler(
            func=DetailedTelegramCalendar.func(calendar_id=self.__ci_cal_id))
        def input_check_in(call) -> None:
            """
            Вложенная функция для выбора начальной даты.

            :param call: вызов функции.
            :return:
            """
            result, key, step = \
                DetailedTelegramCalendar(calendar_id=
                                         self.__ci_cal_id).process(call.data)
            if not result and key:
                self._bot.edit_message_text('Выберите начальную дату.',
                                            call.message.chat.id,
                                            call.message.message_id,
                                            reply_markup=key)
            elif result:
                self._check_in = result
                self.logger_debug()
                # Создаем календарь для даты выезда.
                check_out_cal = \
                    DetailedTelegramCalendar(calendar_id=
                                             self.__co_cal_id).build()[0]
                self._bot.send_message(message.chat.id,
                                       'Выберите конечную дату.',
                                       reply_markup=check_out_cal)

        @self._bot.callback_query_handler(
            func=DetailedTelegramCalendar.func(calendar_id=self.__co_cal_id))
        def input_check_out(call) -> None:
            """
            Вложенная функция для выбора конечной даты.

            :param call: вызов функции.
            :return:
            """
            result, key, step = \
                DetailedTelegramCalendar(calendar_id=
                                         self.__co_cal_id).process(call.data)
            if not result and key:
                self._bot.edit_message_text('Выберите конечную дату.',
                                            call.message.chat.id,
                                            call.message.message_id,
                                            reply_markup=key)
            elif result:
                self._check_out = result
                self.logger_debug()
                keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                     resize_keyboard=True)
                buttons = ['Да', 'Нет']
                keyboard.add(*buttons)
                answer = self._bot.send_message(message.from_user.id,
                                                text='Вывести фотографии.',
                                                reply_markup=keyboard)
                self._bot.register_next_step_handler(answer,
                                                     self.need_photos)

        try:
            self._hotels_count = int(message.text)
            self.logger_debug()
            # Создаем календарь для даты въезда.
            check_in_cal = DetailedTelegramCalendar(
                calendar_id=self.__ci_cal_id).build()[0]
            self._bot.send_message(message.chat.id,
                                   'Выберите начальную дату.',
                                   reply_markup=check_in_cal)
        except ValueError:
            self._bot.send_message(message.from_user.id,
                                   'Количество должно быть в цифрах.')

    def need_photos(self, message) -> None:
        """
        Метод. Определяет, нужны ли фотографии

        :param message: сообщение
        :return:
        """
        if message.text == 'Да':
            self._bot.send_message(message.from_user.id,
                                   text='Сколько фотографий? (не больше 10)')
            self._bot.register_next_step_handler(message,
                                                 self.input_photos_count)
        elif message.text == 'Нет':
            self.output_hotels()
        else:
            self._bot.send_message(message.from_user.id, 'Я не понимаю.')

    def input_photos_count(self, message) -> None:
        """
        Метод для ввода количества фотографий

        :param message: сообщение
        :return:
        """
        try:
            if int(message.text) <= 10:
                self.__photos_count = int(message.text)
            else:
                self.__photos_count = 10
            self.output_hotels()
        except ValueError:
            self._bot.send_message(message.from_user.id,
                                   'Количество должно быть в цифрах.')

    def output_hotels(self) -> None:
        """
        Метод. Вызывает метод find_hotels чтобы найти отели. Если отели
        найдены вызывает output_hotel для кождого из них, в противном
        случае возвращает None.

        :return:
        """
        hotels = self.find_hotels()
        if not hotels:
            self._bot.send_message(self.__message.from_user.id,
                                   'По вашему запросу ничего не найдено.')
            return
        for hotel in hotels:
            self.output_hotel(hotel)

    def find_hotels(self) -> List[dict]:
        """
        Метод. Возвращает список содержащий словари отелей.

        :rtype: List[dict]
        """
        url = "https://hotels4.p.rapidapi.com/properties/list"
        destination_id = self.get_destination_id()
        if not destination_id:
            return list()
        querystring: dict = {"destinationId": destination_id,
                             "pageNumber": "1",
                             "pageSize": self._hotels_count,
                             "checkIn": self._check_in,
                             "checkOut": self._check_out,
                             "adults1": "1",
                             "sortOrder": self.__sort_order,
                             "locale": "ru_RU",
                             "currency": "USD"}
        self._logger.debug('user id: {user_id} | hotels qs: '
                           '{hotels_qs}'.format(user_id=
                                                self.__message.from_user.id,
                                                hotels_qs=querystring))
        results = self.json_deserialization(url=url,
                                            headers=self._headers,
                                            querystring=querystring)
        try:
            return results["data"]["body"]["searchResults"]["results"]
        except BaseException:
            return list()

    def get_destination_id(self) -> str:
        """
        Метод. Возвращает destination id города.

        :rtype: str
        """
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring: dict = {"query": self._city,
                             "locale": "ru_RU",
                             "currency": "USD"}
        self._logger.debug('user id: {user_id} | city qs: '
                           '{city_qs}'.format(user_id=
                                              self.__message.from_user.id,
                                              city_qs=querystring))
        results = self.json_deserialization(url=url,
                                            headers=self._headers,
                                            querystring=querystring)
        try:
            return results["suggestions"][0]["entities"][0]["destinationId"]
        except BaseException:
            return str()

    @classmethod
    def json_deserialization(cls, url: str, headers: dict,
                             querystring: dict) -> dict:
        """
        Статический метод. Производит десериализацию JSON и возвращает
        результат.

        :param url:
        :param headers: словарь, содержащий хост и ключ rapid api
        :param querystring: словарь, содержащий параметры запроса
        :rtype: dict
        """
        response = requests.request("GET", url, headers=headers,
                                    params=querystring)
        return json.loads(response.text)

    def output_hotel(self, hotel: dict) -> None:
        """
        Метод. Выводит информацию об отелях, и фотографии, если
        пользользователь счел нужным вывод последних.

        :param hotel: словарь содержащий данные об отеле.
        :return:
        """
        name = self.get_param(hotel, "name")
        hotel_id = self.get_param(hotel, "id")
        if hotel_id != 'нет данных':
            url = 'https://ru.hotels.com/ho{hotel_id}'.format(
                hotel_id=hotel_id)
        else:
            url = 'отсутствует'
        address = self.get_param(hotel, "address", "streetAddress")
        center_dist = self.get_param(hotel, "landmarks", 0, "distance")
        price = self.get_param(hotel, "ratePlan", "price", "current")
        hotel_info = '{name}\nСсылка: {url}\nАдрес: {address}\n' \
                     'Расстояние от цетра города: {center_dist}\n' \
                     'Цена: {price}'.format(name=name,
                                            url=url,
                                            address=address,
                                            center_dist=center_dist,
                                            price=price)
        self._bot.send_message(self.__message.from_user.id,
                               hotel_info,
                               disable_web_page_preview=True)
        # Ищем фотографии
        if self.__photos_count > 0:
            self.get_photos(hotel)

    @classmethod
    def get_param(cls, hotel: dict, *args) -> str:
        """
        Статический метод. Проверяет словарь содержащий отель на наличие
        ключей и индексов, переданных в метод.

        :param hotel: словарь содержащий данные об отеле.
        :param args:
        :rtype: Any
        """
        param = hotel
        for arg in args:
            try:
                param = param[arg]
            except BaseException:
                return 'нет данных'
        return param

    def get_photos(self, hotel: dict) -> None:
        """
        Метод ищет фотографии, а затем вызывает метод output_photo для каждой.

        :param hotel: словарь содержащий данные об отеле.
        :return:
        """
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        querystring = {"id": hotel["id"]}
        results = self.json_deserialization(url=url,
                                            headers=self._headers,
                                            querystring=querystring)
        try:
            images: List[dict] = results["hotelImages"][:self.__photos_count]
            self.send_photos(images)
        except BaseException:
            return

    def send_photos(self, images: List[dict]) -> None:
        """
        Метод для отправки фотографий пользователю.

        :param images: список, содержащий фотографии.
        :return:
        """
        photos: list = list()
        for item in images:
            try:
                size = item["sizes"][0]["suffix"]
                photo = item["baseUrl"].format(size=size)
                photos.append(InputMediaPhoto(photo))
            except BaseException:
                pass
        self._bot.send_media_group(self.__message.from_user.id, photos)
