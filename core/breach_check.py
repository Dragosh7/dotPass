import hashlib
import requests
from utils.check_internet import has_internet

def check_password_breach(password: str) -> int:

    if not has_internet():
        return -1

    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    headers = {
        "Add-Padding": "true"
    }

    try:
        res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", headers=headers, timeout=10)
        if res.status_code != 200:
            # print("HIBP error:", res.status_code)
            return -1

        hashes = (line.split(":") for line in res.text.splitlines())
        for hash_suffix, count in hashes:
            if hash_suffix == suffix:
                return int(count)

        return 0
    except Exception as e:
        # print("Error checking password breach:", e)
        return -1
