from django.urls import path

from .sse import sensor_stream
from .views import get_emergency_contacts, get_latest_data, get_place_details, get_safe_route, get_sensor_history, get_user_weather_info, get_vehicle_thresholds, get_web_chart_history, run_data_collector, search_places

urlpatterns = [
    #SSE channels for the frontend (such as the web dashboard analytics and the Flutter App itself) to subscribe to for continuous and automatic data retrieval
    path('stream/sensors-channel/', sensor_stream),

    #Standard API Endpointss
    path('latest-data/', get_latest_data), 
    path('history/', get_sensor_history), 
    path('web-history/', get_web_chart_history),
    path('route/', get_safe_route),
    path('vehicle-thresholds/', get_vehicle_thresholds),
    path('emergency/', get_emergency_contacts),
    path('user-weather/', get_user_weather_info),
    path('location-search/', search_places),
    path('location-details/', get_place_details),

    #endpoints that should not be called from the App; starts with 'internal/'
    path('internal/collect-data', run_data_collector)
]