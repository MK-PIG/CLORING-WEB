import re


class Validator:

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return 'Validator class'

    def check_phone_number_correction(self, phone_number: str | None) -> bool:
        """Проверяет корректность номера телефона пользователя

        Args:
            phone_number (str): номер телефона

        Returns:
            bool: Возващает True если номер корректен, False в ином случае
        """
        if not phone_number:
            return False

        # Очищаем номер от пробелов, скобок, дефисов
        cleaned = re.sub(r'[\s\(\)\-+]', '', phone_number)

        # Проверяем основные форматы российских номеров
        patterns = [
            r'^7\d{10}$',      # 79123456789
            r'^8\d{10}$',      # 89123456789
            r'^\+7\d{10}$',    # +79123456789
            r'^\d{10}$'        # 9123456789 (без кода страны)
        ]

        return any(re.match(pattern, cleaned) for pattern in patterns)

    def check_correction_email(self, email: str | None) -> bool:  # type: ignore
        """Проверяет корректнсоть эл почты

        Args:
            email (str): эл почта

        Returns:
            bool: Возващает True если email корректен, False в ином случае
        """
        # Возможно стоит выкидывать исключение, чтобы далее его обабатывать и показывать комментарий исключения пользователю в форме?
        if not email:
            return False
        if len(email) < 4 or len(email) > 254:
            return False
        if '@' not in email or '.' not in email or email.count('.') > 1 or ' ' in email or email.count('@') > 1:
            return False
        local_part, domain = email.split('@')
        if len(local_part) > 64 or len(domain) > 254:
            return False

        return True
