import datetime
import sqlite3


def create_tables(user_id: int,
                  user_name: str,
                  user_surname: str,
                  username: str) -> None:
    """
    Функция. Создает таблицй и вносит данные пользователя в базу данных.
    """
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                       id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       user_id INT UNIQUE NOT NULL,
                       user_name TEXT NOT NULL,
                       user_surname TEXT,
                       username STRING);""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS calendars(
                       id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       user_id INT NOT NULL,
                       FOREIGN KEY (user_id) REFERENCES users(user_id));""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS commands(
                       id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       user_id INT NOT NULL,
                       city TEXT NOT NULL,
                       command_name TEXT NOT NULL,
                       datetime DATETIME NOT NULL,
                       FOREIGN KEY (user_id) REFERENCES users(user_id));""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS hotels(
                       id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       command_id NOT NULL,
                       hotel_name TEXT,
                       FOREIGN KEY (command_id) REFERENCES 
                       users(command_id));""")
        cursor.execute('INSERT INTO users (user_id, user_name, '
                       'user_surname, username) VALUES (?, ?, ?, ?)',
                       (user_id, user_name, user_surname, username))
    except sqlite3.Error:
        pass
    conn.commit()


def db_commands_val(user_id: int,
                    command_name: str,
                    city: str,
                    time: datetime.datetime) -> None:
    """ Функция. Вносит данные запроса пользователя в базу данных. """
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO commands (user_id, command_name, city,'
                       'datetime) VALUES (?, ?, ?, ?)',
                       (user_id, command_name, city, time))
    except sqlite3.Error:
        pass
    conn.commit()


def db_hotels_val(command_id: int, hotel_name: str) -> None:
    """
    Функция. Вносит данные отеля, найденного пользователем, в базу данных.
    """
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO hotels (command_id, hotel_name) '
                       'VALUES (?, ?)',
                       (command_id, hotel_name))
    except sqlite3.Error:
        pass
    conn.commit()


def db_calendar_val(user_id: int) -> None:
    """ Функция. Вносит данные календаря в базу данных. """
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO calendars (user_id) VALUES (?)',
                       (user_id,))
    except sqlite3.Error:
        pass
    conn.commit()
