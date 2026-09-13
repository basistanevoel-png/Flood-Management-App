from rest_framework.response import Response
import math

from api.supabase.utils import get_classification_metrics, get_latest_data_from_supabase, get_latest_overall_analytics_from_supabase, get_regression_metrics, get_sensor_history_from_supabase, get_specific_sensor_details_from_supabase
from api.util.helpers.evaluator import get_severity

VEHICLE_PASSABLE = {
    "pedestrian": ["nf"],
    "bicycle": ["nf"],
    "motorcycle": ["nf", "patv"],
    "car": ["nf", "patv"],
    "truck": ["nf", "patv", "nplv"],
}

def format_latest_sensor_data():
    
    latest_sensor_data = get_latest_data_from_supabase()

    latest_overall_analytics = get_latest_overall_analytics_from_supabase()

    result = {
        "overall": {
            "total_sensors": latest_overall_analytics['total_sensors'],
            "active_sensors": latest_overall_analytics['active_sensors'],
            "offline_sensors": latest_overall_analytics['offline_sensors'],
            "rmse": latest_overall_analytics['rmse'],
            "mse": latest_overall_analytics['mse'],
            "mae": latest_overall_analytics['mae']
        }
    }

    for row in latest_sensor_data:
        sensor_id = row["sensor_id"]

        details = get_specific_sensor_details_from_supabase(sensor_id)
        flood_trend = get_sensor_history_from_supabase(sensor_id)

        prediction = row.get("prediction") or {}

        current = get_severity(row.get("wlvl_now"))
        forecast = get_severity(prediction.get("forecast"))

        classification_metrics = get_classification_metrics(sensor_id)
        regression_metrics = get_regression_metrics(sensor_id, 24)

        result[sensor_id] = {
            #datapoint-specific details
            "datetime": row["timestamp"],

            #sensor-specific details
            "latlong": details['latlong'],
            "ground_distance": details['ground_distance'],
            "radius": details['radius'],
            "location_name": details['location_name'],
            "availability": details['available?'],

            #flood-info-specific details
            "wlvl_now": row.get("wlvl_now"),
            "flood_cat_now": row.get("flood_cat_now"),
            "forecast": prediction.get("forecast"),
            "flood_cat": prediction.get("forecast_category"),

            #weather-specific details
            "temperature": row.get("temperature"),
            "pressure": row.get("pressure"),
            "description": row.get("description"),

            #vehicle-specific flood categories
            "current_severity": current,
            "forecast_severity": forecast,

            #feature details
            "wlvl_lag_1": row['wlvl_lag_t-1'],
            "wlvl_lag_2": row['wlvl_lag_t-2'],
            "wlvl_lag_5": row['wlvl_lag_t-5'],
            "wlvl_lag_10": row['wlvl_lag_t-10'],
            "diff_lag_1": row['diff_lag_t-1'],
            "pct_change_lag_1": row['pct_change_lag_t-1'],
            "slope_lag_10": row['slope_lag_t-10'],
            "rainfall_hr1": row['rainfall_hr1'],
            "rainfall_hr2": row['rainfall_hr2'],
            "rainfall_hr12": row['rainfall_hr12'],
            "rainfall_hr24": row['rainfall_hr24'],

            #per-sensor metric analytics
            "metrics": {
                "regression": regression_metrics,
                "classification": classification_metrics
            },

            #per-sensor 24-hr flood trend
            "hourly_data" : flood_trend['hourly_data'],
            "labels" : flood_trend['labels']
        }

    return result

def find_category(prediction: float):
    if prediction >= 0 and prediction < 0.1:
        return 'nf'
    elif prediction < 33.02 and prediction >= 0.1:
        return 'patv'
    elif prediction < 66.04 and prediction >= 33.02:
        return 'nplv'
    elif prediction > 66.04:
        return 'npatv'
    else:
        return 'inv'
    
def normalize_avoid_zones(zones):
    clean = []

    for z in zones:
        if not isinstance(z, dict):
            continue

        lat = z.get("lat")
        lng = z.get("lng")
        radius = z.get("radius")

        if lat is None or lng is None or radius is None:
            continue

        clean.append({
            "lat": float(lat),
            "lng": float(lng),
            "radius": float(radius),
        })

    return clean

def create_circle(lat, lng, radius_m, points=64):
    earth = 6371000
    coords = []

    for i in range(points + 1):
        angle = 2 * math.pi * i / points

        dx = radius_m * math.cos(angle)
        dy = radius_m * math.sin(angle)

        new_lat = lat + (dy / earth) * (180 / math.pi)
        new_lng = lng + (dx / earth) * (180 / math.pi) / math.cos(lat * math.pi / 180)

        coords.append([new_lng, new_lat])

    return coords

def build_avoid_polygons(avoid_zones):
    polygons = []

    for zone in avoid_zones:

        lat = zone.get("lat")
        lng = zone.get("lng")
        radius = zone.get("radius")

        if lat is None or lng is None or radius is None:
            continue

        circle = create_circle(lat, lng, radius)

        polygons.append([circle])

    return polygons

def clean_route_response(geojson):

    feature = geojson["features"][0]

    geometry = feature["geometry"]

    summary = (
        feature.get("properties", {})
        .get("summary", {})
    )

    return {
        "success": True,

        "route": {
            "type": geometry["type"],
            "coordinates": geometry["coordinates"],
        },

        "summary": {
            "distance_meters": summary.get("distance"),
            "duration_seconds": summary.get("duration"),
        }
    }

def api_response(success=True, data=None, message="", error=None, status=200):
    return Response({
        "success": success,
        "message": message,
        "data": data,
        "error": error
    }, status=status)

def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except:
        return default