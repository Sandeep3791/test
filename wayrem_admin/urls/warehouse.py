from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('list/', views.WarehouseList.as_view(), name='warehouses'),
    path('add', views.WarehouseCreate.as_view(), name='add_warehouse'),
    path('<int:warehouse_pk>',views.WarehouseUpdate.as_view(),name='update_warehouse'),
    path('view/<int:warehouse_pk>',views.WarehouseView.as_view(),name='view_warehouse'),
]
