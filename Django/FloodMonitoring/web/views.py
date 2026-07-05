from django.shortcuts import render

# Dashboard view with session check
def dashboard_view(request):
    
    return render(request, 'web/dashboard.html')