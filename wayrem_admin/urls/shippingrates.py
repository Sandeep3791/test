from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('', views.ShippingRatesList.as_view(), name='shippingrates'),
    path('add', views.ShippingRatesCreate.as_view(), name='shippingratesadd'),
    path('<pk>', views.ShippingRatesUpdate.as_view(), name='shippingratesupdate'),
]
