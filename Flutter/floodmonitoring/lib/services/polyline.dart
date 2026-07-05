import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:google_maps_flutter/google_maps_flutter.dart';

import 'package:floodmonitoring/services/api_configs.dart';

class PolylineService {
  static Future<List<LatLng>> getRoute(
    LatLng origin,
    LatLng destination,
    String vehicleType,
    List<Map<String, dynamic>> avoidZones,
  ) async {
    try {
      final payload = {
        "start": [origin.latitude, origin.longitude],
        "end": [destination.latitude, destination.longitude],
        "vehicle": vehicleType,
        "avoid_zones": avoidZones.map((z) {
          final pos = z["position"];

          return {
            "lat": pos.latitude,
            "lng": pos.longitude,
            "radius": (z["radius"] as num).toDouble(),
          };
        }).toList(),
      };

      final response = await http.post(
        Uri.parse(ApiConfig.safeRoute),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(payload),
      );

      final body = jsonDecode(response.body);

      if (response.statusCode == 200 && body["success"] == true) {
        final coordinates = body["data"]["coordinates"];

        return coordinates.map<LatLng>((coord) {
          return LatLng(coord[1], coord[0]);
        }).toList();
      }

      return [];
    } catch (e) {
      print("Route fetch error: $e");

      return [];
    }
  }
}
