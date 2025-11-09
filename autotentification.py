from db import DateBase
from logger import (info_logger, er_logger)

base = DateBase()


class Autotentificator:
    def __init__(self):
        pass

    def __repr__(self):
        return f'Class Autotentificator'

    def find_user(self, email: str, password: str) -> bool:  # type: ignore
        """Находит пользователя в БД. Возвращает True если пользователь найден, False иначе

        Args:
            email (str): электронная почта пользователя
            password (str): пароль пользователя

        Raises:
            ValueError: если пользователь ввел неверный пароль, то создается исключение и пользователь получает информацию о неверно 
            введенных данных

        Returns:
            bool: 
        """
        rows = base.select('email, password', 'users', f'email == "{email}"')
        if not rows:
            return False  # Тут тоже должено быть логирование, но я не выкупаю, что происходит))
        for em, psw in rows:
            if em == email and psw == password:
                info_logger.info(f"User is found. Email: {email}")
                return True
            if em == email and psw != password:
                er_logger.error(f"Incorrect input data. Input email: {email}")
                raise ValueError("Неверно введены входные данные")


if __name__ == '__main__':
    pass
