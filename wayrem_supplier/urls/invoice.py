from django.urls import path
from wayrem_supplier import views

urlpatterns = [
    path('po-invoice-list/', views.PoInvoiceList.as_view(), name='poinvoicelist'),
    path('invoice-list/', views.InvoiceList.as_view(), name='invoicelist'),
    path('upload-invoice/', views.upload_invoice, name='uploadinvoice'),
    path('status-invoice/', views.status_invoice, name='statusinvoice'),
    path('delete-invoice/', views.DeleteInvoice.as_view(), name='deleteinvoice'),
    path('invoice-excel/', views.invoice_excel, name='invoiceexcel'),
    path('download_invoice/',views.DownloadInvoice.as_view(),name='downloadinvoice')

]