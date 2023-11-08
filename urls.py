from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking_app.urls')),
    path('contact/', include('booking_app.urls')),
]