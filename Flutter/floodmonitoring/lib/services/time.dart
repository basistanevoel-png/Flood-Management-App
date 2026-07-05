import 'package:intl/intl.dart';

String getCurrentTime() {
  final now = DateTime.now();
  final formatter = DateFormat('hh:mm a');
  return formatter.format(now);
}

String getCurrentDate() {
  final now = DateTime.now();
  final formatter = DateFormat('MMM d, yyyy');
  return formatter.format(now);
}
