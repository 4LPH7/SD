import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
SPACETRACK_USERNAME = os.getenv("SPACETRACK_USERNAME")
SPACETRACK_PASSWORD = os.getenv("SPACETRACK_PASSWORD")
BASE_URL = "https://www.space-track.org"
LOGIN_URL = f"{BASE_URL}/ajaxauth/login"

# --- Build the Query URL ---
# This is based on the recommended URL you provided, with two key additions:
# 1. OBJECT_TYPE/DEBRIS: To filter for only debris objects.
# 2. PREDICATES: To show essential fields like OBJECT_NAME, TLE_LINE1, TLE_LINE2, etc.
#    This makes the response cleaner and smaller.
query_url = (
    f"{BASE_URL}/basicspacedata/query/class/gp/OBJECT_TYPE/DEBRIS/"
    "DECAY_DATE/null-val/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID%20asc/"
    "format/json/predicates/OBJECT_NAME,NORAD_CAT_ID,TLE_LINE1,TLE_LINE2"
)

def fetch_space_debris_data():
    """
    Logs into Space-Track.org and fetches the latest TLE data for all
    on-orbit debris objects.
    """
    if not SPACETRACK_USERNAME or not SPACETRACK_PASSWORD:
        print("Error: Space-Track credentials not found in .env file.")
        return None

    # Use a session object to persist the login cookie
    with requests.Session() as session:
        print("Logging into Space-Track.org...")
        login_data = {
            "identity": SPACETRACK_USERNAME,
            "password": SPACETRACK_PASSWORD
        }
        
        try:
            # Step 1: Authenticate
            response = session.post(LOGIN_URL, data=login_data)
            response.raise_for_status()  # Will raise an exception for HTTP errors
            
            # The response might be empty or different from what we expect
            # Let's check if the response exists rather than its specific content
            if not response.text or response.status_code != 200:
                print(f"Login failed. Response: {response.text}")
                return None
            
            print("Login successful.")

            # Step 2: Fetch the debris data
            print(f"Fetching debris data from API...")
            response = session.get(query_url)
            response.raise_for_status()
            
            print(f"Successfully fetched data for {len(response.json())} debris objects.")
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

def process_and_display_data(debris_data):
    """
    Processes the fetched data and displays a sample.
    """
    if not debris_data:
        print("No data to process.")
        return

    print("\n--- Sample of Fetched Debris Data ---")
    for i, satellite in enumerate(debris_data[:5]): # Print first 5 for brevity
        name = satellite.get('OBJECT_NAME', 'N/A')
        norad_id = satellite.get('NORAD_CAT_ID', 'N/A')
        tle_line1 = satellite.get('TLE_LINE1', '')
        tle_line2 = satellite.get('TLE_LINE2', '')
        
        print(f"\nObject #{i+1}: {name} (NORAD ID: {norad_id})")
        print(f"  L1: {tle_line1}")
        print(f"  L2: {tle_line2}")

if __name__ == "__main__":
    data = fetch_space_debris_data()
    if data:
        process_and_display_data(data)
        # Here you would save the data to a cache (like Redis) or a file
        # for your backend API to use.
        with open('debris_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("\nFull dataset saved to debris_data.json")