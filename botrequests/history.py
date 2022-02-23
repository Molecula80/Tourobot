import sqlite3


def history(user_id):
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    commands = cursor.execute("SELECT id, command_name, datetime FROM "
                              "commands WHERE user_id = {}".format(user_id))
    for command in commands:
        get_hotels(command)


def get_hotels(command):
    print(command)
    command_id = command[0]
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    hotels = cursor.execute("SELECT hotel_name FROM hotels "
                            "WHERE command_id = {}".format(command_id))
    print(list(hotels))
