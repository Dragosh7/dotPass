from cryptography.fernet import Fernet

def encrypt_data(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)

def decrypt_data(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)