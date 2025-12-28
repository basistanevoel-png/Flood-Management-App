import 'package:flutter/material.dart';
import 'package:floodmonitoring/utils/style.dart'; // your color/style file
import 'package:url_launcher/url_launcher.dart'; // to make calls

class RescueCall extends StatefulWidget {
  const RescueCall({super.key});

  @override
  State<RescueCall> createState() => _RescueCallState();
}

class _RescueCallState extends State<RescueCall> {
  // Example contacts
  final List<Map<String, String>> emergencyContacts = [
    {
      "name": "Local Rescue Unit",
      "number": "09171234567",
      "description": "Immediate flood response"
    },
    {
      "name": "Fire Department",
      "number": "101",
      "description": "Emergency fire rescue"
    },
    {
      "name": "Police Station",
      "number": "911",
      "description": "Law enforcement / assistance"
    },
    {
      "name": "Hospital / Medical",
      "number": "09221234567",
      "description": "Medical emergencies"
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Emergency Contacts"),
        backgroundColor: color1,
      ),
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 10),
            _header(),
            const SizedBox(height: 20),
            ...emergencyContacts.map((contact) => _contactCard(contact)).toList(),
          ],
        ),
      ),
    );
  }

  // ----------------------------------------
  // UI WIDGETS
  // ----------------------------------------

  Widget _header() {
    return Row(
      children: [
        Icon(Icons.local_phone, color: Colors.deepOrange, size: 40),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Text("Stay Safe!",
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              Text("Quick access to emergency contacts",
                  style: TextStyle(color: Colors.black54)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _contactCard(Map<String, String> contact) {
    return Container(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(contact['name'] ?? "",
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(contact['description'] ?? "",
              style: const TextStyle(fontSize: 15, color: Colors.black54)),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(contact['number'] ?? "",
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              ElevatedButton.icon(
                onPressed: () => _makeCall(contact['number']),
                icon: const Icon(Icons.call, size: 18),
                label: const Text("Call"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: color1,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            ],
          )
        ],
      ),
    );
  }

  void _makeCall(String? number) async {
    if (number == null) return;
    final Uri callUri = Uri(scheme: 'tel', path: number);
    if (await canLaunchUrl(callUri)) {
      await launchUrl(callUri);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Cannot make a call at the moment.")),
      );
    }
  }
}
