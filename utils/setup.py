import os
from utils.config import MASTER_HASH_PATH, DB_PATH, SALT_PATH

def profile_exists():
    return os.path.exists(MASTER_HASH_PATH) and os.path.exists(SALT_PATH)
