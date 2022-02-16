from query import Query


class BestDeal(Query):
    def __init__(self, bot, message, sort_order: str) -> None:
        self.__bd_params = list()
        super().__init__(bot, message, sort_order)

    def input_city(self, message) -> None:
        """
        Метод для ввода города

        :param message: сообщение
        :return:
        """
        self.__city = message.text
        self.__bot.send_message(message.from_user.id,
                                'Сколько отелей нужно отобразить в '
                                'сообщении? (не больше 25)')
        self.__bot.register_next_step_handler(message,
                                              self.input_hotels_count)
