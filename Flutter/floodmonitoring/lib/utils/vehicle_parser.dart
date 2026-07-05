String convertVehicle(String selectedVehicle) {
  String vehicleString = '';

  selectedVehicle = selectedVehicle.toLowerCase();

  switch (selectedVehicle) {
    case "pedestrian":
      vehicleString = 'foot-walking';
      break;
    case "bicycle":
      vehicleString = 'cycling-road';
      break;
    case "motorcycle":
      vehicleString = 'driving-car';
      break;
    case "car":
      vehicleString = 'driving-car';
      break;
    case "truck":
      vehicleString = 'driving-hgv';
      break;
    default:
      vehicleString = 'driving-car';
      break;
  }

  return vehicleString;
}
