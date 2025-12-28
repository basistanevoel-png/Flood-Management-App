import 'package:flutter/material.dart';
import 'package:floodmonitoring/utils/style.dart';

class FloodTips extends StatefulWidget {
  const FloodTips({super.key});

  @override
  State<FloodTips> createState() => _FloodTipsState();
}

class _FloodTipsState extends State<FloodTips> {
  String selectedVehicle = 'Motorcycle';

  final Map<String, String> vehicleTips = {
    'Motorcycle': """
Motorcycles are extremely vulnerable in flooded areas. Avoid riding through water whenever possible. Even shallow water can cause loss of balance or stall the engine.  

• Always keep your engine revs high to prevent water from entering the exhaust.  
• Avoid sudden acceleration or braking to prevent skidding.  
• Look out for debris or potholes hidden under water.  
• Wear waterproof and reflective gear to stay visible.  
• If water depth is uncertain, wait for it to subside or take alternate routes.  
""",
    'Car': """
Cars can handle shallow water but still require caution. Driving through deeper water can lead to engine damage or loss of control.  

• Do not drive through water deeper than 15–20 cm.  
• Drive slowly and steadily; avoid sudden movements.  
• Keep an emergency kit including flashlight, food, and first-aid in your car.  
• Avoid flooded underpasses and low-lying areas.  
• After crossing water, check brakes immediately to ensure they are functioning properly.  
""",
    'Truck': """
Trucks have higher clearance but are not immune to flood risks. Strong currents can easily sweep even large trucks off the road.  

• Avoid crossing fast-flowing water or flooded bridges.  
• Drive in low gear and at low speed to prevent water from entering the engine.  
• Ensure cargo is secured to avoid shifting loads.  
• Take alternate elevated routes and avoid congested flooded areas.  
• Check tire grip and brakes after passing through water.  
""",
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Flood Safety Tips"),
        backgroundColor: color1,
      ),
      backgroundColor: Colors.white,
      body: Column(
        children: [
          // Vehicle selection buttons
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _vehicleButton('Motorcycle', 'assets/images/icons/motorcycle.png'),
                _vehicleButton('Car', 'assets/images/icons/car.png'),
                _vehicleButton('Truck', 'assets/images/icons/truck.png'),
              ],
            ),
          ),

          const SizedBox(height: 10),

          // Tips section scrollable
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: _card(
                title: "$selectedVehicle Tips & Safety",
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      vehicleTips[selectedVehicle] ?? "",
                      style: const TextStyle(fontSize: 16, height: 1.6),
                    ),
                    const SizedBox(height: 20),
                    // Optional Diagram / Illustration placeholder
                    Container(
                      width: double.infinity,
                      height: 180,
                      decoration: BoxDecoration(
                        color: Colors.red.shade50, // optional background color if needed
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade300),
                        image: const DecorationImage(
                          image: AssetImage('assets/images/flood-cars.png'),
                          fit: BoxFit.cover, // or BoxFit.cover depending on your preference
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "Always prioritize safety. If water levels are high, wait or take alternate routes. Flooded roads can hide deep potholes, debris, or strong currents that can easily endanger lives.",
                      style: const TextStyle(fontSize: 16, height: 1.5),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Vehicle selection button
  Widget _vehicleButton(String name, String iconPath) {
    bool isSelected = selectedVehicle == name;

    return GestureDetector(
      onTap: () {
        setState(() {
          selectedVehicle = name;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        decoration: BoxDecoration(
          color: isSelected ? color1 : Colors.white,
          borderRadius: BorderRadius.circular(40),
          boxShadow: isSelected
              ? [BoxShadow(color: Colors.black26, blurRadius: 4, offset: Offset(0, 2))]
              : [BoxShadow(color: Colors.black12, blurRadius: 3, offset: Offset(0, 2))],
        ),
        child: Row(
          children: [
            Image.asset(iconPath, width: 24, height: 24),
            const SizedBox(width: 8),
            Text(
              name,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.black87,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // General card
  Widget _card({required String title, required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
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
          Text(title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }
}
