import os
import ctypes
from utils.config import MASTER_HASH_PATH, DB_PATH, SALT_PATH

def profile_exists():
    return os.path.exists(MASTER_HASH_PATH) and os.path.exists(SALT_PATH)


def protect_file(path):
    if os.name == 'nt':
        os.chmod(path, 0o444)
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x02 | 0x01)  # hidden + readonly
