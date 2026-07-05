import 'dart:convert';
import 'package:floodmonitoring/services/global.dart';
import 'package:http/http.dart' as http;
import 'package:floodmonitoring/services/api_configs.dart';
import 'package:floodmonitoring/services/time.dart';

class FloodLevel {
  static Future<Map<String, dynamic>> fetchLatestSensorData(
    String sensorId,
  ) async {
    try {
      final uri = Uri.parse(
        ApiConfig.latestSpecific,
      ).replace(queryParameters: {"id": sensorId});

      final response = await http.get(uri);

      final body = jsonDecode(response.body);
      print("latest sensor data in flood_level.dart: ${body}");

      if (response.statusCode == 200 && body["success"] == true) {
        final data = body["data"];

        final floodHeight = (data["wlvl_now"] ?? 0).toDouble();
        final forecastHeight = (data["forecast"] ?? 0).toDouble();

        final status = getStatusText(floodHeight);
        final forecastStatus = getStatusText(forecastHeight);

        return {
          "floodHeight": floodHeight,
          "floodCatNow": data["flood_cat_now"].toString(),
          "forecast": forecastHeight,
          "floodForecastCat": data["flood_cat"].toString(),
          "status": status,
          "forecastedStatus": forecastStatus,
          "lastUpdate": data["lastUpdate"].toString(),
        };
      } else {
        throw Exception(body["error"] ?? "Failed to fetch data");
      }
    } catch (e) {
      print("Error fetching latest sensor data: $e");

      return {
        "floodHeight": null,
        "floodCatNow": "-",
        "forecast": null,
        "floodForecastCat": "-",
        "status": "Error",
        "forecastedStatus": "Error",
        "lastUpdate": getCurrentTime(),
      };
    }
  }

  static String getStatusText(double floodHeightCm) {
    final vehicleThreshold = vehicleFloodThresholds.firstWhere(
      (v) => v["vehicle"] == selectedVehicle,
      orElse: () => vehicleFloodThresholds[0],
    );

    if (floodHeightCm <= vehicleThreshold["safeRange_cm"][1]) {
      return 'Safe';
    } else if (floodHeightCm <= vehicleThreshold["warningRange_cm"][1]) {
      return 'Warning';
    } else {
      return 'Danger';
    }
  }
}
