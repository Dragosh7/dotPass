from core.encryption import encrypt_data, decrypt_data, derive_key
from core.hashing import get_or_create_salt
from utils.config import DB_PATH, SALT_PATH
import os
import json

def test_add_account_to_vault():
    salt = get_or_create_salt(SALT_PATH)
    key = derive_key("testpassword", salt)

    accounts = []

    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'rb') as f:
            encrypted = f.read()
        try:
            decrypted_data = decrypt_data(encrypted, key).decode()
            accounts = json.loads(decrypted_data)["accounts"]
        except Exception as e:
            print("Eroare la decriptare:", e)
            assert False, "Vault corupt sau parola gresita"

    new_account = {
        "site": "newsite.com",
        "username": "newuser",
        "password": "newpass321"
    }
    accounts.append(new_account)

    updated_data = json.dumps({"accounts": accounts}).encode()
    encrypted = encrypt_data(updated_data, key)
    with open(DB_PATH, 'wb') as f:
        f.write(encrypted)

    with open(DB_PATH, 'rb') as f:
        encrypted = f.read()
    decrypted = decrypt_data(encrypted, key).decode()
    parsed = json.loads(decrypted)

    print("Conturi curente în vault:", parsed)

    assert parsed["accounts"][-1]["site"] == "newsite.com"
    assert parsed["accounts"][-1]["username"] == "newuser"
    assert parsed["accounts"][-1]["password"] == "newpass321"
