import 'dart:convert';
import 'package:floodmonitoring/services/api_configs.dart';
import 'package:http/http.dart' as http;
import 'package:google_maps_flutter/google_maps_flutter.dart';

class SensorService {
  Future<Map<String, Map<String, dynamic>>> loadSensorsList() async {
    try {
      var res = await http.get(Uri.parse(ApiConfig.latestData));

      var response = jsonDecode(res.body);

      Map<String, Map<String, dynamic>> tempSensors = {};

      if (res.statusCode == 200 && response["success"] == true) {
        final data = response["data"];

        data.forEach((sensorId, item) {
          tempSensors[sensorId] = {
            "position": LatLng(
              double.parse(item["latlong"][0].toString()),
              double.parse(item["latlong"][1].toString()),
            ),
            "radius": double.parse(item["radius"].toString()),
            "height": double.parse(item["ground_distance"].toString()),
            "location": item["location_name"].toString(),

            // Initialize sensor metrics with placeholder "Loading" values
            "sensorData": {
              "distance": 0.0,
              "floodHeight": double.parse(item['wlvl_now'].toString()),
              "floodCatNow": item['flood_cat_now'].toString(),
              "forecast": double.parse(item['forecast'].toString()),
              "floodForecastCat": item['flood_cat'].toString(),
              "status": "Loading...",
              "forecastedStatus": "Loading...",
              "lastUpdate": item['datetime'].toString(),
            },

            // Initialize environmental data placeholders
            "weatherData": {
              "temperature": item['temperature'].toString(),
              "description": item['description'].toString(),
              "pressure": item['pressure'].toString(),
            },
          };
        });
      }
      return tempSensors;
    } catch (e) {
      // Log connection or parsing errors and return an empty map to prevent crashes
      print("Error fetching sensors: $e");
      return {};
    }
  }
}
