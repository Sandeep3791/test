from django.urls import path
from wayrem_admin import views

urlpatterns = [
        path('', views.AvailableStock.as_view(), name='availablestock'),
        path('excel_export/', views.AvailableExportView.as_view(), name='availablestockexport'),
        
]
