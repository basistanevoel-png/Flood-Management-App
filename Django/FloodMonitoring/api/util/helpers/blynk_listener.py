from datetime import datetime, timezone
import time

from queue import Queue
import ssl, json, os
import requests

from api.supabase.utils import get_sensor_details_from_supabase
from api.utils import find_category

def fetch_blynk_data():

    payloads = []
    sensors = get_sensor_details_from_supabase()

    for sensor in sensors:
        if not sensor.get('token') or not sensor.get('pin'):
            print(f"[BLYNK] SENSOR: {sensor['sensor_id']} does not have designated token and pin. Skipping...")
            continue

        url = f"https://blynk.cloud/external/api/get?token={sensor['token']}&pin={sensor['pin']}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            value = float(response.text.strip())

            wlvl_now = max(0.0, sensor['ground_distance'] - value)

            payload = {
                "sensor_id": sensor['sensor_id'],
                "datetime": datetime.now(timezone.utc).isoformat(),
                "wlvl_now": wlvl_now,
                "flood_cat_now": find_category(wlvl_now),
                "latlong": [sensor["latitude"], sensor["longitude"]],
            }

            payloads.append(payload)

    return payloads