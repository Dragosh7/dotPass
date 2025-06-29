from customtkinter import CTkToplevel, CTkLabel, CTkProgressBar
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import threading
import requests
import time
from utils.secrets import SMSO_API_KEY, SMSO_SENDER_ID, GOOGLE_GEOLOCATION_API_KEY
from utils.style import APP_FONT


class PinSendingDialog:
    def __init__(self, parent, phone: str, pin: str, on_result):
        self.phone = phone
        self.pin = pin
        self.on_result = on_result

        self.dialog = CTkToplevel(parent)
        self.dialog.title("Sending PIN")
        self.dialog.geometry("360x180")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.focus_force()

        self.center_window(self.dialog)

        CTkLabel(self.dialog, text="📤 Sending recovery PIN...", font=("Helvetica", 16, "bold")).pack(pady=(20, 10))
        CTkLabel(self.dialog, text=f"To: {phone}", font=("Helvetica", 12)).pack(pady=(0, 10))

        try:
            self.progress = CTkProgressBar(self.dialog, orientation="horizontal", mode="indeterminate", width=220)
            self.progress.pack(pady=(10, 10))
            self.progress.start()
        except KeyError:
            self.progress = None
            CTkLabel(self.dialog, text="Loading...", font=APP_FONT, text_color="#999999").pack(pady=(20, 10))

        threading.Thread(target=self._send_sms_thread, daemon=True).start()

    def center_window(self, win):
        win.update_idletasks()
        w, h = 400, 520
        x = (win.winfo_screenwidth() // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

    def _send_sms_thread(self):
        url = "https://app.smso.ro/api/v1/send"
        headers = {"X-Authorization": SMSO_API_KEY}
        data = {
            "sender": SMSO_SENDER_ID,
            "to": self.phone,
            "body": f"Your dotPass recovery PIN is: {self.pin}"
        }

        print("\n=== DEBUG SMS PAYLOAD ===")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        print("=========================\n")
        success = True
        # try:
        #     response = requests.post(url, headers=headers, data=data)
        #     success = response.status_code == 200
        # except Exception as e:
        #     print(f"[dotPass] SMS error: {e}")
        #     success = False

        self.dialog.after(3500, lambda: self._finish(success))

    def _finish(self, success: bool):
        def safe_callback():
            self.on_result(success)

        self.dialog.destroy()
        self.dialog.after(100, safe_callback)

    # @staticmethod
    # def send_dummy_emergency_sms(phone: str) -> bool:
    #     if not phone or phone.strip() == "":
    #         return False
    #     try:
    #         # IP-API location
    #         ip_response = requests.get("http://ip-api.com/json/").json()
    #         if ip_response.get("status") != "success":
    #             raise Exception("IP-API failed")
    #
    #         ip_lat, ip_lon = ip_response["lat"], ip_response["lon"]
    #         ip_location_link = f"https://www.google.com/maps/search/?api=1&query={ip_lat},{ip_lon}"
    #
    #         # Google Geolocation API location
    #         google_url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_GEOLOCATION_API_KEY}"
    #         google_response = requests.post(google_url, json={}).json()
    #
    #         g_lat, g_lon = google_response["location"]["lat"], google_response["location"]["lng"]
    #         g_location_link = f"https://www.google.com/maps/search/?api=1&query={g_lat},{g_lon}"
    #
    #         # Compose full message
    #         body = (
    #             "Emergency mode activated.\n\n"
    #             f"My location (IP-API): {ip_location_link}\n"
    #             f"My location (Google): {g_location_link}"
    #         )
    #
    #         url = "https://app.smso.ro/api/v1/send"
    #         headers = {"X-Authorization": SMSO_API_KEY}
    #         data = {
    #             "sender": SMSO_SENDER_ID,
    #             "to": phone,
    #             "body": body
    #         }
    #
    #         print("\n=== EMERGENCY SMS DEBUG ===")
    #         print(f"TO:     {phone}")
    #         print(f"BODY:\n{body}")
    #         print("===========================\n")
    #
    #         # Trimite SMS dacă e activ
    #         # response = requests.post(url, headers=headers, data=data)
    #         # return response.status_code == 200
    #
    #         return True  # debug mode
    #
    #     except Exception as e:
    #         print(f"[dotPass - Emergency SMS] Failed to send alert: {e}")
    #         return False

    @staticmethod
    def send_dummy_emergency_sms(phone: str) -> bool:
        if not phone or phone.strip() == "":
            return False
        try:
            lat, lon = None, None

            # 1️⃣ Precizie maximă: headless Chrome + navigator.geolocation
            try:
                options = Options()
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-infobars")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--window-size=0,0")
                options.add_argument("--mute-audio")
                options.add_experimental_option("prefs", {
                    "profile.default_content_setting_values.geolocation": 1
                })

                driver = webdriver.Chrome(options=options)
                driver.get("file://" + os.path.abspath("utils/location/get_location.html"))
                time.sleep(2)
                js = """
                return new Promise(resolve => {
                    navigator.geolocation.getCurrentPosition(
                        pos => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude}),
                        err => resolve({error: err.message})
                    );
                });
                """
                location = driver.execute_script(js)
                driver.quit()

                if "lat" in location and "lon" in location:
                    lat, lon = location["lat"], location["lon"]
                    print("[Geolocation] Found via headless browser.")
            except Exception as e:
                print(f"[Geolocation] Headless failed: {e}")

            # 2️⃣ Alternativ: Google Geolocation API
            if lat is None and lon is None:
                try:
                    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_GEOLOCATION_API_KEY}"
                    g_response = requests.post(url, json={}, timeout=3).json()
                    if "location" in g_response:
                        lat = g_response["location"]["lat"]
                        lon = g_response["location"]["lng"]
                        print("[Geolocation] Found via Google API.")
                except Exception as e:
                    print(f"[Geolocation] Google API failed: {e}")

            # 3️⃣ Fallback: IP-API
            if lat is None and lon is None:
                try:
                    ip_data = requests.get("http://ip-api.com/json/", timeout=2).json()
                    if ip_data.get("status") == "success":
                        lat, lon = ip_data["lat"], ip_data["lon"]
                        print("[Geolocation] Found via IP-API.")
                except Exception as e:
                    print(f"[Geolocation] IP-API failed: {e}")

            if lat is None or lon is None:
                raise Exception("All location methods failed.")

            location_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            body = (
                "Help, it's an Emergency.\n\n"
                f"My location: {location_link}"
            )

            url = "https://app.smso.ro/api/v1/send"
            headers = {"X-Authorization": SMSO_API_KEY}
            data = {
                "sender": SMSO_SENDER_ID,
                "to": phone,
                "body": body
            }

            print("\n=== EMERGENCY SMS DEBUG ===")
            print(f"TO:     {phone}")
            print(f"BODY:\n{body}")
            print("===========================\n")

            # Debug only
            return True

            # Real sending (decomentează pentru producție):
            # resp = requests.post(url, headers=headers, data=data)
            # return resp.status_code == 200

        except Exception as e:
            print(f"[dotPass - Emergency SMS] Failed to send alert: {e}")
            return False

    @staticmethod
    def send_sms_direct(phone: str, pin: str) -> bool:
        url = "https://app.smso.ro/api/v1/send"
        headers = {"X-Authorization": SMSO_API_KEY}
        data = {
            "sender": SMSO_SENDER_ID,
            "to": phone,
            "body": f"Your dotPass recovery PIN is: {pin}"
        }

        print("\n=== DEBUG SMS PAYLOAD ===")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        print("=========================\n")

        # try:
        #     response = requests.post(url, headers=headers, data=data)
        #     return response.status_code == 200
        # except Exception as e:
        #     print(f"[dotPass - send_sms_direct] Error: {e}")
        #     return False
        return True