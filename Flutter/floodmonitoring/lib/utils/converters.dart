import 'package:intl/intl.dart';

class UnitConverter {
  // Convert CM to Inches
  static double cmToInches(double cm) {
    return cm * 0.393701;
  }

  // Optional: Convert CM to Feet
  static double cmToFeet(double cm) {
    return cm * 0.0328084;
  }
}

String formatToPHT(String utcString) {
  final utcTime = DateTime.parse(utcString).toUtc();

  // convert to Philippine Time (UTC+8)
  final phTime = utcTime.add(const Duration(hours: 8));

  return DateFormat('MMM d, yyyy • h:mm a').format(phTime);
}
