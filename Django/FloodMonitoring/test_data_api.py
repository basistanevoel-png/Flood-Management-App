import requests
import json

BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/latest-data"

def test_get_latest_data():
    url = BASE_URL + ENDPOINT

    print(f"[TEST] Calling: {url}")

    try:
        response = requests.get(url, timeout=10)

        print(f"[STATUS] {response.status_code}")

        data = response.json()

        print("\n[RAW RESPONSE]")
        print(json.dumps(data, indent=2))

        # Basic validation
        if "forecasts" not in data:
            print("\n[FAIL] Missing 'forecasts' key")
            return

        forecasts = data["forecasts"]

        if not forecasts:
            print("\n[WARNING] forecasts is empty")
        else:
            print(f"\n[OK] Received {len(forecasts)} sensor(s)")

            for sensor_id, payload in forecasts.items():
                print(f"\nSensor: {sensor_id}")
                print(f"  Time: {payload.get('datetime')}")
                print(f"  WL: {payload.get('wlvl_now')}")
                print(f"  Forecast: {payload.get('forecast')}")
                print(f"  Category: {payload.get('flood_cat')}")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")

    except json.JSONDecodeError:
        print("[ERROR] Response is not valid JSON")


if __name__ == "__main__":
    test_get_latest_data()