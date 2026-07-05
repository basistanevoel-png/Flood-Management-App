class ApiConfig {
  static const String baseUrl =
      'https://flood-monitoring-e7h6.onrender.com'; //change this based on the backend's deployment (either Railway, localhost, or other cloud hosting sites) :P

  //endpoints with no parameters
  static const String latestData = '$baseUrl/api/latest-data/';

  static const String vehicleThreshold = '$baseUrl/api/vehicle-thresholds/';

  static const String emergencyContacts = '$baseUrl/api/emergency/';

  //endpoints with parameters
  static const String locationSearch = '$baseUrl/api/location-search';

  static const String locationDetails = '$baseUrl/api/location-details/';

  static const String sensorHistory = '$baseUrl/api/history';

  static const String safeRoute = '$baseUrl/api/route/';

  static const String webChart = '$baseUrl/api/web-history';

  static const String userWeather = '$baseUrl/api/user-weather';

  static const String latestSpecific = '$baseUrl/api/latest-specific';
}
