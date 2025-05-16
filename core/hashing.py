import hashlib, os

def generate_salt() -> bytes:
    return os.urandom(16)

def hash_password(password: str, salt: bytes) -> str:
    return hashlib.sha256(password.encode() + salt).hexdigest()