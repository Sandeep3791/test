from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("wayrem_admin.urls")),
    path('admin/', admin.site.urls),
]
