import hashlib


def hash_password(password: str):
    """превращает строковое представление пароля в байтовый хэш

    Args:
        password (str): пароль пользователя

    Returns:
        _type_: байтовое предстваление пароля
    """
    password = hashlib.sha3_512(password.encode('utf-8')).hexdigest()
    return password


def verfy_password(password: str, hashed_password: bytes) -> bool:
    """проверяет является ли пароль, введенный пользователем верным по сравнению с хэшем

    Args:
        password (str): пароль 
        hashed_password (bytes): захэшенный пароль

    Returns:
        bool: True если пароли совпадают, False иначе
    """
    if hash_password(password) == hashed_password:
        return True
    return False
