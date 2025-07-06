import string
import secrets

def generate_password(length=16):
    if length < 12:
        raise ValueError("Password length must be at least 12 characters.")

    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))
