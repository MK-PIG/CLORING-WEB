import hashlib


def hash_password(password: str):
    password = hashlib.sha3_512(password.encode('utf-8')).hexdigest()
    return password


def verfy_password(password: str, hashed_password: bytes) -> bool:
    if hash_password(password) == hashed_password:
        return True
    return False
