# utils/salt_manager.py
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

ENC_SALT_PATH = os.path.join(os.getenv("APPDATA"), "dotPass", "salt.enc")

def derive_key(pin: str, length: int = 32) -> bytes:
    """Derivează o cheie criptografică dintr-un PIN cu PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=b"dotpass-salt",  # salt fix pentru derivarea cheii din PIN
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(pin.encode())


def encrypt_salt_with_pin(salt: bytes, pin: str) -> bytes:
    key = derive_key(pin)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # AES-GCM recomanda nonce de 96 biti (12 bytes)
    ciphertext = aesgcm.encrypt(nonce, salt, associated_data=None)
    return nonce + ciphertext


def decrypt_salt_with_pin(enc_data: bytes, pin: str) -> bytes:
    key = derive_key(pin)
    nonce = enc_data[:12]
    ciphertext = enc_data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None)


def save_encrypted_salt(salt: bytes, pin: str):
    enc = encrypt_salt_with_pin(salt, pin)
    with open(ENC_SALT_PATH, "wb") as f:
        f.write(enc)


def load_encrypted_salt(pin: str) -> bytes:
    with open(ENC_SALT_PATH, "rb") as f:
        data = f.read()
    return decrypt_salt_with_pin(data, pin)

# def encrypt_salt_with_pin(salt: bytes, pin: str) -> bytes:
#     key = PBKDF2(pin, b"dotpass-salt", dkLen=32, count=100_000)
#     cipher = AES.new(key, AES.MODE_GCM)
#     ciphertext, tag = cipher.encrypt_and_digest(salt)
#     return cipher.nonce + tag + ciphertext
#
# def decrypt_salt_with_pin(enc_data: bytes, pin: str) -> bytes:
#     key = PBKDF2(pin, b"dotpass-salt", dkLen=32, count=100_000)
#     nonce = enc_data[:16]
#     tag = enc_data[16:32]
#     ciphertext = enc_data[32:]
#     cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
#     return cipher.decrypt_and_verify(ciphertext, tag)
#
# def save_encrypted_salt(salt: bytes, pin: str):
#     enc = encrypt_salt_with_pin(salt, pin)
#     with open(ENC_SALT_PATH, "wb") as f:
#         f.write(enc)
#
# def load_encrypted_salt(pin: str) -> bytes:
#     with open(ENC_SALT_PATH, "rb") as f:
#         data = f.read()
#     return decrypt_salt_with_pin(data, pin)
