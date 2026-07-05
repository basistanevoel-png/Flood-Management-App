import 'dart:convert';
import 'package:floodmonitoring/services/api_configs.dart';
import 'package:http/http.dart' as http;

class ThresholdService {
  Future<List<Map<String, dynamic>>> loadThresholdsList() async {
    try {
      final res = await http.get(
        Uri.parse(ApiConfig.vehicleThreshold),
        headers: {"Content-Type": "application/json"},
      );

      final response = jsonDecode(res.body);

      List<Map<String, dynamic>> tempThresholds = [];

      if (res.statusCode == 200 && response["success"] == true) {
        final data = response["data"];

        for (var item in data) {
          tempThresholds.add({
            // Vehicle type
            "vehicle": item["vehicle_type"],

            // Safe range
            "safeRange_cm": [
              double.parse(item["safe_min"].toString()),
              double.parse(item["safe_max"].toString()),
            ],

            // Warning range
            "warningRange_cm": [
              double.parse(item["warning_min"].toString()),
              double.parse(item["warning_max"].toString()),
            ],

            // Danger range
            "dangerRange_cm": [
              double.parse(item["danger_min"].toString()),
              double.infinity,
            ],
          });
        }

        print("Vehicle thresholds loaded: ${tempThresholds.length}");
      } else {
        print("Failed to fetch thresholds: ${response["message"]}");
      }

      return tempThresholds;
    } catch (e) {
      print("Error fetching thresholds: $e");
      return [];
    }
  }
}
