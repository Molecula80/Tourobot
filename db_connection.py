import datetime
import sqlite3


def db_users_val(user_id: int,
                 user_name: str,
                 user_surname: str,
                 username: str) -> None:
    """ Функция. Вносит данные пользователя в базу данных. """
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (user_id, user_name, '
                       'user_surname, username) VALUES (?, ?, ?, ?)',
                       (user_id, user_name, user_surname, username))
    except sqlite3.Error:
        pass
    conn.commit()


def db_commands_val(user_id: int,
                    command_name: str,
                    time: datetime.datetime) -> None:
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO commands (user_id, command_name, '
                       'datetime) VALUES (?, ?, ?)',
                       (user_id, command_name, time))
    except sqlite3.Error:
        pass
    conn.commit()


def db_hotels_val(command_id: int, hotel_name: str) -> None:
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO hotels (command_id, hotel_name) '
                       'VALUES (?, ?)',
                       (command_id, hotel_name))
    except sqlite3.Error:
        pass
    conn.commit()
