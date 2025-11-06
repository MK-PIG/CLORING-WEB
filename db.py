import sqlite3 as sq
from logger import (info_logger, er_logger)

"""
добавить в функции return bool после execute
"""


class DateBase:
    def __init__(self, db_path="./datebase.db") -> None:
        self.db_path = db_path

    def __repr__(self) -> str:
        return 'Class DateBase'

    # Возможно стоит возвращать True при успехе, False при исключении?
    def create_users_table(self) -> None:
        """
        Создает таблицу users с ниже указаннами полями, если она не сущ, иначе ничего не делает
        """
        with sq.connect(self.db_path) as con:
            cursor = con.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL,
                            phone_number TEXT NULL )""")
            info_logger.info(
                "The table has been created. Columns: user_id, email? password, phone_number")

    def select(self, fields: str, table_name: str, where: str = '') -> list[tuple]:
        """Делает выборку полей fields из таблицы table_name с доп условием где where

        Args:
            fields (str): поля для выборки
            table_name (str): имя таблицы
            where (str, optional): условие выбора полей если сущ. Defaults to ''.

        Returns:
            list: список кортежей значений (но это не точно)
        """
        with sq.connect(self.db_path) as con:
            cursor = con.cursor()
            if where:
                request = f'SELECT {fields} from {table_name} WHERE {where}'
                cursor.execute(request)
                info_logger.info(
                    f"Request completed: SELECT {fields} from {table_name} WHERE {where}")
            else:
                request = f'SELECT {fields} from {table_name}'
                cursor.execute(request)
                info_logger.info(
                    f"Request completed: SELECT {fields} from {table_name}")

            return cursor.fetchall()

    def insert(self, table_name: str, fields: str, values: str) -> bool:
        """Вставляет запись в таблицу

        Args:
            table_name (str): имя таблицы
            fields (str): поля таблицы
            values (str): значения полей
        """
        with sq.connect(self.db_path) as con:
            cursor = con.cursor()
            request = f'INSERT INTO {table_name} ({fields}) VALUES({values})'
            cursor.execute(request)
            info_logger.info(
                f"Insertation is succesfull: INSERT INTO {table_name} ({fields}) VALUES({values})")
        return True

    def update_table(self, table_name: str, fields: list, new_values: list, condition: str = '') -> bool:
        try:
            with sq.connect(self.db_path) as con:
                cursor = con.cursor()
                request = f'UPDATE {table_name} SET '
                for field, value in zip(fields, new_values):
                    request += f'{field}={value},'
                request = request[:-1]
                if condition:
                    request += f' WHERE {condition}'
                cursor.execute(request)
                info_logger.info(f"Table has been updated. Request: {request}")
                return True
        except Exception:
            er_logger.error(
                f"Some error with table updation. Request: {request}")
            return False

    def create_table_users_items(self):
        """
        Создает таблицу users_items с ниже указаннами полями, если она не сущ, иначе ничего не делает
        """
        with sq.connect(self.db_path) as con:
            cursor = con.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users_items (
                            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            clothes_name TEXT NOT NULL,
                            clothes_category TEXT NOT NUll,
                            clothes_size TEXT NOT NULL,
                            clothes_condition TEXT NOT NULL,
                            clothes_brand TEXT,
                            clothes_material TEXT,
                            clothes_color TEXT,
                            clothes_description TEXT,
                            clothes_link_to_photo TEXT,
                           FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE)""")
            info_logger.info("The table 'user_items' has been succesfully created. Columns: item_id, user_id,\n"
                             "clothes_name, clothes_category, clothes_size, clothes_condition,\n"
                             "clothes_brand, clothes_material, clothes_color, clothes_description, clothes_link_to_photo")


if __name__ == '__main__':
    base = DateBase()
    base.create_users_table()
    base.insert('users', 'email, password', '"some@com.ru", "lala"')
    base.update_table('users', ['email', 'phone_number'], [
                      '"2904yr@mail.ru"', '"8-985-697-02-47"'], '"email"="some@com.ru"')
