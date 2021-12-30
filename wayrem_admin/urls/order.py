from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('', views.OrdersList.as_view(), name='orderlist'),
    path('updateorderstatus/<int:id>', views.OrderStatusUpdated.as_view(), name='updateorderstatus'),
    path('invoice-order/<int:id>', views.OrderInvoiceView.as_view(), name='invoiceorder'),
    path('<pk>', views.OrderUpdateView.as_view(), name='orderupdate'),
    path('export-order/',views.OrderExportView.as_view(),name='exportorder')
]
