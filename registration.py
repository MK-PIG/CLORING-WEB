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
        rows = base.select('email, password', 'users', f'email == "{email}"')
        if not rows:
            return False
        for em, psw in rows:
            if em == email and psw == password:
                return True
            if em == email and psw != password:
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

    def check_correction_email(self, email: str) -> bool:  # type: ignore
        """Проверяет корректнсоть эл почты
            Возващает True если email корректен, False в ином случае
        Args:
            email (str): 

        Returns:
            bool: 
        """
        # Возможно стоит выкидывать исключение, чтобы далее его обабатывать и показывать комментарий исключения пользователю в форме?
        if len(email) < 4 or len(email) > 254:
            return False
        if '@' not in email or '.' not in email or email.count('.') > 1 or ' ' in email or email.count('@') > 1:
            return False
        local_part, domain = email.split('@')
        if len(local_part) > 64 or len(domain) > 254:
            return False

        return True
