from cryptography.fernet import Fernet
import base64
import hashlib

def derive_key(password: str, salt: bytes) -> bytes:
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return base64.urlsafe_b64encode(hashed)

def encrypt_data(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)

def decrypt_data(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)
