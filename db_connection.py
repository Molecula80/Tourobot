import sqlite3


def db_table_val(user_id: int,
                 user_name: str,
                 user_surname: str,
                 username: str) -> None:
    """ Функция. Вносит данные пользователя в базу данных. """
    conn = sqlite3.connect('tourobot.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id, user_name, '
                   'user_surname, username) VALUES (?, ?, ?, ?)',
                   (user_id, user_name, user_surname, username))
    conn.commit()
