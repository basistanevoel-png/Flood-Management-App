from django.shortcuts import render
from api.models import Sensor

# Dashboard view with session check
def dashboard_view(request):
    
    return render(request, 'web/dashboard.html')