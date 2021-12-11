from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_supplier/', views.supplier_excel, name='excelsupplier'),
    path('supplier-registration/', views.supplier_register, name='suppregister'),
    path('supplier-list/', views.SupplierList.as_view(), name='supplierlist'),
    path('delete-supplier/', views.DeleteSupplier.as_view(), name='deletesupplier'),
    path('activeblock-supplier/<str:id>/',
         views.Active_BlockSupplier.as_view(), name='activeblocksupplier'),
    path('update-supplier/<str:id>/',
         views.update_supplier, name='updatesupplier'),
    path('supplier-details/<str:id>/',
         views.supplier_details, name='supplierdetails'),
    path('allproduct-supplier/', views.allproductsupplier, name='allproductsupplier'),
    path('supplier-product-po/', views.supplier_products_po, name='supplier_product_po'),
#     path('lowest-price-supplierview/<str:id>/',views.lowest_price_supplierview,name = 'lowest_price_supplierview')

]
