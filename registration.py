from db import DateBase


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
            if em == email and psw == password:
                return True
            if em == email:
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
            base.insert('users', 'email, password',
                        f'"{email}", "{password}"')
            return True
        except Exception:  # нужно постараться конкретизировать ошибки, чтобы их качественно обрабатывать
            return False
