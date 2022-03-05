import sqlite3


def history(bot, user_id):
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    conn.commit()
    commands = cursor.execute("SELECT id, command_name, city, datetime FROM "
                              "commands WHERE user_id = {}".format(user_id))
    for command in commands:
        answer = get_hotels(command)
        bot.send_message(user_id, answer)


def get_hotels(command):
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
