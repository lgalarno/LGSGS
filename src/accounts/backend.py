from django.conf import settings
from cryptography.fernet import Fernet


FERNET_KEY = settings.FERNET_KEY
key = bytes(FERNET_KEY, "utf-8")


def encrypt(password):
    if password and FERNET_KEY:
        cipher_obj = Fernet(key)
        encrypted = cipher_obj.encrypt(bytes(password, "utf-8"))
        return encrypted.decode("utf-8")
    else:
        return False


def decrypt(password):
    if password and FERNET_KEY:
        cipher_obj = Fernet(key)
        decrypted_str = cipher_obj.decrypt(password)
        result = decrypted_str.decode("unicode_escape")
        return result
    else:
        return False
