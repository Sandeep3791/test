from django.urls import path
from wayrem_admin import views
from wayrem_admin.views.customer import PaymentForm

urlpatterns = [
    path('customers-list/', views.CustomersList.as_view(), name='customerslist'),
    path('excel_customers/', views.customers_excel, name='excelcustomer'),
    path('customerstatus/<str:id>/',
         views.Active_BlockCustomer.as_view(), name='customerstatus'),
    path('customer-details/<str:id>/',
         views.customer_details, name='customerdetails'),
    path('customer-verify/<str:id>/', views.customer_verification,
         name='customer_verification'),
    path('customer-email-update/<str:id>/',
         views.customer_email_update, name='customer_email_update'),
    path('customer-payment/', views.PaymentForm.as_view(), name='customer_payment'),
    path('hyperpay/payment', views.HyperpayPayment.as_view(),
         name='hyperpay_payment'),
    path('hyperpay/registration', views.HyperpayRegistration.as_view(),
         name='hyperpay_registration'),
    path('hyperpay/risk', views.HyperpayRisk.as_view(),
         name='hyperpay_risk'),


]
