from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from wayrem_admin.loginext.views import webhook_order_views,webhook_loginext_order_views
'''
path('order/createrequest',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'createorderrequest'}),name='createrequest'),
path('order/create',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'createorder'}),name='createorder'),
path('order/updateorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'updateorder'}),name='updateorder'),
path('order/orderstatusupdate',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'orderstatusupdate'}),name='orderstatusupdate'),
path('order/acceptedorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'acceptedorder'}),name='acceptedorder'),
path('order/rejectedorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'rejectedorder'}),name='rejectedorder'),
path('order/cancelorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'cancelorder'}),name='cancelorder'),
path('order/checkinorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'checkinorder'}),name='checkinorder'),
path('order/deliveredorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'deliveredorder'}),name='deliveredorder'),
path('order/attempteddeliveryorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'attempteddeliveryorder'}),name='attempteddeliveryorder'),
path('order/partiallydeliveredorder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'partiallydeliveredorder'}),name='partiallydeliveredorder'),
path('order/pickeduporder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'pickeduporder'}),name='pickeduporder'),
path('order/orderattemptedpickuporder',webhook_order_views.LogiNextWeebHookOrderAPI.as_view({'post': 'orderattemptedpickuporder'}),name='orderattemptedpickuporder'),
'''
urlpatterns = [
    
    path('order/createrequest',webhook_loginext_order_views.LogiNextCreateRequestAPI.as_view(),name='createrequest'),
    path('order/create',webhook_loginext_order_views.LogiNextCreateOrderAPI.as_view(),name='createorder'),
    path('order/updateorder',webhook_loginext_order_views.LogiNextUpdateOrderAPI.as_view(),name='updateorder'),
    path('order/orderstatusupdate',webhook_loginext_order_views.LogiNextorderStatusUpdateAPI.as_view(),name='orderstatusupdate'),
    path('order/acceptedorder',webhook_loginext_order_views.LogiNextAcceptedOrderAPI.as_view(),name='acceptedorder'),
    path('order/rejectedorder',webhook_loginext_order_views.LogiNextRejectedOrderAPI.as_view(),name='rejectedorder'),
    path('order/cancelorder',webhook_loginext_order_views.LogiNextCancelOrderAPI.as_view(),name='cancelorder'),
    path('order/checkinorder',webhook_loginext_order_views.LogiNextCheckinOrderAPI.as_view(),name='checkinorder'),
    path('order/deliveredorder',webhook_loginext_order_views.LogiNextDeliveredOrderAPI.as_view(),name='deliveredorder'),
    path('order/attempteddeliveryorder',webhook_loginext_order_views.LogiNextAttemptedDeliveryOrderAPI.as_view(),name='attempteddeliveryorder'),
    path('order/partiallydeliveredorder',webhook_loginext_order_views.LogiNextPartiallyDeliveredOrderAPI.as_view(),name='partiallydeliveredorder'),
    path('order/pickeduporder',webhook_loginext_order_views.LogiNextPickedupOrderAPI.as_view(),name='pickeduporder'),
    path('order/orderattemptedpickuporder',webhook_loginext_order_views.LogiNextOrderAttemptedPickupOrderAPI.as_view(),name='orderattemptedpickuporder'),

    path('order/cashtransaction',webhook_loginext_order_views.LogiNextCashTransactionAPI.as_view(),name='ordercashtransaction'),

]
