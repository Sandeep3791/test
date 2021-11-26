from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('customers-list/', views.CustomersList.as_view(), name='customerslist'),
    path('excel_customers/', views.customers_excel, name='excelcustomer'),
    path('customerstatus/<str:id>/',
         views.Active_BlockCustomer.as_view(), name='customerstatus'),
    path('customer-details/<str:id>/',
         views.customer_details, name='customerdetails'),

]
