import re
from src.logger import (info_logger, er_logger)


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
            er_logger.error(f"{phone_number} does not exist")
            return False
        for ch in '-!@#$%^&*!"№;:?':
            if ch in phone_number:
                return False

        cleaned = re.sub(r'[\s\(\)\-+]', '', phone_number)

        patterns = [
            r'^7\d{10}$',      # 79123456789
            r'^8\d{10}$',      # 89123456789
            r'^\+7\d{10}$',    # +79123456789
            r'^\d{10}$'        # 9123456789
        ]
        # Где ты выкидываешь ошибку, если неверный номер звонилки?
        info_logger.info(f"{phone_number} is correct")
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
            er_logger.error(f"Incorrect format of email: {email}")
            return False

        for ch in " !#$%&~=,'":
            if ch in email:
                return False

        if len(email) < 4 or len(email) > 254:
            er_logger.error(f"Incorrect format of email: {email}")
            return False
        if '@' not in email or '.' not in email or email.count('.') > 1 or ' ' in email or email.count('@') > 1:
            er_logger.error(f"Incorrect format of email: {email}")
            return False
        local_part, domain = email.split('@')
        if len(local_part) > 64 or len(domain) > 254:
            er_logger.error(f"Incorrect format of email: {email}")
            return False

        info_logger.info(f"Email is correct: {email}")
        return True

    def check_clothes_name(self, clothes_name: str | None) -> bool:  # type: ignore
        """Проверяет корректность названия одежды

        Args:
            clothes_name (str): название одежды

        Returns:
            bool: Возвращает True если название корректно, False в ином случае
        """
        if not clothes_name:
            er_logger.error(
                f"Incorrect format of clothes_name: {clothes_name}")
            return False

        # Проверяем, что строка начинается с буквы и содержит только русские и латинские буквы,
        # пробелы (не в начале) и дефисы
        pattern = r'^[a-zA-Zа-яёА-ЯЁ][a-zA-Zа-яёА-ЯЁ\s\-]*$'
        if not re.match(pattern, clothes_name):
            er_logger.error(
                f"Incorrect format of clothes_name: {clothes_name}")
            return False

        info_logger.info(f"Clothes name is correct: {clothes_name}")
        return True

    def check_clothes_brand(self, clothes_brand: str | None) -> bool:  # type: ignore
        """Проверяет корректность бренда одежды

        Args:
            clothes_brand (str): бренд одежды

        Returns:
            bool: Возвращает True если бренд корректен, False в ином случае
        """
        if not clothes_brand:
            er_logger.error(
                f"Incorrect format of clothes_brand: {clothes_brand}")
            return False

        # Проверяем, что строка начинается с буквы и содержит только русские и латинские буквы,
        # пробелы (не в начале) и спец символы
        pattern = r'^[a-zA-Zа-яёА-ЯЁ][a-zA-Zа-яёА-ЯЁ\s\-\&*#$%&!~?+=]*$'
        if not re.match(pattern, clothes_brand):
            er_logger.error(
                f"Incorrect format of clothes_brand: {clothes_brand}")
            return False

        info_logger.info(f"Clothes brand is correct: {clothes_brand}")
        return True

    def check_clothes_material(self, clothes_material: str | None) -> bool:  # type: ignore
        """Проверяет корректность материала одежды

        Args:
            clothes_material (str): материал одежды

        Returns:
            bool: Возвращает True если материал корректен, False в ином случае
        """
        if not clothes_material:
            er_logger.error(
                f"Incorrect format of clothes_material: {clothes_material}")
            return False

        # Проверяем, что строка начинается с буквы и содержит только русские и латинские буквы,
        # пробелы (не в начале) и %
        pattern = r'^[a-zA-Zа-яёА-ЯЁ][a-zA-Zа-яёА-ЯЁ\s\%]*$'
        if not re.match(pattern, clothes_material):
            er_logger.error(
                f"Incorrect format of clothes_material: {clothes_material}")
            return False

        info_logger.info(f"Clothes material is correct: {clothes_material}")
        return True

    def check_clothes_color(self, clothes_color: str | None) -> bool:  # type: ignore
        """Проверяет корректность цвета одежды

        Args:
            clothes_color (str): цвет одежды

        Returns:
            bool: Возвращает True если цвет корректен, False в ином случае
        """
        if not clothes_color:
            er_logger.error(
                f"Incorrect format of clothes_color: {clothes_color}")
            return False

        # Проверяем, что строка начинается с буквы и содержит только русские и латинские буквы,
        # пробелы (не в начале) и дефисы
        pattern = r'^[a-zA-Zа-яёА-ЯЁ][a-zA-Zа-яёА-ЯЁ\s\-]*$'
        if not re.match(pattern, clothes_color):
            er_logger.error(
                f"Incorrect format of clothes_color: {clothes_color}")
            return False

        info_logger.info(f"Clothes color is correct: {clothes_color}")
        return True

    # type: ignore
    def check_clothes_description(self, clothes_description: str | None) -> bool:
        """Проверяет корректность описания одежды

        Args:
            clothes_description (str): описание одежды

        Returns:
            bool: Возвращает True если описание корректно, False в ином случае
        """
        if not clothes_description:
            er_logger.error(
                f"Incorrect format of clothes_description: {clothes_description}")
            return False

        # Проверяем, что строка начинается с буквы и содержит только русские и латинские буквы,
        # пробелы (не в начале) и дефисы
        pattern = r'^[a-zA-Zа-яёА-ЯЁ][a-zA-Zа-яёА-ЯЁ\s\-.]*$'
        if not re.match(pattern, clothes_description):
            er_logger.error(
                f"Incorrect format of clothes_description: {clothes_description}")
            return False

        info_logger.info(
            f"Clothes description is correct: {clothes_description}")
        return True
