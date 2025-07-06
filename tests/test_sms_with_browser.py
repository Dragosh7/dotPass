import requests
import time

from utils.secrets import SMSO_API_KEY, SMSO_SENDER_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_precise_location():
    try:
        options = Options()
        options.headless = True
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1
        })

        driver = webdriver.Chrome(options=options)
        driver.get("https://my-location.org/")  # sau o pagină goală locală

        script = """
        return new Promise(resolve => {
            navigator.geolocation.getCurrentPosition(pos => {
                resolve({lat: pos.coords.latitude, lon: pos.coords.longitude});
            }, err => {
                resolve({error: err.message});
            });
        });
        """
        location = driver.execute_script(script)
        driver.quit()

        if 'error' in location:
            raise Exception(location['error'])

        return location['lat'], location['lon']

    except Exception as e:
        print(f"[dotPass - Geolocation] Failed to retrieve location: {e}")
        return None, None

def send_dummy_emergency_sms(phone: str) -> bool:
    try:
        lat, lon = get_precise_location()
        if lat is None or lon is None:
            raise Exception("Could not get precise location")

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

        return True
        # Dacă vrei să testezi cu trimitere reală:
        # resp = requests.post(url, headers=headers, data=sms_data)
        # return resp.status_code == 200

    except Exception as e:
        print(f"[dotPass - Emergency SMS] Failed to send alert: {e}")
        return False

def test_precise_location():
    phone = "+40700000000"
    result = send_dummy_emergency_sms(phone)
    assert result == True
