from django.urls import path
from wayrem_admin import views

urlpatterns = [
    path('', views.OrdersList.as_view(), name='orderlist'),
    path('updateorderstatus/<int:id>', views.OrderStatusUpdated.as_view(), name='updateorderstatus'),
    path('update-payment-status/<int:id>', views.OrderPaymentStatusUpdated.as_view(), name='updatepaymentstatusstatus'),
    path('invoice-order/<int:id>', views.OrderInvoiceView.as_view(), name='invoiceorder'),
    path('<pk>', views.OrderUpdateView.as_view(), name='orderupdate'),
    path('export-order/',views.OrderExportView.as_view(),name='exportorder'),

    path('invoice-orders/<int:id>', views.OrderReferenceExport.as_view(), name='invoiceorders'),
    path('wallet/<int:id>', views.WalletList.as_view(), name='walletlistcreate'),
    path('wallet-way/<int:id>', views.WalletCustomerPay.as_view(), name='walletpay'),
    
    path('cancel-clone-order/<int:id>',views.OrderCancelCloneOrder.as_view(), name='cancelcloneorder'),
    path('insert-order-detail/<int:id>/<int:pid>',views.InsertOrderdetail.as_view(), name='insertorderdetail'),
    path('clone-order/<pk>', views.CloneOrderView.as_view(), name='cloneorder'),
    path('ajax_calls/search', views.AutoCompleteModelView.as_view(), name='autocompletemodel'),
    path('removeorder/', views.OrderRemoveDetail.as_view(), name='removeorderdetail'),
    path('updateorder/', views.OrderUpdateDetail.as_view(), name='updateorderdetail'),
    path('clonecreateorder/<int:id>',views.Clonecreateorder.as_view(),name='clonecreateorder')

]
