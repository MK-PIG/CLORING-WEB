from db import DateBase
from logger import info_logger, er_logger
from passwords import verfy_password, hash_password
base = DateBase()


class Registartor:

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "Class Registrator"

    def find_user(self, email: str, password: str) -> bool:  # type: ignore
        """Находит пользователя в БД. Возвращает True если пользователь найден, False иначе

        Args:
            email (str): электронная почта пользователя
            password (str): пароль пользователя

        Raises:
            ValueError: если такой пользователя уже есть в БД, то создаем исключение, которое нужно бы обрабатывать

        Returns:
            bool: 
        """
        # если пользователь вводит верный пароль и email то его можно просто авторизовывать
        rows = base.select('email, password', 'users', f'email == "{email}"')
        if not rows:
            return False
        for em, psw in rows:
            if em == email and verfy_password(password, psw):
                info_logger.info(f"User has been found. Email: {email}")
                return True
            if em == email:
                er_logger.error(f"User with email: {email} already exist")
                raise ValueError("Пользователь с таким email уже существует")

    def reg(self, email: str, password: str) -> bool:  # type: ignore
        """Функция, нужная для регистрации пользователя в БД. Если возникает ошибка, то возвращаем False

        Args:
            email (str): 
            password (str): 

        Returns:
            bool: 
        """
        try:
            password = hash_password(password)
            base.insert('users', 'email, password',
                        f'"{email}", "{password}"')
            info_logger.info(f"Successfully registration. Email: {email}")
            return True
        except Exception:  # нужно постараться конкретизировать ошибки, чтобы их качественно обрабатывать
            er_logger.error(f"Some error with registration. Email: {email}")
            return False
