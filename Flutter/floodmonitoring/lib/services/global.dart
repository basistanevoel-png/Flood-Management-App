

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

String serverUri = "http://0.0.0.0:8000";


const String googleMapAPI = "YOUR GOOGLE API KEY";
const String hereAPIKey = "YOUR HERE API KEY";
const String mapboxAPI = "YOUR MAPBOX API KEY";


Position? currentPosition;

String selectedVehicle = "Motorcycle";

int sensorHeight = 200;



final List<Map<String, dynamic>> floodStatuses = [
  {
    "text": "Safe",
    "color": const Color(0xFF4CAF50), // Green
    "icon": Icons.check_circle,
    "message": "No flooding detected."
  },
  {
    "text": "Warning",
    "color": const Color(0xFFFFC107), // Yellow
    "icon": Icons.warning_amber_rounded,
    "message": "Rising water level, stay alert."
  },
  {
    "text": "Danger",
    "color": const Color(0xFFF44336), // Red
    "icon": Icons.error,
    "message": "Flooding likely, move to higher ground."
  },
];



