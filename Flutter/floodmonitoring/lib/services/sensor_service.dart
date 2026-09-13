import 'dart:async';
import 'dart:convert';
import 'package:floodmonitoring/services/api_configs.dart';
import 'package:floodmonitoring/services/global.dart';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;

class SensorService {
  final StreamController<void> _sensorStreamController =
      StreamController<void>.broadcast();
  Stream<void> get stream => _sensorStreamController.stream;

  bool _connected = false;
  bool _connecting = false;
  bool get isConnected => _connected;
  StreamSubscription<String>? _subscription;

  SensorService._();
  static final SensorService instance = SensorService._();

  final Map<String, Map<String, dynamic>> sensors = {};

  Future<void> connect({
    Function()? onConnected,
    Function(dynamic error)? onError,
  }) async {
    debugPrint("CONNECT() CALLED");

    if (_connected || _connecting) {
      debugPrint(
        "CONNECT() IGNORED — "
        "connected=$_connected, connecting=$_connecting",
      );
      return;
    }

    _connecting = true;

    try {
      final request = http.Request("GET", Uri.parse(ApiConfig.sensorStream));
      request.headers.addAll({
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      });
      final response = await request.send();

      if (response.statusCode != 200) {
        throw Exception("Unable to connect to SSE");
      }

      _connected = true;

      onConnected?.call();
      _subscription = response.stream
          .transform(utf8.decoder)
          .transform(const LineSplitter())
          .listen(
            (line) {
              debugPrint("SSE [$hashCode] RECEIVED: $line");

              if (!line.startsWith("data: ")) {
                return;
              }

              if (line.startsWith(":")) {
                debugPrint("SSE [$hashCode] HEARTBEAT");
                return;
              }

              if (line.trim().isEmpty) {
                return;
              }

              final rawData = line.substring(6).trim();

              if (rawData.isEmpty) {
                return;
              }

              // Ignore heartbeat/null events
              if (rawData == "null") {
                debugPrint("SSE heartbeat/null event received.");
                return;
              }

              try {
                final jsonData = jsonDecode(rawData);

                if (jsonData is! Map<String, dynamic>) {
                  debugPrint("SSE invalid JSON structure: $jsonData");
                  return;
                }

                if (jsonData["type"] != "sensor_update") {
                  debugPrint("SSE ignored event type: ${jsonData["type"]}");
                  return;
                }

                final data = jsonData["data"];

                if (data is! Map<String, dynamic>) {
                  debugPrint("SSE sensor data is invalid: $data");
                  return;
                }

                final parsed = parseSensors(data);

                sensors
                  ..clear()
                  ..addAll(parsed);

                _sensorStreamController.add(null);
              } catch (e, stackTrace) {
                debugPrint("SSE JSON parse error: $e");
                debugPrint("$stackTrace");
              }
            },
            onError: (exception) {
              debugPrint("SSE [$hashCode] ERROR: $exception");

              _connected = false;
              _subscription = null;

              onError?.call(exception);
            },
            onDone: () {
              debugPrint("SSE [$hashCode] CLOSED");

              _connected = false;
              _subscription = null;
            },
            cancelOnError: false,
          );
    } catch (e) {
      _connected = false;
      onError?.call(e);
    } finally {
      _connecting = false;
    }
  }

  Future<void> disconnect() async {
    await _subscription?.cancel();
    _subscription = null;
    _connected = false;
  }

  Future<void> reconnect({
    Function()? onConnected,
    Function(dynamic error)? onError,
  }) async {
    debugPrint("SSE RECONNECT()");

    await disconnect();

    await connect(onConnected: onConnected, onError: onError);
  }

  void dispose() {}

  Future<void> loadInitialSensors() async {
    final sensorData = await _loadSensorsFromAPI();

    sensors
      ..clear()
      ..addAll(sensorData);

    _sensorStreamController.add(null);
  }

  Map<String, Map<String, dynamic>> parseSensors(Map<String, dynamic> data) {
    Map<String, Map<String, dynamic>> tempSensors = {};

    data.forEach((sensorId, item) {
      if (sensorId == "overall") {
        return;
      }

      if (item is! Map<String, dynamic>) {
        return;
      }

      final floodHeight = double.tryParse(item["wlvl_now"].toString()) ?? 0.0;
      final forecastHeight =
          double.tryParse(item["forecast"].toString()) ?? 0.0;

      final status = getStatusText(floodHeight);
      final forecastStatus = getStatusText(forecastHeight);

      tempSensors[sensorId] = {
        "position": LatLng(
          double.parse(item["latlong"][0].toString()),
          double.parse(item["latlong"][1].toString()),
        ),
        "radius": double.parse(item["radius"].toString()),
        "height": double.parse(item["ground_distance"].toString()),
        "location": item["location_name"].toString().length > 12
            ? "${item["location_name"].toString().substring(0, 12)}..."
            : item["location_name"].toString(),

        "sensorData": {
          "distance": 0.0,
          "floodHeight": floodHeight,
          "floodCatNow": item['flood_cat_now'].toString(),
          "forecast": forecastHeight,
          "floodForecastCat": item['flood_cat'].toString(),
          "status": (status.isNotEmpty) ? status : "Loading...",
          "forecastedStatus": (forecastStatus.isNotEmpty)
              ? forecastStatus
              : "Loading...",
          "lastUpdate": item['datetime'].toString(),
        },

        "weatherData": {
          "temperature": item['temperature'].toString(),
          "description": item['description'].toString(),
          "pressure": item['pressure'].toString(),
        },
      };
    });

    return tempSensors;
  }

  static String getStatusText(double floodHeightCm) {
    if (selectedVehicle.isEmpty) return "";

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

  void refreshStatuses() {
    sensors.forEach((_, sensor) {
      final sensorData = sensor["sensorData"];

      final floodHeight = (sensorData["floodHeight"] as num).toDouble();

      final forecast = (sensorData["forecast"] as num).toDouble();

      sensorData["status"] = getStatusText(floodHeight);

      sensorData["forecastedStatus"] = getStatusText(forecast);
    });

    _sensorStreamController.add(null);
  }

  Future<Map<String, Map<String, dynamic>>> _loadSensorsFromAPI() async {
    try {
      final res = await http.get(Uri.parse(ApiConfig.latestData));

      if (res.statusCode != 200) {
        return {};
      }

      final response = jsonDecode(res.body);

      if (response["success"] != true) {
        return {};
      }

      return parseSensors(response["data"]);
    } catch (e) {
      debugPrint("Error fethcing sensors: $e");
      return {};
    }
  }
}
