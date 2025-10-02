import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

SPACETRACK_USERNAME = os.getenv("SPACETRACK_USERNAME")
SPACETRACK_PASSWORD = os.getenv("SPACETRACK_PASSWORD")
BASE_URL = "https://www.space-track.org"
LOGIN_URL = f"{BASE_URL}/ajaxauth/login"
CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', 'cache', 'debris_data.json')

query_url = (
    f"{BASE_URL}/basicspacedata/query/class/gp/OBJECT_TYPE/DEBRIS/"
    "DECAY_DATE/null-val/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID%20asc/"
    "format/json/predicates/OBJECT_NAME,NORAD_CAT_ID,TLE_LINE1,TLE_LINE2"
)

def fetch_and_cache_debris_data():
    """Logs into Space-Track.org, fetches debris data, and saves it to a local cache file."""
    if not SPACETRACK_USERNAME or not SPACETRACK_PASSWORD:
        print("Error: Space-Track credentials not found.")
        return

    with requests.Session() as session:
        print("Logging into Space-Track.org...")
        login_data = {"identity": SPACETRACK_USERNAME, "password": SPACETRACK_PASSWORD}
        
        try:
            resp = session.post(LOGIN_URL, data=login_data)
            resp.raise_for_status()
            if not resp.ok or resp.status_code != 200:
                print(f"Login failed. Response: {resp.text}")
                return

            print("Login successful. Fetching debris data...")
            resp = session.get(query_url)
            resp.raise_for_status()
            data = resp.json()
            
            print(f"Successfully fetched data for {len(data)} debris objects.")
            
            os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
            with open(CACHE_PATH, 'w') as f:
                json.dump(data, f)
            print(f"Data cached to {CACHE_PATH}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")