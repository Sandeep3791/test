from django.urls import path
from wayrem_supplier import views

urlpatterns = [
    path('purchase-order-list/', views.PurchaseOrderList.as_view(), name= 'purchase_order_list'),
    path('po-details/<str:id>', views.po_details, name='podetails'),
    path('po-details-invoice/<str:id>', views.po_details_invoice, name='podetailsinvoice'),
    path('edit-po-status/<str:id>', views.statuspo, name='po_status'), 
    path('po-excel/', views.po_excel, name='poexcel'),
    path('deny-comment/<str:id>', views.deny_comment, name='deny_comment'),
    path('delivered-status/', views.delivered_status, name='delivered_status'),
    path('invoice-status/', views.invoice_status, name='invoice_status'),
    path('pdf_po/', views.po_pdf, name='pdf_po'),
    
    # path('po-log-details/<str:id>', views.po_log_details, name='pologdetails'),    
]
