import 'dart:convert';
import 'package:floodmonitoring/services/global.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:google_maps_flutter/google_maps_flutter.dart';

class PlaceSearchPopup extends StatefulWidget {
  const PlaceSearchPopup({super.key});

  @override
  State<PlaceSearchPopup> createState() => _PlaceSearchPopupState();
}

class _PlaceSearchPopupState extends State<PlaceSearchPopup> {
  final TextEditingController _controller = TextEditingController();
  List<dynamic> _results = [];
  bool _loading = false;

  final List<Map<String, dynamic>> _famousPlaces = [
    {'name': 'Rizal Park, Manila', 'latLng': LatLng(14.5826, 120.9794)},
    {'name': 'SM Mall of Asia, Pasay', 'latLng': LatLng(14.5345, 120.9816)},
    {'name': 'Intramuros, Manila', 'latLng': LatLng(14.5897, 120.9744)},
    {'name': 'Fort Santiago, Manila', 'latLng': LatLng(14.5939, 120.9740)},
  ];

  /// 🔍 Google Places Autocomplete (Philippines only)
  Future<void> _searchPlace(String input) async {
    if (input.isEmpty) {
      setState(() => _results.clear());
      return;
    }

    setState(() => _loading = true);

    final url =
        'https://maps.googleapis.com/maps/api/place/autocomplete/json'
        '?input=$input'
        '&components=country:PH'
        '&key=$googleMapAPI';

    final res = await http.get(Uri.parse(url));
    final data = jsonDecode(res.body);

    setState(() {
      _results = data['predictions'] ?? [];
      _loading = false;
    });
  }

  /// 📍 Get place LatLng
  Future<void> _selectPlace(String placeId, String name) async {
    final url =
        'https://maps.googleapis.com/maps/api/place/details/json'
        '?place_id=$placeId'
        '&fields=geometry'
        '&key=$googleMapAPI';

    final res = await http.get(Uri.parse(url));
    final data = jsonDecode(res.body);

    final loc = data['result']['geometry']['location'];

    Navigator.pop(
      context,
      {
        'name': name,
        'latLng': LatLng(loc['lat'], loc['lng']),
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white, // ✅ White background
      body: SafeArea(
        child: Column(
          children: [
            // Top bar with back button
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: [
                  GestureDetector(
                    onTap: () => Navigator.pop(context),
                    child: const Icon(Icons.arrow_back, size: 28, color: Colors.black87),
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    "Select Location",
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),

            // Search Bar
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              padding: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(24),
                boxShadow: const [
                  BoxShadow(
                    color: Colors.black12,
                    blurRadius: 4,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: TextField(
                controller: _controller,
                autofocus: true,
                onChanged: _searchPlace,
                decoration: const InputDecoration(
                  hintText: 'Search for a place',
                  border: InputBorder.none,
                  icon: Icon(Icons.search),
                ),
              ),
            ),

            // Results
            Expanded(
              child: Container(
                decoration: const BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 10,
                      offset: Offset(0, -2),
                    ),
                  ],
                ),
                child: _loading
                    ? const Center(child: CircularProgressIndicator())
                    : ListView.separated(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemCount: _controller.text.isEmpty
                      ? _famousPlaces.length
                      : _results.length,
                  itemBuilder: (context, index) {
                    if (_controller.text.isEmpty) {
                      final place = _famousPlaces[index];
                      return ListTile(
                        leading: const Icon(Icons.star, color: Colors.orange),
                        title: Text(place['name']),
                        onTap: () {
                          Navigator.pop(context, {
                            'name': place['name'],
                            'latLng': place['latLng'],
                          });
                        },
                      );
                    } else {
                      final place = _results[index];
                      return ListTile(
                        leading: const Icon(Icons.location_on, color: Colors.blue),
                        title: Text(place['description']),
                        onTap: () => _selectPlace(
                          place['place_id'],
                          place['description'],
                        ),
                      );
                    }
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
