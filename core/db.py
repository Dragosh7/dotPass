import os
import sqlite3
from core.encryption import encrypt_data, decrypt_data

def init_vault_database(conn: sqlite3.Connection):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """)

def export_db(conn: sqlite3.Connection) -> bytes:
    with conn:
        dump = "\n".join(conn.iterdump()).encode()
        return dump

def save_vault(conn: sqlite3.Connection, key: bytes, path: str):
    if os.path.exists(path):
        os.chmod(path, 0o600)

    with open(path, "wb") as f:
        f.write(encrypt_data(export_db(conn), key))

def load_or_create_vault(key: bytes, path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")

    if not os.path.exists(path):
        init_vault_database(conn)
        with open(path, "wb") as f:
            f.write(encrypt_data(export_db(conn), key))
        return conn

    try:
        with open(path, "rb") as f:
            decrypted_sql = decrypt_data(f.read(), key).decode()
            conn.executescript(decrypted_sql)
            return conn
    except Exception as e:
        raise Exception(f"Failed to load vault from {path}: {str(e)}")
