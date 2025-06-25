import requests
from utils.secrets import SMSO_API_KEY, SMSO_SENDER_ID

def send_dummy_emergency_sms(phone: str) -> bool:
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()

        if data["status"] != "success":
            raise Exception("Could not determine location")

        lat, lon = data["lat"], data["lon"]
        location_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        body = f"Help! I am in trouble. My location: {location_link}"

        url = "https://app.smso.ro/api/v1/send"
        headers = {"X-Authorization": SMSO_API_KEY}
        sms_data = {
            "sender": SMSO_SENDER_ID,
            "to": phone,
            "body": body
        }

        print("\n=== EMERGENCY SMS DEBUG ===")
        print(f"TO:     {phone}")
        print(f"BODY:   {body}")
        print(f"URL:    {url}")
        print(f"HEADERS:{headers}")
        print("===========================\n")

        # Doar debug, fără trimitere reală
        return True

        # Dacă vrei să testezi cu trimitere reală:
        # resp = requests.post(url, headers=headers, data=sms_data)
        # return resp.status_code == 200

    except Exception as e:
        print(f"[dotPass - Emergency SMS] Failed to send alert: {e}")
        return False


# ✅ Acesta este testul real detectat de pytest
def test_send_dummy_emergency_sms():
    phone = "+40700000000"  # înlocuiește cu ceva valid de test (nu va fi trimis)
    result = send_dummy_emergency_sms(phone)
    assert result == True
