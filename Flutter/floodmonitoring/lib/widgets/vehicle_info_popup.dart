import 'package:floodmonitoring/services/global.dart';
import 'package:floodmonitoring/utils/style.dart';
import 'package:flutter/material.dart';

class VehicleInfoPopup {
  // Added optional callback
  static void show(BuildContext context, String vehicleName, {Function()? onConfirm}) {
    final data = _vehicleData[vehicleName];
    if (data == null) return;

    showDialog(
      context: context,
      barrierDismissible: false, // cannot tap outside
      builder: (context) {
        return WillPopScope(
          onWillPop: () async => false, // prevent back button
          child: Dialog(
            backgroundColor: Colors.transparent,
            insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 40),
            child: StatefulBuilder(
              builder: (context, setState) {
                return Container(
                  width: 350, // fixed width
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 10,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // TITLE
                      Text(
                        vehicleName,
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 10),

                      // DESCRIPTION
                      Text(
                        data.description,
                        style: const TextStyle(fontSize: 14, height: 1.4),
                      ),
                      const SizedBox(height: 16),

                      // LEVELS
                      _levelRow("Safe", data.safe, Colors.green),
                      _levelRow("Warning", data.warning, Colors.orange),
                      _levelRow("Danger", data.danger, Colors.red),
                      const SizedBox(height: 24),

                      // BUTTON ROW
                      Row(
                        children: [
                          // CANCEL BUTTON
                          Expanded(
                            child: SizedBox(
                              height: 50,
                              child: OutlinedButton(
                                style: OutlinedButton.styleFrom(
                                  side: BorderSide(color: color1, width: 2),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                                onPressed: () {
                                  setState(() {
                                    selectedVehicle = "";
                                  });
                                  Navigator.pop(context);
                                },
                                child: const Text(
                                  "CANCEL",
                                  style: TextStyle(
                                    color: color1,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                ),
                              ),
                            ),
                          ),

                          const SizedBox(width: 12),

                          // CONFIRM BUTTON
                          Expanded(
                            child: SizedBox(
                              height: 50,
                              child: ElevatedButton(
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: color1,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                                onPressed: () {
                                  // Call the callback from map.dart
                                  if (onConfirm != null) onConfirm();
                                  Navigator.pop(context);
                                },
                                child: const Text(
                                  "CONFIRM",
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        );
      },
    );
  }

  static Widget _levelRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            "$label: ",
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
          Text(value),
        ],
      ),
    );
  }

  static final Map<String, _VehicleFloodInfo> _vehicleData = {
    "Motorcycle": _VehicleFloodInfo(
      description:
      "Motorcycles are very vulnerable to floods even at low levels. "
          "Unlike cars and trucks, they can easily lose balance or submerge. "
          "Extra caution is needed when riding in flood-prone areas.",
      safe: "0–20 cm",
      warning: "20.1–50 cm",
      danger: "50.1+ cm",
    ),
    "Car": _VehicleFloodInfo(
      description:
      "Cars can normally withstand floods that are below the door step. "
          "They are less vulnerable than motorcycles but may still be at risk "
          "if water rises higher than the engine level.",
      safe: "0–15 cm",
      warning: "15.1–30 cm",
      danger: "30.1+ cm",
    ),
    "Truck": _VehicleFloodInfo(
      description:
      "Trucks can handle large floods because of their size and higher chassis. "
          "They are the safest among common vehicles in deep water, but caution "
          "is still advised in extreme flood conditions.",
      safe: "0–40 cm",
      warning: "40.1–60 cm",
      danger: "60.1+ cm",
    ),
  };
}

class _VehicleFloodInfo {
  final String description;
  final String safe;
  final String warning;
  final String danger;

  const _VehicleFloodInfo({
    required this.description,
    required this.safe,
    required this.warning,
    required this.danger,
  });
}
