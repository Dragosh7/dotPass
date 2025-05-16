from core.encryption import encrypt_data, decrypt_data
from cryptography.fernet import Fernet

def test_encryption_cycle():
    key = Fernet.generate_key()
    original = b"secret"
    encrypted = encrypt_data(original, key)
    decrypted = decrypt_data(encrypted, key)
    assert original == decrypted