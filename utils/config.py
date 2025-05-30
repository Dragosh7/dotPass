import os

APPDATA_PATH = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~/.dotPass"), "dotPass")
os.makedirs(APPDATA_PATH, exist_ok=True)

SALT_PATH = os.path.join(APPDATA_PATH, "salt.bin")
MASTER_HASH_PATH = os.path.join(APPDATA_PATH, "master.hash")
DUMMY_HASH_PATH = os.path.join(APPDATA_PATH, "dummy.hash")
PROFILE_PATH = os.path.join(APPDATA_PATH, "profile.json")
DB_PATH = os.path.join(APPDATA_PATH, "vault.db")
DUMMY_PATH = os.path.join(APPDATA_PATH, "dummy.db")
