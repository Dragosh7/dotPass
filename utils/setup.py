import os
import ctypes
from utils.config import MASTER_HASH_PATH, DB_PATH, SALT_PATH, PROFILE_PATH

def profile_exists():
    return os.path.exists(MASTER_HASH_PATH) and os.path.exists(SALT_PATH)

def check_integrity():
    if not os.path.exists(PROFILE_PATH):
        if os.path.exists(MASTER_HASH_PATH) or os.path.exists(SALT_PATH):
            return "create_profile_only"
        else:
            return "new_install"

    missing = []
    if not os.path.exists(SALT_PATH):
        missing.append("salt.bin")

    warn_only = []
    if not os.path.exists(MASTER_HASH_PATH):
        warn_only.append("master.hash")

    if missing:
        return f"missing:{','.join(missing)}"

    if warn_only:
        return f"warn:{','.join(warn_only)}"

    return "ok"

def protect_file(path):
    if os.name == 'nt':
        os.chmod(path, 0o444)
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x02 | 0x01)  # hidden + readonly
