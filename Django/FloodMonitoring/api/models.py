from django.db import models

class Sensor(models.Model):
    sensor_id = models.CharField(max_length=50, unique=True, primary_key=True, help_text="e.g., sensor_01")
    location_name = models.CharField(max_length=255, blank=True, help_text="e.g., Near basketball Court")
    
    # Position
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    
    # Connection Info
    token = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)
    radius = models.FloatField(default=100.0) # (Meter) Effective monitoring radius around the sensor
    height = models.FloatField(default=1.0) # (Meter) Height of the sensor from the ground in meters

    def __str__(self):
        return f"{self.sensor_id} - {self.location_name}"
    
class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, to_field='sensor_id',on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField(auto_now_add=True)
    water_level = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.sensor.sensor_id} - {self.timestamp} - {self.water_level}cm"