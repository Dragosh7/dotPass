# utils/salt_manager.py
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

ENC_SALT_PATH = os.path.join(os.getenv("APPDATA"), "dotPass", "salt.enc")

def encrypt_salt_with_pin(salt: bytes, pin: str) -> bytes:
    key = PBKDF2(pin, b"dotpass-salt", dkLen=32, count=100_000)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(salt)
    return cipher.nonce + tag + ciphertext

def decrypt_salt_with_pin(enc_data: bytes, pin: str) -> bytes:
    key = PBKDF2(pin, b"dotpass-salt", dkLen=32, count=100_000)
    nonce = enc_data[:16]
    tag = enc_data[16:32]
    ciphertext = enc_data[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def save_encrypted_salt(salt: bytes, pin: str):
    enc = encrypt_salt_with_pin(salt, pin)
    with open(ENC_SALT_PATH, "wb") as f:
        f.write(enc)

def load_encrypted_salt(pin: str) -> bytes:
    with open(ENC_SALT_PATH, "rb") as f:
        data = f.read()
    return decrypt_salt_with_pin(data, pin)
