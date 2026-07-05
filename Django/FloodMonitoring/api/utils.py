from datetime import datetime
from rest_framework.response import Response
import math

VEHICLE_PASSABLE = {
    "pedestrian": ["nf"],
    "bicycle": ["nf"],
    "motorcycle": ["nf", "patv"],
    "car": ["nf", "patv"],
    "truck": ["nf", "patv", "nplv"],
}

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