from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('invoice-list/', views.InvoiceList.as_view(), name='invoicelist'),
    path('download_invoice/',views.DownloadInvoice.as_view(),name='downloadinvoice')
]
