import hashlib
import os

from core.salt_manager import save_encrypted_salt
from utils.setup import protect_file

def get_or_create_salt(path="data/salt.bin", pin: str = None) -> bytes:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        salt = os.urandom(16)
        with open(path, 'wb') as f:
            f.write(salt)
            protect_file(path)

        if pin:
            try:
                save_encrypted_salt(salt, pin)
            except Exception as e:
                print(f"[dotPass] Failed to save encrypted salt: {e}")

    else:
        with open(path, 'rb') as f:
            salt = f.read()
    return salt

def hash_password(password: str, salt: bytes) -> str:
    return hashlib.sha256(password.encode() + salt).hexdigest()
