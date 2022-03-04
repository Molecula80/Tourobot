from typing import List
from .query import Query


class BestDeal(Query):
    """
    Класс BestDeal. Родитель Query. Вызввается если пользователь ввел команду
    /bestdeal.

    __x_rapid_api_key: ключ rapid api
    _headers (dict): словарь, содержащий хост и ключ rapid api
    __bd_messages (List[str]): список содержащий сообщения бота.

    Args:
        bot: передается бот
        message: передается сообщение
        sort_order (str): передается порядок сортировки

    Atributes:
        __bd_params (list): список в который вносятся минимаальные и
        максимальные цены и расстояния от центра города
        __bd_index (int): индекс элемента, вносящегося в список __bd_params
        _city (str): город
        _hotels_count (int): количество отелей
        _check_in (str): дата въезда
        _check_out (str): дата выезда
        __photos_count (int): количество фотографий
        __command_id (int): id команды введенной пользователем
    """
    __bd_messages: List[str] = [
        'Введите максимальную цену за сутки.',
        'Введите минимальное расстояние от центра города.',
        'Введите максимальное расстояние от центра города.',
        'Сколько отелей нужно отобразить в сообщении? (не больше 25)'
    ]

    def __init__(self, bot, message, sort_order: str = "PRICE") -> None:
        self.__bd_params = list()
        self.__bd_index = 0
        super().__init__(bot, message, sort_order)

    def logger_debug(self) -> None:
        """ Метод для вывода логов. """
        super(BestDeal, self).logger_debug()
        self._logger.debug('bestdeal params: {bd_params}'.format(
            bd_params=self.__bd_params))

    def input_city(self, message) -> None:
        """
        Метод для ввода города

        :param message: сообщение
        :return:
        """
        self._city = message.text
        self.logger_debug()
        self._bot.send_message(message.from_user.id,
                               'Введите минимальную цену за сутки.')
        self._bot.register_next_step_handler(message, self.input_bd_params)

    def input_bd_params(self, message) -> None:
        """
        Метод для ввода минимальных и максимальных цен и расстояний от центра
        города.

        :param message:
        :return:
        """
        try:
            self.__bd_params.append(float(message.text))
            self.logger_debug()
        except ValueError:
            self._bot.send_message(message.from_user.id,
                                   'Значение должно быть в цифрах.')
            return
        self._bot.send_message(message.from_user.id,
                               self.__bd_messages[self.__bd_index])
        self.__bd_index += 1
        if self.__bd_index < 4:
            self._bot.register_next_step_handler(message,
                                                 self.input_bd_params)
        else:
            self._bot.register_next_step_handler(message,
                                                 self.input_hotels_count)

    def find_hotels(self) -> List[dict]:
        """
        Метод. Возвращает список содержащий словари отелей.

        :rtype: List[dict]
        """
        url = "https://hotels4.p.rapidapi.com/properties/list"
        destination_id = self.get_destination_id()
        if not destination_id:
            return list()
        price_min = int(self.__bd_params[0])
        price_max = int(self.__bd_params[1])
        querystring: dict = {"destinationId": destination_id,
                             "pageNumber": "1",
                             "pageSize": "25",
                             "checkIn": self._check_in,
                             "checkOut": self._check_out,
                             "adults1": "1",
                             "priceMin": price_min,
                             "priceMax": price_max,
                             "sortOrder": "PRICE",
                             "locale": "ru_RU",
                             "currency": "USD",
                             "landmarkIds": "Центр города"}
        self._logger.debug('user id: {user_id} | hotels qs: '
                           '{hotels_qs}'.format(user_id=
                                                self._message.from_user.id,
                                                hotels_qs=querystring))
        results = self.json_deserialization(url=url,
                                            headers=self._headers,
                                            querystring=querystring)
        try:
            hotels = results["data"]["body"]["searchResults"]["results"]
        except BaseException:
            return list()
        req_hotels = [hotel for hotel in hotels
                      if self.in_range(hotel)][:self._hotels_count]
        return req_hotels

    def in_range(self, hotel: dict) -> bool:
        """
        Метод. Возвращает True, если отель находится в указанном диапозоне
        расстояний.

        :param hotel:
        :return:
        """
        dist_min = self.__bd_params[2]
        dist_max = self.__bd_params[3]
        distance_str = self.get_param(hotel, "landmarks", 0, "distance")
        try:
            distance = float(distance_str.split()[0])
        except ValueError:
            return False
        if dist_min <= distance <= dist_max:
            return True
