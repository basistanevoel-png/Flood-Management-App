import requests
import os
import time
import threading
import re
from datetime import datetime

def get_weather_from_api(latlong):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": latlong[0],
        "lon": latlong[1],
        "appid": os.getenv("OPENWEATHER_KEY"),
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    print("[WEATHER] response acquired: ", response)

    json_response = response.json()

    weather_list = json_response.get('weather', [])
    weather = weather_list[0] if weather_list else {}

    hourly_rainfall = json_response.get('rain', {}).get('1h', 0.00)
    
    other_weather_info = {
        'temperature': json_response.get('main', {}).get('temp', 0.0),

        'description': " ".join(
            word.capitalize() for word in weather.get('description', 'N/A').split()
        ),

        'pressure': json_response.get('main', {}).get('pressure', 0),

        'iconCode': re.sub(r'[a-zA-Z]', '', weather.get('icon', '')),
    }

    return hourly_rainfall, other_weather_info
