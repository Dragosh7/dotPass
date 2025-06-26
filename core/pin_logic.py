import random
import json
import datetime
from utils.config import PROFILE_PATH

class PinLogic:
    def __init__(self):
        self.pin = None

    def generate_pin(self):
        self.pin = str(random.randint(100000, 999999))
        return self.pin

def should_remind_pin():
    try:
        with open(PROFILE_PATH, "r") as f:
            profile = json.load(f)

        if not profile.get("pin_sent", False):
            return True

        last_reminder = profile.get("reminder")
        if not last_reminder:
            return True

        last_dt = datetime.datetime.fromisoformat(last_reminder)
        return (datetime.datetime.now() - last_dt).days >= 7

    except Exception as e:
        # print(f"[dotPass] Failed to check pin reminder: {e}")
        return False