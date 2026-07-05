import json

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.utils import api_response, build_avoid_polygons, normalize_avoid_zones
from api.util.data_collector import run_data_collection_cycle
from .supabase.utils import get_emergency_contacts_from_supabase, get_latest_data_from_supabase, get_latest_sensor_wl_data_from_supabase, get_sensor_history_from_supabase, get_specific_sensor_details_from_supabase, get_vehicle_thresholds_from_supabase, get_web_chart_data_from_supabase
import requests, os

@api_view(['POST'])
def run_data_collector(request):

    token = request.headers.get("Authorization")

    if token != f"Bearer {os.getenv('SECRET_TOKEN_FOR_LISTENER')}":
        return JsonResponse({"ok": False})

    run_data_collection_cycle()

    return JsonResponse({"ok": True})
@api_view(['GET'])
def get_latest_data(request): 

    """
    REQUEST:
    /api/latest-data/
    """

    latest_sensor_data = get_latest_data_from_supabase()

    result = {}

    for row in latest_sensor_data:
        sensor_id = row["sensor_id"]

        details = get_specific_sensor_details_from_supabase(sensor_id)

        prediction = row.get("prediction") or {}

        result[sensor_id] = {
            #datapoint-specific details
            "datetime": row["timestamp"],

            #sensor-specific details
            "latlong": details['latlong'],
            "ground_distance": details['ground_distance'],
            "radius": details['radius'],
            "location_name": details['location_name'],

            #flood-info-specific details
            "wlvl_now": row.get("wlvl_now"),
            "flood_cat_now": row.get("flood_cat_now"),
            "forecast": prediction.get("forecast"),
            "flood_cat": prediction.get("forecast_category"),

            #weather-specific details
            "temperature": row.get("temperature"),
            "pressure": row.get("pressure"),
            "description": row.get("description")
        }

    return api_response(
        success=True,
        data= result,
        message="Latest Sensor Data Retrieved"
    )

@api_view(['GET'])
def get_latest_specific_sensor_water_level_data(request):
    """
    REQUEST:
    /api/latest-specific?id=<sensor_id>
    """

    sensor_id = request.GET.get("id")

    if not sensor_id:
        return api_response(
            success=False,
            data=None,
            message="Missing sensor_id",
            status=400
        )

    data = get_latest_sensor_wl_data_from_supabase(sensor_id)

    if not data:
        return api_response(
            success=False,
            data=None,
            message="No data found for sensor",
            status=404
        )

    prediction = data.get("prediction") or {}

    result = {
        "wlvl_now": data.get("wlvl_now"),
        "flood_cat_now": data.get("flood_cat_now"),
        "forecast": prediction.get("forecast"),
        "flood_cat": prediction.get("forecast_category"),
        "lastUpdate": data.get("timestamp"),
    }

    return api_response(
        success=True,
        data=result,
        message="Latest Sensor Data Retrieved"
    )

@api_view(['GET'])
def get_vehicle_thresholds(request):

    raw = get_vehicle_thresholds_from_supabase()

    return api_response(
        success=True,
        data=raw,
        message="Vehicle thresholds retrieved"
    )

@api_view(['GET'])
def get_emergency_contacts(request):
    """
    REQUEST:
    /api/emergency/
    """    

    raw = get_emergency_contacts_from_supabase()

    return api_response(
        success=True,
        data=raw,
        message="Emergency Contacts retrieved"
    )

@api_view(['GET'])
def forward_geocode(request):#unused in flutter app, use this to switch to a more open-source api service
    """
    REQUEST:
    /api/location-search?q=<place_name>&viewbox=<optional>
    """

    query = request.GET.get("q")
    viewbox = request.GET.get("viewbox")

    nominatim_email = os.getenv("NOMINATIM_EMAIL")

    if not query:
        return api_response(
            success=False,
            error="query parameter 'q' is required",
            status=400
        )

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": 10,
        "addressdetails": 1,
    }

    if viewbox:
        params["viewbox"] = viewbox
        params["bounded"] = 1

    headers = {
        "User-Agent": f"Flood Detect Waze/1.0 ({nominatim_email})"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data:
            return Response({"error": "location not found"}, status=404)

        results = [
            {
                "lat": item.get("lat"),
                "lon": item.get("lon"),
                "display_name": item.get("display_name"),
                "address": item.get("address")
            }
            for item in data
        ]

        return api_response(
            success=True,
            data={
                "query": query,
                "results": results
            },
            message="Location results found"
        )

    except Exception as e:
        return api_response(
            success=False,
            error=str(e),
            status=500
        )
    
@api_view(['GET'])
def get_sensor_history(request):
    """
    REQUEST:
    /api/history?id=<sensor_id>
    """

    sensor_id = request.GET.get('id')

    if not sensor_id:
        return api_response(
            success=False,
            error="Missing sensor id",
            status=400
        )

    result = get_sensor_history_from_supabase(sensor_id)

    return api_response(
        success=True,
        data=result,
        message="Sensor history retrieved"
    )

@api_view(['GET'])
def get_web_chart_history(request):
    """
    REQUEST:
    /api/web-history?id=<sensor_id>
    """
    sensor_id = request.GET.get("id", "all")
    time_range = request.GET.get("range", "hour")

    result = get_web_chart_data_from_supabase(
        sensor_id,
        time_range
    )

    return api_response(
        success=True,
        data=result,
        message="Chart data retrieved"
    )

@api_view(['POST'])
def get_safe_route(request):
    try:
        body = request.data
        print("RAW BODY:", body)

        start = body.get("start")
        end = body.get("end")
        vehicle = body.get("vehicle", "driving-car")

        if not start or not end:
            return api_response(False, error="start/end required", status=400)

        avoid_zones = normalize_avoid_zones(body.get("avoid_zones", []))
        print("NORMALIZED ZONES:", avoid_zones)

        avoid_polygons = build_avoid_polygons(avoid_zones)
        print("POLYGONS:", avoid_polygons)

        payload = {
            "coordinates": [
                [start[1], start[0]],
                [end[1], end[0]]
            ]
        }

        if avoid_polygons:
            payload["options"] = {
                "avoid_polygons": {
                    "type": "MultiPolygon",
                    "coordinates": avoid_polygons
                }
            }

        print("FINAL ORS PAYLOAD:", json.dumps(payload, indent=2))

        response = requests.post(
            f"https://api.openrouteservice.org/v2/directions/{vehicle}/geojson",
            json=payload,
            headers={
                "Authorization": os.getenv("ORS_API_KEY"),
                "Content-Type": "application/json"
            },
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        coords = data["features"][0]["geometry"]["coordinates"]

        return api_response(
            True,
            data={"coordinates": coords},
            message="Route generated successfully"
        )

    except Exception as e:
        return api_response(False, error=str(e), status=500)

@api_view(['GET'])
def get_user_weather_info(request):

    try:
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")

        if latitude is None or longitude is None:
            return api_response(
                success=False,
                error="latitude and longitude are required",
                status=400
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return api_response(
                success=False,
                error="latitude and longitude must be valid numbers",
                status=400
            )

        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": os.getenv("OPENWEATHER_KEY"),
            "units": "metric"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather = (data.get("weather") or [{}])[0]

        result = {
            "temperature": data.get("main", {}).get("temp", 0.0),
            "description": weather.get("description", "N/A").title(),
            "pressure": data.get("main", {}).get("pressure", 0),
            "iconCode": weather.get("icon", "")
        }

        return api_response(
            success=True,
            data=result,
            message="Weather fetched successfully"
        )
    
    except Exception as e:
        return api_response(
            success=False,
            error=f"Unexpected error: {str(e)}",
            status=500
        )
    
@api_view(['GET'])
def search_places(request):

    query = request.GET.get("q")

    if not query:
        return api_response(
            success=False,
            error="Missing query parameter",
            status=400
        )

    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

    params = {
        "input": query,
        "components": "country:PH",
        "key": os.getenv("GOOGLEMAPS_API_KEY")
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        json_data = response.json()

        results = []

        for item in json_data.get("predictions", []):

            results.append({
                "place_id": item.get("place_id"),
                "name": item.get(
                    "structured_formatting",
                    {}
                ).get("main_text"),

                "description": item.get("description")
            })

        return api_response(
            success=True,
            data=results,
            message="Places retrieved"
        )

    except Exception as e:

        return api_response(
            success=False,
            error=str(e),
            status=500
        )
    
@api_view(['GET'])
def get_place_details(request):

    place_id = request.GET.get("id")

    if not place_id:

        return api_response(
            success=False,
            error="Missing place id",
            status=400
        )

    url = "https://maps.googleapis.com/maps/api/place/details/json"

    params = {
        "place_id": place_id,
        "fields": "geometry,name",
        "key": os.getenv("GOOGLEMAPS_API_KEY")
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        json_data = response.json()

        result = json_data.get("result", {})

        geometry = result.get("geometry", {})
        location = geometry.get("location", {})

        data = {
            "name": result.get("name"),
            "latlong": [
                location.get("lat"),
                location.get("lng")
            ]
        }

        return api_response(
            success=True,
            data=data,
            message="Place details retrieved"
        )

    except Exception as e:

        return api_response(
            success=False,
            error=str(e),
            status=500
        )