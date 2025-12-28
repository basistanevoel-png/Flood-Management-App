import 'dart:async';
import 'package:floodmonitoring/services/weather.dart';
import 'package:flutter/material.dart';
import 'package:floodmonitoring/services/flood_level.dart';
import 'package:floodmonitoring/utils/style.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class Info extends StatefulWidget {
  const Info({super.key});

  @override
  State<Info> createState() => _InfoState();
}

class _InfoState extends State<Info> {
  final blynk = BlynkService();

  Map<String, Map<String, dynamic>> sensors = {
  };




  Timer? _timer;

  @override
  void initState() {
    super.initState();
    fetchDataForSensor("sensor_01");
    getWeather("sensor_01");

    _timer = Timer.periodic(const Duration(seconds: 1), (_) => fetchDataForSensor("sensor_01"));
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  ///Get Update For Specific Sensor
  Future<void> fetchDataForSensor(String sensorId) async {
    final sensor = sensors[sensorId];
    if (sensor == null) return;

    final String token = sensor['token'];
    final String pin = sensor['pin'];

    final data = await BlynkService().fetchDistance(token, pin);

    setState(() {
      sensors[sensorId]!['sensorData'] = data;
    });

    print("Updated $sensorId → pin=$pin → $data");
  }

  ///Get Data for Weather Update
  Future<void> getWeather(String sensorId) async {
    final sensor = sensors[sensorId];
    if (sensor == null) return;

    final weather = await loadWeather(
        sensor['position'].latitude, sensor['position'].longitude);

    if (weather != null) {
      setState(() {
        sensor['weatherData'] = {
          "temperature": weather['temperature'],
          "description": weather['description'],
          "pressure": weather['pressure'],
        };
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Sensor Information"),
        backgroundColor: color1,
      ),

      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            // SECTION: SENSOR HEADER
            _header(),

            const SizedBox(height: 20),

            // SECTION: LIVE MEASUREMENTS
            _liveMeasurements(),

            const SizedBox(height: 20),

            // SECTION: SENSOR DETAILS
            _sensorDetails(),

            const SizedBox(height: 20),

            // SECTION: WEATHER
            _weatherSection(),

            const SizedBox(height: 20),

            // SECTION: ALERTS
            _alertSection(),

            const SizedBox(height: 20),

            // ADVANCED
            _advancedSection(),
          ],
        ),
      ),
    );
  }

  // ----------------------------------------
  // UI WIDGETS
  // ----------------------------------------


  IconData statusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'safe':
        return Icons.check_circle_rounded;
      case 'warning':
        return Icons.warning_amber_rounded;
      case 'danger':
        return Icons.dangerous_rounded;
      default:
        return Icons.help_outline_rounded;
    }
  }

  Widget _header() {
    return Row(
      children: [
        Icon(Icons.sensors, color: Colors.deepOrange, size: 40),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Text("Ortigas Ave Sensor #1",
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              Text("Flood Monitoring Unit",
                  style: TextStyle(color: Colors.black54)),
            ],
          ),
        ),

        // STATUS CHIP
        Container(
          padding: const EdgeInsets.all(5),
          decoration: BoxDecoration(
            color: dataStatusColor(),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Icon(
            statusIcon(sensors["sensor_01"]!["sensorData"]['status']),
            color: Colors.white,
            size: 25,
          ),
        ),
      ],
    );
  }

  Color dataStatusColor() {
    switch (sensors["sensor_01"]!["sensorData"]['status']) {
      case 'Safe':
        return color_safe;
      case 'Warning':
        return color_warning;
      case 'Danger':
        return color_danger;
      default:
        return Colors.grey;
    }
  }

  Widget _liveMeasurements() {
    return _card(
      title: "Live Measurements",
      child: Column(
        children: [
          _item("Flood Height", "${sensors["sensor_01"]!["sensorData"]['floodHeight']} cm"),
          _item("Distance to Water", "${sensors["sensor_01"]!["sensorData"]['distance']} cm"),
          _item("Flood Status", sensors["sensor_01"]!["sensorData"]['status'], color: dataStatusColor()),
          _item("Last Update", sensors["sensor_01"]!["sensorData"]['lastUpdate']),
        ],
      ),
    );
  }

  Widget _sensorDetails() {
    return _card(
      title: "Sensor Details",
      child: Column(
        children: [
          _item("Location", "Ortigas Ave Sensor"),
          _item("Monitoring Radius", "20 meters"),
          _item("Battery Level", "85%"),
          _item("Connection", "Online"),
        ],
      ),
    );
  }

  Widget _weatherSection() {
    return _card(
      title: "Weather",
      child: Column(
        children: [
          _item("Temperature", "${sensors["sensor_01"]!["weatherData"]['temperature']}°C"),
          _item("Condition", "${sensors["sensor_01"]!["weatherData"]['description']}"),
          _item("Pressure", "${sensors["sensor_01"]!["weatherData"]['pressure']} hPa"),
        ],
      ),
    );
  }

  Widget _alertSection() {
    return _card(
      title: "Alerts",
      child: Column(
        children: const [
          Text("No active alerts",
              style: TextStyle(fontSize: 16, color: Colors.black54)),
        ],
      ),
    );
  }

  Widget _advancedSection() {
    return _card(
      title: "Advanced Info",
      child: Column(
        children: [
          _item("Sensor ID", "SN-1028391"),
          _item("Blynk Token", "••••••••••••••••••••"),
        ],
      ),
    );
  }

  // GENERAL CARD
  Widget _card({required String title, required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(
              color: Colors.black12, blurRadius: 6, offset: Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style:
              const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }

  // SINGLE ITEM
  Widget _item(String name, String value, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(name, style: const TextStyle(fontSize: 16)),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color ?? Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}
