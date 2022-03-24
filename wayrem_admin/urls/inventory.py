from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('list/', views.InventoriesList.as_view(), name='inventories'),
    path('add', views.InventoryCreate.as_view(), name='add_inventory'),
    path('<int:inventory_pk>',views.InventoryUpdate.as_view(),name='update_inventory'),
    path('view/<int:inventory_pk>',views.InventoryView.as_view(),name='view_inventory'),
    path('product_det_autocomplete/', views.InventoryAutocomplete.as_view(), name='product_det_autocomplete')
]
