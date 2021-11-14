from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]
