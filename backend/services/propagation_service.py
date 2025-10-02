import json
import os
import numpy as np
from skyfield.api import load, EarthSatellite

CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', 'cache', 'debris_data.json')
ts = load.timescale()

def get_current_debris_positions():
    """Loads cached debris data and calculates the current position and velocity for each object."""
    try:
        with open(CACHE_PATH, 'r') as f:
            debris_catalog = json.load(f)
    except FileNotFoundError:
        print("Error: Debris data cache not found. Run scheduler.py first.")
        return []

    positions = []
    now = ts.now()

    for debris in debris_catalog:
        try:
            satellite = EarthSatellite(
                debris['TLE_LINE1'],
                debris['TLE_LINE2'],
                debris.get('OBJECT_NAME', 'UNKNOWN'),
                ts
            )
            geocentric = satellite.at(now)
            
            # Get position
            lat, lon = geocentric.subpoint().latitude.degrees, geocentric.subpoint().longitude.degrees
            alt_km = geocentric.subpoint().elevation.km

            # Get velocity
            velocity_kms = geocentric.velocity.km_per_s
            speed_kms = np.linalg.norm(velocity_kms)

            positions.append({
                "id": debris['NORAD_CAT_ID'],
                "name": debris.get('OBJECT_NAME', 'UNKNOWN'),
                "lat": lat,
                "lon": lon,
                "alt": alt_km,
                "vel": round(speed_kms, 2)
            })
        except Exception as e:
            # Some TLEs might be invalid or out of date
            # print(f"Could not propagate NORAD ID {debris['NORAD_CAT_ID']}: {e}")
            continue
            
    return positions