import os
import sqlite3
from core.encryption import encrypt_data, decrypt_data

VAULT_PATH = "data/vault.db"

def init_vault_database(conn):
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """)

def load_or_create_vault(key: bytes) -> sqlite3.Connection:
    if not os.path.exists(VAULT_PATH):
        # create and encrypt new database
        conn = sqlite3.connect(":memory:")
        init_vault_database(conn)

        with open(VAULT_PATH, "wb") as f:
            f.write(encrypt_data(export_db(conn), key))
        return conn
    else:
        with open(VAULT_PATH, "rb") as f:
            decrypted = decrypt_data(f.read(), key)
            conn = sqlite3.connect(":memory:")
            conn.executescript(decrypted.decode())
            return conn

def export_db(conn: sqlite3.Connection) -> bytes:
    # Export SQLite memory db as SQL string
    with conn:
        dump = "\n".join(conn.iterdump()).encode()
        return dump

def save_vault(conn: sqlite3.Connection, key: bytes):
    with open(VAULT_PATH, "wb") as f:
        f.write(encrypt_data(export_db(conn), key))
