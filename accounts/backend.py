from django.conf import settings
from cryptography.fernet import Fernet


FERNET_KEY = settings.FERNET_KEY
key = bytes(FERNET_KEY, "utf-8")


def encrypt_password(password):
    if password and FERNET_KEY:
        cipher_obj = Fernet(key)
        return cipher_obj.encrypt(bytes(password, "utf-8"))
    else:
        return False


def decrypt_password(password):
    if password and FERNET_KEY:
        cipher_obj = Fernet(key)
        decoded_str = cipher_obj.decrypt(password)
        return decoded_str.decode("utf-8")
    else:
        return False
