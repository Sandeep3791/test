from django.urls import path
from wayrem_supplier import views

urlpatterns = [
    path('supplier-product-list/', views.SupplierProductList.as_view(), name='supplier_product_list'),
    path('wayrem-product-list/', views.WayremproductList.as_view(), name='wayrem_product_list'),
    path('add-product/<str:id>/', views.add_product, name='add_product'),
    path('add-product-save/', views.add_product_save, name='add_product_save'),
    path('delete-product/', views.DeleteProduct.as_view(), name='deleteproduct'),
    path('supplier-product-update/<str:id>/', views.supplier_product_update, name='supplierproductupdate'),
    path('supplier-product-excel/', views.supplier_product_excel, name='supplierproductexcel'),

]