import sqlite3


def history(bot, user_id: int) -> None:
    """
    Фкнкция. Ищет команды, введенные пользователем, в базе данных и шлет
    пользователю историю поиска.

    :param bot:
    :param user_id:
    :return:
    """
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    conn.commit()
    commands = cursor.execute("SELECT id, command_name, city, datetime FROM "
                              "commands WHERE user_id = {}".format(user_id))
    empty = True
    for command in commands:
        empty = False
        answer = get_hotels(command)
        bot.send_message(user_id, answer)
    if empty:
        bot.send_message(user_id, 'Вы еще не сделали ни одного запроса.')


def get_hotels(command: tuple) -> str:
    """
    Функция. Возврает сообщение, содержашее команду, введенную пользователем,
    и найденные отели.

    :param command:
    :return answer:
    """
    command_id = command[0]
    command_str = ' | '.join(command[1:])
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    conn.commit()
    hotels = cursor.execute("SELECT hotel_name FROM hotels "
                            "WHERE command_id = {}".format(command_id))
    hotels_str = '\n\t - '.join(hotel[0] for hotel in hotels)
    answer = "{command_str}\nНайденные отели:\n\t - {hotels_str}".format(
        command_str=command_str, hotels_str=hotels_str)
    return answer
