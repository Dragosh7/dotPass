import hashlib
import os

def get_or_create_salt(path="data/salt.bin") -> bytes:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        salt = os.urandom(16)
        with open(path, 'wb') as f:
            f.write(salt)
    else:
        with open(path, 'rb') as f:
            salt = f.read()
    return salt

def hash_password(password: str, salt: bytes) -> str:
    return hashlib.sha256(password.encode() + salt).hexdigest()
