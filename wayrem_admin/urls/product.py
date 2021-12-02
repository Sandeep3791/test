from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_product/', views.product_excel, name='excelproduct'),
    path('pdf_product/', views.pdf_product, name='productpdf'),
    path('inputBar/', views.inputBar, name='inputBar'),
    path('product/', views.product, name='product'),
    path('details/', views.details_gs1, name='get_detail'),
    path('ajax/load-supplier/', views.load_supplier, name='ajax_load_supplier'),
    path('product-view-one/', views.product_view_one, name='productviewone'),
    #    path('product-view-two/', views.product_view_two, name='productviewtwo'),
    #    path('product-view-three/', views.product_view_three, name='productviewthree'),
    #    path('product-view-four/', views.product_view_four, name='productviewfour'),
    path('product-list/', views.ProductList.as_view(), name='productlist'),
    path('product-details/<str:id>', views.product_details, name='productdetails'),
    path('update-product/<str:id>/', views.update_product, name='updateproduct'),
    path('delete-product/', views.DeleteProduct.as_view(), name='deleteproduct'),
    path('product-suppliers/', views.view_product_suppliers,
         name='viewprodsupplier'),
    path('lowest-price-suppliers/',
         views.lowest_price_supplier, name='lowest_price'),
    path('lowest-deliverable-suppliers/',
         views.lowest_deliverytime_supplier, name='lowest_time'),


]
