from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('', views.OrdersList.as_view(), name='orderlist'),
 
   

]
