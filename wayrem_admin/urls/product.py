from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('excel_product/', views.product_excel, name='excelproduct'),
    path('inputBar/', views.inputBar, name='inputBar'),
    path('update_prodimg/', views.update_product_images,
         name='update_product_images'),
    path('product/', views.ProductCreate.as_view(), name='product'),
    path('product-barcode/', views.BarcodeProduct.as_view(), name='product_barcode'),
    path('details/', views.details_gs1, name='get_detail'),
    path('product-scan/', views.scan_result, name='scaned_product'),
    path('ajax/load-supplier/', views.load_supplier, name='ajax_load_supplier'),
    path('ajax/load-category-margin/', views.load_category_margin,
         name='ajax_load_category_margin'),
    path('product-view-one/', views.product_view_one, name='productviewone'),
    path('product-view-two/', views.product_images, name='product_images'),
    path('product-list/', views.ProductList.as_view(), name='productlist'),
    path('product-details/<str:id>',
         views.product_details, name='productdetails'),
    path('update-product/<str:id>/', views.update_product, name='updateproduct'),
    path('delete-product/', views.DeleteProduct.as_view(), name='deleteproduct'),
    path('product-suppliers/', views.view_product_suppliers,
         name='viewprodsupplier'),
    path('lowest-price-suppliers/',
         views.lowest_price_supplier, name='lowest_price'),
    path('lowest-deliverable-suppliers/',
         views.lowest_deliverytime_supplier, name='lowest_time'),
    path('delete_prodimg/', views.delete_product_images,
         name='delete_product_images'),
    path('import-excel/', views.import_excel, name="import_excel"),
    path('import-products/', views.import_products, name="importproducts"),
    path('import-products-result/', views.import_result, name="import_result"),
    path('import-image-status/', views.check_import_status, name="image_import"),
    path('publish-import/', views.bulk_publish_excel, name="bulk_publish"),
    path('price-import/', views.bulk_price_excel, name="bulk_price"),
    path('quantity-import/', views.bulk_quantity_excel, name="bulk_quantity"),
    path('import-single-image/', views.import_single_image,
         name="import_single_image"),



]
